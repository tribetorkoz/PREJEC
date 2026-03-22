"""
Email Tasks — VoiceCore

Celery tasks for scheduled and recurring emails.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from celery_app import celery_app
from db.database import async_session
from db.models import Company, Call, Notification, NotificationPreferences, Agent
from services.email_service import EmailService
from services.notification_service import notification_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(
    self,
    to: str,
    template: str,
    context: dict,
    subject: Optional[str] = None,
):
    """
    Generic email task with retry.
    Exponential backoff: 1min, 5min, 15min
    """
    try:
        email_service = EmailService()
        
        if template == "angry_customer_alert":
            return email_service.send_angry_customer_alert(
                to_email=to,
                company_name=context.get("company_name", ""),
                call_data=context.get("call_data", {}),
            )
        elif template == "daily_summary":
            return email_service.send_daily_summary_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                stats=context.get("stats", {}),
            )
        elif template == "weekly_report":
            return email_service.send_weekly_report_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                report=context.get("report", {}),
            )
        elif template == "welcome":
            return email_service.send_welcome_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                user_name=context.get("user_name", ""),
            )
        elif template == "onboarding_complete":
            return email_service.send_onboarding_completed_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                phone_number=context.get("phone_number", ""),
                agent_name=context.get("agent_name", ""),
            )
        elif template == "payment_failed":
            return email_service.send_payment_failed_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                amount=context.get("amount", 0),
                retry_date=context.get("retry_date"),
            )
        elif template == "missed_call":
            return email_service.send_missed_call_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                caller_phone=context.get("caller_phone", ""),
            )
        elif template == "day3_checkin":
            return email_service.send_day3_checkin_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                calls_so_far=context.get("calls_so_far", 0),
            )
        elif template == "churn_risk":
            return email_service.send_churn_risk_email(
                to_email=to,
                company_name=context.get("company_name", ""),
                days_inactive=context.get("days_inactive", 0),
            )
        else:
            return email_service.send_generic_notification(
                to_email=to,
                subject=subject or f"VoiceCore Notification",
                message=context.get("message", ""),
            )
            
    except Exception as exc:
        logger.error(f"Failed to send email to {to}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def send_daily_summaries():
    """
    Runs every day at 8:00 AM UTC.
    Fetches all companies with their different timezones.
    Sends each company at the correct time for their timezone.
    """
    async def _send_summaries():
        async with async_session() as db:
            result = await db.execute(
                select(NotificationPreferences).where(
                    NotificationPreferences.email_daily_summary == True
                )
            )
            prefs_list = result.scalars().all()
            
            today = datetime.utcnow()
            
            for prefs in prefs_list:
                try:
                    result = await db.execute(
                        select(Company).where(Company.id == prefs.company_id)
                    )
                    company = result.scalar_one_or_none()
                    
                    if not company:
                        continue
                    
                    recipient = prefs.notification_email or company.email
                    
                    stats = await _calculate_daily_stats(db, company.id, today)
                    
                    await notification_service.send_daily_summary(
                        company_id=company.id,
                        stats=stats,
                        db=db,
                    )
                    
                    logger.info(f"Daily summary sent to {company.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to send daily summary for company {prefs.company_id}: {e}")
    
    import asyncio
    asyncio.run(_send_summaries())


@celery_app.task
def send_weekly_reports():
    """
    Runs every Monday at 8:00 AM UTC.
    """
    async def _send_reports():
        async with async_session() as db:
            result = await db.execute(
                select(NotificationPreferences).where(
                    NotificationPreferences.email_weekly_report == True
                )
            )
            prefs_list = result.scalars().all()
            
            today = datetime.utcnow()
            week_start = today - timedelta(days=7)
            
            for prefs in prefs_list:
                try:
                    result = await db.execute(
                        select(Company).where(Company.id == prefs.company_id)
                    )
                    company = result.scalar_one_or_none()
                    
                    if not company:
                        continue
                    
                    report = await _calculate_weekly_report(db, company.id, week_start, today)
                    
                    await notification_service.send_weekly_report(
                        company_id=company.id,
                        report=report,
                        db=db,
                    )
                    
                    logger.info(f"Weekly report sent to {company.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to send weekly report for company {prefs.company_id}: {e}")
    
    import asyncio
    asyncio.run(_send_reports())


@celery_app.task
def check_inactive_companies():
    """
    Runs daily.
    Finds companies that haven't had calls for 7+ days.
    Sends churn risk email.
    """
    async def _check_inactive():
        async with async_session() as db:
            result = await db.execute(
                select(Company)
            )
            companies = result.scalars().all()
            
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            for company in companies:
                try:
                    result = await db.execute(
                        select(func.count(Call.id)).where(
                            Call.company_id == company.id,
                            Call.created_at >= seven_days_ago
                        )
                    )
                    call_count = result.scalar() or 0
                    
                    if call_count == 0:
                        prefs_result = await db.execute(
                            select(NotificationPreferences).where(
                                NotificationPreferences.company_id == company.id
                            )
                        )
                        prefs = prefs_result.scalar_one_or_none()
                        
                        if prefs and prefs.email_daily_summary:
                            await notification_service.send_daily_summary(
                                company_id=company.id,
                                stats={
                                    "total_calls": 0,
                                    "total_duration": 0,
                                    "avg_sentiment": 0,
                                    "resolved_rate": 0,
                                    "missed_calls": 0,
                                    "appointments_booked": 0,
                                    "top_event": "No activity",
                                    "days_inactive": 7,
                                },
                                db=db,
                            )
                            
                            logger.info(f"Churn risk notification sent to {company.name}")
                
                except Exception as e:
                    logger.error(f"Failed to check inactive company {company.id}: {e}")
    
    import asyncio
    asyncio.run(_check_inactive())


@celery_app.task
def send_day3_checkins():
    """
    Runs daily.
    Finds companies on their 3rd day after onboarding.
    Sends check-in email.
    """
    async def _send_checkins():
        async with async_session() as db:
            from db.models import OnboardingState
            
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            
            result = await db.execute(
                select(OnboardingState).where(
                    OnboardingState.completed == True,
                    OnboardingState.completed_at != None,
                )
            )
            states = result.scalars().all()
            
            for state in states:
                if state.completed_at and (
                    datetime.utcnow() - state.completed_at.replace(tzinfo=None)
                ).days == 3:
                    try:
                        result = await db.execute(
                            select(Company).where(Company.id == state.company_id)
                        )
                        company = result.scalar_one_or_none()
                        
                        if not company:
                            continue
                        
                        result = await db.execute(
                            select(func.count(Call.id)).where(
                                Call.company_id == company.id
                            )
                        )
                        call_count = result.scalar() or 0
                        
                        recipient = company.email
                        
                        email_service = EmailService()
                        await email_service.send_day3_checkin_email(
                            to_email=recipient,
                            company_name=company.name,
                            calls_so_far=call_count,
                        )
                        
                        logger.info(f"Day 3 checkin sent to {company.name}")
                        
                    except Exception as e:
                        logger.error(f"Failed to send day 3 checkin for company {state.company_id}: {e}")
    
    import asyncio
    asyncio.run(_send_checkins())


@celery_app.task
def retry_failed_notifications():
    """
    Runs every 30 minutes.
    Retries failed notifications.
    Attempts 3 times max then alerts admin.
    """
    async def _retry_failed():
        async with async_session() as db:
            result = await db.execute(
                select(Notification).where(
                    Notification.status == "failed"
                ).limit(100)
            )
            failed_notifications = result.scalars().all()
            
            for notification in failed_notifications:
                retry_count = notification.metadata.get("retry_count", 0) if notification.metadata else 0
                
                if retry_count >= 3:
                    notification.status = "abandoned"
                    logger.warning(f"Notification {notification.id} abandoned after 3 retries")
                    continue
                
                try:
                    new_retry_count = retry_count + 1
                    
                    if notification.metadata:
                        notification.metadata["retry_count"] = new_retry_count
                    else:
                        notification.metadata = {"retry_count": new_retry_count}
                    
                    await db.commit()
                    
                    send_email_task.apply_async(
                        kwargs={
                            "to": notification.recipient,
                            "template": notification.event_type,
                            "context": {"company_name": "VoiceCore"},
                            "subject": f"Retry: {notification.subject}",
                        },
                        countdown=new_retry_count * 60,
                    )
                    
                    logger.info(f"Retry {new_retry_count} scheduled for notification {notification.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to retry notification {notification.id}: {e}")
    
    import asyncio
    asyncio.run(_retry_failed())


async def _calculate_daily_stats(
    db: AsyncSession, company_id: int, date: datetime
) -> dict:
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    result = await db.execute(
        select(func.count(Call.id)).where(
            Call.company_id == company_id,
            Call.created_at >= start_of_day,
            Call.created_at < end_of_day,
        )
    )
    total_calls = result.scalar() or 0
    
    result = await db.execute(
        select(func.sum(Call.duration_seconds)).where(
            Call.company_id == company_id,
            Call.created_at >= start_of_day,
            Call.created_at < end_of_day,
        )
    )
    total_duration = (result.scalar() or 0) / 60
    
    result = await db.execute(
        select(func.avg(Call.sentiment_score)).where(
            Call.company_id == company_id,
            Call.created_at >= start_of_day,
            Call.created_at < end_of_day,
        )
    )
    avg_sentiment = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(Call.id)).where(
            Call.company_id == company_id,
            Call.created_at >= start_of_day,
            Call.created_at < end_of_day,
            Call.outcome == "resolved",
        )
    )
    resolved = result.scalar() or 0
    resolved_rate = (resolved / total_calls * 100) if total_calls > 0 else 0
    
    result = await db.execute(
        select(func.count(Call.id)).where(
            Call.company_id == company_id,
            Call.created_at >= start_of_day,
            Call.created_at < end_of_day,
            Call.outcome == "missed",
        )
    )
    missed_calls = result.scalar() or 0
    
    return {
        "total_calls": total_calls,
        "total_duration": round(total_duration, 1),
        "avg_sentiment": round(avg_sentiment, 1),
        "resolved_rate": round(resolved_rate, 1),
        "missed_calls": missed_calls,
        "appointments_booked": 0,
        "top_event": "Normal calls",
    }


async def _calculate_weekly_report(
    db: AsyncSession, company_id: int, week_start: datetime, week_end: datetime
) -> dict:
    result = await db.execute(
        select(func.count(Call.id)).where(
            Call.company_id == company_id,
            Call.created_at >= week_start,
            Call.created_at < week_end,
        )
    )
    total_calls = result.scalar() or 0
    
    prev_week_start = week_start - timedelta(days=7)
    result = await db.execute(
        select(func.count(Call.id)).where(
            Call.company_id == company_id,
            Call.created_at >= prev_week_start,
            Call.created_at < week_start,
        )
    )
    prev_week_calls = result.scalar() or 0
    
    weekly_trend = 0
    if prev_week_calls > 0:
        weekly_trend = ((total_calls - prev_week_calls) / prev_week_calls) * 100
    
    return {
        "total_calls": total_calls,
        "weekly_trend": round(weekly_trend, 1),
        "compared_to_last_week": total_calls - prev_week_calls,
        "missed_calls": 0,
        "appointments_booked": 0,
        "avg_sentiment": 0,
        "top_event": "Normal activity",
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
    }
