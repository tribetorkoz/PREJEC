from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Float, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="super_admin")
    is_active = Column(Boolean, default=True)
    totp_secret = Column(String(255), nullable=True)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminLog(Base):
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    target = Column(String(255), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="free")
    status = Column(String(50), default="active")
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    whatsapp_number = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    timezone = Column(String(100), default="America/New_York")
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    trial_used = Column(Boolean, default=False)
    hipaa_baa_signed = Column(Boolean, default=False)
    hipaa_baa_signed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    agents = relationship("Agent", back_populates="company", cascade="all, delete-orphan")
    calls = relationship("Call", back_populates="company", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    feature_flags = relationship("FeatureFlagCompany", back_populates="company", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="company", cascade="all, delete-orphan")
    notification_preferences = relationship("NotificationPreferences", back_populates="company", uselist=False, cascade="all, delete-orphan")
    onboarding_state = relationship("OnboardingState", back_populates="company", uselist=False, cascade="all, delete-orphan")
    baa = relationship("BAA", back_populates="company", uselist=False, cascade="all, delete-orphan")
    demo_sessions = relationship("DemoSession", back_populates="company", cascade="all, delete-orphan")


class User(Base):
    """Individual user account (multiple users per company)."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="member")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="users")


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    language = Column(String(10), default="en")
    voice_id = Column(String(255), nullable=True)
    system_prompt = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    business_hours = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="agents")
    
    __table_args__ = (
        Index('idx_agents_company_active', 'company_id', 'is_active'),
    )


class Call(Base):
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    call_sid = Column(String(255), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    caller_phone = Column(String(50), nullable=False, index=True)
    direction = Column(String(20), default="inbound")
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    outcome = Column(String(255), nullable=True)
    recording_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    company = relationship("Company", back_populates="calls")
    
    __table_args__ = (
        Index('idx_calls_company_created', 'company_id', 'created_at'),
        Index('idx_calls_caller_phone', 'caller_phone'),
    )


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    last_call_at = Column(DateTime(timezone=True), nullable=True)
    total_calls = Column(Integer, default=0)
    is_vip = Column(Boolean, default=False)
    vip_reason = Column(String(255), nullable=True)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="customers")
    
    __table_args__ = (
        Index('idx_customers_phone_company', 'phone', 'company_id', unique=True),
    )


class Appointment(Base):
    """Persisted appointments booked by voice agents."""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(10), nullable=False)
    service = Column(String(255), nullable=True)
    status = Column(String(50), default="confirmed")
    notes = Column(Text, nullable=True)
    reminder_sent_24h = Column(Boolean, default=False)
    reminder_sent_2h = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Subscription(Base):
    """Subscription tracking for companies."""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    stripe_price_id = Column(String(255), nullable=True)
    plan = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    encrypted_value = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_global_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    company_flags = relationship("FeatureFlagCompany", back_populates="feature_flag")


class FeatureFlagCompany(Base):
    __tablename__ = "feature_flag_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_flag_id = Column(Integer, ForeignKey("feature_flags.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    feature_flag = relationship("FeatureFlag", back_populates="company_flags")
    company = relationship("Company", back_populates="feature_flags")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    channel = Column(String(20), nullable=False)
    recipient = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    status = Column(String(20), default="sent", index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    extra_data = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    company = relationship("Company")
    call = relationship("Call")
    
    __table_args__ = (
        Index('idx_notifications_company_created', 'company_id', 'created_at'),
    )


class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False)
    email_angry_customer = Column(Boolean, default=True)
    sms_angry_customer = Column(Boolean, default=False)
    email_missed_call = Column(Boolean, default=True)
    email_daily_summary = Column(Boolean, default=True)
    email_weekly_report = Column(Boolean, default=True)
    webhook_url = Column(String(500), nullable=True)
    webhook_events = Column(JSON, default=[])
    notification_email = Column(String(255), nullable=True)
    notification_phone = Column(String(50), nullable=True)
    timezone = Column(String(100), default="America/New_York")
    daily_summary_time = Column(String(5), default="08:00")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    company = relationship("Company")


class OnboardingState(Base):
    __tablename__ = "onboarding_states"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False)
    current_step = Column(Integer, default=1)
    step1_data = Column(JSON, nullable=True)
    step2_data = Column(JSON, nullable=True)
    step3_data = Column(JSON, nullable=True)
    step4_data = Column(JSON, nullable=True)
    step5_data = Column(JSON, nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    company = relationship("Company")


class PHIAccessLog(Base):
    """HIPAA-required audit log for PHI access"""
    __tablename__ = "phi_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    record_type = Column(String(50))
    record_id = Column(Integer)
    action = Column(String(50))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_phi_access_company_timestamp', 'company_id', 'timestamp'),
    )


class BAA(Base):
    """Business Associate Agreements"""
    __tablename__ = "baas"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False)
    accepted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    accepted_at = Column(DateTime(timezone=True))
    ip_address = Column(String(45))
    baa_version = Column(String(20), default="1.0")
    document_url = Column(String(500), nullable=True)
    
    company = relationship("Company")


class DemoSession(Base):
    """Track every demo session"""
    __tablename__ = "demo_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    session_token = Column(String(255), unique=True, nullable=False)
    industry = Column(String(50))
    demo_type = Column(String(20))
    ip_hash = Column(String(255))
    country = Column(String(50))
    duration_seconds = Column(Integer)
    converted_to_signup = Column(Boolean, default=False)
    was_satisfied = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company")
    
    __table_args__ = (
        Index('idx_demo_sessions_token', 'session_token'),
    )


class MarketingEvent(Base):
    """Track marketing events"""
    __tablename__ = "marketing_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100), index=True)
    properties = Column(JSON)
    session_id = Column(String(255), nullable=True)
    ip_hash = Column(String(255))
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_marketing_events_event_created', 'event', 'created_at'),
    )
