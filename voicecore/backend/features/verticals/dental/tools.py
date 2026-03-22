from typing import Optional, Dict, Any
from pydantic import BaseModel


class DentalToolInput(BaseModel):
    carrier: Optional[str] = None
    procedure: Optional[str] = None
    patient_name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    insurance: Optional[str] = None
    date: Optional[str] = None
    appointment_type: Optional[str] = None
    symptom: Optional[str] = None
    appointment_id: Optional[str] = None
    reason: Optional[str] = None


def check_insurance_coverage(carrier: str, procedure: str) -> Dict[str, Any]:
    """
    Check insurance coverage for a dental procedure.
    Returns typical coverage percentages and patient responsibility.
    """
    coverage_rates = {
        "cleaning": {"preventive": 100, "basic": 80, "major": 50},
        "filling": {"preventive": 0, "basic": 80, "major": 50},
        "root_canal": {"preventive": 0, "basic": 50, "major": 50},
        "crown": {"preventive": 0, "basic": 50, "major": 50},
        "extraction": {"preventive": 0, "basic": 80, "major": 50},
        "implant": {"preventive": 0, "basic": 0, "major": 0},
    }
    
    procedure_type = "basic"
    if procedure.lower() in ["cleaning", "xray"]:
        procedure_type = "preventive"
    elif procedure.lower() in ["implant", "invisalign"]:
        procedure_type = "major"
    
    coverage = coverage_rates.get(procedure.lower(), {}).get(procedure_type, 0)
    
    return {
        "carrier": carrier,
        "procedure": procedure,
        "typical_coverage": f"{coverage}%",
        "patient_responsibility": f"{100-coverage}%",
        "note": "Exact coverage varies by specific plan. We'll verify at your visit."
    }


def book_dental_appointment(
    appointment_type: str,
    patient_name: str,
    phone: str,
    dob: str,
    insurance: Optional[str] = None,
    is_emergency: bool = False
) -> Dict[str, Any]:
    """
    Book a dental appointment with all required patient info.
    """
    appointment_id = f"DENT-{hash(phone) % 10000:04d}"
    
    slot_priority = "URGENT" if is_emergency else "standard"
    
    return {
        "appointment_id": appointment_id,
        "patient_name": patient_name,
        "phone": phone,
        "date_of_birth": dob,
        "insurance": insurance,
        "appointment_type": appointment_type,
        "priority": slot_priority,
        "status": "confirmed",
        "confirmation_sent": False
    }


def check_dental_availability(date: str, appointment_type: str) -> Dict[str, Any]:
    """
    Check available slots for dental appointments.
    """
    base_slots = ["9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", 
                  "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM"]
    
    emergency_slots = ["8:00 AM", "8:30 AM", "12:00 PM", "12:30 PM", "4:00 PM", "4:30 PM"]
    
    if appointment_type.lower() == "emergency":
        available = emergency_slots[:3]
    else:
        available = base_slots[:5]
    
    return {
        "date": date,
        "appointment_type": appointment_type,
        "available_slots": available,
        "next_available": date if available else "next day"
    }


def flag_dental_emergency(symptom: str) -> Dict[str, Any]:
    """
    Flag a dental emergency and alert the dental team.
    """
    return {
        "emergency": True,
        "symptom": symptom,
        "alert_sent_to": "dentist on call",
        "priority": "immediate",
        "same_day_appointment": True,
        "instructions": "Patient should be offered next available slot today"
    }


def calculate_dental_estimate(procedure: str, insurance_carrier: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate estimated cost for a dental procedure.
    """
    from backend.features.verticals.dental.knowledge import DENTAL_PROCEDURES
    
    procedure_info = DENTAL_PROCEDURES.get(procedure.lower(), {})
    
    base_price = procedure_info.get("price_range", "TBD")
    insurance_info = procedure_info.get("insurance", "varies")
    
    return {
        "procedure": procedure,
        "estimated_price": base_price,
        "insurance_coverage": insurance_info,
        "with_insurance_estimate": "Pricing depends on your specific insurance plan",
        "note": "We can provide exact pricing after verifying your insurance"
    }


def send_new_patient_forms(phone: str, patient_name: str) -> Dict[str, Any]:
    """
    Send new patient intake forms via WhatsApp.
    """
    return {
        "sent": True,
        "method": "whatsapp",
        "recipient": phone,
        "patient_name": patient_name,
        "forms_included": [
            "Patient information",
            "Medical history",
            "Dental history",
            "Insurance information",
            "HIPAA consent"
        ],
        "message": f"Hi {patient_name}, welcome to our practice! Please complete your intake forms before your visit: [link]"
    }


def confirm_dental_appointment(appointment_id: str) -> Dict[str, Any]:
    """
    Confirm a dental appointment and send reminders.
    """
    return {
        "appointment_id": appointment_id,
        "status": "confirmed",
        "reminder_schedule": [
            "24 hours before: SMS reminder",
            "2 hours before: SMS reminder",
            "Day of: WhatsApp reminder"
        ],
        "what_to_bring": [
            "Photo ID",
            "Insurance card",
            "List of current medications",
            "Any previous dental records (if available)"
        ]
    }


def cancel_dental_appointment(appointment_id: str, reason: str) -> Dict[str, Any]:
    """
    Cancel a dental appointment.
    """
    return {
        "appointment_id": appointment_id,
        "status": "cancelled",
        "reason": reason,
        "reschedule_offered": True,
        "cancellation_policy": "Please give 24 hours notice to avoid fees"
    }


DENTAL_TOOLS = [
    {
        "name": "check_insurance_coverage",
        "description": "Check dental insurance coverage for a specific procedure",
        "parameters": {
            "carrier": "Insurance carrier name",
            "procedure": "Type of dental procedure"
        }
    },
    {
        "name": "book_dental_appointment",
        "description": "Book a dental appointment with patient information",
        "parameters": {
            "appointment_type": "Type of appointment (cleaning, filling, etc.)",
            "patient_name": "Patient full name",
            "phone": "Patient phone number",
            "dob": "Date of birth",
            "insurance": "Insurance carrier (optional)"
        }
    },
    {
        "name": "check_dental_availability",
        "description": "Check available appointment slots",
        "parameters": {
            "date": "Desired date",
            "appointment_type": "Type of dental procedure"
        }
    },
    {
        "name": "flag_dental_emergency",
        "description": "Flag an emergency and alert the dental team",
        "parameters": {
            "symptom": "Patient's emergency symptom"
        }
    },
    {
        "name": "calculate_dental_estimate",
        "description": "Calculate estimated cost for a procedure",
        "parameters": {
            "procedure": "Type of dental procedure",
            "insurance_carrier": "Insurance carrier (optional)"
        }
    },
    {
        "name": "send_new_patient_forms",
        "description": "Send intake forms to new patient via WhatsApp",
        "parameters": {
            "phone": "Patient phone number",
            "patient_name": "Patient name"
        }
    },
    {
        "name": "confirm_dental_appointment",
        "description": "Confirm appointment and schedule reminders",
        "parameters": {
            "appointment_id": "Appointment ID to confirm"
        }
    },
    {
        "name": "cancel_dental_appointment",
        "description": "Cancel a dental appointment",
        "parameters": {
            "appointment_id": "Appointment ID",
            "reason": "Reason for cancellation"
        }
    }
]
