"""
Notification System — VoiceCore

Companies get notified of everything important immediately.

Supported channels:
  1. Email (SendGrid) — for important events
  2. SMS (Twilio) — for emergencies and angry customers
  3. Webhook — for companies wanting Zapier/Slack integration

Events that trigger notifications:
  ANGRY_CUSTOMER      → email + sms immediately
  MISSED_CALL         → email within 5 minutes
  HOT_LEAD (realty)   → email + sms immediately
  EMERGENCY (dental)  → sms immediately
  DAILY_SUMMARY       → email every day 8 AM
  WEEKLY_REPORT       → email every Monday
  CALLS_LIMIT_90%     → warning email
  CALLS_LIMIT_100%    → email + disable agent
  PAYMENT_FAILED      → email
"""

import logging
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_dependency
from db.models import Company, Notification, NotificationPreferences, Call
from config import settings

logger = logging.getLogger(__name__)


class NotificationEvent(str, Enum):
    ANGRY_CUSTOMER = "angry_customer"
    MISSED_CALL = "missed_call"
    HOT_LEAD = "hot_lead"
    EMERGENCY = "emergency"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    CALLS_LIMIT_WARNING = "calls_limit_warning"
    CALLS_LIMIT_REACHED = "calls_limit_reached"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_SUCCESS = "payment_success"
    NEW_APPOINTMENT = "new_appointment"
    CALL_RECORDING_READY = "call_recording_ready"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationPriority(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationService:
    
    def __init__(self):
        self.email_service = None
        self.sms_service = None
    
    async def _get_email_service(self):
        if self.email_service is None:
            try:
                from services.email_service import EmailService
                self.email_service = EmailService()
            except ImportError:
                logger.warning("Email service not available")
                self.email_service = None
        return self.email_service
    
    async def _get_sms_service(self):
        if self.sms_service is None:
            try:
                from services.sms_service import SMSService
                self.sms_service = SMSService()
            except ImportError:
                logger.warning("SMS service not available")
                self.sms_service = None
        return self.sms_service
    
    async def get_preferences(
        self, company_id: int, db: AsyncSession
    ) -> Optional[NotificationPreferences]:
        result = await db.execute(
            select(NotificationPreferences).where(
                NotificationPreferences.company_id == company_id
            )
        )
        return result.scalar_one_or_none()
    
    async def notify(
        self,
        company_id: int,
        event: NotificationEvent,
        data: dict,
        priority: str = "normal",
        db: AsyncSession = None,
    ) -> bool:
        if db is None:
            db = await get_db_dependency().__anext__()
        
        prefs = await self.get_preferences(company_id, db)
        
        if prefs is None:
            prefs = NotificationPreferences(company_id=company_id)
            db.add(prefs)
            await db.commit()
        
        result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            logger.error(f"Company {company_id} not found")
            return False
        
        notification_targets = self._determine_channels(event, priority, prefs)
        
        success = True
        for channel in notification_targets:
            try:
                await self._send_via_channel(
                    channel=channel,
                    company_id=company_id,
                    event=event,
                    data=data,
                    company=company,
                    prefs=prefs,
                    db=db,
                )
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                success = False
        
        return success
    
    def _determine_channels(
        self,
        event: NotificationEvent,
        priority: str,
        prefs: NotificationPreferences,
    ) -> list[NotificationChannel]:
        channels = []
        
        if event == NotificationEvent.ANGRY_CUSTOMER:
            if priority == NotificationPriority.CRITICAL or prefs.email_angry_customer:
                channels.append(NotificationChannel.EMAIL)
            if prefs.sms_angry_customer:
                channels.append(NotificationChannel.SMS)
            channels.append(NotificationChannel.IN_APP)
            
        elif event == NotificationEvent.MISSED_CALL:
            if prefs.email_missed_call:
                channels.append(NotificationChannel.EMAIL)
            channels.append(NotificationChannel.IN_APP)
            
        elif event == NotificationEvent.EMERGENCY:
            channels.append(NotificationChannel.SMS)
            channels.append(NotificationChannel.EMAIL)
            channels.append(NotificationChannel.IN_APP)
            
        elif event == NotificationEvent.DAILY_SUMMARY:
            if prefs.email_daily_summary:
                channels.append(NotificationChannel.EMAIL)
            channels.append(NotificationChannel.IN_APP)
            
        elif event == NotificationEvent.WEEKLY_REPORT:
            if prefs.email_weekly_report:
                channels.append(NotificationChannel.EMAIL)
            channels.append(NotificationChannel.IN_APP)
            
        elif event in [
            NotificationEvent.CALLS_LIMIT_WARNING,
            NotificationEvent.CALLS_LIMIT_REACHED,
            NotificationEvent.PAYMENT_FAILED,
        ]:
            channels.append(NotificationChannel.EMAIL)
            channels.append(NotificationChannel.IN_APP)
            
        else:
            channels.append(NotificationChannel.IN_APP)
        
        return channels
    
    async def _send_via_channel(
        self,
        channel: NotificationChannel,
        company_id: int,
        event: NotificationEvent,
        data: dict,
        company: Company,
        prefs: NotificationPreferences,
        db: AsyncSession,
    ) -> bool:
        recipient = prefs.notification_email or company.email
        phone = prefs.notification_phone or company.phone_number
        
        notification = Notification(
            company_id=company_id,
            event_type=event.value,
            channel=channel.value,
            recipient=recipient if channel == NotificationChannel.EMAIL else phone,
            status="pending",
            metadata=data,
        )
        db.add(notification)
        await db.flush()
        
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(
                    event=event,
                    data=data,
                    company=company,
                    recipient=recipient,
                    notification_id=notification.id,
                    db=db,
                )
                
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(
                    event=event,
                    data=data,
                    company=company,
                    phone=phone,
                    notification_id=notification.id,
                    db=db,
                )
                
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(
                    event=event,
                    data=data,
                    prefs=prefs,
                    notification_id=notification.id,
                    db=db,
                )
                
            elif channel == NotificationChannel.IN_APP:
                notification.status = "delivered"
                await db.commit()
                return True
                
        except Exception as e:
            notification.status = "failed"
            await db.commit()
            raise e
        
        return False
    
    async def _send_email(
        self,
        event: NotificationEvent,
        data: dict,
        company: Company,
        recipient: str,
        notification_id: int,
        db: AsyncSession,
    ) -> bool:
        email_service = await self._get_email_service()
        
        if email_service is None:
            logger.warning("Email service not available")
            return False
        
        try:
            if event == NotificationEvent.ANGRY_CUSTOMER:
                await email_service.send_angry_customer_alert(
                    to_email=recipient,
                    company_name=company.name,
                    call_data=data,
                )
            elif event == NotificationEvent.MISSED_CALL:
                await email_service.send_missed_call_email(
                    to_email=recipient,
                    company_name=company.name,
                    caller_phone=data.get("caller_phone", "Unknown"),
                )
            elif event == NotificationEvent.DAILY_SUMMARY:
                await email_service.send_daily_summary_email(
                    to_email=recipient,
                    company_name=company.name,
                    stats=data,
                )
            elif event == NotificationEvent.WEEKLY_REPORT:
                await email_service.send_weekly_report_email(
                    to_email=recipient,
                    company_name=company.name,
                    report=data,
                )
            elif event == NotificationEvent.PAYMENT_FAILED:
                await email_service.send_payment_failed_email(
                    to_email=recipient,
                    company_name=company.name,
                    amount=data.get("amount", 0),
                    retry_date=data.get("retry_date"),
                )
            else:
                await email_service.send_generic_notification(
                    to_email=recipient,
                    subject=f"VoiceCore Notification: {event.value}",
                    message=data.get("message", ""),
                )
            
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            if notification:
                notification.status = "sent"
                notification.subject = f"VoiceCore: {event.value}"
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def _send_sms(
        self,
        event: NotificationEvent,
        data: dict,
        company: Company,
        phone: str,
        notification_id: int,
        db: AsyncSession,
    ) -> bool:
        sms_service = await self._get_sms_service()
        
        if sms_service is None:
            logger.warning("SMS service not available")
            return False
        
        if not phone:
            return False
        
        try:
            message = self._build_sms_message(event, data)
            
            await sms_service.send_sms(to=phone, message=message)
            
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            if notification:
                notification.status = "sent"
                notification.content = message
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def _build_sms_message(self, event: NotificationEvent, data: dict) -> str:
        if event == NotificationEvent.ANGRY_CUSTOMER:
            return "VoiceCore Alert: Angry customer call just ended. Check dashboard."
        elif event == NotificationEvent.EMERGENCY:
            return f"VoiceCore Emergency: {data.get('message', 'Immediate attention required')}"
        elif event == NotificationEvent.MISSED_CALL:
            return f"VoiceCore: Missed call from {data.get('caller_phone', 'Unknown')}"
        elif event == NotificationEvent.HOT_LEAD:
            return f"VoiceCore: Hot lead from {data.get('caller_phone', 'Unknown')} - call back now!"
        else:
            return f"VoiceCore: {event.value}"
    
    async def _send_webhook(
        self,
        event: NotificationEvent,
        data: dict,
        prefs: NotificationPreferences,
        notification_id: int,
        db: AsyncSession,
    ) -> bool:
        if not prefs.webhook_url:
            return False
        
        if event.value not in prefs.webhook_events:
            return True
        
        try:
            import aiohttp
            
            payload = {
                "event": event.value,
                "company_id": data.get("company_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    prefs.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    success = response.status < 400
            
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            if notification:
                notification.status = "sent" if success else "failed"
                await db.commit()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False
    
    async def notify_angry_customer(
        self, company_id: int, call_data: dict, db: AsyncSession = None
    ) -> bool:
        return await self.notify(
            company_id=company_id,
            event=NotificationEvent.ANGRY_CUSTOMER,
            data=call_data,
            priority=NotificationPriority.CRITICAL,
            db=db,
        )
    
    async def notify_missed_call(
        self, company_id: int, caller_phone: str, db: AsyncSession = None
    ) -> bool:
        return await self.notify(
            company_id=company_id,
            event=NotificationEvent.MISSED_CALL,
            data={"caller_phone": caller_phone},
            priority=NotificationPriority.URGENT,
            db=db,
        )
    
    async def notify_hot_lead(
        self, company_id: int, lead_data: dict, db: AsyncSession = None
    ) -> bool:
        return await self.notify(
            company_id=company_id,
            event=NotificationEvent.HOT_LEAD,
            data=lead_data,
            priority=NotificationPriority.CRITICAL,
            db=db,
        )
    
    async def notify_emergency(
        self, company_id: int, message: str, db: AsyncSession = None
    ) -> bool:
        return await self.notify(
            company_id=company_id,
            event=NotificationEvent.EMERGENCY,
            data={"message": message},
            priority=NotificationPriority.CRITICAL,
            db=db,
        )
    
    async def send_daily_summary(
        self, company_id: int, stats: dict, db: AsyncSession = None
    ) -> bool:
        return await self.notify(
            company_id=company_id,
            event=NotificationEvent.DAILY_SUMMARY,
            data=stats,
            priority=NotificationPriority.NORMAL,
            db=db,
        )
    
    async def send_weekly_report(
        self, company_id: int, report: dict, db: AsyncSession = None
    ) -> bool:
        return await self.notify(
            company_id=company_id,
            event=NotificationEvent.WEEKLY_REPORT,
            data=report,
            priority=NotificationPriority.NORMAL,
            db=db,
        )
    
    async def check_and_notify_limits(
        self, company_id: int, current_calls: int, max_calls: int, db: AsyncSession = None
    ) -> None:
        if max_calls <= 0:
            return
        
        percentage = (current_calls / max_calls) * 100
        
        if percentage >= 100:
            await self.notify(
                company_id=company_id,
                event=NotificationEvent.CALLS_LIMIT_REACHED,
                data={
                    "current_calls": current_calls,
                    "max_calls": max_calls,
                    "percentage": percentage,
                },
                priority=NotificationPriority.CRITICAL,
                db=db,
            )
        elif percentage >= 90:
            await self.notify(
                company_id=company_id,
                event=NotificationEvent.CALLS_LIMIT_WARNING,
                data={
                    "current_calls": current_calls,
                    "max_calls": max_calls,
                    "percentage": percentage,
                },
                priority=NotificationPriority.URGENT,
                db=db,
            )


notification_service = NotificationService()
