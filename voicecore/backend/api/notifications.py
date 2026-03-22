"""
Notifications API — VoiceCore

API endpoints for managing notifications.
"""

import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import User, Notification, NotificationPreferences, Company
from api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    event_type: str
    channel: str
    subject: Optional[str]
    content: Optional[str]
    status: str
    created_at: datetime
    read: bool = False
    call_id: Optional[int] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class NotificationPreferencesUpdate(BaseModel):
    email_angry_customer: Optional[bool] = None
    sms_angry_customer: Optional[bool] = None
    email_missed_call: Optional[bool] = None
    email_daily_summary: Optional[bool] = None
    email_weekly_report: Optional[bool] = None
    webhook_url: Optional[str] = None
    webhook_events: Optional[List[str]] = None
    notification_email: Optional[str] = None
    notification_phone: Optional[str] = None
    timezone: Optional[str] = None
    daily_summary_time: Optional[str] = None


class NotificationPreferencesResponse(BaseModel):
    id: int
    email_angry_customer: bool
    sms_angry_customer: bool
    email_missed_call: bool
    email_daily_summary: bool
    email_weekly_report: bool
    webhook_url: Optional[str]
    webhook_events: List[str]
    notification_email: Optional[str]
    notification_phone: Optional[str]
    timezone: str
    daily_summary_time: str

    class Config:
        from_attributes = True


@router.get("", response_model=dict)
async def get_notifications(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(
        Notification.company_id == current_user.company_id
    )
    
    if event_type:
        query = query.where(Notification.event_type == event_type)
    
    count_query = select(func.count(Notification.id)).where(
        Notification.company_id == current_user.company_id
    )
    if event_type:
        count_query = count_query.where(Notification.event_type == event_type)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    unread_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.company_id == current_user.company_id,
            Notification.status == "pending",
        )
    )
    unread_count = unread_result.scalar() or 0
    
    query = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return {
        "notifications": [
            NotificationResponse(
                id=n.id,
                event_type=n.event_type,
                channel=n.channel,
                subject=n.subject,
                content=n.content,
                status=n.status,
                created_at=n.created_at,
                read=n.status != "pending",
                call_id=n.call_id,
                metadata=n.metadata,
            ).model_dump()
            for n in notifications
        ],
        "total": total,
        "unread_count": unread_count,
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.company_id == current_user.company_id,
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.company_id == current_user.company_id,
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "delivered"
    await db.commit()
    
    return {"success": True}


@router.post("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.company_id == current_user.company_id,
            Notification.status == "pending",
        )
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.status = "delivered"
    
    await db.commit()
    
    return {"success": True, "marked_count": len(notifications)}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.company_id == current_user.company_id,
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await db.delete(notification)
    await db.commit()
    
    return {"success": True}


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationPreferences).where(
            NotificationPreferences.company_id == current_user.company_id
        )
    )
    prefs = result.scalar_one_or_none()
    
    if not prefs:
        prefs = NotificationPreferences(
            company_id=current_user.company_id,
            email_angry_customer=True,
            sms_angry_customer=False,
            email_missed_call=True,
            email_daily_summary=True,
            email_weekly_report=True,
            timezone="America/New_York",
            daily_summary_time="08:00",
        )
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)
    
    return prefs


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    data: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationPreferences).where(
            NotificationPreferences.company_id == current_user.company_id
        )
    )
    prefs = result.scalar_one_or_none()
    
    if not prefs:
        prefs = NotificationPreferences(company_id=current_user.company_id)
        db.add(prefs)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(prefs, field):
            setattr(prefs, field, value)
    
    await db.commit()
    await db.refresh(prefs)
    
    return prefs


@router.post("/preferences/test-email")
async def send_test_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.email_service import EmailService
    
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    email_service = EmailService()
    
    try:
        success = await email_service.send_generic_notification(
            to_email=company.email,
            subject="Test Notification from VoiceCore",
            message="This is a test notification from VoiceCore. Your email settings are configured correctly!",
        )
        
        if success:
            return {"success": True, "message": "Test email sent successfully"}
        else:
            return {"success": False, "message": "Failed to send test email"}
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        return {"success": False, "message": str(e)}


@router.post("/preferences/test-sms")
async def send_test_sms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.sms_service import SMSService
    
    result = await db.execute(
        select(NotificationPreferences).where(
            NotificationPreferences.company_id == current_user.company_id
        )
    )
    prefs = result.scalar_one_or_none()
    
    if not prefs or not prefs.notification_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number not configured. Please add a phone number first.",
        )
    
    sms_service = SMSService()
    
    try:
        result = await sms_service.send_sms(
            to=prefs.notification_phone,
            message="This is a test notification from VoiceCore. Your SMS settings are configured correctly!",
        )
        
        if result.get("success"):
            return {"success": True, "message": "Test SMS sent successfully"}
        else:
            return {"success": False, "message": result.get("error", "Failed to send SMS")}
    except Exception as e:
        logger.error(f"Failed to send test SMS: {e}")
        return {"success": False, "message": str(e)}
