"""
SMS Service — VoiceCore

Twilio-based SMS service.
"""

import logging
from typing import Optional
import httpx

from config import settings

logger = logging.getLogger(__name__)


class SMSService:
    
    def __init__(self):
        self.twilio_account_sid = getattr(settings, "twilio_account_sid", None)
        self.twilio_auth_token = getattr(settings, "twilio_auth_token", None)
        self.twilio_from_number = getattr(settings, "twilio_phone_number", None)
    
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> dict:
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
            logger.warning("Twilio credentials not fully configured")
            return {
                "success": False,
                "error": "Twilio not configured",
                "message_sid": None,
            }
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
        
        data = {
            "To": to,
            "From": from_number or self.twilio_from_number,
            "Body": message[:1600],
        }
        
        auth = (self.twilio_account_sid, self.twilio_auth_token)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=auth,
                    timeout=30.0,
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"SMS sent to {to}: {result.get('sid')}")
                    return {
                        "success": True,
                        "message_sid": result.get("sid"),
                        "status": result.get("status"),
                    }
                else:
                    error = response.json()
                    logger.error(f"Twilio SMS error: {error}")
                    return {
                        "success": False,
                        "error": error.get("message", "Unknown error"),
                        "message_sid": None,
                    }
                    
        except Exception as e:
            logger.error(f"SMS send exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_sid": None,
            }
    
    async def send_whatsapp(
        self,
        to: str,
        message: str,
    ) -> dict:
        if not all([self.twilio_account_sid, self.twilio_auth_token]):
            return {
                "success": False,
                "error": "Twilio not configured",
                "message_sid": None,
            }
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
        
        to_formatted = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        from_formatted = self.twilio_from_number if self.twilio_from_number.startswith("whatsapp:") else f"whatsapp:{self.twilio_from_number}"
        
        data = {
            "To": to_formatted,
            "From": from_formatted,
            "Body": message[:1600],
        }
        
        auth = (self.twilio_account_sid, self.twilio_auth_token)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=auth,
                    timeout=30.0,
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return {
                        "success": True,
                        "message_sid": result.get("sid"),
                        "status": result.get("status"),
                    }
                else:
                    error = response.json()
                    return {
                        "success": False,
                        "error": error.get("message", "Unknown error"),
                        "message_sid": None,
                    }
                    
        except Exception as e:
            logger.error(f"WhatsApp send exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_sid": None,
            }
    
    async def send_appointment_reminder(
        self,
        customer_phone: str,
        customer_name: str,
        company_name: str,
        appointment_date: str,
        appointment_time: str,
    ) -> dict:
        message = (
            f"Hi {customer_name}! Reminder: You have an appointment at {company_name} "
            f"tomorrow at {appointment_time}. "
            f"Reply 'C' to confirm or 'R' to reschedule. "
            f"Powered by VoiceCore."
        )
        
        return await self.send_sms(to=customer_phone, message=message)
    
    async def get_message_status(self, message_sid: str) -> dict:
        if not all([self.twilio_account_sid, self.twilio_auth_token]):
            return {"status": "unknown", "error": "Twilio not configured"}
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages/{message_sid}.json"
        auth = (self.twilio_account_sid, self.twilio_auth_token)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, auth=auth, timeout=30.0)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": result.get("status"),
                        "date_sent": result.get("date_sent"),
                        "date_updated": result.get("date_updated"),
                        "error_code": result.get("error_code"),
                        "error_message": result.get("error_message"),
                    }
                else:
                    return {"status": "unknown", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
