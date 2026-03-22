import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Any
from pydantic import BaseModel

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.models import Customer
from config import settings

logger = logging.getLogger(__name__)

# TTL constants
PROFILE_TTL = 90 * 24 * 60 * 60  # 90 days in seconds
SESSION_TTL = 24 * 60 * 60       # 24 hours in seconds
COMPANY_KNOWLEDGE_TTL = 7 * 24 * 60 * 60  # 7 days in seconds
CALL_HISTORY_MAX = 10            # Maximum call summaries to keep


class CallSummary(BaseModel):
    """Model for a single call summary."""
    call_id: str
    date: str
    duration_seconds: int
    outcome: str
    sentiment: str
    summary: str


class CustomerProfile(BaseModel):
    """Full customer profile model."""
    phone: str
    company_id: int
    name: Optional[str] = None
    total_calls: int = 0
    last_call_at: Optional[str] = None
    is_vip: bool = False
    vip_reason: Optional[str] = None
    notes: Optional[str] = None
    preferences: dict = {}
    call_history: List[dict] = []
    created_at: Optional[str] = None


class CallContext(BaseModel):
    """Context object for a call session."""
    customer: Optional[CustomerProfile] = None
    history_text: str = ""
    is_returning_customer: bool = False
    days_since_last_call: Optional[int] = None
    company_knowledge: str = ""


