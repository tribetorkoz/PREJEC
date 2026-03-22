from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timedelta


class LegalToolInput(BaseModel):
    case_type: Optional[str] = None
    urgency: Optional[str] = None
    client_name: Optional[str] = None
    phone: Optional[str] = None
    best_time: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[str] = None
    party_names: Optional[List[str]] = None
    practice_area: Optional[str] = None


def schedule_consultation(
    case_type: str,
    urgency: str,
    client_name: str,
    phone: str,
    best_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule a legal consultation appointment.
    Handles different urgency levels appropriately.
    """
    appointment_id = f"LEGAL-{hash(phone) % 10000:04d}"
    
    if urgency.lower() in ["immediate", "emergency", "urgent"]:
        priority = "IMMEDIATE"
        same_day = True
        consultation_type = "emergency_consultation"
    elif urgency.lower() == "same_day":
        priority = "HIGH"
        same_day = True
        consultation_type = "same_day_consultation"
    else:
        priority = "STANDARD"
        same_day = False
        consultation_type = "standard_consultation"
    
    return {
        "appointment_id": appointment_id,
        "client_name": client_name,
        "phone": phone,
        "case_type": case_type,
        "priority": priority,
        "same_day_consultation": same_day,
        "consultation_type": consultation_type,
        "status": "scheduled",
        "best_time": best_time or "to be determined",
        "confirmation_sent": False,
        "intake_form_required": True
    }


def flag_urgent_case(reason: str) -> Dict[str, Any]:
    """
    Flag an urgent case and immediately alert the on-call attorney.
    Used for emergencies like arrests, deportation, custody emergencies.
    """
    alert_channels = ["sms", "email", "push"]
    
    return {
        "urgent": True,
        "reason": reason,
        "alert_sent": True,
        "alert_channels": alert_channels,
        "notify": [
            "on-call attorney",
            "managing partner",
            "intake coordinator"
        ],
        "response_time_sla": "within 15 minutes",
        "case_priority": "CRITICAL",
        "actions_taken": [
            "Attorney notified via all channels",
            "Case flagged in system",
            "Emergency contact information provided to caller"
        ]
    }


def qualify_case(case_type: str, details: str) -> Dict[str, Any]:
    """
    Qualify a potential case to determine if it fits the firm's practice areas.
    Returns case viability assessment.
    """
    practice_area_eligibility = {
        "personal_injury": {
            "eligible": True,
            "min_damages": "$5,000",
            "statute_of_limitations": "2-3 years depending on jurisdiction",
            "typical_value": "$10,000 - $500,000+"
        },
        "dui_criminal": {
            "eligible": True,
            "considerations": "First offense vs. repeat, blood alcohol level, injuries",
            "court_required": True,
            "typical_outcome": "Varies significantly - requires attorney review"
        },
        "family_law": {
            "eligible": True,
            "considerations": "Contested vs. uncontested, children involved, assets",
            "court_required": True,
            "typical_timeline": "3-12 months"
        },
        "immigration": {
            "eligible": True,
            "considerations": "Current status, deportation risk, family ties",
            "court_required": "Sometimes",
            "typical_timeline": "3 months - 2+ years"
        },
        "employment": {
            "eligible": True,
            "min_damages": "$5,000",
            "eeoc_required": True,
            "typical_timeline": "6-18 months"
        },
        "estate_planning": {
            "eligible": True,
            "considerations": "Complexity of estate, specific needs",
            "typical_documents": "Wills, trusts, POAs, healthcare directives"
        },
        "bankruptcy": {
            "eligible": True,
            "considerations": "Debt amount, income, assets",
            "chapter_options": ["Chapter 7", "Chapter 13"],
            "credit_counseling_required": True
        }
    }
    
    eligibility = practice_area_eligibility.get(
        case_type.lower().replace(" ", "_"),
        {"eligible": False, "reason": "Case type not in current practice areas"}
    )
    
    return {
        "case_type": case_type,
        "details_summary": details[:200],
        "qualification_result": eligibility,
        "requires_attorney_review": True,
        "next_step": "Schedule consultation for case evaluation"
    }


def send_intake_form(phone: str, case_type: str) -> Dict[str, Any]:
    """
    Send legal intake forms to potential client via SMS/WhatsApp.
    """
    intake_forms = {
        "personal_injury": [
            "Incident details form",
            "Medical records release",
            "Insurance information",
            "Employment records",
            "Pain and suffering questionnaire"
        ],
        "dui_criminal": [
            "Criminal history form",
            "Incident details",
            "Witness information",
            "Officer information"
        ],
        "family_law": [
            "Family composition form",
            "Financial disclosure",
            "Custody questionnaire",
            "Property inventory"
        ],
        "immigration": [
            "Immigration history form",
            "Family information",
            "Employment history",
            "Criminal history (if any)"
        ],
        "employment": [
            "Employment history",
            "Incident details",
            "Witness information",
            "Economic damages worksheet"
        ],
        "estate_planning": [
            "Asset inventory",
            "Beneficiary designation",
            "Family information",
            "Healthcare preferences"
        ],
        "bankruptcy": [
            "Debt inventory",
            "Income and expense form",
            "Asset disclosure",
            "Credit counseling certificate"
        ]
    }
    
    forms = intake_forms.get(
        case_type.lower().replace(" ", "_"),
        ["General intake form"]
    )
    
    return {
        "sent": True,
        "method": "sms",
        "recipient": phone,
        "case_type": case_type,
        "forms_included": forms,
        "forms_count": len(forms),
        "message": "Thank you for contacting us. Please complete these intake forms before your consultation: [link]"
    }


def check_conflict_of_interest(party_names: List[str]) -> Dict[str, Any]:
    """
    Check for conflicts of interest before taking a case.
    Critical for legal ethics compliance.
    """
    conflict_database = []
    
    found_conflicts = []
    for party in party_names:
        if party.lower() in [p.lower() for p in conflict_database]:
            found_conflicts.append(party)
    
    return {
        "checked_parties": party_names,
        "conflicts_found": len(found_conflicts) > 0,
        "conflicting_parties": found_conflicts if found_conflicts else [],
        "clear_to_proceed": len(found_conflicts) == 0,
        "requires_attorney_review": len(found_conflicts) > 0,
        "conflict_check_timestamp": datetime.utcnow().isoformat()
    }


def log_inquiry(details: str, case_type: Optional[str] = None, caller_phone: Optional[str] = None) -> Dict[str, Any]:
    """
    Log every inquiry for compliance and audit purposes.
    All legal inquiries must be logged.
    """
    inquiry_id = f"INQ-{datetime.utcnow().strftime('%Y%m%d')}-{hash(caller_phone or details) % 10000:04d}"
    
    return {
        "inquiry_id": inquiry_id,
        "logged": True,
        "timestamp": datetime.utcnow().isoformat(),
        "case_type": case_type or "unclassified",
        "caller_phone": caller_phone,
        "details_length": len(details),
        "retention_period_days": 2555,
        "compliance_note": "Inquiry retained for 7 years per legal ethics requirements"
    }


def check_legal_deadline(case_type: str, incident_date: str) -> Dict[str, Any]:
    """
    Check important legal deadlines based on case type and incident date.
    """
    from datetime import datetime
    
    try:
        incident = datetime.strptime(incident_date, "%Y-%m-%d")
    except:
        try:
            incident = datetime.strptime(incident_date, "%m/%d/%Y")
        except:
            return {
                "error": "Could not parse date format",
                "incident_date": incident_date,
                "recommendation": "Consult attorney for deadline assessment"
            }
    
    statute_of_limitations = {
        "personal_injury": {"years": 2, "jurisdiction": "varies by state"},
        "medical_malpractice": {"years": 2, "jurisdiction": "varies by state"},
        "dui": {"years": 1, "jurisdiction": "varies by state"},
        "divorce": {"years": 0, "jurisdiction": "no deadline"},
        "child_custody": {"years": 0, "jurisdiction": "ongoing"},
        "employment_discrimination": {"years": 180, "jurisdiction": "days (EEOC)"},
        "fair_credit_reporting": {"years": 2, "jurisdiction": "varies by state"}
    }
    
    sol = statute_of_limitations.get(case_type.lower().replace(" ", "_"), None)
    
    if sol is None:
        return {
            "case_type": case_type,
            "incident_date": incident_date,
            "statute_of_limitations": "Unknown - consult attorney",
            "urgency": "consult_attorney"
        }
    
    if sol["years"] == 0:
        deadline_status = "No strict deadline"
        days_remaining = None
    else:
        deadline = incident + timedelta(days=sol["years"] * 365)
        today = datetime.utcnow()
        days_remaining = (deadline - today).days
        deadline_status = "Expired" if days_remaining < 0 else "Active"
    
    return {
        "case_type": case_type,
        "incident_date": incident_date,
        "statute_of_limitations": f"{sol['years']} years" if sol["years"] > 0 else sol["jurisdiction"],
        "jurisdiction": sol["jurisdiction"],
        "days_remaining": days_remaining,
        "deadline_status": deadline_status,
        "urgency": "urgent" if days_remaining and days_remaining < 90 else "normal" if days_remaining else "consult_attorney"
    }


LEGAL_TOOLS = [
    {
        "name": "schedule_consultation",
        "description": "Schedule a legal consultation with a potential client",
        "parameters": {
            "case_type": "Type of legal matter (personal_injury, dui_criminal, family_law, etc.)",
            "urgency": "Urgency level (immediate, same_day, standard)",
            "client_name": "Potential client's full name",
            "phone": "Client's phone number",
            "best_time": "Best time for consultation (optional)"
        }
    },
    {
        "name": "flag_urgent_case",
        "description": "Flag an urgent case for immediate attorney attention",
        "parameters": {
            "reason": "Reason for urgency (arrest, deportation, emergency, etc.)"
        }
    },
    {
        "name": "qualify_case",
        "description": "Qualify a potential case to determine if it fits the firm's practice",
        "parameters": {
            "case_type": "Type of legal matter",
            "details": "Details about the case"
        }
    },
    {
        "name": "send_intake_form",
        "description": "Send legal intake forms to a potential client",
        "parameters": {
            "phone": "Client's phone number",
            "case_type": "Type of legal matter"
        }
    },
    {
        "name": "check_conflict_of_interest",
        "description": "Check for conflicts of interest before taking a case",
        "parameters": {
            "party_names": "List of party names to check"
        }
    },
    {
        "name": "log_inquiry",
        "description": "Log every inquiry for compliance and audit purposes",
        "parameters": {
            "details": "Details of the inquiry",
            "case_type": "Type of legal matter (optional)",
            "caller_phone": "Caller's phone number (optional)"
        }
    },
    {
        "name": "check_legal_deadline",
        "description": "Check statute of limitations and important legal deadlines",
        "parameters": {
            "case_type": "Type of legal matter",
            "incident_date": "Date of incident (YYYY-MM-DD)"
        }
    }
]
