from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel


class RealtyToolInput(BaseModel):
    property_address: Optional[str] = None
    buyer_name: Optional[str] = None
    phone: Optional[str] = None
    date_time: Optional[str] = None
    seller_name: Optional[str] = None
    mls_number: Optional[str] = None
    zip_code: Optional[str] = None
    pre_approved: Optional[bool] = None
    timeline: Optional[str] = None
    budget: Optional[str] = None
    property_url: Optional[str] = None
    lead_details: Optional[str] = None


def schedule_showing(
    property_address: str,
    buyer_name: str,
    phone: str,
    date_time: str,
    email: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule a property showing for a buyer.
    """
    showing_id = f"SHOW-{hash(phone) % 10000:04d}"
    
    return {
        "showing_id": showing_id,
        "property_address": property_address,
        "buyer_name": buyer_name,
        "phone": phone,
        "email": email,
        "date_time": date_time,
        "duration_minutes": 30,
        "status": "scheduled",
        "reminder_sent": False,
        "property_details_sent": False,
        "notes": notes,
        "confirmation_method": "sms"
    }


def schedule_listing_consultation(
    address: str,
    seller_name: str,
    phone: str,
    date_time: Optional[str] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule a listing consultation (CMA appointment) with a seller.
    """
    consultation_id = f"LIST-{hash(phone) % 10000:04d}"
    
    return {
        "consultation_id": consultation_id,
        "property_address": address,
        "seller_name": seller_name,
        "phone": phone,
        "email": email,
        "date_time": date_time or "to be scheduled",
        "consultation_type": "CMA (Comparative Market Analysis)",
        "status": "scheduled",
        "documents_needed": [
            "Property deed",
            "Tax records",
            "Any recent improvements",
            "HOA documents (if applicable)"
        ],
        "confirmation_sent": False
    }


def check_property_availability(
    mls_number: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if a property is still available using MLS data.
    """
    if mls_number:
        property_id = mls_number
    elif address:
        property_id = address
    else:
        return {"error": "MLS number or address required"}
    
    return {
        "mls_number": mls_number,
        "address": address,
        "available": True,
        "status": "Active",
        "days_on_market": 12,
        "price_history": [
            {"date": "2024-01-15", "price": "$450,000", "change": "Listed"}
        ],
        "showing_available": True,
        "next_available_showing": "Tomorrow at 2:00 PM"
    }


def get_market_stats(zip_code: str) -> Dict[str, Any]:
    """
    Get market statistics for a zip code.
    """
    return {
        "zip_code": zip_code,
        "median_price": "$425,000",
        "average_price": "$445,000",
        "price_change_12mo": "+5.2%",
        "average_days_on_market": 28,
        "inventory_level": "Low",
        "months_of_supply": 2.1,
        "market_type": "Seller's Market",
        "tip": "Good time to sell, buyers are active"
    }


def qualify_buyer_lead(
    pre_approved: bool,
    timeline: str,
    budget: Optional[str] = None,
    property_type: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Qualify a buyer lead based on pre-approval status, timeline, and budget.
    """
    if pre_approved and timeline in ["immediately", "30_days", "60_days"]:
        priority = "hot"
        lead_score = 90
        recommendation = "Immediate follow-up - schedule showing"
    elif pre_approved or timeline in ["30_days", "60_days"]:
        priority = "warm"
        lead_score = 70
        recommendation = "Schedule consultation within 24 hours"
    else:
        priority = "cold"
        lead_score = 40
        recommendation = "Add to nurture campaign, follow up in 2 weeks"
    
    return {
        "pre_approved": pre_approved,
        "timeline": timeline,
        "budget": budget,
        "property_type": property_type,
        "location": location,
        "priority": priority,
        "lead_score": lead_score,
        "recommendation": recommendation,
        "next_action": "Call" if priority == "hot" else "Schedule follow-up",
        "pre_approval_message": "Great! Let me schedule some showings for you" if pre_approved else "I can connect you with a great lender first"
    }


def send_property_details(
    phone: str,
    property_url: str,
    buyer_name: Optional[str] = None,
    include_photos: bool = True
) -> Dict[str, Any]:
    """
    Send property details to a potential buyer via SMS/WhatsApp.
    """
    return {
        "sent": True,
        "method": "sms",
        "recipient": phone,
        "buyer_name": buyer_name,
        "property_url": property_url,
        "includes_photos": include_photos,
        "includes_details": True,
        "message": f"Here are the details for the property you requested: {property_url}",
        "scheduled_showing_link": True
    }


def connect_to_lender(
    buyer_name: str,
    phone: str,
    budget: Optional[str] = None,
    timeline: Optional[str] = None
) -> Dict[str, Any]:
    """
    Connect buyer with a lender partner for pre-approval.
    """
    return {
        "referral_sent": True,
        "lender_contact": "preferred_lender@partnernetwork.com",
        "buyer_name": buyer_name,
        "phone": phone,
        "budget": budget,
        "timeline": timeline,
        "lender_note": f"Hot lead from {buyer_name} - {budget} budget, {timeline} timeline",
        "follow_up_scheduled": False
    }


def flag_hot_lead(
    lead_details: str,
    lead_name: Optional[str] = None,
    lead_phone: Optional[str] = None,
    lead_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Flag a hot lead for immediate agent notification.
    """
    alert_id = f"HOT-{datetime.utcnow().strftime('%Y%m%d')}-{hash(lead_phone or lead_name or lead_details) % 10000:04d}"
    
    return {
        "alert_id": alert_id,
        "urgent": True,
        "lead_name": lead_name,
        "lead_phone": lead_phone,
        "lead_type": lead_type,
        "details": lead_details,
        "notification_sent": True,
        "notification_method": "sms",
        "notify_agent_immediately": True,
        "response_time_sla": "within 5 minutes"
    }


def calculate_closing_costs(purchase_price: float) -> Dict[str, Any]:
    """
    Estimate closing costs for a property purchase.
    """
    loan_costs = purchase_price * 0.02
    title_insurance = purchase_price * 0.005
    transfer_taxes = purchase_price * 0.01
    appraisal = 500
    inspection = 400
    escrow_fee = purchase_price * 0.001
    
    total_closing_costs = loan_costs + title_insurance + transfer_taxes + appraisal + inspection + escrow_fee
    
    return {
        "purchase_price": f"${purchase_price:,.0f}",
        "estimated_closing_costs": f"${total_closing_costs:,.0f}",
        "breakdown": {
            "loan_costs": f"${loan_costs:,.0f} (2%)",
            "title_insurance": f"${title_insurance:,.0f} (0.5%)",
            "transfer_taxes": f"${transfer_taxes:,.0f} (1%)",
            "appraisal": f"${appraisal}",
            "inspection": f"${inspection}",
            "escrow": f"${escrow_fee:,.0f} (0.1%)"
        },
        "total_as_percentage": "3-5% of purchase price",
        "note": "Exact costs vary by lender and location"
    }


def get_investor_properties(
    max_budget: Optional[str] = None,
    min_cap_rate: Optional[float] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find investment properties based on criteria.
    """
    sample_properties = [
        {
            "address": "123 Investment Lane",
            "price": "$385,000",
            "rental_income": "$3,200/month",
            "cap_rate": "7.2%",
            "cash_flow": "$1,400/month",
            "units": 4
        },
        {
            "address": "456 Multi-Family Way",
            "price": "$475,000",
            "rental_income": "$4,100/month",
            "cap_rate": "6.8%",
            "cash_flow": "$1,850/month",
            "units": 6
        }
    ]
    
    return {
        "search_criteria": {
            "max_budget": max_budget,
            "min_cap_rate": min_cap_rate,
            "location": location
        },
        "properties_found": len(sample_properties),
        "properties": sample_properties,
        "note": "Contact for full MLS search with current listings"
    }


REALTY_TOOLS = [
    {
        "name": "schedule_showing",
        "description": "Schedule a property showing for a buyer",
        "parameters": {
            "property_address": "Address of property to show",
            "buyer_name": "Full name of buyer",
            "phone": "Buyer's phone number",
            "date_time": "Preferred date and time",
            "email": "Buyer's email (optional)"
        }
    },
    {
        "name": "schedule_listing_consultation",
        "description": "Schedule a listing consultation/CMA with a seller",
        "parameters": {
            "address": "Seller's property address",
            "seller_name": "Full name of seller",
            "phone": "Seller's phone number",
            "date_time": "Preferred consultation time (optional)"
        }
    },
    {
        "name": "check_property_availability",
        "description": "Check if a property is still available via MLS",
        "parameters": {
            "mls_number": "MLS listing number (optional)",
            "address": "Property address (optional)"
        }
    },
    {
        "name": "get_market_stats",
        "description": "Get market statistics for a zip code",
        "parameters": {
            "zip_code": "Zip code for market data"
        }
    },
    {
        "name": "qualify_buyer_lead",
        "description": "Qualify a buyer lead based on readiness to buy",
        "parameters": {
            "pre_approved": "Whether buyer is pre-approved for mortgage",
            "timeline": "When buyer wants to purchase",
            "budget": "Buyer's budget (optional)",
            "property_type": "Type of property looking for (optional)"
        }
    },
    {
        "name": "send_property_details",
        "description": "Send property details to a buyer via SMS",
        "parameters": {
            "phone": "Recipient's phone number",
            "property_url": "Link to property details",
            "buyer_name": "Buyer's name (optional)"
        }
    },
    {
        "name": "connect_to_lender",
        "description": "Connect buyer with a lender for pre-approval",
        "parameters": {
            "buyer_name": "Buyer's full name",
            "phone": "Buyer's phone number",
            "budget": "Buyer's budget (optional)"
        }
    },
    {
        "name": "flag_hot_lead",
        "description": "Flag a hot lead for immediate agent notification",
        "parameters": {
            "lead_details": "Details about the lead",
            "lead_name": "Lead's name (optional)",
            "lead_phone": "Lead's phone (optional)",
            "lead_type": "Type of lead (buyer/seller/investor)"
        }
    },
    {
        "name": "calculate_closing_costs",
        "description": "Estimate closing costs for a purchase",
        "parameters": {
            "purchase_price": "Purchase price of property"
        }
    },
    {
        "name": "get_investor_properties",
        "description": "Find investment properties meeting criteria",
        "parameters": {
            "max_budget": "Maximum budget (optional)",
            "min_cap_rate": "Minimum cap rate desired (optional)",
            "location": "Preferred location (optional)"
        }
    }
]
