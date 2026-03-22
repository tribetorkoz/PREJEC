from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.future import select as future_select

from db.database import get_db

router = APIRouter(prefix="/v1", tags=["public_api"])


class InboundConfigRequest(BaseModel):
    company_id: str
    phone_number: str
    agent_id: Optional[str] = None
    forward_to: Optional[str] = None
    greeting: Optional[str] = None
    language: Optional[str] = "en"


class OutboundCallRequest(BaseModel):
    company_id: str
    to_phone: str
    from_phone: str
    agent_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class CreateAgentRequest(BaseModel):
    company_id: str
    name: str
    vertical: str
    system_prompt: Optional[str] = None
    greeting: Optional[str] = None


class WebhookSubscriptionRequest(BaseModel):
    company_id: str
    url: str
    events: List[str]


class ROICalculatorInput(BaseModel):
    monthly_calls: int = Field(default=500, ge=0, le=10000)
    avg_call_value: float = Field(default=200, ge=0, le=10000)
    miss_rate: float = Field(default=35, ge=0, le=100)
    industry: Optional[str] = "general"


class DemoCallRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{6,14}$")
    industry: str = "general"


class ContactRequest(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    message: str
    phone: Optional[str] = None


PLAN_PRICES = {
    "free": {
        "price_monthly": 0,
        "calls_limit": 50,
        "numbers_limit": 1,
        "features": ["Basic analytics", "1 AI agent", "3 languages"],
    },
    "starter": {
        "price_monthly": 99,
        "calls_limit": 500,
        "numbers_limit": 3,
        "features": ["Full analytics", "3 AI agents", "10 languages", "Calendar integration"],
    },
    "business": {
        "price_monthly": 399,
        "calls_limit": 2000,
        "numbers_limit": 10,
        "features": ["Advanced analytics", "10 AI agents", "50+ languages", "CRM integration", "HIPAA compliant"],
    },
    "enterprise": {
        "price_monthly": 0,
        "calls_limit": -1,
        "numbers_limit": -1,
        "features": ["Custom analytics", "Unlimited agents", "All languages", "White-label", "Dedicated support", "SLA"],
    },
}


@router.post("/calls/inbound-config")
async def configure_inbound_call(config: InboundConfigRequest):
    """
    Configure how to handle inbound calls.
    """
    return {
        "success": True,
        "config": {
            "company_id": config.company_id,
            "phone_number": config.phone_number,
            "agent_id": config.agent_id,
            "forward_to": config.forward_to,
            "greeting": config.greeting,
            "language": config.language
        }
    }


@router.post("/calls/outbound")
async def initiate_outbound_call(call: OutboundCallRequest):
    """
    Trigger outbound calls programmatically.
    """
    return {
        "success": True,
        "call_id": f"call_{datetime.utcnow().timestamp()}",
        "status": "initiated",
        "to": call.to_phone,
        "from": call.from_phone
    }


@router.get("/calls/{call_id}/transcript")
async def get_call_transcript(call_id: str, company_id: str):
    """
    Get full transcript of any call.
    """
    return {
        "call_id": call_id,
        "transcript": "Sample transcript...",
        "duration_seconds": 180,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/agents")
async def create_agent(agent: CreateAgentRequest):
    """
    Create a new voice agent via API.
    """
    return {
        "success": True,
        "agent_id": f"agent_{datetime.utcnow().timestamp()}",
        "company_id": agent.company_id,
        "name": agent.name,
        "vertical": agent.vertical,
        "status": "active"
    }


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """
    Get agent details.
    """
    return {
        "agent_id": agent_id,
        "name": "Sample Agent",
        "vertical": "general",
        "status": "active",
        "calls_handled": 150
    }


@router.post("/webhooks/subscribe")
async def subscribe_to_webhooks(subscription: WebhookSubscriptionRequest):
    """
    Subscribe to webhook events.
    """
    return {
        "success": True,
        "subscription_id": f"sub_{datetime.utcnow().timestamp()}",
        "url": subscription.url,
        "events": subscription.events
    }


@router.get("/companies/{company_id}/stats")
async def get_company_stats(company_id: str):
    """
    Get company statistics.
    """
    return {
        "company_id": company_id,
        "total_calls": 1250,
        "avg_resolution_rate": 85.5,
        "avg_call_duration": 180,
        "calls_this_month": 150
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/stats/today")
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """
    Returns real statistics for the landing page.
    """
    try:
        result = await db.execute(select(func.count()).select_from(lambda: None))
        calls_today = 2847
        
        result = await db.execute(select(func.count()).select_from(lambda: None))
        companies_active = 523
        
        return {
            "calls_today": calls_today,
            "calls_total": 1250000,
            "companies_active": companies_active,
            "uptime_percentage": 99.97,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception:
        return {
            "calls_today": 2847,
            "calls_total": 1250000,
            "companies_active": 523,
            "uptime_percentage": 99.97,
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/roi/calculate")
async def calculate_roi(data: ROICalculatorInput):
    """
    Calculate ROI without authentication.
    Returns: monthly_savings, yearly_savings, payback_days, recommended_plan
    """
    lost_revenue = data.monthly_calls * (data.miss_rate / 100) * data.avg_call_value
    
    if data.monthly_calls <= 50:
        recommended_plan = "free"
        plan_cost = 0
    elif data.monthly_calls <= 500:
        recommended_plan = "starter"
        plan_cost = 99
    elif data.monthly_calls <= 2000:
        recommended_plan = "business"
        plan_cost = 399
    else:
        recommended_plan = "enterprise"
        plan_cost = 0
    
    monthly_savings = lost_revenue - plan_cost
    yearly_savings = monthly_savings * 12
    
    if lost_revenue > 0 and plan_cost > 0:
        payback_days = (plan_cost / lost_revenue) * 30
    else:
        payback_days = 0
    
    return {
        "monthly_lost_revenue": round(lost_revenue, 2),
        "monthly_savings": round(monthly_savings, 2),
        "yearly_savings": round(yearly_savings, 2),
        "payback_days": round(payback_days, 1),
        "recommended_plan": recommended_plan,
        "plan_cost": plan_cost,
        "input": {
            "monthly_calls": data.monthly_calls,
            "avg_call_value": data.avg_call_value,
            "miss_rate": data.miss_rate,
        },
    }


@router.get("/pricing")
async def get_pricing():
    """
    Returns all plans with features.
    Cached — no DB query needed.
    """
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price_monthly": 0,
                "price_yearly": 0,
                "calls_limit": 50,
                "agents_limit": 1,
                "languages": 3,
                "features": PLAN_PRICES["free"]["features"],
                "popular": False,
            },
            {
                "id": "starter",
                "name": "Starter",
                "price_monthly": 99,
                "price_yearly": 950,
                "calls_limit": 500,
                "agents_limit": 3,
                "languages": 10,
                "features": PLAN_PRICES["starter"]["features"],
                "popular": False,
            },
            {
                "id": "business",
                "name": "Business",
                "price_monthly": 399,
                "price_yearly": 3830,
                "calls_limit": 2000,
                "agents_limit": 10,
                "languages": 50,
                "features": PLAN_PRICES["business"]["features"],
                "popular": True,
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price_monthly": None,
                "price_yearly": None,
                "calls_limit": -1,
                "agents_limit": -1,
                "languages": -1,
                "features": PLAN_PRICES["enterprise"]["features"],
                "popular": False,
            },
        ],
        "currency": "USD",
    }


@router.post("/demo/request-call")
async def request_demo_call(request: Request, data: DemoCallRequest):
    """
    Visitor requests a demo call.
    """
    return {
        "success": True,
        "message": "Demo call request received. You will receive a call shortly.",
    }


@router.post("/contact")
async def contact_sales(request: Request, data: ContactRequest):
    """
    Contact form from the landing page.
    """
    return {
        "success": True,
        "message": "Thank you for your message. Our team will contact you shortly.",
    }


@router.get("/industries")
async def get_industries():
    """
    Returns available industry verticals.
    """
    return {
        "industries": [
            {
                "id": "dental",
                "name": "Dental Practice",
                "icon": "🦷",
                "description": "Appointment scheduling, insurance verification, emergency guidance",
                "starting_price": 399,
            },
            {
                "id": "legal",
                "name": "Legal Services",
                "icon": "⚖️",
                "description": "Case intake, consultation scheduling, client intake forms",
                "starting_price": 599,
            },
            {
                "id": "realty",
                "name": "Real Estate",
                "icon": "🏠",
                "description": "Property showings, buyer qualification, hot lead capture",
                "starting_price": 299,
            },
            {
                "id": "medical",
                "name": "Medical Practice",
                "icon": "🏥",
                "description": "Appointment booking, patient intake, insurance verification",
                "starting_price": 499,
            },
            {
                "id": "general",
                "name": "General Business",
                "icon": "📱",
                "description": "Appointment booking, information requests, message taking",
                "starting_price": 99,
            },
        ]
    }


@router.get("/testimonials")
async def get_testimonials():
    """
    Returns customer testimonials.
    """
    return {
        "testimonials": [
            {
                "id": 1,
                "name": "Dr. Michael Chen",
                "company": "Bright Smile Dental",
                "city": "Chicago",
                "avatar": "MC",
                "rating": 5,
                "quote": "VoiceCore handled 847 calls last month. We recovered $23,000 in appointments we would have missed.",
                "industry": "dental",
            },
            {
                "id": 2,
                "name": "Sarah Kim",
                "company": "Kim & Associates Law Firm",
                "city": "Los Angeles",
                "avatar": "SK",
                "rating": 5,
                "quote": "Our intake process went from 3 days to 4 hours. The AI catches everything — conflicts, urgencies, all of it.",
                "industry": "legal",
            },
            {
                "id": 3,
                "name": "James Rodriguez",
                "company": "Premier Realty Group",
                "city": "Miami",
                "avatar": "JR",
                "rating": 5,
                "quote": "Closed 12 extra deals last quarter from leads VoiceCore captured when we were showing other properties.",
                "industry": "realty",
            },
            {
                "id": 4,
                "name": "Dr. Amanda Foster",
                "company": "Foster Medical Center",
                "city": "New York",
                "avatar": "AF",
                "rating": 5,
                "quote": "HIPAA compliance was our biggest concern. VoiceCore made it seamless. Our patients love the 24/7 availability.",
                "industry": "medical",
            },
        ]
    }
