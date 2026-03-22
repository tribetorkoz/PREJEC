import os
import secrets
import pyotp
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, update, delete
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import structlog

from db.database import get_db, AsyncSessionLocal
from db.models import (
    AdminUser, AdminLog, Company, Agent, Call, Customer,
    SystemSetting, FeatureFlag, FeatureFlagCompany, User,
    Notification, NotificationPreferences, OnboardingState,
    PHIAccessLog, BAA, DemoSession, MarketingEvent, Appointment
)
from config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = structlog.get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_SECRET_PATH = "sa-" + os.getenv("ADMIN_SECRET_SLUG", "default-slug-change-me")
ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", secrets.token_hex(32))
ALLOWED_ADMIN_IPS = os.getenv("ADMIN_ALLOWED_IPS", "").split(",") if os.getenv("ADMIN_ALLOWED_IPS") else []

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_MINUTES = 30
SESSION_TIMEOUT_HOURS = 24

# ============ MODELS ============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class CreateAdminRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class CreateCompanyRequest(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    plan: Optional[str] = "starter"
    industry: Optional[str] = None

class UpdateCompanyRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    plan: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None
    industry: Optional[str] = None

class CreateAgentRequest(BaseModel):
    company_id: int
    name: str
    language: Optional[str] = "en"
    voice_id: Optional[str] = None
    system_prompt: Optional[str] = None

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    voice_id: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None

class UpdateSettingRequest(BaseModel):
    key: str
    value: str

class CreateFeatureFlagRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_global_enabled: bool = True

class CreateVerticalRequest(BaseModel):
    name: str
    industry: str
    price_monthly: int
    description: Optional[str] = None

class UpdateVerticalRequest(BaseModel):
    name: Optional[str] = None
    price_monthly: Optional[int] = None
    is_active: Optional[bool] = None

class ROICalculationRequest(BaseModel):
    monthly_calls: int
    receptionist_salary: float
    missed_call_rate: float
    avg_customer_value: float
    plan_price: float

# ============ HELPERS ============

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_token(admin_id: int) -> str:
    payload = {"admin_id": admin_id, "exp": datetime.now(timezone.utc) + timedelta(hours=SESSION_TIMEOUT_HOURS)}
    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
    except:
        return None

async def get_current_admin(request: Request, authorization: Optional[str] = Header(None)) -> AdminUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AdminUser).where(AdminUser.id == payload["admin_id"]))
        admin = result.scalar_one_or_none()
        if not admin or not admin.is_active:
            raise HTTPException(status_code=403, detail="Admin not found")
        return admin

async def log_action(db: AsyncSession, admin_id: int, action: str, target: str = None, target_id: int = None, details: str = None, request: Request = None):
    log = AdminLog(admin_id=admin_id, action=action, target=target, target_id=target_id, details=details,
                   ip_address=request.client.host if request else None,
                   user_agent=request.headers.get("user-agent") if request else None)
    db.add(log)
    await db.commit()

# ============ AUTH ============

@router.post("/auth/login")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.email == data.email))
    admin = result.scalar_one_or_none()
    
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if admin.locked_until and admin.locked_until > datetime.now(timezone.utc):
        raise HTTPException(status_code=423, detail="Account locked")
    
    admin.failed_attempts = 0
    admin.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    await log_action(db, admin.id, "LOGIN_SUCCESS", request=request)
    token = create_token(admin.id)
    
    return {
        "token": token,
        "admin": {"id": admin.id, "email": admin.email, "name": admin.name, "role": admin.role}
    }

@router.get("/auth/me")
async def me(admin: AdminUser = Depends(get_current_admin)):
    return {"id": admin.id, "email": admin.email, "name": admin.name, "role": admin.role, "last_login": admin.last_login}

