from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from db.database import get_db
from db.models import Call, Customer, Agent, Company
from db.schemas import CallCreate, CallResponse
from services.twilio_service import twilio_service
from config import settings
from api.auth import get_current_user


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["calls"])


class InboundCallRequest(BaseModel):
    company_id: int
    caller_phone: str
    agent_id: Optional[int] = None


class OutboundCallRequest(BaseModel):
    company_id: int
    to_phone: str
    agent_id: int
    message: Optional[str] = None


class CallHistoryResponse(BaseModel):
    calls: List[CallResponse]
    total: int
    page: int
    page_size: int


class CallAnalyticsResponse(BaseModel):
    total_calls: int
    total_duration: int
    avg_duration: float
    calls_today: int
    calls_this_week: int
    calls_this_month: int
    sentiment_breakdown: dict
    outcome_breakdown: dict


# IMPORTANT: Static routes MUST come before parametric routes to avoid conflicts

@router.get("/analytics", response_model=CallAnalyticsResponse)
async def get_call_analytics(
    company_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        total_calls_result = await db.execute(
            select(func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
        )
        total_calls = total_calls_result.scalar() or 0
        
        total_duration_result = await db.execute(
            select(func.sum(Call.duration_seconds))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
        )
        total_duration = total_duration_result.scalar() or 0
        
        avg_duration_result = await db.execute(
            select(func.avg(Call.duration_seconds))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
        )
        avg_duration = float(avg_duration_result.scalar() or 0)
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=datetime.now().weekday())
        month_start = today_start.replace(day=1)
        
        calls_today_result = await db.execute(
            select(func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= today_start)
        )
        calls_today = calls_today_result.scalar() or 0
        
        calls_this_week_result = await db.execute(
            select(func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= week_start)
        )
        calls_this_week = calls_this_week_result.scalar() or 0
        
        calls_this_month_result = await db.execute(
            select(func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= month_start)
        )
        calls_this_month = calls_this_month_result.scalar() or 0
        
        sentiment_result = await db.execute(
            select(Call.sentiment, func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
            .where(Call.sentiment.isnot(None))
            .group_by(Call.sentiment)
        )
        sentiment_breakdown = {row[0]: row[1] for row in sentiment_result.all() if row[0]}
        
        outcome_result = await db.execute(
            select(Call.outcome, func.count(Call.id))
            .where(Call.company_id == company_id)
            .where(Call.created_at >= start_date)
            .where(Call.outcome.isnot(None))
            .group_by(Call.outcome)
        )
        outcome_breakdown = {row[0]: row[1] for row in outcome_result.all() if row[0]}
        
        return CallAnalyticsResponse(
            total_calls=total_calls,
            total_duration=total_duration,
            avg_duration=avg_duration,
            calls_today=calls_today,
            calls_this_week=calls_this_week,
            calls_this_month=calls_this_month,
            sentiment_breakdown=sentiment_breakdown,
            outcome_breakdown=outcome_breakdown,
        )
        
    except Exception as e:
        logger.error(f"Error getting call analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=CallHistoryResponse)
async def get_call_history(
    company_id: int,
    page: int = 1,
    page_size: int = 20,
    caller_phone: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = select(Call).where(Call.company_id == company_id)
        
        if caller_phone:
            query = query.where(Call.caller_phone.ilike(f"%{caller_phone}%"))
        
        if sentiment:
            query = query.where(Call.sentiment == sentiment)
        
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        
        query = query.order_by(desc(Call.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        calls_list = result.scalars().all()
        calls_response = [CallResponse.model_validate(call) for call in calls_list]
        
        return CallHistoryResponse(
            calls=calls_response,
            total=total,
            page=page,
            page_size=page_size,
        )
        
    except Exception as e:
        logger.error(f"Error getting call history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inbound")
async def handle_inbound_call(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid", "")
        caller_phone = form_data.get("From", "")
        called_phone = form_data.get("To", "")
        call_status = form_data.get("CallStatus", "")
        
        logger.info(f"Inbound call: {call_sid} from {caller_phone}")
        
        company_result = await db.execute(
            select(Company).where(Company.phone_number == called_phone)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            logger.warning(f"No company found for phone: {called_phone}")
            return JSONResponse(
                content={"error": "Company not found"},
                status_code=404
            )
        
        customer_result = await db.execute(
            select(Customer).where(
                Customer.phone == caller_phone,
                Customer.company_id == company.id
            )
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            customer = Customer(
                company_id=company.id,
                phone=caller_phone,
                name="",
                total_calls=0,
            )
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
        
        agent_result = await db.execute(
            select(Agent).where(
                Agent.company_id == company.id,
                Agent.is_active == True
            ).limit(1)
        )
        agent = agent_result.scalar_one_or_none()
        
        call = Call(
            company_id=company.id,
            call_sid=call_sid,
            agent_id=agent.id if agent else None,
            caller_phone=caller_phone,
            direction="inbound",
            duration_seconds=0,
            transcript="",
            sentiment="NEUTRAL",
            outcome="inbound",
        )
        db.add(call)
        await db.commit()
        await db.refresh(call)
        
        livekit_ws_url = settings.livekit_url or "ws://localhost:7880"
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you for calling. Please wait while we connect you to our AI assistant.</Say>
    <Connect>
        <Stream url="wss://{livekit_ws_url}/voice/{agent.id if agent else 1}"/>
    </Connect>
</Response>"""
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling inbound call: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@router.post("/outbound")
async def initiate_outbound_call(
    call_request: OutboundCallRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        company_result = await db.execute(
            select(Company).where(Company.id == call_request.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        agent_result = await db.execute(
            select(Agent).where(Agent.id == call_request.agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        twiml_url = f"{settings.next_public_api_url}/api/webhooks/twilio/voice"
        
        result = await twilio_service.make_call(
            to=call_request.to_phone,
            twiml_url=twiml_url,
        )
        
        call = Call(
            company_id=call_request.company_id,
            call_sid=result.get("call_sid"),
            agent_id=call_request.agent_id,
            caller_phone=call_request.to_phone,
            direction="outbound",
            duration_seconds=0,
            transcript="",
            sentiment="NEUTRAL",
            outcome="outbound initiated",
        )
        db.add(call)
        await db.commit()
        await db.refresh(call)
        
        return {
            "call_sid": result.get("call_sid"),
            "status": result.get("status"),
            "call_id": call.id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating outbound call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=CallResponse)
async def create_call(
    call: CallCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_call = Call(**call.model_dump())
        db.add(db_call)
        await db.commit()
        await db.refresh(db_call)
        return db_call
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CallResponse])
async def list_calls(
    company_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Call)
            .where(Call.company_id == company_id)
            .order_by(Call.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        calls = result.scalars().all()
        return calls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Parametric routes AFTER static routes
@router.get("/{call_id}", response_model=CallResponse)
async def get_call_details(
    call_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Call).where(Call.id == call_id))
        call = result.scalar_one_or_none()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return call
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting call details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{call_id}")
async def delete_call(
    call_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Call).where(Call.id == call_id))
        call = result.scalar_one_or_none()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        await db.delete(call)
        await db.commit()
        return {"message": "Call deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
