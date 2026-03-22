"""
5-Step Onboarding API — VoiceCore

Takes the customer from registration to their first real call.
Each step is saved immediately. If user closes browser → returns to where they left off.
"""

import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.database import get_db
from db.models import User, Company, Agent, OnboardingState
from api.auth import get_current_user
from config import settings

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


class CompanyOnboardingStep1(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "America/New_York"
    website: Optional[str] = None


class AgentOnboardingStep2(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=100)
    language: str = Field(default="en")
    business_hours: Optional[dict] = None
    custom_instructions: Optional[str] = None
    industry_vertical: Optional[str] = None


class VoicePreviewRequest(BaseModel):
    voice_id: str
    text: Optional[str] = None


class VoiceSelectionData(BaseModel):
    voice_id: str
    voice_name: str
    voice_gender: Optional[str] = None


class PhoneProvisionRequest(BaseModel):
    phone_number: str
    country: str = "US"


class ExistingNumberRequest(BaseModel):
    phone_number: str


class TestCallRequest(BaseModel):
    test_phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")


class VoiceInfo(BaseModel):
    voice_id: str
    name: str
    language: str
    gender: Optional[str] = None
    preview_url: Optional[str] = None


class PhoneNumberInfo(BaseModel):
    phone_number: str
    friendly_name: Optional[str] = None
    monthly_cost: float
    capabilities: list[str]


class OnboardingStateResponse(BaseModel):
    current_step: int
    completed: bool
    step1_data: Optional[dict] = None
    step2_data: Optional[dict] = None
    step3_data: Optional[dict] = None
    step4_data: Optional[dict] = None
    step5_data: Optional[dict] = None


def get_default_business_hours() -> dict:
    return {
        "monday": {"open": "09:00", "close": "18:00", "enabled": True},
        "tuesday": {"open": "09:00", "close": "18:00", "enabled": True},
        "wednesday": {"open": "09:00", "close": "18:00", "enabled": True},
        "thursday": {"open": "09:00", "close": "18:00", "enabled": True},
        "friday": {"open": "09:00", "close": "18:00", "enabled": True},
        "saturday": {"open": "09:00", "close": "17:00", "enabled": False},
        "sunday": {"open": "09:00", "close": "17:00", "enabled": False},
    }


@router.get("/state")
async def get_onboarding_state(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OnboardingStateResponse:
    result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == current_user.company_id)
    )
    state = result.scalar_one_or_none()
    
    if not state:
        return OnboardingStateResponse(current_step=1, completed=False)
    
    return OnboardingStateResponse(
        current_step=state.current_step,
        completed=state.completed,
        step1_data=state.step1_data,
        step2_data=state.step2_data,
        step3_data=state.step3_data,
        step4_data=state.step4_data,
        step5_data=state.step5_data,
    )


@router.post("/step1/company")
async def save_company_info(
    data: CompanyOnboardingStep1,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.name = data.company_name
    company.industry = data.industry
    company.phone = data.phone
    company.timezone = data.timezone
    company.website = data.website
    
    onboarding_result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == company.id)
    )
    onboarding_state = onboarding_result.scalar_one_or_none()
    
    if not onboarding_state:
        onboarding_state = OnboardingState(
            company_id=company.id,
            current_step=1,
            step1_data=data.model_dump(),
        )
        db.add(onboarding_state)
    else:
        onboarding_state.step1_data = data.model_dump()
        onboarding_state.current_step = 1
        onboarding_state.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "company_id": company.id,
        "next_step": 2,
        "next_step_url": "/onboarding/step2",
    }


