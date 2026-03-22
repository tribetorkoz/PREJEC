import os
import secrets
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI Services
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # LiveKit
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
    
    # Database
    database_url: str = ""
    redis_url: str = ""
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_starter_price_id: str = ""
    stripe_business_price_id: str = ""
    
    # JWT Auth - must be a secure random string in production
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 30
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # URLs
    next_public_api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Email
    sendgrid_api_key: str = ""
    from_email: str = "noreply@voicecore.ai"
    
    @property
    def effective_jwt_secret(self) -> str:
        """Return jwt_secret or generate a random one (development only)."""
        if self.jwt_secret:
            return self.jwt_secret
        # In development, generate a random secret (logs a warning)
        import logging
        logging.getLogger(__name__).warning(
            "JWT_SECRET not set! Using a random secret. "
            "This is only acceptable in development. "
            "Set JWT_SECRET in .env for production."
        )
        return secrets.token_hex(32)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


# Pricing plans (source of truth)
PLAN_PRICES = {
    "free": {"price_monthly": 0, "price_yearly": 0, "calls_limit": 50, "numbers_limit": 0},
    "starter": {"price_monthly": 299, "price_yearly": 2868, "calls_limit": 500, "numbers_limit": 1},
    "business": {"price_monthly": 899, "price_yearly": 8630, "calls_limit": 2500, "numbers_limit": 3},
    "enterprise": {"price_monthly": 0, "price_yearly": 0, "calls_limit": -1, "numbers_limit": -1},  # custom
}


VERTICALS: Dict[str, Dict[str, Any]] = {
    "general": {
        "name": "VoiceCore",
        "domain": "voicecore.ai",
        "industry": "general",
    },
    "dental": {
        "name": "DentalVoice",
        "domain": "dentalvoice.ai",
        "industry": "dental",
        "system_prompt": "You are a professional voice assistant for a dental clinic...",
        "greeting": "Thank you for calling...",
        "emergency_keywords": ["toothache", "broken tooth", "abscess"],
        "features": [
            "New patient intake",
            "Insurance verification",
            "Appointment booking",
            "Emergency priority",
            "WhatsApp confirmations"
        ]
    },
    "legal": {
        "name": "LegalVoice",
        "domain": "legalvoice.ai",
        "industry": "legal",
        "system_prompt_module": "backend.features.verticals.legal.prompt",
        "tools_module": "backend.features.verticals.legal.tools",
        "compliance_module": "backend.features.verticals.legal.compliance",
        "practice_areas": [
            "Personal Injury",
            "Criminal Defense",
            "Family Law",
            "Immigration",
            "Employment Law",
            "Estate Planning",
            "Bankruptcy"
        ],
        "emergency_keywords": ["arrested", "deported", "custody", "hospital", "emergency"],
        "compliance_features": [
            "AES-256 transcript encryption",
            "30-day PII retention",
            "Audit logging",
            "Conflict checking",
            "Attorney-client privilege",
            "SOC 2 compliant"
        ],
        "features": [
            "Legal intake specialist",
            "Case qualification",
            "Conflict of interest check",
            "Urgency detection",
            "Statute of limitations tracking",
            "Secure transcript storage",
            "HIPAA and privilege compliant"
        ]
    },
    "realty": {
        "name": "RealtyVoice",
        "domain": "realtyvoice.ai",
        "industry": "real_estate",
        "system_prompt_module": "backend.features.verticals.realty.prompt",
        "tools_module": "backend.features.verticals.realty.tools",
        "mls_integration": "backend.integrations.mls.client",
        "property_types": [
            "Single Family Home",
            "Condo",
            "Townhouse",
            "Multi-family",
            "Land",
            "Commercial"
        ],
        "features": [
            "Showing scheduling",
            "Buyer lead qualification",
            "Seller listing consultations",
            "CMA (market analysis)",
            "MLS integration",
            "Property availability check",
            "Hot lead flagging",
            "Lender referral connection",
            "Market statistics",
            "Investor property search"
        ]
    }
}


def get_vertical_config(vertical: str) -> Dict[str, Any]:
    """Get configuration for a specific vertical."""
    return VERTICALS.get(vertical, VERTICALS["general"])


def get_plan_config(plan: str) -> Dict[str, Any]:
    """Get pricing/limits for a specific plan."""
    return PLAN_PRICES.get(plan, PLAN_PRICES["free"])
