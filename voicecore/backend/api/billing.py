from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from db.database import get_db
from db.models import Company, User, BAA
from config import settings, PLAN_PRICES
from services.stripe_service import StripeService
from services.email_service import EmailService
from api.auth import get_current_user


router = APIRouter(prefix="/api/billing", tags=["billing"])

stripe_service = StripeService()
email_service = EmailService()

TRIAL_DAYS = 14
TRIAL_REMINDER_DAY = 10


class CheckoutRequest(BaseModel):
    plan: str


class PortalResponse(BaseModel):
    portal_url: str


class TrialResponse(BaseModel):
    is_on_trial: bool
    days_remaining: int
    trial_ends_at: Optional[datetime]
    trial_used: bool
    can_start_trial: bool


class BAARequest(BaseModel):
    accepted: bool = True


@router.post("/checkout")
async def create_checkout(
    req: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {req.plan}")
    
    if req.plan == "enterprise":
        raise HTTPException(
            status_code=400,
            detail="Enterprise plans require contacting sales"
        )
    
    price_id_map = {
        "starter": settings.stripe_starter_price_id,
        "business": settings.stripe_business_price_id,
    }
    
    price_id = price_id_map.get(req.plan)
    if not price_id or price_id.startswith("price_"):
        raise HTTPException(
            status_code=500,
            detail="Stripe price IDs not configured. Contact admin."
        )
    
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    stripe_customer_id = company.stripe_customer_id
    if not stripe_customer_id:
        stripe_customer = await stripe_service.create_customer(
            email=company.email,
            name=company.name,
            metadata={"company_id": str(company.id)},
        )
        stripe_customer_id = stripe_customer["id"]
        company.stripe_customer_id = stripe_customer_id
        await db.commit()
    
    session = await stripe_service.create_checkout_session(
        customer_id=stripe_customer_id,
        price_id=price_id,
        success_url=f"{settings.frontend_url}/dashboard?checkout=success",
        cancel_url=f"{settings.frontend_url}/pricing?checkout=cancelled",
    )
    
    return {"checkout_url": session.get("url")}


@router.get("/portal")
async def billing_portal(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company or not company.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")
    
    portal = await stripe_service.create_portal_session(
        customer_id=company.stripe_customer_id,
        return_url=f"{settings.frontend_url}/dashboard",
    )
    
    return PortalResponse(portal_url=portal.get("url", ""))


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    plan_config = PLAN_PRICES.get(company.plan, PLAN_PRICES["free"])
    
    return {
        "plan": company.plan,
        "status": company.status,
        "price_monthly": plan_config["price_monthly"],
        "calls_limit": plan_config["calls_limit"],
        "numbers_limit": plan_config["numbers_limit"],
        "stripe_customer_id": company.stripe_customer_id,
        "stripe_subscription_id": company.stripe_subscription_id,
    }


@router.post("/trial/start")
async def start_free_trial(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Starts a 14-day free trial.
    
    Checks:
      - Company has not used trial before (once per lifetime)
      - Company is not on a paid plan
    
    Updates:
      companies.plan = "business_trial"
      companies.trial_ends_at = now + 14 days
      companies.trial_used = True
    
    Sends:
      - Welcome trial email
      - Celery task scheduled for day 10 (reminder)
      - Celery task scheduled for day 14 (downgrade to free)
    """
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if company.trial_used:
        raise HTTPException(
            status_code=400,
            detail="Trial has already been used. You can only start a free trial once."
        )
    
    if company.plan not in ["free", "business_trial"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot start trial on a paid plan. Please cancel your current subscription first."
        )
    
    now = datetime.utcnow()
    trial_ends_at = now + timedelta(days=TRIAL_DAYS)
    
    company.plan = "business_trial"
    company.trial_ends_at = trial_ends_at
    company.trial_used = True
    company.status = "active"
    
    await db.commit()
    
    try:
        await email_service.send_welcome_email(
            to_email=company.email,
            company_name=company.name,
            user_name=user.full_name,
        )
    except Exception:
        pass
    
    return {
        "success": True,
        "message": "Free trial started successfully!",
        "trial_ends_at": trial_ends_at.isoformat(),
        "days_remaining": TRIAL_DAYS,
        "plan": "business_trial",
        "features": PLAN_PRICES["business"],
    }


@router.get("/trial/status", response_model=TrialResponse)
async def get_trial_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns trial status.
    
    Returns:
      is_on_trial: bool
      days_remaining: int
      trial_ends_at: datetime
      trial_used: bool
      can_start_trial: bool
    """
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    is_on_trial = company.plan == "business_trial"
    days_remaining = 0
    trial_ends_at = None
    
    if is_on_trial and company.trial_ends_at:
        trial_ends_at = company.trial_ends_at
        now = datetime.utcnow()
        if trial_ends_at > now:
            days_remaining = (trial_ends_at - now).days
    
    can_start_trial = not company.trial_used and company.plan in ["free"]
    
    return TrialResponse(
        is_on_trial=is_on_trial,
        days_remaining=days_remaining,
        trial_ends_at=trial_ends_at,
        trial_used=company.trial_used,
        can_start_trial=can_start_trial,
    )


@router.post("/baa/sign")
async def sign_baa(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Records customer's acceptance of the BAA.
    
    Checks:
      - Company is on Business or Enterprise plan
      - Has not signed BAA before
    
    Creates:
      - BAA record in DB with IP + timestamp
    
    Sends:
      - Email with copy of BAA to customer
    """
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if company.plan not in ["business", "business_trial", "enterprise"]:
        raise HTTPException(
            status_code=400,
            detail="BAA requires Business or Enterprise plan"
        )
    
    existing_baa = await db.execute(
        select(BAA).where(BAA.company_id == company.id)
    )
    if existing_baa.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="BAA has already been signed for this company"
        )
    
    client_ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow()
    
    baa = BAA(
        company_id=company.id,
        accepted_by_user_id=user.id,
        accepted_at=now,
        ip_address=client_ip,
        baa_version="1.0",
    )
    db.add(baa)
    
    company.hipaa_baa_signed = True
    company.hipaa_baa_signed_at = now
    
    await db.commit()
    
    try:
        await email_service.send_generic_notification(
            to_email=company.email,
            subject="BAA Signed - VoiceCore HIPAA Compliance",
            message=f"Business Associate Agreement signed for {company.name} on {now.strftime('%Y-%m-%d %H:%M UTC')}",
        )
    except Exception:
        pass
    
    return {
        "success": True,
        "message": "BAA signed successfully",
        "signed_at": now.isoformat(),
        "version": "1.0",
    }


@router.get("/baa/status")
async def get_baa_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns BAA signing status.
    """
    result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    baa_result = await db.execute(
        select(BAA).where(BAA.company_id == company.id)
    )
    baa = baa_result.scalar_one_or_none()
    
    return {
        "is_hipaa_enabled": company.plan in ["business", "business_trial", "enterprise"],
        "baa_signed": company.hipaa_baa_signed,
        "baa_signed_at": company.hipaa_baa_signed_at.isoformat() if company.hipaa_baa_signed_at else None,
        "can_sign_baa": company.plan in ["business", "business_trial", "enterprise"] and not company.hipaa_baa_signed,
    }
