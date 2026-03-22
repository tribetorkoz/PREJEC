"""
Notification Tasks — VoiceCore

Celery tasks for real-time notifications.
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from celery_app import celery_app
from db.database import async_session
from db.models import Call, Company, NotificationPreferences, Agent
from services.notification_service import notification_service, NotificationEvent

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_angry_alert(self, company_id: int, call_id: int):
    """
    Sends angry customer alert immediately.
    High priority queue.
    """
    import asyncio
    
    async def _send_alert():
        async with async_session() as db:
            try:
                result = await db.execute(
                    select(Call).where(Call.id == call_id)
                )
                call = result.scalar_one_or_none()
                
                if not call:
                    logger.error(f"Call {call_id} not found")
                    return False
                
                call_data = {
                    "call_id": call.id,
                    "caller_phone": call.caller_phone,
                    "call_time": call.created_at.isoformat() if call.created_at else datetime.utcnow().isoformat(),
                    "duration": call.duration_seconds,
                    "sentiment": call.sentiment,
                    "last_statement": _extract_last_statement(call.transcript),
                    "recording_url": call.recording_url,
                }
                
                await notification_service.notify_angry_customer(
                    company_id=company_id,
                    call_data=call_data,
                    db=db,
                )
                
                logger.info(f"Angry customer alert sent for call {call_id}")
                return True
                
            except Exception as exc:
                logger.error(f"Failed to send angry alert for call {call_id}: {exc}")
                raise self.retry(exc=exc, countdown=30)
    
    asyncio.run(_send_alert())


@celery_app.task(bind=True, max_retries=3)
def send_missed_call_alert(self, company_id: int, caller_phone: str, call_id: int):
    """
    Sends missed call alert after 5 minutes.
    """
    import asyncio
    
    async def _send_alert():
        async with async_session() as db:
            try:
                await notification_service.notify_missed_call(
                    company_id=company_id,
                    caller_phone=caller_phone,
                    db=db,
                )
                
                logger.info(f"Missed call alert sent for {caller_phone}")
                return True
                
            except Exception as exc:
                logger.error(f"Failed to send missed call alert: {exc}")
                raise self.retry(exc=exc, countdown=60)
    
    asyncio.run(_send_alert())


@celery_app.task(bind=True, max_retries=3)
def send_emergency_alert(self, company_id: int, message: str, call_id: int = None):
    """
    Sends emergency alert immediately.
    Critical priority.
    """
    import asyncio
    
    async def _send_alert():
        async with async_session() as db:
            try:
                await notification_service.notify_emergency(
                    company_id=company_id,
                    message=message,
                    db=db,
                )
                
                logger.info(f"Emergency alert sent for company {company_id}")
                return True
                
            except Exception as exc:
                logger.error(f"Failed to send emergency alert: {exc}")
                raise self.retry(exc=exc, countdown=30)
    
    asyncio.run(_send_alert())


@celery_app.task
def send_hot_lead_alert(company_id: int, lead_data: dict):
    """
    Sends hot lead alert for real estate verticals.
    """
    import asyncio
    
    async def _send_alert():
        async with async_session() as db:
            try:
                await notification_service.notify_hot_lead(
                    company_id=company_id,
                    lead_data=lead_data,
                    db=db,
                )
                
                logger.info(f"Hot lead alert sent for company {company_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send hot lead alert: {e}")
                return False
    
    asyncio.run(_send_alert())


@celery_app.task
def check_provider_health():
    """
    Runs every 5 minutes.
    Checks health of voice providers (Deepgram, ElevenLabs, etc.)
    Sends alerts if any provider is down.
    """
    import asyncio
    
    async def _check_health():
        async with async_session() as db:
            try:
                from services.provider_registry import provider_registry
                
                unhealthy_providers = []
                
                for provider_name in ["deepgram", "elevenlabs"]:
                    health = await provider_registry.get_provider_health(provider_name)
                    
                    if not health.get("healthy", False):
                        unhealthy_providers.append({
                            "provider": provider_name,
                            "error": health.get("error", "Unknown error"),
                            "last_check": health.get("last_check"),
                        })
                
                if unhealthy_providers:
                    logger.warning(f"Unhealthy providers detected: {unhealthy_providers}")
                    
                    result = await db.execute(
                        select(Company)
                    )
                    companies = result.scalars().all()
                    
                    for company in companies:
                        prefs_result = await db.execute(
                            select(NotificationPreferences).where(
                                NotificationPreferences.company_id == company.id
                            )
                        )
                        prefs = prefs_result.scalar_one_or_none()
                        
                        if prefs and prefs.notification_email:
                            await notification_service.notify(
                                company_id=company.id,
                                event=NotificationEvent.EMERGENCY,
                                data={
                                    "message": f"Voice provider issue: {unhealthy_providers[0]['provider']}",
                                    "providers": unhealthy_providers,
                                },
                                priority="critical",
                                db=db,
                            )
                
                logger.info("Provider health check completed")
                
            except Exception as e:
                logger.error(f"Provider health check failed: {e}")
    
    asyncio.run(_check_health())


@celery_app.task
def check_calls_limit(company_id: int):
    """
    Checks if company is approaching or has reached their calls limit.
    """
    import asyncio
    
    async def _check_limit():
        async with async_session() as db:
            try:
                result = await db.execute(
                    select(Company).where(Company.id == company_id)
                )
                company = result.scalar_one_or_none()
                
                if not company:
                    return
                
                plan_limits = {
                    "free": 50,
                    "starter": 500,
                    "professional": 2000,
                    "business": 10000,
                    "enterprise": 100000,
                }
                
                max_calls = plan_limits.get(company.plan, 50)
                
                start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                result = await db.execute(
                    select(func.count(Call.id)).where(
                        Call.company_id == company_id,
                        Call.created_at >= start_of_month,
                    )
                )
                current_calls = result.scalar() or 0
                
                await notification_service.check_and_notify_limits(
                    company_id=company_id,
                    current_calls=current_calls,
                    max_calls=max_calls,
                    db=db,
                )
                
                logger.info(f"Calls limit check for {company.name}: {current_calls}/{max_calls}")
                
            except Exception as e:
                logger.error(f"Calls limit check failed for company {company_id}: {e}")
    
    asyncio.run(_check_limit())


def _extract_last_statement(transcript: str) -> str:
    """
    Extracts the last statement from a transcript.
    """
    if not transcript:
        return "Customer was speaking during the call."
    
    lines = transcript.strip().split("\n")
    if not lines:
        return "Customer was speaking during the call."
    
    last_lines = [l for l in lines[-3:] if l.strip()]
    
    if last_lines:
        return last_lines[-1].strip()
    
    return "Customer was speaking during the call."
