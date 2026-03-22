from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio


class ProactiveCallEngine:
    """
    The agent doesn't just wait for calls.
    It reaches out to customers proactively.
    
    Use cases:
    - Appointment reminders (24h + 2h before)
    - Follow-up after previous issue
    - Re-engage dormant customers
    - Payment reminders
    - New service announcements
    
    This feature alone can increase revenue 30%+ for clients.
    """
    
    def __init__(self, db_session, twilio_client, scheduler):
        self.db = db_session
        self.twilio = twilio_client
        self.scheduler = scheduler
    
    async def schedule_proactive_call(
        self,
        company_id: str,
        customer_phone: str,
        reason: str,
        scheduled_time: datetime,
        script_context: Dict[str, Any],
        max_attempts: int = 3,
        retry_delay_minutes: int = 60
    ):
        if not self._is_appropriate_time(scheduled_time, customer_phone):
            scheduled_time = self._next_appropriate_time(customer_phone)
        
        task = {
            "type": "outbound",
            "company_id": company_id,
            "phone": customer_phone,
            "reason": reason,
            "scheduled_time": scheduled_time.isoformat(),
            "script": script_context,
            "max_attempts": max_attempts,
            "retry_delay_minutes": retry_delay_minutes
        }
        
        await self.scheduler.schedule(task)
        return task
    
    def _is_appropriate_time(self, scheduled_time: datetime, phone: str) -> bool:
        hour = scheduled_time.hour
        return 9 <= hour <= 19
    
    def _next_appropriate_time(self, phone: str) -> datetime:
        now = datetime.utcnow()
        next_valid = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        if now.hour >= 19:
            next_valid += timedelta(days=1)
        
        return next_valid
    
    async def auto_reminder_system(self, company_id: str):
        appointments = await self.db.get_upcoming_appointments(
            company_id,
            hours_ahead=24
        )
        
        for appointment in appointments:
            reminder_24h = appointment["datetime"] - timedelta(hours=24)
            reminder_2h = appointment["datetime"] - timedelta(hours=2)
            
            await self.schedule_proactive_call(
                company_id=company_id,
                customer_phone=appointment["patient_phone"],
                reason="appointment_reminder_24h",
                scheduled_time=reminder_24h,
                script_context={
                    "appointment_time": appointment["datetime"].isoformat(),
                    "provider": appointment["provider"],
                    "service_type": appointment["service_type"]
                }
            )
            
            await self.schedule_proactive_call(
                company_id=company_id,
                customer_phone=appointment["patient_phone"],
                reason="appointment_reminder_2h",
                scheduled_time=reminder_2h,
                script_context={
                    "appointment_time": appointment["datetime"].isoformat(),
                    "provider": appointment["provider"],
                    "service_type": appointment["service_type"]
                }
            )
    
    async def reengage_dormant_customers(self, company_id: str, days_inactive: int = 90):
        customers = await self.db.get_dormant_customers(
            company_id,
            days_inactive=days_inactive
        )
        
        for customer in customers:
            await self.schedule_proactive_call(
                company_id=company_id,
                customer_phone=customer["phone"],
                reason="dormant_customer_reengagement",
                scheduled_time=datetime.utcnow(),
                script_context={
                    "last_appointment": customer.get("last_appointment"),
                    "preferred_service": customer.get("preferred_service"),
                    "customer_name": customer.get("name")
                }
            )
    
    async def payment_reminder_system(self, company_id: str):
        due_payments = await self.db.get_due_payments(company_id)
        
        for payment in due_payments:
            await self.schedule_proactive_call(
                company_id=company_id,
                customer_phone=payment["customer_phone"],
                reason="payment_reminder",
                scheduled_time=datetime.utcnow(),
                script_context={
                    "amount_due": payment["amount"],
                    "due_date": payment["due_date"],
                    "invoice_id": payment["invoice_id"]
                }
            )


class OutboundCallScheduler:
    """
    Manages scheduling and execution of outbound calls.
    """
    
    def __init__(self, db_session, voice_agent):
        self.db = db_session
        self.voice_agent = voice_agent
    
    async def schedule(self, task: Dict[str, Any]):
        await self.db.create_scheduled_task(task)
    
    async def execute_due_tasks(self):
        due_tasks = await self.db.get_due_tasks()
        
        for task in due_tasks:
            try:
                await self._execute_task(task)
                await self.db.mark_task_complete(task["id"])
            except Exception as e:
                await self._handle_task_failure(task, str(e))
    
    async def _execute_task(self, task: Dict[str, Any]):
        await self.voice_agent.initiate_outbound(
            phone=task["phone"],
            company_id=task["company_id"],
            context=task["script"],
            reason=task["reason"]
        )
    
    async def _handle_task_failure(self, task: Dict[str, Any], error: str):
        attempts = task.get("attempts", 0)
        
        if attempts < task.get("max_attempts", 3):
            retry_time = datetime.utcnow() + timedelta(
                minutes=task.get("retry_delay_minutes", 60)
            )
            await self.db.reschedule_task(task["id"], retry_time, attempts + 1)
        else:
            await self.db.mark_task_failed(task["id"], error)
