from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    plan: str = "free"
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    timezone: str = "America/New_York"


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    status: str = "active"
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentBase(BaseModel):
    name: str
    language: str = "en"
    voice_id: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: bool = True


class AgentCreate(AgentBase):
    company_id: int


class AgentUpdate(BaseModel):
    """Separate schema for updates - doesn't require company_id."""
    name: Optional[str] = None
    language: Optional[str] = None
    voice_id: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CallBase(BaseModel):
    company_id: int
    caller_phone: str
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    sentiment: Optional[str] = None
    outcome: Optional[str] = None


class CallCreate(CallBase):
    call_sid: Optional[str] = None
    direction: str = "inbound"
    agent_id: Optional[int] = None


class CallResponse(CallBase):
    id: int
    call_sid: Optional[str] = None
    direction: str = "inbound"
    agent_id: Optional[int] = None
    recording_url: Optional[str] = None
    sentiment_score: Optional[float] = None
    created_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    company_id: int
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    last_call_at: Optional[datetime] = None
    total_calls: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    total_calls: int
    total_duration: int
    avg_sentiment_score: Optional[float] = None
    sentiment_breakdown: dict = {}
    calls_by_day: dict


class AppointmentBase(BaseModel):
    customer_name: str
    customer_phone: str
    date: str
    time: str
    service: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    company_id: int
    customer_id: Optional[int] = None


class AppointmentResponse(AppointmentBase):
    id: int
    company_id: int
    customer_id: Optional[int] = None
    status: str = "confirmed"
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    company_id: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
