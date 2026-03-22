from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone
import json
import logging

from db.database import get_db
from db.models import Call, Customer, Company
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def find_call_by_sid(db: AsyncSession, call_sid: str) -> Optional[Call]:
    """Look up a call record by its Twilio call SID."""
    if not call_sid:
        return None
    result = await db.execute(select(Call).where(Call.call_sid == call_sid))
    return result.scalar_one_or_none()


@router.post("/twilio/voice")
async def twilio_voice_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Twilio voice webhook for incoming calls."""
    try:
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid", "")
        caller_phone = form_data.get("From", "")
        called_phone = form_data.get("To", "")
        call_status = form_data.get("CallStatus", "")
        
        logger.info(f"Twilio voice webhook: sid={call_sid}, from={caller_phone}, status={call_status}")
        
        # Find company by phone number
        company_result = await db.execute(
            select(Company).where(Company.phone_number == called_phone)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            logger.warning(f"No company found for number: {called_phone}")
            twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, this number is not configured.</Say></Response>'
            return Response(content=twiml, media_type="application/xml")
        
        # Find or create customer
        customer_result = await db.execute(
            select(Customer).where(
                Customer.phone == caller_phone,
                Customer.company_id == company.id,
            )
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            customer = Customer(
                company_id=company.id,
                phone=caller_phone,
                total_calls=0,
            )
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
        
        # Update customer call count
        customer.total_calls = (customer.total_calls or 0) + 1
        customer.last_call_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Create call record
        call = Call(
            company_id=company.id,
            call_sid=call_sid,
            caller_phone=caller_phone,
            direction="inbound",
            sentiment="NEUTRAL",
            outcome="answered",
        )
        db.add(call)
        await db.commit()
        
        # Return TwiML to connect to voice agent
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{settings.next_public_api_url.replace('http://', '').replace('https://', '')}/ws/voice/{company.id}">
            <Parameter name="call_sid" value="{call_sid}"/>
            <Parameter name="company_id" value="{company.id}"/>
        </Stream>
    </Connect>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Twilio voice webhook error: {e}")
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred. Please try again later.</Say></Response>'
        return Response(content=twiml, media_type="application/xml")


@router.post("/twilio/status")
async def twilio_status_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Twilio call status updates."""
    try:
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid", "")
        call_status = form_data.get("CallStatus", "")
        duration = form_data.get("CallDuration")
        
        logger.info(f"Call status update: sid={call_sid}, status={call_status}")
        
        # Find call by SID (not by ordering!)
        call = await find_call_by_sid(db, call_sid)
        
        if call:
            if duration:
                call.duration_seconds = int(duration)
            if call_status in ("completed", "failed", "busy", "no-answer", "canceled"):
                call.ended_at = datetime.now(timezone.utc)
                call.outcome = call_status
            await db.commit()
        else:
            logger.warning(f"No call record found for SID: {call_sid}")
        
        return JSONResponse(content={"status": "ok"})
    
    except Exception as e:
        logger.error(f"Twilio status webhook error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/twilio/transfer")
async def twilio_transfer_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle call transfer webhook."""
    try:
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid", "")
        transfer_to = form_data.get("TransferTo", "")
        
        logger.info(f"Transfer request: sid={call_sid}, to={transfer_to}")
        
        call = await find_call_by_sid(db, call_sid)
        if call:
            call.outcome = f"transferred_to_{transfer_to}"
            call.ended_at = datetime.now(timezone.utc)
            await db.commit()
        
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Transferring your call now. Please hold.</Say>
    <Dial>{transfer_to}</Dial>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Transfer webhook error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/twilio/recording")
async def twilio_recording_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Twilio recording webhook."""
    try:
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid", "")
        recording_url = form_data.get("RecordingUrl", "")
        recording_sid = form_data.get("RecordingSid", "")
        recording_duration = form_data.get("RecordingDuration", "0")
        
        logger.info(f"Recording available: sid={call_sid}, recording={recording_sid}")
        
        call = await find_call_by_sid(db, call_sid)
        if call:
            call.recording_url = recording_url
            if not call.duration_seconds:
                call.duration_seconds = int(recording_duration)
            await db.commit()
        
        return JSONResponse(content={"status": "ok"})
    
    except Exception as e:
        logger.error(f"Recording webhook error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/twilio/whatsapp")
async def twilio_whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle incoming WhatsApp messages via Twilio."""
    try:
        form_data = await request.form()
        
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        to_number = form_data.get("To", "").replace("whatsapp:", "")
        body = form_data.get("Body", "")
        num_media = int(form_data.get("NumMedia", "0"))
        
        logger.info(f"WhatsApp message from {from_number}: {body[:50]}...")
        
        # Find company by WhatsApp number
        company_result = await db.execute(
            select(Company).where(Company.whatsapp_number == to_number)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            logger.warning(f"No company found for WhatsApp number: {to_number}")
            return Response(content="", status_code=200)
        
        # Find or create customer
        customer_result = await db.execute(
            select(Customer).where(
                Customer.phone == from_number,
                Customer.company_id == company.id,
            )
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            customer = Customer(
                company_id=company.id,
                phone=from_number,
                total_calls=0,
            )
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
        
        # Create call record for tracking
        call = Call(
            company_id=company.id,
            caller_phone=from_number,
            direction="inbound",
            transcript=body,
            sentiment="NEUTRAL",
            outcome="whatsapp_message",
        )
        db.add(call)
        await db.commit()
        
        # TODO: Process message through WhatsApp service
        
        return Response(content="", status_code=200)
    
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    try:
        body = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        # Verify webhook signature
        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key
            event = stripe.Webhook.construct_event(
                body, sig_header, settings.stripe_webhook_secret
            )
        except Exception as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})
        
        logger.info(f"Stripe event: {event_type}")
        
        if event_type == "checkout.session.completed":
            customer_id = data.get("customer")
            subscription_id = data.get("subscription")
            
            if customer_id:
                result = await db.execute(
                    select(Company).where(Company.stripe_customer_id == customer_id)
                )
                company = result.scalar_one_or_none()
                if company:
                    company.stripe_subscription_id = subscription_id
                    company.status = "active"
                    await db.commit()
        
        elif event_type == "invoice.paid":
            customer_id = data.get("customer")
            logger.info(f"Invoice paid for customer: {customer_id}")
        
        elif event_type == "customer.subscription.deleted":
            customer_id = data.get("customer")
            if customer_id:
                result = await db.execute(
                    select(Company).where(Company.stripe_customer_id == customer_id)
                )
                company = result.scalar_one_or_none()
                if company:
                    company.plan = "free"
                    company.stripe_subscription_id = None
                    company.status = "cancelled"
                    await db.commit()
        
        elif event_type == "customer.subscription.updated":
            customer_id = data.get("customer")
            status = data.get("status")
            if customer_id:
                result = await db.execute(
                    select(Company).where(Company.stripe_customer_id == customer_id)
                )
                company = result.scalar_one_or_none()
                if company:
                    company.status = status or "active"
                    await db.commit()
        
        return JSONResponse(content={"status": "ok"})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/twilio/lookup")
async def twilio_lookup(phone: str):
    """Perform phone number lookup via Twilio."""
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise HTTPException(status_code=500, detail="Twilio credentials not configured")
        
        phone_number = client.lookups.v2.phone_numbers(phone).fetch()
        
        return {
            "phone": phone_number.phone_number,
            "country_code": phone_number.country_code,
            "valid": phone_number.valid,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Twilio lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
