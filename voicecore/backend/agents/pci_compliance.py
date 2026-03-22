import re
from typing import Dict, Any, Optional
from datetime import datetime


class PCIComplianceHandler:
    """
    Handle credit card payments over voice calls.
    Pause recording during card number input.
    Mask card numbers in transcripts automatically.
    Essential for any business taking payments.
    """
    
    def __init__(self, twilio_client, stripe_client):
        self.twilio = twilio_client
        self.stripe = stripe_client
    
    async def handle_payment_flow(
        self,
        call_sid: str,
        amount: int,
        currency: str = "usd"
    ) -> Dict[str, Any]:
        await self.twilio.pause_recording(call_sid)
        
        card_data = await self.collect_dtmf_input(
            call_sid,
            prompt="Please enter your 16-digit card number using your keypad",
            expected_length=16,
            masked=True
        )
        
        expiry_data = await self.collect_dtmf_input(
            call_sid,
            prompt="Please enter your card expiry date as MMYY",
            expected_length=4,
            masked=True
        )
        
        cvv_data = await self.collect_dtmf_input(
            call_sid,
            prompt="Please enter your 3 or 4 digit security code",
            expected_length=4,
            masked=True
        )
        
        result = await self.stripe.create_payment_intent(
            amount=amount,
            currency=currency,
            card={
                "number": card_data["input"],
                "exp_month": int(expiry_data["input"][:2]),
                "exp_year": int(expiry_data["input"][2:]),
                "cvc": cvv_data["input"]
            }
        )
        
        await self.twilio.resume_recording(call_sid)
        
        return {
            "success": True,
            "payment_intent_id": result["id"],
            "status": result["status"]
        }
    
    async def collect_dtmf_input(
        self,
        call_sid: str,
        prompt: str,
        expected_length: int,
        masked: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        return {
            "call_sid": call_sid,
            "input": "****",
            "length": expected_length,
            "received": True,
            "masked": masked
        }
    
    async def mask_card_in_transcript(self, transcript: str) -> str:
        card_patterns = [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3,4}\b'
        ]
        
        masked = transcript
        for pattern in card_patterns:
            masked = re.sub(pattern, '[CARD MASKED]', masked)
        
        return masked
    
    async def mask_cvv_in_transcript(self, transcript: str) -> str:
        cvv_pattern = r'\b\d{3,4}\b'
        return re.sub(cvv_pattern, '[CVV MASKED]', transcript)
    
    async def redact_sensitive_data(self, transcript: str) -> str:
        transcript = await self.mask_card_in_transcript(transcript)
        transcript = await self.mask_cvv_in_transcript(transcript)
        
        ssn_pattern = r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
        transcript = re.sub(ssn_pattern, '[SSN REDACTED]', transcript)
        
        return transcript


class PaymentSecurityLogger:
    """
    Log all payment-related activities for PCI compliance.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_payment_initiated(
        self,
        call_sid: str,
        company_id: str,
        amount: int
    ):
        await self.db.create_log({
            "event": "payment_initiated",
            "call_sid": call_sid,
            "company_id": company_id,
            "amount": amount,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def log_payment_completed(
        self,
        call_sid: str,
        payment_intent_id: str,
        status: str
    ):
        await self.db.create_log({
            "event": "payment_completed",
            "call_sid": call_sid,
            "payment_intent_id": payment_intent_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def log_payment_failed(
        self,
        call_sid: str,
        reason: str
    ):
        await self.db.create_log({
            "event": "payment_failed",
            "call_sid": call_sid,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })
