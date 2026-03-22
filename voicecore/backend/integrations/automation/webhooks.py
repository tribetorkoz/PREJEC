from typing import Dict, Any, List
import hmac
import hashlib
import json
from datetime import datetime


class AutomationWebhooks:
    """
    Connect VoiceCore to 5000+ apps via Zapier/Make.
    Every event triggers automations.
    No code needed for integrations.
    """
    
    EVENTS = {
        "call.completed": "Fired when any call ends",
        "call.missed": "Fired when a call comes in and no one answers",
        "appointment.booked": "Fired when agent books appointment",
        "lead.qualified": "Fired when agent qualifies a sales lead",
        "human.requested": "Fired when customer asks for human",
        "emergency.detected": "Fired when emergency keywords detected",
        "sentiment.negative": "Fired when customer is angry/frustrated",
        "competitor.mentioned": "Fired when customer mentions competitor",
    }
    
    def __init__(self, db_session, http_client):
        self.db = db_session
        self.http = http_client
        self.webhook_secret = "voicecore_webhook_secret"
    
    async def trigger_webhook(
        self,
        company_id: str,
        event: str,
        data: Dict[str, Any]
    ):
        company = await self.db.get_company(company_id)
        
        webhooks = company.get("webhooks", {}).get(event, [])
        
        payload = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "company_id": company_id,
            "data": data
        }
        
        signature = self._generate_signature(payload)
        
        for webhook_url in webhooks:
            try:
                await self.http.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-VoiceCore-Signature": signature
                    }
                )
            except Exception as e:
                await self._log_webhook_failure(company_id, event, webhook_url, str(e))
    
    def _generate_signature(self, payload: Dict) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.webhook_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _log_webhook_failure(
        self,
        company_id: str,
        event: str,
        webhook_url: str,
        error: str
    ):
        await self.db.create_webhook_log({
            "company_id": company_id,
            "event": event,
            "webhook_url": webhook_url,
            "status": "failed",
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def register_webhook(
        self,
        company_id: str,
        event: str,
        webhook_url: str
    ):
        await self.db.add_webhook(company_id, event, webhook_url)
    
    async def unregister_webhook(
        self,
        company_id: str,
        event: str,
        webhook_url: str
    ):
        await self.db.remove_webhook(company_id, event, webhook_url)
    
    def get_available_events(self) -> Dict[str, str]:
        return self.EVENTS


class WebhookEventBuilder:
    """
    Helper to build webhook payloads for different event types.
    """
    
    @staticmethod
    def call_completed(call_data: Dict) -> Dict:
        return {
            "call_id": call_data.get("id"),
            "phone_number": call_data.get("phone_number"),
            "duration_seconds": call_data.get("duration"),
            "outcome": call_data.get("outcome"),
            "transcript": call_data.get("transcript"),
            "recording_url": call_data.get("recording_url")
        }
    
    @staticmethod
    def appointment_booked(appointment_data: Dict) -> Dict:
        return {
            "appointment_id": appointment_data.get("id"),
            "customer_name": appointment_data.get("customer_name"),
            "customer_phone": appointment_data.get("phone"),
            "appointment_time": appointment_data.get("datetime"),
            "service_type": appointment_data.get("service_type")
        }
    
    @staticmethod
    def lead_qualified(lead_data: Dict) -> Dict:
        return {
            "lead_id": lead_data.get("id"),
            "customer_name": lead_data.get("name"),
            "phone": lead_data.get("phone"),
            "qualification_score": lead_data.get("score"),
            "interest_level": lead_data.get("interest"),
            "next_action": lead_data.get("next_action")
        }
    
    @staticmethod
    def sentiment_negative(call_data: Dict) -> Dict:
        return {
            "call_id": call_data.get("id"),
            "sentiment": call_data.get("sentiment"),
            "escalation_reason": call_data.get("escalation_reason"),
            "recommended_action": "Follow up with customer"
        }
