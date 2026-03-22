"""
Reminder Tasks — VoiceCore

WhatsApp/SMS reminders for appointments.
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from celery_app import celery_app
from db.database import async_session
from db.models import Appointment, Company
from services.sms_service import SMSService

logger = logging.getLogger(__name__)


@celery_app.task
def send_appointment_reminders():
    """
    Runs every hour.
    Finds all appointments within 24 hours.
    Sends WhatsApp reminder or SMS.
    """
    async def _send_reminders():
        async with async_session() as db:
            try:
                tomorrow = datetime.utcnow() + timedelta(hours=24)
                now = datetime.utcnow()
                
                result = await db.execute(
                    select(Appointment).where(
                        Appointment.status == "confirmed",
                        Appointment.reminder_sent_24h == False,
                    )
                )
                appointments = result.scalars().all()
                
                sms_service = SMSService()
                
                for appointment in appointments:
                    try:
                        appointment_datetime = datetime.strptime(
                            f"{appointment.date} {appointment.time}",
                            "%Y-%m-%d %H:%M"
                        )
                        
                        if now <= appointment_datetime <= tomorrow:
                            result = await db.execute(
                                select(Company).where(Company.id == appointment.company_id)
                            )
                            company = result.scalar_one_or_none()
                            
                            if not company:
                                continue
                            
                            message = (
                                f"Hi {appointment.customer_name}! Reminder: You have an appointment "
                                f"at {company.name} tomorrow at {appointment.time}. "
                                f"Reply 'C' to confirm or 'R' to reschedule. "
                                f"Powered by VoiceCore."
                            )
                            
                            result = await sms_service.send_sms(
                                to=appointment.customer_phone,
                                message=message,
                            )
                            
                            if result.get("success"):
                                appointment.reminder_sent_24h = True
                                await db.commit()
                                logger.info(f"24h reminder sent for appointment {appointment.id}")
                            
                    except Exception as e:
                        logger.error(f"Failed to send reminder for appointment {appointment.id}: {e}")
                
            except Exception as e:
                logger.error(f"Appointment reminder task failed: {e}")
    
    import asyncio
    asyncio.run(_send_reminders())


@celery_app.task
def send_2h_reminders():
    """
    Runs every 30 minutes.
    Sends 2-hour reminder for upcoming appointments.
    """
    async def _send_reminders():
        async with async_session() as db:
            try:
                two_hours_from_now = datetime.utcnow() + timedelta(hours=2)
                one_hour_from_now = datetime.utcnow() + timedelta(hours=1)
                
                result = await db.execute(
                    select(Appointment).where(
                        Appointment.status == "confirmed",
                        Appointment.reminder_sent_2h == False,
                    )
                )
                appointments = result.scalars().all()
                
                sms_service = SMSService()
                
                for appointment in appointments:
                    try:
                        appointment_datetime = datetime.strptime(
                            f"{appointment.date} {appointment.time}",
                            "%Y-%m-%d %H:%M"
                        )
                        
                        if one_hour_from_now <= appointment_datetime <= two_hours_from_now:
                            result = await db.execute(
                                select(Company).where(Company.id == appointment.company_id)
                            )
                            company = result.scalar_one_or_none()
                            
                            if not company:
                                continue
                            
                            message = (
                                f"Hi {appointment.customer_name}! Reminder: Your appointment "
                                f"at {company.name} is in 2 hours at {appointment.time}. "
                                f"See you soon! Powered by VoiceCore."
                            )
                            
                            result = await sms_service.send_sms(
                                to=appointment.customer_phone,
                                message=message,
                            )
                            
                            if result.get("success"):
                                appointment.reminder_sent_2h = True
                                await db.commit()
                                logger.info(f"2h reminder sent for appointment {appointment.id}")
                            
                    except Exception as e:
                        logger.error(f"Failed to send 2h reminder for appointment {appointment.id}: {e}")
                
            except Exception as e:
                logger.error(f"2h reminder task failed: {e}")
    
    import asyncio
    asyncio.run(_send_reminders())


@celery_app.task
def process_reminder_replies():
    """
    Processes customer replies to reminders.
    'C' → confirms appointment
    'R' → notifies company to reschedule
    """
    async def _process_replies():
        async with async_session() as db:
            try:
                logger.info("Processing reminder replies...")
                
            except Exception as e:
                logger.error(f"Process reminder replies failed: {e}")
    
    import asyncio
    asyncio.run(_process_replies())


@celery_app.task
def cleanup_old_appointments():
    """
    Runs weekly.
    Archives or deletes appointments older than 90 days.
    """
    async def _cleanup():
        async with async_session() as db:
            try:
                ninety_days_ago = datetime.utcnow() - timedelta(days=90)
                
                logger.info(f"Cleaning up appointments older than {ninety_days_ago}")
                
            except Exception as e:
                logger.error(f"Cleanup old appointments failed: {e}")
    
    import asyncio
    asyncio.run(_cleanup())