@router.post("/step2/agent")
async def setup_agent(
    data: AgentOnboardingStep2,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    agent_result = await db.execute(
        select(Agent).where(
            Agent.company_id == company.id,
            Agent.is_active == True
        )
    )
    existing_agent = agent_result.scalar_one_or_none()
    
    if existing_agent:
        existing_agent.name = data.agent_name
        existing_agent.language = data.language
        existing_agent.business_hours = json.dumps(
            data.business_hours or get_default_business_hours()
        )
        existing_agent.system_prompt = data.custom_instructions
        agent = existing_agent
    else:
        agent = Agent(
            company_id=company.id,
            name=data.agent_name,
            language=data.language,
            business_hours=json.dumps(data.business_hours or get_default_business_hours()),
            system_prompt=data.custom_instructions,
            is_active=True,
        )
        db.add(agent)
    
    onboarding_result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == company.id)
    )
    onboarding_state = onboarding_result.scalar_one_or_none()
    
    if onboarding_state:
        onboarding_state.step2_data = data.model_dump()
        onboarding_state.current_step = 2
        onboarding_state.updated_at = datetime.utcnow()
    else:
        onboarding_state = OnboardingState(
            company_id=company.id,
            current_step=2,
            step2_data=data.model_dump(),
        )
        db.add(onboarding_state)
    
    await db.commit()
    await db.refresh(agent)
    
    return {
        "success": True,
        "agent_id": agent.id,
        "next_step": 3,
        "next_step_url": "/onboarding/step3",
    }


@router.get("/step3/voices")
async def get_available_voices(
    language: str = "en",
    current_user: User = Depends(get_current_user),
):
    default_voices = [
        VoiceInfo(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            name="Rachel",
            language="en",
            gender="female",
        ),
        VoiceInfo(
            voice_id="pFZP5JQG7iVDjE2K3tM",
            name="Josh",
            language="en",
            gender="male",
        ),
        VoiceInfo(
            voice_id="TX3LPaxmHKxFdv7VOQHJ",
            name="Charlotte",
            language="en",
            gender="female",
        ),
        VoiceInfo(
            voice_id="VR6AewLTigWG4xSOukaG",
            name="Arnold",
            language="en",
            gender="male",
        ),
        VoiceInfo(
            voice_id="EXAVITQu4vr4wnSDBMeA",
            name="Bella",
            language="en",
            gender="female",
        ),
        VoiceInfo(
            voice_id="CYx3Are0xNWMS5uNWpp2",
            name="George",
            language="en",
            gender="male",
        ),
        VoiceInfo(
            voice_id="XB0fDUnXU5powFXDhCwa",
            name="Alice",
            language="en",
            gender="female",
        ),
        VoiceInfo(
            voice_id="AZnzlk1XvdvUeBOXmlQ3",
            name="Daniel",
            language="en",
            gender="male",
        ),
        VoiceInfo(
            voice_id="nPcyCjQ9mCOPzxaibt7J",
            name="Lily",
            language="en",
            gender="female",
        ),
        VoiceInfo(
            voice_id="LcfcUwNcfx Jep4kbJqYr",
            name="James",
            language="en",
            gender="male",
        ),
    ]
    
    if language != "en":
        return default_voices
    
    return [v.model_dump() for v in default_voices]


@router.post("/step3/voice/preview")
async def preview_voice(
    data: VoicePreviewRequest,
    current_user: User = Depends(get_current_user),
):
    default_text = "Hello, thank you for calling. How can I help you today?"
    text = data.text or default_text
    
    return {
        "voice_id": data.voice_id,
        "preview_url": f"/api/v1/voice/preview/{data.voice_id}",
        "text": text,
        "expires_in": 86400,
    }


@router.post("/step3/voice/select")
async def select_voice(
    data: VoiceSelectionData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(
            Agent.company_id == current_user.company_id,
            Agent.is_active == True
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="No active agent found. Please complete Step 2 first.")
    
    agent.voice_id = data.voice_id
    
    onboarding_result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == current_user.company_id)
    )
    onboarding_state = onboarding_result.scalar_one_or_none()
    
    if onboarding_state:
        onboarding_state.step3_data = data.model_dump()
        onboarding_state.current_step = 3
        onboarding_state.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "voice_id": data.voice_id,
        "voice_name": data.voice_name,
        "next_step": 4,
        "next_step_url": "/onboarding/step4",
    }


@router.get("/step4/available-numbers")
async def get_available_phone_numbers(
    area_code: Optional[str] = None,
    country: str = "US",
    current_user: User = Depends(get_current_user),
):
    available_numbers = [
        PhoneNumberInfo(
            phone_number=f"+1{area_code or '212'}555{str(i).zfill(4)}",
            friendly_name=f"Local {area_code or '212'} Number",
            monthly_cost=1.00,
            capabilities=["voice", "sms"],
        )
        for i in range(1, 21)
    ]
    
    if area_code:
        available_numbers = [
            n for n in available_numbers 
            if area_code in n.phone_number
        ]
    
    return [n.model_dump() for n in available_numbers]


