from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from twilio.rest import Client
from twilio.request_validator import RequestValidator
import logging
import json

from config import settings
from db.database import AsyncSessionLocal
from db.models import Company, Agent, Customer, Call
from sqlalchemy import select, and_


logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.validator = RequestValidator(settings.twilio_auth_token)
        self.from_number = f"whatsapp:{settings.twilio_phone_number}"
        self.livekit_url = settings.livekit_url

    def validate_request(self, url: str, params: Dict[str, str], signature: str) -> bool:
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error validating WhatsApp request: {e}")
            return False

    async def handle_whatsapp_voice(
        self,
        company_id: int,
        caller_wa_id: str,
        call_sid: str
    ) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as session:
                company_result = await session.execute(
                    select(Company).where(Company.id == company_id)
                )
                company = company_result.scalar_one_or_none()
                
                if not company:
                    raise ValueError(f"Company {company_id} not found")
                
                phone = caller_wa_id.replace("whatsapp:", "")
                
                customer_result = await session.execute(
                    select(Customer).where(
                        and_(
                            Customer.phone == phone,
                            Customer.company_id == company_id
                        )
                    )
                )
                customer = customer_result.scalar_one_or_none()
                
                if not customer:
                    customer = Customer(
                        company_id=company_id,
                        phone=phone,
                        name="",
                        total_calls=0
                    )
                    session.add(customer)
                    await session.commit()
                
                agent_result = await session.execute(
                    select(Agent).where(
                        and_(Agent.company_id == company_id, Agent.is_active == True)
                    ).limit(1)
                )
                agent = agent_result.scalar_one_or_none()
                
                call = Call(
                    company_id=company_id,
                    caller_phone=phone,
                    duration_seconds=0,
                    transcript="",
                    sentiment="NEUTRAL",
                    outcome="whatsapp_voice"
                )
                session.add(call)
                await session.commit()
                await session.refresh(call)
                
                logger.info(f"WhatsApp voice call handled: {call_sid} from {phone}")
                
                return {
                    "call_sid": call_sid,
                    "company_id": company_id,
                    "call_id": call.id,
                    "agent_id": agent.id if agent else None,
                    "customer_phone": phone
                }
        except Exception as e:
            logger.error(f"Error handling WhatsApp voice: {e}")
            raise

    async def handle_whatsapp_text(
        self,
        company_id: int,
        from_number: str,
        message_body: str,
        message_sid: str
    ) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as session:
                phone = from_number.replace("whatsapp:", "")
                
                customer_result = await session.execute(
                    select(Customer).where(
                        and_(
                            Customer.phone == phone,
                            Customer.company_id == company_id
                        )
                    )
                )
                customer = customer_result.scalar_one_or_none()
                
                if not customer:
                    customer = Customer(
                        company_id=company_id,
                        phone=phone,
                        name="",
                        total_calls=0
                    )
                    session.add(customer)
                    await session.commit()
                    await session.refresh(customer)
                
                response_text = await self._generate_text_response(
                    message_body,
                    customer_name=customer.name or "Valued Customer",
                    company_id=company_id
                )
                
                await self.send_message(
                    to=phone,
                    body=response_text
                )
                
                logger.info(f"WhatsApp text handled: {message_sid} from {phone}")
                
                return {
                    "message_sid": message_sid,
                    "company_id": company_id,
                    "customer_id": customer.id,
                    "incoming_message": message_body,
                    "response": response_text
                }
        except Exception as e:
            logger.error(f"Error handling WhatsApp text: {e}")
            raise

    async def _generate_text_response(
        self,
        message: str,
        customer_name: str,
        company_id: int
    ) -> str:
        message_lower = message.lower()
        
        greetings = ["hello", "hi", "hey", "السلام", "مرحبا", "bonjour"]
        help_keywords = ["help", "help me", "مساعدة", "support", "info"]
        booking_keywords = ["book", "appointment", "reserve", "حجز", "موعد"]
        cancel_keywords = ["cancel", "cancelar", "إلغاء", "cancel"]
        status_keywords = ["status", "check", "حالة", "موعدي"]
        
        if any(greet in message_lower for greet in greetings):
            return f"Hello {customer_name}! Thank you for contacting us. How can I help you today?"
        
        elif any(keyword in message_lower for keyword in help_keywords):
            return "I can help you with:\n- Booking appointments\n- Checking appointment status\n- General inquiries\n\nJust let me know what you need!"
        
        elif any(keyword in message_lower for keyword in booking_keywords):
            return "I'd be happy to help you book an appointment! Please provide:\n1. The service you need\n2. Preferred date (YYYY-MM-DD)\n3. Preferred time"
        
        elif any(keyword in message_lower for keyword in cancel_keywords):
            return "I'm sorry to hear you need to cancel. To cancel your appointment, please provide your booking reference number."
        
        elif any(keyword in message_lower for keyword in status_keywords):
            return "To check your appointment status, please provide your phone number or booking reference."
        
        else:
            return f"Thank you for your message, {customer_name}! I'm here to help. Would you like to:\n- Book an appointment\n- Check your existing appointments\n- Get more information about our services?"

    async def send_confirmation(
        self,
        phone: str,
        appointment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            date = appointment_details.get("date", "TBD")
            time = appointment_details.get("time", "TBD")
            service = appointment_details.get("service", "appointment")
            
            message = f"""✅ Your {service} is confirmed!

📅 Date: {date}
🕐 Time: {time}

Reply CANCEL to cancel your appointment.

We look forward to seeing you!"""
            
            result = await self.send_message(to=phone, body=message)
            
            logger.info(f"Confirmation sent to {phone} for {date} at {time}")
            
            return {
                "status": "sent",
                "phone": phone,
                "appointment": appointment_details
            }
        except Exception as e:
            logger.error(f"Error sending confirmation: {e}")
            raise

    async def send_reminder(
        self,
        phone: str,
        appointment_details: Dict[str, Any],
        reminder_type: str = "24h"
    ) -> Dict[str, Any]:
        try:
            date = appointment_details.get("date", "TBD")
            time = appointment_details.get("time", "TBD")
            service = appointment_details.get("service", "appointment")
            
            if reminder_type == "24h":
                message = f"""⏰ Reminder: You have a {service} tomorrow!

📅 Date: {date}
🕐 Time: {time}

Reply CONFIRM to confirm or CANCEL to cancel.

See you soon!"""
            elif reminder_type == "2h":
                message = f"""⏰ Your {service} is in 2 hours!

📅 Date: {date}
🕐 Time: {time}

We look forward to seeing you!"""
            else:
                message = f"""⏰ Reminder: You have a {service} soon!

📅 Date: {date}
🕐 Time: {time}"""
            
            result = await self.send_message(to=phone, body=message)
            
            logger.info(f"{reminder_type} reminder sent to {phone}")
            
            return {
                "status": "sent",
                "phone": phone,
                "reminder_type": reminder_type,
                "appointment": appointment_details
            }
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            raise

    async def send_message(
        self,
        to: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            to = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
            
            message_params = {
                "from_": self.from_number,
                "to": to,
                "body": body
            }
            
            if media_url:
                message_params["media_url"] = [media_url]
            
            message = self.client.messages.create(**message_params)
            
            return {
                "message_sid": message.sid,
                "status": message.status,
                "to": to,
                "body": body
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            raise

    async def send_template(
        self,
        to: str,
        template_name: str,
        variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            to = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
            
            content_variables = None
            if variables:
                content_variables = {}
                for i, (key, value) in enumerate(variables.items(), 1):
                    content_variables[str(i)] = value
            
            message = self.client.messages.create(
                from_=self.from_number,
                to=to,
                content_sid="HX_TEMPLATE_SID",
                content_variables=content_variables
            )
            
            return {
                "message_sid": message.sid,
                "status": message.status
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp template: {e}")
            raise

    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "message_sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            raise

    async def handle_incoming_message(
        self,
        from_number: str,
        body: str,
        message_sid: str
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Received WhatsApp message from {from_number}: {body}")
            
            return {
                "from": from_number,
                "body": body,
                "message_sid": message_sid,
                "handled": True
            }
            
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
            raise


whatsapp_service = WhatsAppService()
