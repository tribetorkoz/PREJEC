from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy import text
import structlog
import time
import logging
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from db.database import init_db
from config import settings, PLAN_PRICES
from api.agents import router as agents_router
from api.calls import router as calls_router
from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.billing import router as billing_router
from api.webhooks import router as webhooks_router
from api.voice import router as voice_router
from api.companies import router as companies_router
from api.customers import router as customers_router
from api.onboarding import router as onboarding_router
from api.notifications import router as notifications_router
from api.demo import router as demo_router
from api.public.router import router as public_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting VoiceCore API...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down VoiceCore API...")


app = FastAPI(
    title="VoiceCore API",
    description="B2B Voice AI Agent Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ===== Enterprise Rate Limiting =====
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ===== Structlog Configuration =====
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if not settings.frontend_url.startswith("http://localhost") else structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# CORS middleware - restrict in production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    settings.frontend_url,
]
# Remove empty strings and duplicates
allowed_origins = list(set(o for o in allowed_origins if o))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# ===== Static Files Serving (at root level) =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Request timing middleware
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


# Include routers
app.include_router(auth_router)
app.include_router(agents_router, prefix="/api/v1")
app.include_router(calls_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(billing_router)
app.include_router(webhooks_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(onboarding_router)
app.include_router(notifications_router)
app.include_router(demo_router)
app.include_router(public_router)


# Try to include admin router (optional - may not exist in all deployments)
try:
    from api.admin import router as admin_router
    app.include_router(admin_router)
except ImportError:
    logger.info("Admin router not available")


# ===== Mount Static Files Directory =====
if os.path.exists(BASE_DIR):
    try:
        app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")


# ===== Static HTML Files =====
@app.get("/super-admin.html")
async def super_admin_page():
    path = os.path.join(BASE_DIR, "super-admin.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse(content="<h1>Super Admin not found</h1>", status_code=404)

@app.get("/admin-login.html")
async def admin_login_page():
    path = os.path.join(BASE_DIR, "admin-login.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse(content="<h1>Login page not found</h1>", status_code=404)

@app.get("/landing.html")
async def landing_page():
    path = os.path.join(BASE_DIR, "landing.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse(content="<h1>Landing page not found</h1>", status_code=404)

@app.get("/")
async def root_page():
    path = os.path.join(BASE_DIR, "landing.html")
    if os.path.exists(path):
        return FileResponse(path)
    path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse(content="<h1>VoiceCore</h1><p><a href='/landing.html'>Go to Landing</a></p>", status_code=200)


# Public endpoints
@app.get("/api/public/stats")
async def public_stats():
    return {
        "companies": "500+",
        "calls_processed": "2.3M+",
        "uptime": "99.9%",
        "avg_response_time": "< 1s",
    }


class SignupRequest(BaseModel):
    business_name: str
    name: str
    email: str
    phone: str


@app.post("/api/public/signup")
async def public_signup(data: SignupRequest):
    from pydantic import EmailStr
    return {
        "success": True,
        "message": "Welcome to VoiceCore! Check your email to verify your account.",
        "demo_url": f"/demo?industry=general"
    }


@app.get("/api/public/pricing")
async def public_pricing():
    plans = []
    for plan_name, config in PLAN_PRICES.items():
        if plan_name == "free":
            continue
        
        features = {
            "starter": [
                "1 phone number",
                f"{config['calls_limit']} calls/month",
                "Basic analytics",
                "Email support",
            ],
            "business": [
                f"{config['numbers_limit']} phone numbers",
                f"{config['calls_limit']} calls/month",
                "Advanced analytics",
                "Priority support",
                "WhatsApp integration",
                "CRM integration",
            ],
            "enterprise": [
                "Unlimited numbers",
                "Unlimited calls",
                "Custom analytics",
                "24/7 support",
                "Dedicated account manager",
                "SLA guarantee",
            ],
        }
        
        plans.append({
            "name": plan_name.capitalize(),
            "price": config["price_monthly"],
            "yearly_price": config["price_yearly"],
            "features": features.get(plan_name, []),
            "popular": plan_name == "business",
        })
    
    return {"plans": plans}


# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    """Check if the application is ready to serve traffic."""
    checks = {"database": False, "redis": False}
    
    # Check database
    try:
        from db.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            checks["database"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        checks["database"] = False
    
    # Check Redis
    try:
        import redis.asyncio as aioredis
        if settings.redis_url:
            r = aioredis.from_url(settings.redis_url)
            await r.ping()
            checks["redis"] = True
            await r.close()
    except Exception:
        checks["redis"] = False
    
    all_healthy = all(checks.values())
    
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "ready" if all_healthy else "degraded",
            "checks": checks,
        }
    )