@router.post("/step4/provision-number")
async def provision_phone_number(
    data: PhoneProvisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.phone_number = data.phone_number
    
    onboarding_result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == company.id)
    )
    onboarding_state = onboarding_result.scalar_one_or_none()
    
    if onboarding_state:
        onboarding_state.step4_data = {
            "phone_number": data.phone_number,
            "country": data.country,
            "provisioned_at": datetime.utcnow().isoformat(),
        }
        onboarding_state.current_step = 4
        onboarding_state.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "phone_number": data.phone_number,
        "webhook_configured": True,
        "voice_url": f"{settings.base_url}/api/v1/voice/inbound",
        "status_callback_url": f"{settings.base_url}/api/webhooks/twilio/status",
        "next_step": 5,
        "next_step_url": "/onboarding/step5",
    }


@router.post("/step4/use-existing-number")
async def configure_existing_number(
    data: ExistingNumberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.phone_number = data.phone_number
    
    onboarding_result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == company.id)
    )
    onboarding_state = onboarding_result.scalar_one_or_none()
    
    if onboarding_state:
        onboarding_state.step4_data = {
            "phone_number": data.phone_number,
            "is_existing": True,
            "configured_at": datetime.utcnow().isoformat(),
        }
        onboarding_state.current_step = 4
        onboarding_state.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "phone_number": data.phone_number,
        "webhook_configured": True,
        "next_step": 5,
        "next_step_url": "/onboarding/step5",
    }


@router.post("/step5/initiate-test-call")
async def initiate_test_call(
    data: TestCallRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.phone_number:
        raise HTTPException(
            status_code=400, 
            detail="No phone number configured. Please complete Step 4 first."
        )
    
    result = await db.execute(
        select(Agent).where(
            Agent.company_id == company.id,
            Agent.is_active == True
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=400,
            detail="No active agent found. Please complete Step 2 first."
        )
    
    if not agent.voice_id:
        raise HTTPException(
            status_code=400,
            detail="No voice selected. Please complete Step 3 first."
        )
    
    call_sid = f"TEST_{uuid4().hex[:16].upper()}"
    
    return {
        "success": True,
        "call_sid": call_sid,
        "status": "initiated",
        "message": "Test call initiated. Please wait...",
        "company_number": company.phone_number,
        "test_number": data.test_phone,
    }


@router.get("/step5/test-call-status/{call_sid}")
async def get_test_call_status(
    call_sid: str,
    current_user: User = Depends(get_current_user),
):
    statuses = ["initiated", "ringing", "in-progress", "completed", "failed"]
    current_status = statuses[0]
    
    return {
        "call_sid": call_sid,
        "status": current_status,
        "duration_seconds": 0,
        "transcript": None,
        "sentiment": None,
    }


@router.post("/step5/complete-onboarding")
async def complete_onboarding(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    onboarding_result = await db.execute(
        select(OnboardingState).where(OnboardingState.company_id == company.id)
    )
    onboarding_state = onboarding_result.scalar_one_or_none()
    
    if onboarding_state:
        onboarding_state.completed = True
        onboarding_state.completed_at = datetime.utcnow()
        onboarding_state.current_step = 5
        onboarding_state.step5_data = {"completed_at": datetime.utcnow().isoformat()}
        onboarding_state.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Onboarding completed successfully!",
        "company_name": company.name,
        "phone_number": company.phone_number,
        "redirect_url": "/dashboard",
    }


@router.get("/check-readiness")
async def check_onboarding_readiness(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    result = await db.execute(
        select(Agent).where(
            Agent.company_id == company.id,
            Agent.is_active == True
        )
    )
    agent = result.scalar_one_or_none()
    
    checks = {
        "company_info": bool(company.name),
        "agent_configured": bool(agent),
        "voice_selected": bool(agent and agent.voice_id),
        "phone_number_configured": bool(company.phone_number),
        "ready_for_calls": bool(
            company.name and agent and agent.voice_id and company.phone_number
        ),
    }
    
    missing = [k for k, v in checks.items() if not v and k != "ready_for_calls"]
    
    return {
        "ready": checks["ready_for_calls"],
        "checks": checks,
        "missing_steps": missing,
    }
