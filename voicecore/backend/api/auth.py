from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime, timezone
from typing import Optional
import jwt
import secrets
from passlib.context import CryptContext

from db.database import get_db
from db.models import Company, Agent, User
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_jwt_secret() -> str:
    return settings.effective_jwt_secret


class RegisterRequest(BaseModel):
    company_name: str
    full_name: str
    email: EmailStr
    password: str
    phone: str
    industry: str = "general"
    plan: str = "starter"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    user_id: int
    company_id: int
    email: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, _get_jwt_secret(), algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Dependency to get the current authenticated user from cookie or header."""
    token = request.cookies.get("access_token")
    
    # Also check Authorization header
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


@router.post("/register")
async def register(reg_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    existing_user = await db.execute(select(User).where(User.email == reg_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_company = await db.execute(select(Company).where(Company.email == reg_data.email))
    if existing_company.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create company
    valid_plans = ["starter", "business"]
    plan = reg_data.plan if reg_data.plan in valid_plans else "starter"
    
    company = Company(
        name=reg_data.company_name,
        email=reg_data.email,
        phone_number=reg_data.phone,
        industry=reg_data.industry,
        plan=plan,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)

    # Create user with hashed password
    user = User(
        company_id=company.id,
        email=reg_data.email,
        password_hash=pwd_context.hash(reg_data.password),
        full_name=reg_data.full_name,
        role="owner",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create default agent
    agent = Agent(
        company_id=company.id,
        name=f"{company.name} Agent",
        language="en",
        is_active=True,
    )
    db.add(agent)
    await db.commit()

    # Generate token
    token = create_access_token({
        "sub": reg_data.email,
        "user_id": user.id,
        "company_id": company.id,
    })

    response = JSONResponse(
        content={
            "message": "Registered successfully",
            "company_id": company.id,
            "user_id": user.id,
        }
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )

    return response


@router.post("/login")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Look up user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    # Verify password
    if not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # Generate token
    token = create_access_token({
        "sub": login_data.email,
        "user_id": user.id,
        "company_id": user.company_id,
    })

    response = JSONResponse(
        content={
            "message": "Login successful",
            "company_id": user.company_id,
            "user_id": user.id,
        }
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    return response


@router.get("/me")
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Load company
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "company_id": user.company_id,
        "company_name": company.name if company else None,
        "plan": company.plan if company else None,
    }


@router.get("/google")
async def google_auth():
    if not settings.google_client_id:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    redirect_uri = f"{settings.next_public_api_url}/api/auth/google/callback"
    
    auth_url = (
        f"{google_auth_url}"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid email profile"
    )
    
    return {"url": auth_url}


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    
    try:
        import httpx
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": f"{settings.next_public_api_url}/api/auth/google/callback",
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_result = token_response.json()
            
            access_token = token_result.get("access_token")
            
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
            
            email = user_info.get("email")
            name = user_info.get("name", "")
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not provided by Google")
            
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                company = Company(
                    name=f"{name}'s Company",
                    email=email,
                    plan="free",
                )
                db.add(company)
                await db.commit()
                await db.refresh(company)
                
                user = User(
                    company_id=company.id,
                    email=email,
                    password_hash=pwd_context.hash(secrets.token_hex(16)),
                    full_name=name,
                    role="owner",
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            
            token = create_access_token({
                "sub": email,
                "user_id": user.id,
                "company_id": user.company_id,
            })
            
            response = JSONResponse(content={
                "message": "Login successful",
                "company_id": user.company_id,
                "user_id": user.id,
            })
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=settings.access_token_expire_minutes * 60,
            )
            return response
            
    except httpx.HTTPError as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(status_code=400, detail=f"Google OAuth failed: {str(e)}")
