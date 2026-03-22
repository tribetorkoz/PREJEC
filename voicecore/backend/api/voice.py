from datetime import datetime
from typing import Optional, List
import logging

from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from fastapi.responses import Response
import jwt

from agents.voice_agent import VoiceAgent, create_voice_agent
from sqlalchemy import select

from db.database import AsyncSessionLocal
from db.models import Agent, Company, Call, Customer
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


class ConnectionManager:
    """Manages WebSocket connections for voice calls."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.agent_instances: dict[str, VoiceAgent] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.agent_instances:
            del self.agent_instances[client_id]
        logger.info(f"Client {client_id} disconnected")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)


manager = ConnectionManager()


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and return payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload dictionary
        
    Raises:
        HTTPException if token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.effective_jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_twilio_signature(
    request: Request,
    twilio_signature: str,
    account_sid: str
) -> bool:
    """
    Verify Twilio webhook signature.
    
    Args:
        request: FastAPI request
        twilio_signature: Signature from Twilio
        account_sid: Twilio account SID
        
    Returns:
        True if signature is valid
    """
    try:
        from twilio.request_validator import RequestValidator
        
        validator = RequestValidator(settings.twilio_auth_token)
        
        url = str(request.url)
        params = dict(request.query_params)
        
        if request.method == "POST":
            params.update(await request.form())
        
        is_valid = validator.validate(
            url,
            params,
            twilio_signature
        )
        
        return is_valid
    except Exception as e:
        logger.error(f"Twilio signature verification error: {e}")
        return False


async def voice_websocket(
    websocket: WebSocket,
    call_sid: str,
    token: str
) -> None:
    """
    WebSocket endpoint for LiveKit voice streaming.
    
    Flow:
    1. Verify JWT token
    2. Get call info from DB
    3. Create VoiceAgent instance
    4. Call agent.on_call_start() - Send greeting
    5. Loop: receive audio -> process -> send response
    6. On disconnect: call agent.on_call_end()
    
    Args:
        websocket: FastAPI WebSocket
        call_sid: Call identifier
        token: JWT authentication token
    """
    try:
        payload = verify_jwt_token(token)
    except HTTPException as e:
        await websocket.close(code=4001, reason=str(e.detail))
        return
    
    client_id = f"call_{call_sid}"
    voice_agent: Optional[VoiceAgent] = None
    call_record: Optional[Call] = None
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Call).where(Call.call_sid == call_sid)
            )
            call_record = result.scalar_one_or_none()
            
            if not call_record:
                agent_id = payload.get("agent_id")
                company_id = payload.get("company_id")
            else:
                agent_id = call_record.agent_id
                company_id = call_record.company_id
            
            agent_result = await session.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            agent_db = agent_result.scalar_one_or_none()
            
            if not agent_db:
                await websocket.send_json({
                    "type": "error",
                    "message": "Agent not found"
                })
                await websocket.close()
                return
            
            voice_agent = await create_voice_agent(
                agent_id=agent_db.id,
                company_id=agent_db.company_id,
                language=agent_db.language,
                voice_id=agent_db.voice_id,
                system_prompt=agent_db.system_prompt,
            )
            
            caller_phone = payload.get("caller_phone", "unknown")
            
            greeting = await voice_agent.on_call_start(
                call_sid=call_sid,
                caller_phone=caller_phone,
                company_id=agent_db.company_id,
                agent_id=agent_db.id
            )
            
            manager.agent_instances[client_id] = voice_agent
        
        await manager.connect(client_id, websocket)
        
        await websocket.send_json({
            "type": "ready",
            "call_sid": call_sid,
            "greeting": greeting
        })
        
        while True:
            data = await websocket.receive_bytes()
            
            audio_response = await voice_agent.on_audio_received(data)
            
            if audio_response:
                await websocket.send_bytes(audio_response)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in voice websocket: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        if voice_agent:
            try:
                outcome = "completed" if not voice_agent.current_call or not voice_agent.current_call.needs_transfer else "transferred"
                summary = await voice_agent.on_call_end(outcome)
                
                async with AsyncSessionLocal() as session:
                    if call_record:
                        call_record.duration_seconds = summary.duration_seconds
                        call_record.sentiment = summary.sentiment
                        call_record.sentiment_score = summary.sentiment_score
                        call_record.outcome = summary.outcome
                        call_record.transcript = summary.transcript
                        from datetime import datetime
                        call_record.ended_at = datetime.utcnow()
                        await session.commit()
            except Exception as e:
                logger.error(f"Error saving call summary: {e}")
        
        manager.disconnect(client_id)


async def handle_inbound_call(request: Request, db) -> Response:
    """
    Twilio webhook handler for inbound calls.
    
    Flow:
    1. Verify Twilio signature
    2. Find company by To number
    3. Find active agent
    4. Create Call record in DB
    5. Return TwiML to connect to LiveKit
    
    Args:
        request: FastAPI request
        db: Database session
        
    Returns:
        TwiML response XML
    """
    twilio_signature = request.headers.get("X-Twilio-Signature", "")
    
    if settings.twilio_auth_token:
        is_valid = await verify_twilio_signature(
            request,
            twilio_signature,
            settings.twilio_account_sid
        )
        if not is_valid:
            logger.warning("Invalid Twilio signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
    
    form_data = await request.form()
    
    from_number = form_data.get("From", "")
    to_number = form_data.get("To", "")
    call_sid = form_data.get("CallSid", "")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Company).where(Company.phone_number == to_number)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            result = await session.execute(
                select(Company).where(Company.whatsapp_number == to_number)
            )
            company = result.scalar_one_or_none()
        
        if not company:
            logger.warning(f"Company not found for number: {to_number}")
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Thank you for calling. We're unable to locate your account. Please try again later.</Say>
    <Hangup/>
</Response>"""
            return Response(content=twiml, media_type="application/xml")
        
        result = await session.execute(
            select(Agent).where(
                Agent.company_id == company.id,
                Agent.is_active == True
            ).limit(1)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            logger.warning(f"No active agent for company: {company.id}")
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Thank you for calling. All agents are currently unavailable. Please call back later.</Say>
    <Hangup/>
</Response>"""
            return Response(content=twiml, media_type="application/xml")
        
        existing_call = await session.execute(
            select(Call).where(Call.call_sid == call_sid)
        )
        existing = existing_call.scalar_one_or_none()
        
        if not existing:
            new_call = Call(
                company_id=company.id,
                agent_id=agent.id,
                caller_phone=from_number,
                call_sid=call_sid,
                direction="inbound",
                created_at=datetime.utcnow()
            )
            session.add(new_call)
            await session.commit()
        
        jwt_payload = {
            "call_sid": call_sid,
            "agent_id": agent.id,
            "company_id": company.id,
            "caller_phone": from_number,
            "exp": datetime.utcnow().timestamp() + 3600
        }
        jwt_token = jwt.encode(
            jwt_payload,
            settings.effective_jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        
        server_url = settings.next_public_api_url or "https://your-server.com"
        stream_url = f"{server_url}/api/v1/voice/ws/{call_sid}?token={jwt_token}"
        
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{stream_url}"/>
    </Connect>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")


async def initiate_outbound_call(
    call_data: dict,
    current_user,
    db
) -> dict:
    """
    Initiate an outbound call.
    
    Args:
        call_data: Call parameters (to_number, agent_id, etc.)
        current_user: Authenticated user making the request
        db: Database session
        
    Returns:
        Call initiation result
    """
    to_number = call_data.get("to_number")
    agent_id = call_data.get("agent_id")
    
    if not to_number or not agent_id:
        raise HTTPException(status_code=400, detail="to_number and agent_id are required")
    
    async with AsyncSessionLocal() as session:
        agent_result = await session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to your company")
        
        company_result = await session.execute(
            select(Company).where(Company.id == agent.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        from config import get_plan_config
        plan_config = get_plan_config(company.plan)
        calls_limit = plan_config.get("calls_limit", 0)
        
        from sqlalchemy import func
        count_result = await session.execute(
            select(func.count(Call.id)).where(
                Call.company_id == company.id
            )
        )
        monthly_calls = count_result.scalar() or 0
        
        if calls_limit > 0 and monthly_calls >= calls_limit:
            raise HTTPException(
                status_code=402,
                detail=f"Monthly call limit reached ({monthly_calls}/{calls_limit})"
            )
        
        try:
            from twilio.rest import Client as TwilioClient
            
            twilio = TwilioClient(
                settings.twilio_account_sid,
                settings.twilio_auth_token
            )
            
            server_url = settings.next_public_api_url or "https://your-server.com"
            
            callback_url = f"{server_url}/api/v1/voice/callback"
            
            call = twilio.calls.create(
                to=to_number,
                from_=company.phone_number,
                url=callback_url,
                status_callback=callback_url,
                status_callback_event=["completed", "failed", "no_answer"]
            )
            
            new_call = Call(
                company_id=company.id,
                agent_id=agent_id,
                caller_phone=to_number,
                call_sid=call.sid,
                direction="outbound",
                created_at=datetime.utcnow()
            )
            session.add(new_call)
            await session.commit()
            
            logger.info("Outbound call initiated", extra={
                "call_sid": call.sid,
                "to_number_hash": hash(to_number) % 10000,
                "company_id": company.id
            })
            
            return {
                "status": "initiated",
                "call_sid": call.sid,
                "to": to_number
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate outbound call: {e}")
            raise HTTPException(status_code=500, detail=str(e))


async def handle_call_callback(request: Request) -> Response:
    """
    Handle Twilio status callback.
    
    Args:
        request: FastAPI request
        
    Returns:
        Empty response
    """
    form_data = await request.form()
    
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    duration = form_data.get("CallDuration", 0)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Call).where(Call.call_sid == call_sid)
        )
        call_record = result.scalar_one_or_none()
        
        if call_record:
            if call_status == "completed":
                call_record.outcome = "completed"
                call_record.duration_seconds = int(duration) if duration else 0
            elif call_status == "failed":
                call_record.outcome = "failed"
            elif call_status == "no_answer":
                call_record.outcome = "no_answer"
            
            call_record.ended_at = datetime.utcnow()
            await session.commit()
    
    return Response(content="", media_type="application/xml")
