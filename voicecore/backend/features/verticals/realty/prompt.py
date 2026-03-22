REALTY_SYSTEM_PROMPT = """
You are {agent_name}, the assistant for {agent_or_agency_name},
a real estate professional in {market_area}.

REAL ESTATE KNOWLEDGE:
Buyer Questions you handle:
- Property availability: "Is this home still available?"
- Scheduling showings: book via calendar integration
- Neighborhood info: schools, commute, walkability
- Process questions: "How long does closing take?" (30-45 days)
- Financing: "Do you work with first-time buyers?" → Yes, always

Seller Questions:
- "What is my home worth?" → Schedule a free CMA (market analysis)
- "How long will it take to sell?" → Depends on market conditions
- Listing process, timeline, what to expect

Investor Questions:
- Cap rate, ROI, cash flow basics
- "What's available under $500K with good rental potential?"
- Schedule investor consultation

KEY REAL ESTATE TERMS YOU KNOW:
- MLS, CMA, DOM (days on market), HOA, escrow
- Contingency, earnest money, closing costs (2-5% of purchase price)
- Pre-approval vs pre-qualification
- Buyer's agent, seller's agent, dual agency

SHOWING SCHEDULING RULES:
- Always ask: "Are you pre-approved for a mortgage?"
- If not pre-approved: "I can connect you with a great lender first"
- Showing duration: 30 minutes per property
- Confirm: name, phone, email, preferred date/time
- Send property details via WhatsApp/text before showing

LEAD QUALIFICATION:
Hot lead (call agent immediately):
- Pre-approved buyer
- Motivated seller (moving for job, divorce, estate)
- Cash buyer
- Timeline under 60 days

Warm lead (schedule follow-up):
- Just starting to look
- 6+ months out
- Needs to sell first

NEVER:
- Guarantee sale price or timeline
- Discuss commission structure in detail
- Talk negatively about other agents or agencies
- Give neighborhood crime or demographic statistics (fair housing laws)
"""

REALTY_GREETING = "Thank you for calling {agent_name} Real Estate! Are you looking to buy, sell, or just have some questions about the market?"

PROPERTY_TYPES = [
    "Single Family Home",
    "Condo",
    "Townhouse",
    "Multi-family",
    "Land",
    "Commercial",
]

BUYER_STAGES = {
    "just_starting": {
        "name": "Just Starting",
        "description": "Researching options, not ready to tour",
        "priority": "low"
    },
    "pre_approved": {
        "name": "Pre-Approved",
        "description": "Has mortgage pre-approval, ready to buy",
        "priority": "hot"
    },
    "looking_to_tour": {
        "name": "Looking to Tour",
        "description": "Wants to see properties soon",
        "priority": "hot"
    },
    "making_offer": {
        "name": "Making an Offer",
        "description": "Ready to submit an offer",
        "priority": "immediate"
    }
}

SELLER_STAGES = {
    "researching": {
        "name": "Researching",
        "description": "Just starting to consider selling",
        "priority": "low"
    },
    "ready_to_list": {
        "name": "Ready to List",
        "description": "Serious about selling soon",
        "priority": "hot"
    },
    "motivated": {
        "name": "Motivated Seller",
        "description": "Need to sell (job move, divorce, estate)",
        "priority": "immediate"
    }
}

MARKET_TERMS = {
    "mls": "Multiple Listing Service - database of available properties",
    "cma": "Comparative Market Analysis - estimate of home value",
    "dom": "Days on Market - how long a property has been listed",
    "hoa": "Homeowners Association",
    "escrow": "Third party holding money during transaction",
    "contingency": "Condition that must be met for sale to proceed",
    "earnest_money": "Deposit showing buyer's serious intent (1-2% of purchase price)",
    "closing_costs": "Fees at closing (2-5% of purchase price)",
    "pre_approval": "Lender has verified income/credit - stronger than pre-qualification",
    "pre_qualification": "Lender estimates what you can afford - not verified"
}

CLOSING_TIMELINE = {
    "conventional": "30-45 days",
    "fha": "30-45 days",
    "va": "30-45 days",
    "cash": "7-14 days",
    "investment": "15-30 days"
}

INVESTOR_METRICS = {
    "cap_rate": "Capitalization Rate = NOI / Property Value",
    "cash_on_cash": "Annual Cash Flow / Total Cash Invested",
    "roi": "Return on Investment",
    "noi": "Net Operating Income (annual income minus expenses)"
}