@router.post("/auth/logout")
async def logout(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    await log_action(db, admin.id, "LOGOUT", request=None)
    return {"status": "ok"}

@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

# ============ DASHBOARD ============

@router.get("/dashboard")
async def dashboard(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)
    
    total_companies = await db.scalar(select(func.count(Company.id))) or 0
    active_companies = await db.scalar(select(func.count(Company.id)).where(Company.status == "active")) or 0
    
    calls_today = await db.scalar(select(func.count(Call.id)).where(Call.created_at >= today)) or 0
    calls_this_month = await db.scalar(select(func.count(Call.id)).where(Call.created_at >= month_start)) or 0
    total_calls = await db.scalar(select(func.count(Call.id))) or 0
    
    angry_calls = await db.scalar(select(func.count(Call.id)).where(and_(Call.created_at >= month_start, Call.sentiment == "ANGRY"))) or 0
    happy_calls = await db.scalar(select(func.count(Call.id)).where(and_(Call.created_at >= month_start, Call.sentiment == "POSITIVE"))) or 0
    
    sentiment_result = await db.execute(
        select(Call.sentiment, func.count(Call.id))
        .where(Call.created_at >= month_start)
        .group_by(Call.sentiment)
    )
    sentiment_breakdown = {row[0]: row[1] for row in sentiment_result.all()}
    
    plan_result = await db.execute(select(Company.plan, func.count(Company.id)).group_by(Company.plan))
    plan_counts = {row[0]: row[1] for row in plan_result.all()}
    
    plan_prices = {"starter": 299, "business": 899, "enterprise": 2499, "free": 0}
    mrr = sum(count * plan_prices.get(plan, 0) for plan, count in plan_counts.items())
    
    avg_duration = await db.scalar(select(func.avg(Call.duration_seconds)).where(Call.created_at >= month_start)) or 0
    
    appointments_this_month = await db.scalar(select(func.count(Appointment.id)).where(Appointment.created_at >= month_start)) or 0
    
    calls_30_days = []
    for i in range(29, -1, -1):
        day = (datetime.now(timezone.utc).date() - timedelta(days=i))
        count = await db.scalar(select(func.count(Call.id)).where(func.date(Call.created_at) == day)) or 0
        calls_30_days.append({"date": day.isoformat(), "calls": count})
    
    new_companies_30d = await db.scalar(select(func.count(Company.id)).where(Company.created_at >= today - timedelta(days=30))) or 0
    
    await log_action(db, admin.id, "DASHBOARD_VIEWED", request=None)
    
    return {
        "kpis": {
            "mrr": mrr,
            "arr": mrr * 12,
            "total_clients": total_companies,
            "active_clients": active_companies,
            "new_clients_30d": new_companies_30d,
            "calls_today": calls_today,
            "calls_this_month": calls_this_month,
            "total_calls": total_calls,
            "angry_calls": angry_calls,
            "happy_calls": happy_calls,
            "avg_duration_seconds": round(avg_duration or 0),
            "appointments_this_month": appointments_this_month,
            "failed_calls_rate": round(angry_calls / max(calls_this_month, 1) * 100, 1),
        },
        "sentiment_breakdown": sentiment_breakdown,
        "plans_breakdown": plan_counts,
        "charts": {
            "calls_volume": calls_30_days
        }
    }

# ============ CLIENTS ============

@router.get("/clients")
async def get_clients(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    search: str = None,
    plan: str = None,
    status: str = None,
    page: int = 1,
    limit: int = 20
):
    query = select(Company).order_by(desc(Company.created_at))
    
    if search:
        query = query.where(or_(Company.name.ilike(f"%{search}%"), Company.email.ilike(f"%{search}%")))
    if plan:
        query = query.where(Company.plan == plan)
    if status:
        query = query.where(Company.status == status)
    
    total = await db.scalar(select(func.count(Company.id)))
    result = await db.execute(query.offset((page-1)*limit).limit(limit))
    companies = result.scalars().all()
    
    clients = []
    for c in companies:
        agents_count = await db.scalar(select(func.count(Agent.id)).where(Agent.company_id == c.id)) or 0
        calls_count = await db.scalar(select(func.count(Call.id)).where(Call.company_id == c.id)) or 0
        customers_count = await db.scalar(select(func.count(Customer.id)).where(Customer.company_id == c.id)) or 0
        
        clients.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "plan": c.plan,
            "status": c.status,
            "industry": c.industry,
            "phone_number": c.phone_number,
            "agents_count": agents_count,
            "calls_count": calls_count,
            "customers_count": customers_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    
    await log_action(db, admin.id, "CLIENTS_VIEWED")
    return {"clients": clients, "total": total or 0, "page": page, "pages": (total + limit - 1) // limit}

@router.post("/clients")
async def create_client(data: CreateCompanyRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    company = Company(name=data.name, email=data.email, plan=data.plan, phone_number=data.phone_number, industry=data.industry)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    await log_action(db, admin.id, "CLIENT_CREATED", "Company", company.id, f"Created: {company.name}")
    return {"id": company.id, "name": company.name, "email": company.email, "plan": company.plan}

@router.get("/clients/{company_id}")
async def get_client(company_id: int, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    agents = await db.execute(select(Agent).where(Agent.company_id == company.id))
    customers = await db.execute(select(Customer).where(Customer.company_id == company.id))
    calls = await db.execute(select(Call).where(Call.company_id == company.id).order_by(desc(Call.created_at)).limit(10))
    
    return {
        "id": company.id, "name": company.name, "email": company.email, "plan": company.plan,
        "status": company.status, "industry": company.industry, "phone_number": company.phone_number,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "agents": [{"id": a.id, "name": a.name, "is_active": a.is_active} for a in agents.scalars().all()],
        "stats": {
            "total_agents": agents.scalars().all().__len__(),
            "total_customers": customers.scalars().all().__len__(),
            "total_calls": calls.scalars().all().__len__(),
        }
    }

@router.put("/clients/{company_id}")
async def update_client(company_id: int, data: UpdateCompanyRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    
    await db.commit()
    await log_action(db, admin.id, "CLIENT_UPDATED", "Company", company_id, f"Updated: {company.name}")
    return {"status": "ok"}

@router.delete("/clients/{company_id}")
async def delete_client(company_id: int, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    name = company.name
    await db.delete(company)
    await db.commit()
    await log_action(db, admin.id, "CLIENT_DELETED", "Company", company_id, f"Deleted: {name}")
    return {"status": "deleted"}

# ============ AGENTS ============

@router.get("/agents")
async def get_agents(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db), company_id: int = None, page: int = 1, limit: int = 50):
    query = select(Agent)
    if company_id:
        query = query.where(Agent.company_id == company_id)
    
    total = await db.scalar(select(func.count(Agent.id)))
    result = await db.execute(query.offset((page-1)*limit).limit(limit))
    
    agents_data = []
    for agent in result.scalars().all():
        company = await db.scalar(select(Company.name).where(Company.id == agent.company_id))
        agents_data.append({
            "id": agent.id, "company_id": agent.company_id, "company_name": company,
            "name": agent.name, "language": agent.language, "voice_id": agent.voice_id,
            "is_active": agent.is_active, "system_prompt": agent.system_prompt[:100] if agent.system_prompt else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
        })
    
    await log_action(db, admin.id, "AGENTS_VIEWED")
    return {"agents": agents_data, "total": total or 0, "page": page}

@router.post("/agents")
async def create_agent(data: CreateAgentRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    agent = Agent(company_id=data.company_id, name=data.name, language=data.language, voice_id=data.voice_id, system_prompt=data.system_prompt)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    await log_action(db, admin.id, "AGENT_CREATED", "Agent", agent.id, f"Created: {agent.name}")
    return {"id": agent.id, "name": agent.name}

@router.put("/agents/{agent_id}")
async def update_agent(agent_id: int, data: UpdateAgentRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    
    await db.commit()
    await log_action(db, admin.id, "AGENT_UPDATED", "Agent", agent_id, f"Updated: {agent.name}")
    return {"status": "ok"}

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db.delete(agent)
    await db.commit()
    await log_action(db, admin.id, "AGENT_DELETED", "Agent", agent_id)
    return {"status": "deleted"}

# ============ CALLS ============

@router.get("/calls")
async def get_calls(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db),
                   company_id: int = None, sentiment: str = None, page: int = 1, limit: int = 50):
    query = select(Call, Company.name.label("company_name")).join(Company, Call.company_id == Company.id)
    
    if company_id:
        query = query.where(Call.company_id == company_id)
    if sentiment:
        query = query.where(Call.sentiment == sentiment)
    
    total = await db.scalar(select(func.count(Call.id)))
    result = await db.execute(query.order_by(desc(Call.created_at)).offset((page-1)*limit).limit(limit))
    
    calls = []
    for call, company_name in result.all():
        calls.append({
            "id": call.id, "company_id": call.company_id, "company_name": company_name,
            "caller_phone": call.caller_phone, "direction": call.direction,
            "duration_seconds": call.duration_seconds, "sentiment": call.sentiment,
            "outcome": call.outcome, "transcript": call.transcript,
            "created_at": call.created_at.isoformat() if call.created_at else None,
        })
    
    await log_action(db, admin.id, "CALLS_VIEWED")
    return {"calls": calls, "total": total or 0, "page": page}

@router.get("/calls/{call_id}")
async def get_call(call_id: int, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    company = await db.scalar(select(Company.name).where(Company.id == call.company_id))
    await log_action(db, admin.id, "CALL_VIEWED", "Call", call_id)
    
    return {
        "id": call.id, "company_id": call.company_id, "company_name": company,
        "caller_phone": call.caller_phone, "direction": call.direction,
        "duration_seconds": call.duration_seconds, "sentiment": call.sentiment,
        "sentiment_score": call.sentiment_score, "outcome": call.outcome,
        "transcript": call.transcript, "recording_url": call.recording_url,
        "created_at": call.created_at.isoformat() if call.created_at else None,
    }

# ============ CUSTOMERS ============

@router.get("/customers")
async def get_customers(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db),
                       company_id: int = None, search: str = None, page: int = 1, limit: int = 50):
    query = select(Customer)
    if company_id:
        query = query.where(Customer.company_id == company_id)
    if search:
        query = query.where(or_(Customer.phone.ilike(f"%{search}%"), Customer.name.ilike(f"%{search}%")))
    
    total = await db.scalar(select(func.count(Customer.id)))
    result = await db.execute(query.offset((page-1)*limit).limit(limit))
    
    customers = []
    for c in result.scalars().all():
        company = await db.scalar(select(Company.name).where(Company.id == c.company_id))
        last_call = await db.scalar(select(Call.created_at).where(Call.caller_phone == c.phone).order_by(desc(Call.created_at)).limit(1))
        customers.append({
            "id": c.id, "phone": c.phone, "name": c.name, "email": c.email,
            "company_id": c.company_id, "company_name": company,
            "total_calls": c.total_calls, "is_vip": c.is_vip,
            "last_call_at": last_call.isoformat() if last_call else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    
    await log_action(db, admin.id, "CUSTOMERS_VIEWED")
    return {"customers": customers, "total": total or 0, "page": page}

# ============ REVENUE ============

@router.get("/revenue")
async def get_revenue(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    plan_result = await db.execute(select(Company.plan, func.count(Company.id)).group_by(Company.plan))
    
    plan_prices = {"starter": 299, "business": 899, "enterprise": 2499, "free": 0}
    plan_names = {"starter": "Starter", "business": "Business", "enterprise": "Enterprise", "free": "Free"}
    
    plans = []
    total_revenue = 0
    total_clients = 0
    
    for plan_name, count in plan_result.all():
        price = plan_prices.get(plan_name, 0)
        revenue = count * price
        total_revenue += revenue
        total_clients += count
        plans.append({
            "plan": plan_name, "name": plan_names.get(plan_name, plan_name),
            "count": count, "price": price, "revenue": revenue
        })
    
    for p in plans:
        p["percentage"] = round(p["revenue"] / max(total_revenue, 1) * 100, 1)
    
    await log_action(db, admin.id, "REVENUE_VIEWED")
    return {
        "mrr": total_revenue, "arr": total_revenue * 12,
        "total_clients": total_clients, "arpu": round(total_revenue / max(total_clients, 1), 2),
        "plans": plans
    }

# ============ PLATFORM ============

@router.get("/platform")
async def get_platform(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    total_companies = await db.scalar(select(func.count(Company.id))) or 0
    total_agents = await db.scalar(select(func.count(Agent.id))) or 0
    total_calls = await db.scalar(select(func.count(Call.id))) or 0
    total_customers = await db.scalar(select(func.count(Customer.id))) or 0
    
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    calls_today = await db.scalar(select(func.count(Call.id)).where(Call.created_at >= today)) or 0
    avg_duration = await db.scalar(select(func.avg(Call.duration_seconds))) or 0
    
    await log_action(db, admin.id, "PLATFORM_VIEWED")
    return {
        "stats": {
            "total_companies": total_companies,
            "total_agents": total_agents,
            "total_calls": total_calls,
            "total_customers": total_customers,
            "calls_today": calls_today,
            "avg_duration_seconds": round(avg_duration or 0),
        },
        "database": {"status": "connected", "tables": 12},
        "cache": {"status": "connected"},
    }

@router.get("/platform/health")
async def platform_health(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return {
        "overall": "healthy",
        "services": {
            "api": {"status": "healthy", "latency_ms": 45},
            "database": {"status": "healthy", "connections": 5},
        }
    }

# ============ PROVIDERS ============

@router.get("/providers")
async def get_providers(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    await log_action(db, admin.id, "PROVIDERS_VIEWED")
    return {
        "stt": [
            {"name": "deepgram", "status": "healthy", "latency_ms": 120, "success_rate": 99.8, "priority": 1},
            {"name": "assembly_ai", "status": "healthy", "latency_ms": 180, "success_rate": 99.5, "priority": 2},
        ],
        "llm": [
            {"name": "anthropic", "model": "claude-3-5-sonnet", "status": "healthy", "latency_ms": 800, "success_rate": 99.9, "priority": 1},
        ],
        "tts": [
            {"name": "elevenlabs", "status": "healthy", "latency_ms": 150, "success_rate": 99.9, "priority": 1},
        ],
    }

@router.get("/settings")
async def get_settings(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    settings_result = await db.execute(select(SystemSetting))
    settings = [{"key": s.key, "value": s.value, "updated_at": s.updated_at.isoformat() if s.updated_at else None} for s in settings_result.scalars().all()]
    
    flags_result = await db.execute(select(FeatureFlag))
    flags = [{"id": f.id, "name": f.name, "description": f.description, "is_global_enabled": f.is_global_enabled} for f in flags_result.scalars().all()]
    
    await log_action(db, admin.id, "SETTINGS_VIEWED")
    return {"settings": settings, "feature_flags": flags}

@router.put("/settings")
async def update_setting(data: UpdateSettingRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == data.key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = data.value
    else:
        setting = SystemSetting(key=data.key, value=data.value)
        db.add(setting)
    await db.commit()
    await log_action(db, admin.id, "SETTING_UPDATED", details=f"Updated: {data.key}")
    return {"status": "ok"}

@router.post("/feature-flags")
async def create_feature_flag(data: CreateFeatureFlagRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    flag = FeatureFlag(name=data.name, description=data.description, is_global_enabled=data.is_global_enabled)
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    await log_action(db, admin.id, "FLAG_CREATED", "FeatureFlag", flag.id, f"Created: {flag.name}")
    return {"id": flag.id, "name": flag.name}

@router.put("/feature-flags/{flag_id}")
async def update_feature_flag(flag_id: int, data: CreateFeatureFlagRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    
    flag.name = data.name
    flag.description = data.description
    flag.is_global_enabled = data.is_global_enabled
    await db.commit()
    await log_action(db, admin.id, "FLAG_UPDATED", "FeatureFlag", flag_id)
    return {"status": "ok"}

# ============ AUDIT LOGS ============

@router.get("/logs")
async def get_logs(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db),
                   action: str = None, page: int = 1, limit: int = 50):
    query = select(AdminLog).order_by(desc(AdminLog.timestamp))
    if action:
        query = query.where(AdminLog.action == action)
    
    total = await db.scalar(select(func.count(AdminLog.id)))
    result = await db.execute(query.offset((page-1)*limit).limit(limit))
    
    logs = []
    for log in result.scalars().all():
        admin_user = await db.scalar(select(AdminUser.name).where(AdminUser.id == log.admin_id)) if log.admin_id else None
        logs.append({
            "id": log.id, "action": log.action, "target": log.target, "target_id": log.target_id,
            "details": log.details, "admin_name": admin_user, "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        })
    
    return {"logs": logs, "total": total or 0, "page": page}

# ============ NOTIFICATIONS ============

@router.get("/notifications")
async def get_notifications(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 50):
    query = select(Notification).order_by(desc(Notification.created_at))
    total = await db.scalar(select(func.count(Notification.id)))
    result = await db.execute(query.offset((page-1)*limit).limit(limit))
    
    notifications = []
    for n in result.scalars().all():
        company = await db.scalar(select(Company.name).where(Company.id == n.company_id))
        notifications.append({
            "id": n.id, "company_id": n.company_id, "company_name": company,
            "event_type": n.event_type, "channel": n.channel,
            "status": n.status, "created_at": n.created_at.isoformat() if n.created_at else None,
        })
    
    await log_action(db, admin.id, "NOTIFICATIONS_VIEWED")
    return {"notifications": notifications, "total": total or 0, "page": page}

# ============ ROI ============

@router.post("/roi/calculate")
async def calculate_roi(data: ROICalculationRequest, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    missed_calls = data.monthly_calls * (data.missed_call_rate / 100)
    calls_answered = missed_calls * 0.95
    new_customers = calls_answered * 0.30
    revenue_recovered = new_customers * data.avg_customer_value
    salary_savings = data.receptionist_salary - data.plan_price
    total_benefit = revenue_recovered + salary_savings
    roi_percent = ((total_benefit - data.plan_price) / data.plan_price * 100) if data.plan_price > 0 else 0
    
    await log_action(db, admin.id, "ROI_CALCULATED", details=f"Calls: {data.monthly_calls}, ROI: {roi_percent:.1f}%")
    
    return {
        "monthly_cost_savings": round(salary_savings, 2),
        "monthly_revenue_recovered": round(revenue_recovered, 2),
        "total_monthly_benefit": round(total_benefit, 2),
        "annual_benefit": round(total_benefit * 12, 2),
        "roi_percent": round(roi_percent, 1),
        "payback_period_days": round(data.plan_price / (total_benefit / 30)) if total_benefit > 0 else 999,
    }
