from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from twilio.request_validator import RequestValidator
import logging

from config import settings
from db.database import AsyncSessionLocal
from db.models import Company, Agent, Call, Customer
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)


class TwilioService:
    def __init__(self):
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise ValueError("Twilio credentials not configured")
        
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.validator = RequestValidator(settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number
        self.livekit_url = settings.livekit_url

    def validate_request(self, url: str, params: Dict[str, str], signature: str) -> bool:
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error validating Twilio request: {e}")
            return False

    async def route_call_to_company(self, to_number: str) -> Optional[Dict[str, Any]]:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Company).where(Company.phone_number == to_number)
                )
                company = result.scalar_one_or_none()
                
                if not company:
                    logger.warning(f"No company found for phone number: {to_number}")
                    return None
                
                agent_result = await session.execute(
                    select(Agent).where(
                        and_(Agent.company_id == company.id, Agent.is_active == True)
                    ).limit(1)
                )
                agent = agent_result.scalar_one_or_none()
                
                return {
                    "company": company,
                    "agent": agent
                }
        except Exception as e:
            logger.error(f"Error routing call to company: {e}")
            return None

    async def handle_inbound_call(
        self,
        company_id: int,
        caller_phone: str,
        call_sid: str
    ) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Company).where(Company.id == company_id)
                )
                company = result.scalar_one_or_none()
                
                if not company:
                    raise ValueError(f"Company {company_id} not found")
                
                customer_result = await session.execute(
                    select(Customer).where(
                        and_(
                            Customer.phone == caller_phone,
                            Customer.company_id == company_id
                        )
                    )
                )
                customer = customer_result.scalar_one_or_none()
                
                if not customer:
                    customer = Customer(
                        company_id=company_id,
                        phone=caller_phone,
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
                    caller_phone=caller_phone,
                    duration_seconds=0,
                    transcript="",
                    sentiment="NEUTRAL",
                    outcome="inbound"
                )
                session.add(call)
                await session.commit()
                await session.refresh(call)
                
                twiml = self._generate_inbound_twiml(agent.id if agent else 1)
                
                logger.info(f"Inbound call handled: {call_sid} from {caller_phone}")
                
                return {
                    "call_sid": call_sid,
                    "company_id": company_id,
                    "call_id": call.id,
                    "agent_id": agent.id if agent else None,
                    "customer_name": customer.name,
                    "twiml": twiml
                }
        except Exception as e:
            logger.error(f"Error handling inbound call: {e}")
            raise

    def _generate_inbound_twiml(self, agent_id: int) -> str:
        response = VoiceResponse()
        
        response.say(
            voice="alice",
            language="en-US"
        ).text("Thank you for calling. Please wait while we connect you to our AI assistant.")
        
        connect = response.connect()
        connect.voiceML(
            href=f"wss://{self.livekit_url}/voice/{agent_id}",
            name="voice-assistant"
        )
        
        return str(response)

    async def make_outbound_call(
        self,
        company_id: int,
        customer_phone: str,
        reason: str,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as session:
                company_result = await session.execute(
                    select(Company).where(Company.id == company_id)
                )
                company = company_result.scalar_one_or_none()
                
                if not company:
                    raise ValueError(f"Company {company_id} not found")
                
                if not self._is_within_business_hours(company):
                    logger.warning(f"Call outside business hours for company {company_id}")
                    return {
                        "status": "failed",
                        "reason": "outside_business_hours"
                    }
                
                if agent_id is None:
                    agent_result = await session.execute(
                        select(Agent).where(
                            and_(Agent.company_id == company_id, Agent.is_active == True)
                        ).limit(1)
                    )
                    agent = agent_result.scalar_one_or_none()
                    agent_id = agent.id if agent else 1
                
                twiml_url = f"{settings.next_public_api_url}/api/v1/webhooks/twilio/outbound/{agent_id}"
                
                call = self.client.calls.create(
                    to=customer_phone,
                    from_=company.phone_number or self.phone_number,
                    url=twiml_url,
                    method="POST"
                )
                
                db_call = Call(
                    company_id=company_id,
                    caller_phone=customer_phone,
                    duration_seconds=0,
                    transcript="",
                    sentiment="NEUTRAL",
                    outcome=f"outbound: {reason}"
                )
                session.add(db_call)
                await session.commit()
                
                logger.info(f"Outbound call initiated: {call.sid} to {customer_phone}")
                
                return {
                    "call_sid": call.sid,
                    "status": call.status,
                    "company_id": company_id,
                    "customer_phone": customer_phone,
                    "reason": reason
                }
        except Exception as e:
            logger.error(f"Error making outbound call: {e}")
            raise

    def _is_within_business_hours(self, company: Company) -> bool:
        now = datetime.now(timezone.utc)
        
        weekday = now.weekday()
        if weekday >= 5:
            return False
        
        hour = now.hour
        if hour < 9 or hour >= 18:
            return False
        
        return True

    async def transfer_to_human(
        self,
        call_sid: str,
        agent_phone: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            call = self.client.calls(call_sid).update(
                url=f"{settings.next_public_api_url}/api/v1/webhooks/twilio/transfer",
                method="POST"
            )
            
            if context:
                context_summary = self._generate_context_summary(context)
                self._send_sms_to_agent(agent_phone, context_summary)
            
            logger.info(f"Call {call_sid} transferred to human at {agent_phone}")
            
            return {
                "call_sid": call_sid,
                "status": "transferring",
                "agent_phone": agent_phone
            }
        except Exception as e:
            logger.error(f"Error transferring to human: {e}")
            raise

    def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        summary_parts = []
        
        if context.get("customer_name"):
            summary_parts.append(f"Customer: {context['customer_name']}")
        
        if context.get("caller_phone"):
            summary_parts.append(f"Phone: {context['caller_phone']}")
        
        if context.get("issue"):
            summary_parts.append(f"Issue: {context['issue']}")
        
        if context.get("transcript"):
            transcript = context["transcript"]
            if len(transcript) > 200:
                transcript = transcript[:200] + "..."
            summary_parts.append(f"Summary: {transcript}")
        
        return "VoiceCore Transfer:\n" + "\n".join(summary_parts)

    def _send_sms_to_agent(self, agent_phone: str, message: str) -> None:
        try:
            self.client.messages.create(
                to=agent_phone,
                from_=self.phone_number,
                body=message
            )
            logger.info(f"SMS sent to agent {agent_phone}")
        except Exception as e:
            logger.error(f"Error sending SMS to agent: {e}")

    async def make_call(
        self,
        to: str,
        twiml_url: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            from_num = from_number or self.phone_number
            
            call = self.client.calls.create(
                to=to,
                from_=from_num,
                url=twiml_url,
                method="POST"
            )
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": to,
                "from": from_num
            }
            
        except Exception as e:
            logger.error(f"Error making call: {e}")
            raise

    async def make_call_with_twiml(
        self,
        to: str,
        twiml_response: VoiceResponse,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            from_num = from_number or self.phone_number
            
            call = self.client.calls.create(
                to=to,
                from_=from_num,
                twiml=str(twiml_response),
                method="POST"
            )
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": to,
                "from": from_num
            }
            
        except Exception as e:
            logger.error(f"Error making call with TwiML: {e}")
            raise

    async def end_call(self, call_sid: str) -> Dict[str, Any]:
        try:
            call = self.client.calls(call_sid).update(
                status="completed"
            )
            
            return {
                "call_sid": call.sid,
                "status": call.status
            }
            
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            raise

    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "direction": call.direction,
                "from": call.from_,
                "to": call.to
            }
            
        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            raise

    async def get_recordings(self, call_sid: str) -> List[Dict[str, Any]]:
        try:
            recordings = self.client.calls(call_sid).recordings.list()
            
            return [
                {
                    "sid": r.sid,
                    "duration": r.duration,
                    "url": r.uri
                }
                for r in recordings
            ]
            
        except Exception as e:
            logger.error(f"Error getting recordings: {e}")
            return []

    def generate_twiml_for_transfer(self, agent_phone: str) -> str:
        response = VoiceResponse()
        response.say(
            voice="alice",
            language="en-US"
        ).text("Connecting you to a specialist now. Please hold.")
        response.dial(agent_phone)
        return str(response)

    def generate_twiml_not_in_service(self) -> str:
        response = VoiceResponse()
        response.say(
            voice="alice",
            language="en-US"
        ).text("This number is not in service. Please check the number and try again.")
        return str(response)


def get_twilio_service():
    try:
        return TwilioService()
    except ValueError:
        return None


twilio_service = get_twilio_service()