class CustomerMemoryManager:
    """
    Manages permanent customer memory across calls.
    Uses Redis for fast access with database fallback.
    Remembers details from calls months ago - competitors reset after each session.
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url or "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    def _profile_key(self, company_id: int, phone: str) -> str:
        """Generate Redis key for customer profile."""
        return f"customer:{company_id}:{phone}:profile"

    def _history_key(self, company_id: int, phone: str) -> str:
        """Generate Redis key for call history."""
        return f"customer:{company_id}:{phone}:history"

    def _session_key(self, call_id: str) -> str:
        """Generate Redis key for session context."""
        return f"session:{call_id}:context"

    def _company_knowledge_key(self, company_id: int) -> str:
        """Generate Redis key for company knowledge."""
        return f"company:{company_id}:knowledge"

    async def get_customer_profile(
        self,
        phone: str,
        company_id: int,
        db: AsyncSession
    ) -> Optional[CustomerProfile]:
        """
        Get customer profile from Redis first, fallback to database.
        
        Args:
            phone: Customer phone number (masked in logs)
            company_id: Company identifier
            db: Database session
            
        Returns:
            CustomerProfile if found, None otherwise
        """
        try:
            r = await self._get_redis()
            profile_key = self._profile_key(company_id, phone)
            
            cached = await r.get(profile_key)
            if cached:
                logger.debug("Customer profile loaded from Redis", extra={
                    "company_id": company_id,
                    "phone_hash": hash(phone) % 10000
                })
                return CustomerProfile(**json.loads(cached))
        except Exception as e:
            logger.warning(f"Redis unavailable, falling back to DB: {e}")

        # Fallback to database
        try:
            result = await db.execute(
                select(Customer).where(
                    Customer.phone == phone,
                    Customer.company_id == company_id
                )
            )
            customer = result.scalar_one_or_none()
            
            if customer:
                profile = CustomerProfile(
                    phone=customer.phone,
                    company_id=customer.company_id,
                    name=customer.name,
                    total_calls=customer.total_calls or 0,
                    last_call_at=customer.last_call_at.isoformat() if customer.last_call_at else None,
                    is_vip=getattr(customer, 'is_vip', False),
                    vip_reason=getattr(customer, 'vip_reason', None),
                    notes=customer.notes,
                    preferences=getattr(customer, 'preferences', {}) or {},
                    created_at=customer.created_at.isoformat() if customer.created_at else None
                )
                
                # Cache in Redis for next time
                try:
                    r = await self._get_redis()
                    await r.setex(
                        self._profile_key(company_id, phone),
                        PROFILE_TTL,
                        json.dumps(profile.model_dump(), default=str)
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache profile in Redis: {e}")
                
                return profile
        except Exception as e:
            logger.error(f"Database error getting customer profile: {e}")
        
        return None

    async def update_customer_profile(
        self,
        phone: str,
        company_id: int,
        updates: dict,
        db: AsyncSession
    ) -> bool:
        """
        Update customer profile in both Redis and database.
        
        Args:
            phone: Customer phone number
            company_id: Company identifier
            updates: Dictionary of fields to update
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update database first
            result = await db.execute(
                select(Customer).where(
                    Customer.phone == phone,
                    Customer.company_id == company_id
                )
            )
            customer = result.scalar_one_or_none()
            
            if customer:
                for key, value in updates.items():
                    if hasattr(customer, key):
                        setattr(customer, key, value)
                
                await db.commit()
                
                # Invalidate Redis cache - will be refreshed on next read
                try:
                    r = await self._get_redis()
                    await r.delete(self._profile_key(company_id, phone))
                except Exception as e:
                    logger.warning(f"Failed to invalidate Redis cache: {e}")
                
                return True
            else:
                logger.warning("Customer not found for profile update", extra={
                    "company_id": company_id,
                    "phone_hash": hash(phone) % 10000
                })
        except Exception as e:
            logger.error(f"Error updating customer profile: {e}")
            await db.rollback()
        
        return False

    async def save_call_summary(
        self,
        phone: str,
        company_id: int,
        call_id: str,
        summary: str,
        outcome: str,
        sentiment: str,
        duration_seconds: int
    ) -> bool:
        """
        Save a call summary to the customer's history.
        Maintains a maximum of 10 most recent summaries.
        
        Args:
            phone: Customer phone number
            company_id: Company identifier
            call_id: Unique call identifier
            summary: Call summary text
            outcome: Call outcome (completed, transferred, etc.)
            sentiment: Overall sentiment (positive, neutral, negative)
            duration_seconds: Call duration in seconds
            
        Returns:
            True if successful
        """
        try:
            r = await self._get_redis()
            history_key = self._history_key(company_id, phone)
            
            call_summary = CallSummary(
                call_id=call_id,
                date=datetime.utcnow().isoformat(),
                duration_seconds=duration_seconds,
                outcome=outcome,
                sentiment=sentiment,
                summary=summary
            )
            
            # Push to the left of the list (most recent first)
            await r.lpush(history_key, json.dumps(call_summary.model_dump(), default=str))
            
            # Trim to keep only the most recent CALL_HISTORY_MAX items
            await r.ltrim(history_key, 0, CALL_HISTORY_MAX - 1)
            
            # Set TTL on the history key
            await r.expire(history_key, PROFILE_TTL)
            
            logger.debug("Call summary saved", extra={
                "company_id": company_id,
                "call_id": call_id,
                "phone_hash": hash(phone) % 10000
            })
            
            return True
        except Exception as e:
            logger.error(f"Error saving call summary: {e}")
        
        return False

    async def get_call_history_summary(
        self,
        phone: str,
        company_id: int,
        max_calls: int = 3
    ) -> str:
        """
        Get a formatted text summary of call history for system prompt.
        
        Args:
            phone: Customer phone number
            company_id: Company identifier
            max_calls: Maximum number of calls to include (default 3)
            
        Returns:
            Formatted string for system prompt
        """
        try:
            r = await self._get_redis()
            history_key = self._history_key(company_id, phone)
            
            # Get the most recent calls
            raw_history = await r.lrange(history_key, 0, max_calls - 1)
            
            if not raw_history:
                return "No previous call history with this customer."
            
            summaries = []
            for i, raw in enumerate(raw_history, 1):
                call = json.loads(raw)
                date = call.get('date', 'Unknown date')
                duration = call.get('duration_seconds', 0)
                outcome = call.get('outcome', 'Unknown')
                sentiment = call.get('sentiment', 'Unknown')
                call_summary = call.get('summary', 'No summary')
                
                summaries.append(
                    f"Call {i} ({date}, {duration}s): "
                    f"[{sentiment.upper()}] {outcome}. {call_summary}"
                )
            
            return "PREVIOUS CALLS:\n" + "\n".join(summaries)
        except Exception as e:
            logger.error(f"Error getting call history: {e}")
            return "Error retrieving call history."

    async def load_context_for_call(
        self,
        phone: str,
        company_id: int,
        call_id: str,
        db: AsyncSession
    ) -> CallContext:
        """
        Load full context for an incoming call.
        
        Args:
            phone: Customer phone number
            company_id: Company identifier
            call_id: Current call identifier
            db: Database session
            
        Returns:
            CallContext object with all relevant information
        """
        context = CallContext()
        
        # Load customer profile
        profile = await self.get_customer_profile(phone, company_id, db)
        context.customer = profile
        
        # Load call history summary
        context.history_text = await self.get_call_history_summary(phone, company_id)
        
        # Determine if returning customer
        context.is_returning_customer = profile is not None and profile.total_calls > 0
        
        # Calculate days since last call
        if profile and profile.last_call_at:
            try:
                last_call = datetime.fromisoformat(profile.last_call_at)
                context.days_since_last_call = (datetime.utcnow() - last_call).days
            except Exception:
                context.days_since_last_call = None
        
        # Load company knowledge
        context.company_knowledge = await self._get_company_knowledge(company_id)
        
        # Save session context for this call
        await self.save_session_context(call_id, context)
        
        return context

    async def save_session_context(
        self,
        call_id: str,
        context: CallContext,
        ttl_seconds: int = SESSION_TTL
    ) -> bool:
        """
        Save session context to Redis for quick access.
        
        Args:
            call_id: Call identifier
            context: CallContext object
            ttl_seconds: Time to live (default 24 hours)
            
        Returns:
            True if successful
        """
        try:
            r = await self._get_redis()
            session_key = self._session_key(call_id)
            
            context_dict = context.model_dump()
            # Convert datetime objects to strings for JSON serialization
            for key, value in context_dict.items():
                if hasattr(value, 'isoformat'):
                    context_dict[key] = value.isoformat()
            
            await r.setex(session_key, ttl_seconds, json.dumps(context_dict, default=str))
            
            return True
        except Exception as e:
            logger.error(f"Error saving session context: {e}")
        
        return False

    async def mark_customer_vip(
        self,
        phone: str,
        company_id: int,
        reason: str,
        db: AsyncSession
    ) -> bool:
        """
        Mark a customer as VIP.
        
        Args:
            phone: Customer phone number
            company_id: Company identifier
            reason: Reason for VIP status
            db: Database session
            
        Returns:
            True if successful
        """
        try:
            # Update database
            result = await db.execute(
                select(Customer).where(
                    Customer.phone == phone,
                    Customer.company_id == company_id
                )
            )
            customer = result.scalar_one_or_none()
            
            if customer:
                customer.is_vip = True
                customer.vip_reason = reason
                await db.commit()
                
                # Update Redis cache
                try:
                    r = await self._get_redis()
                    profile_key = self._profile_key(company_id, phone)
                    cached = await r.get(profile_key)
                    
                    if cached:
                        profile_data = json.loads(cached)
                        profile_data['is_vip'] = True
                        profile_data['vip_reason'] = reason
                        await r.setex(profile_key, PROFILE_TTL, json.dumps(profile_data))
                except Exception as e:
                    logger.warning(f"Failed to update Redis VIP status: {e}")
                
                logger.info("Customer marked as VIP", extra={
                    "company_id": company_id,
                    "phone_hash": hash(phone) % 10000,
                    "reason": reason
                })
                
                return True
            else:
                logger.warning("Customer not found for VIP marking", extra={
                    "company_id": company_id,
                    "phone_hash": hash(phone) % 10000
                })
        except Exception as e:
            logger.error(f"Error marking customer as VIP: {e}")
            await db.rollback()
        
        return False

    async def get_or_create_customer(
        self,
        phone: str,
        company_id: int,
        name: str,
        db: AsyncSession
    ) -> CustomerProfile:
        """
        Get existing customer or create a new one.
        
        Args:
            phone: Customer phone number
            company_id: Company identifier
            name: Customer name (if known)
            db: Database session
            
        Returns:
            CustomerProfile object
        """
        # Try to get existing profile
        existing = await self.get_customer_profile(phone, company_id, db)
        
        if existing:
            return existing
        
        # Create new customer
        try:
            customer = Customer(
                phone=phone,
                company_id=company_id,
                name=name,
                total_calls=0
            )
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
            
            profile = CustomerProfile(
                phone=customer.phone,
                company_id=customer.company_id,
                name=customer.name,
                total_calls=0,
                is_vip=False,
                preferences={},
                call_history=[],
                created_at=customer.created_at.isoformat() if customer.created_at else None
            )
            
            # Cache in Redis
            try:
                r = await self._get_redis()
                await r.setex(
                    self._profile_key(company_id, phone),
                    PROFILE_TTL,
                    json.dumps(profile.model_dump(), default=str)
                )
            except Exception as e:
                logger.warning(f"Failed to cache new customer: {e}")
            
            logger.info("New customer created", extra={
                "company_id": company_id,
                "phone_hash": hash(phone) % 10000
            })
            
            return profile
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            await db.rollback()
            
            # Return empty profile as fallback
            return CustomerProfile(
                phone=phone,
                company_id=company_id,
                name=name,
                total_calls=0
            )

    async def _get_company_knowledge(self, company_id: int) -> str:
        """
        Get company-specific knowledge from Redis.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Company knowledge string or empty string
        """
        try:
            r = await self._get_redis()
            knowledge_key = self._company_knowledge_key(company_id)
            
            knowledge = await r.get(knowledge_key)
            return knowledge if knowledge else ""
        except Exception as e:
            logger.error(f"Error getting company knowledge: {e}")
            return ""

    async def set_company_knowledge(
        self,
        company_id: int,
        knowledge: str,
        ttl_seconds: int = COMPANY_KNOWLEDGE_TTL
    ) -> bool:
        """
        Set company-specific knowledge in Redis.
        
        Args:
            company_id: Company identifier
            knowledge: Knowledge text to store
            ttl_seconds: Time to live (default 7 days)
            
        Returns:
            True if successful
        """
        try:
            r = await self._get_redis()
            knowledge_key = self._company_knowledge_key(company_id)
            await r.setex(knowledge_key, ttl_seconds, knowledge)
            return True
        except Exception as e:
            logger.error(f"Error setting company knowledge: {e}")
            return False
