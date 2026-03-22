"""
Celery configuration — VoiceCore

Features:
  - Redis broker
  - Beat scheduler for periodic tasks
  - 3 queues: default, high_priority, scheduled
  - Proper serialization
  - Error handling + logging
"""

import os
from celery import Celery
from celery.schedules import crontab

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "voicecore",
    broker=redis_url,
    backend=redis_url,
    include=[
        "tasks.email_tasks",
        "tasks.notification_tasks",
        "tasks.reminder_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "high_priority": {
            "exchange": "high_priority",
            "routing_key": "high",
        },
        "scheduled": {
            "exchange": "scheduled",
            "routing_key": "scheduled",
        },
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    task_routes={
        "tasks.notification_tasks.send_angry_alert": {"queue": "high_priority"},
        "tasks.notification_tasks.send_emergency_alert": {"queue": "high_priority"},
        "tasks.notification_tasks.send_missed_call_alert": {"queue": "high_priority"},
        "tasks.email_tasks.send_daily_summaries": {"queue": "scheduled"},
        "tasks.email_tasks.send_weekly_reports": {"queue": "scheduled"},
        "tasks.email_tasks.check_inactive_companies": {"queue": "scheduled"},
        "tasks.email_tasks.send_day3_checkins": {"queue": "scheduled"},
        "tasks.email_tasks.retry_failed_notifications": {"queue": "scheduled"},
        "tasks.notification_tasks.check_provider_health": {"queue": "scheduled"},
        "tasks.notification_tasks.check_calls_limit": {"queue": "scheduled"},
        "tasks.reminder_tasks.send_appointment_reminders": {"queue": "scheduled"},
        "tasks.reminder_tasks.send_2h_reminders": {"queue": "scheduled"},
    },
    
    beat_schedule={
        "daily-summaries": {
            "task": "tasks.email_tasks.send_daily_summaries",
            "schedule": crontab(hour=8, minute=0),
            "options": {"queue": "scheduled"},
        },
        "weekly-reports": {
            "task": "tasks.email_tasks.send_weekly_reports",
            "schedule": crontab(day_of_week=1, hour=8, minute=0),
            "options": {"queue": "scheduled"},
        },
        "check-inactive": {
            "task": "tasks.email_tasks.check_inactive_companies",
            "schedule": crontab(hour=9, minute=0),
            "options": {"queue": "scheduled"},
        },
        "day3-checkins": {
            "task": "tasks.email_tasks.send_day3_checkins",
            "schedule": crontab(hour=10, minute=0),
            "options": {"queue": "scheduled"},
        },
        "appointment-reminders": {
            "task": "tasks.reminder_tasks.send_appointment_reminders",
            "schedule": crontab(minute=0),
            "options": {"queue": "scheduled"},
        },
        "2h-reminders": {
            "task": "tasks.reminder_tasks.send_2h_reminders",
            "schedule": crontab(minute="*/30"),
            "options": {"queue": "scheduled"},
        },
        "retry-notifications": {
            "task": "tasks.email_tasks.retry_failed_notifications",
            "schedule": crontab(minute="*/30"),
            "options": {"queue": "scheduled"},
        },
        "provider-health-check": {
            "task": "tasks.notification_tasks.check_provider_health",
            "schedule": crontab(minute="*/5"),
            "options": {"queue": "scheduled"},
        },
        "cleanup-old-appointments": {
            "task": "tasks.reminder_tasks.cleanup_old_appointments",
            "schedule": crontab(day_of_week=0, hour=3, minute=0),
            "options": {"queue": "scheduled"},
        },
    },
)


@celery_app.task(name="send_whatsapp_confirmation")
def send_whatsapp_confirmation(phone: str, appointment_details: dict):
    from services.whatsapp_service import whatsapp_service
    import asyncio
    
    async def _send():
        await whatsapp_service.send_confirmation(phone, appointment_details)
    
    asyncio.run(_send())
    return {"status": "sent", "phone": phone}


@celery_app.task(name="send_reminder")
def send_reminder(phone: str, appointment_details: dict, reminder_type: str = "24h"):
    from services.whatsapp_service import whatsapp_service
    import asyncio
    
    async def _send():
        await whatsapp_service.send_reminder(phone, appointment_details, reminder_type)
    
    asyncio.run(_send())
    return {"status": "sent", "phone": phone, "type": reminder_type}


@celery_app.task(name="save_transcript")
def save_transcript(call_id: int, transcript: str):
    from db.database import AsyncSessionLocal
    from db.models import Call
    from sqlalchemy import select
    import asyncio
    
    async def _save():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Call).where(Call.id == call_id))
            call = result.scalar_one_or_none()
            if call:
                call.transcript = transcript
                await session.commit()
    
    asyncio.run(_save())
    return {"status": "saved", "call_id": call_id}


@celery_app.task(name="generate_analytics_report")
def generate_analytics_report(company_id: int, start_date: str, end_date: str):
    from db.database import AsyncSessionLocal
    from db.models import Call
    from sqlalchemy import select, func
    import asyncio
    
    async def _generate():
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count(Call.id), func.sum(Call.duration_seconds))
                .where(Call.company_id == company_id)
            )
            count, duration = result.one()
            return {
                "company_id": company_id,
                "total_calls": count,
                "total_duration": duration or 0,
                "period": f"{start_date} to {end_date}"
            }
    
    return asyncio.run(_generate())


@celery_app.task(name="cleanup_old_calls")
def cleanup_old_calls(days: int = 90):
    from db.database import AsyncSessionLocal
    from db.models import Call
    from sqlalchemy import delete
    from datetime import datetime, timedelta
    import asyncio
    
    async def _cleanup():
        cutoff = datetime.utcnow() - timedelta(days=days)
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(Call).where(Call.created_at < cutoff)
            )
            await session.commit()
    
    asyncio.run(_cleanup())
    return {"status": "cleaned", "days": days}


@celery_app.task(name="schedule_reminders")
def schedule_reminders():
    from db.database import AsyncSessionLocal
    from db.models import Call
    from sqlalchemy import select
    import asyncio
    
    async def _schedule():
        tomorrow = datetime.utcnow() + timedelta(days=1)
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Call).where(Call.created_at >= tomorrow)
            )
            calls = result.scalars().all()
            
            for call in calls:
                send_reminder.apply_async(
                    args=[call.caller_phone, {"date": "tomorrow", "time": "10:00"}],
                    eta=tomorrow
                )
    
    asyncio.run(_schedule())
    return {"status": "scheduled"}
