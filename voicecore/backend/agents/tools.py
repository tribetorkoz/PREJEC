from typing import Dict, Any, Optional
from datetime import datetime


async def get_business_hours() -> Dict[str, Any]:
    return {
        "open": "9:00 AM",
        "close": "6:00 PM",
        "timezone": "UTC",
        "days": "Monday-Friday"
    }


async def get_product_info(product_id: str) -> Dict[str, Any]:
    products = {
        "1": {"name": "Basic Plan", "price": "$29/month", "features": ["5 agents", "1000 calls/month"]},
        "2": {"name": "Pro Plan", "price": "$99/month", "features": ["25 agents", "10000 calls/month", "Analytics"]},
        "3": {"name": "Enterprise Plan", "price": "Custom", "features": ["Unlimited agents", "Unlimited calls", "Priority support"]}
    }
    return products.get(product_id, {"error": "Product not found"})


async def create_support_ticket(customer_phone: str, issue: str) -> Dict[str, Any]:
    return {
        "ticket_id": f"TICKET-{datetime.now().timestamp()}",
        "status": "created",
        "customer_phone": customer_phone,
        "issue": issue,
        "created_at": datetime.now().isoformat()
    }


async def transfer_to_human(reason: str, customer_info: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "transferring",
        "reason": reason,
        "customer": customer_info,
        "queue_position": 1
    }


async def get_customer_orders(phone: str) -> Dict[str, Any]:
    return {
        "phone": phone,
        "orders": [],
        "message": "No orders found"
    }


AGENT_TOOLS = [
    {
        "name": "get_business_hours",
        "description": "Get business operating hours",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_product_info",
        "description": "Get information about products or plans",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product ID"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "create_support_ticket",
        "description": "Create a support ticket for customer issues",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_phone": {"type": "string"},
                "issue": {"type": "string"}
            },
            "required": ["customer_phone", "issue"]
        }
    },
    {
        "name": "transfer_to_human",
        "description": "Transfer call to a human agent",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "customer_info": {"type": "object"}
            },
            "required": ["reason"]
        }
    }
]
