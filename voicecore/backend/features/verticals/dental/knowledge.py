DENTAL_PROCEDURES = {
    "cleaning": {
        "duration": 60, 
        "price_range": "$100-$200", 
        "insurance": "usually covered 100%",
        "new_patient": 90,
        "description": "Regular dental cleaning and polish"
    },
    "deep_cleaning": {
        "duration": 90, 
        "price_range": "$200-$400", 
        "insurance": "usually 80% covered",
        "new_patient": 90,
        "description": "Scaling and root planing for gum disease"
    },
    "filling": {
        "duration": 60, 
        "price_range": "$150-$300", 
        "insurance": "usually 80% covered",
        "new_patient": 90,
        "description": "Composite or amalgam filling for cavities"
    },
    "root_canal": {
        "duration": 90, 
        "price_range": "$700-$1500", 
        "insurance": "usually 50-80% covered",
        "new_patient": 90,
        "description": "Endodontic treatment to save infected tooth"
    },
    "crown": {
        "duration": 120, 
        "price_range": "$1000-$1800", 
        "insurance": "usually 50% covered",
        "new_patient": 90,
        "description": "Dental crown to restore damaged tooth"
    },
    "extraction": {
        "duration": 45, 
        "price_range": "$150-$400", 
        "insurance": "usually 80% covered",
        "new_patient": 90,
        "description": "Tooth extraction (simple or surgical)"
    },
    "implant": {
        "duration": 180, 
        "price_range": "$3000-$5000", 
        "insurance": "rarely covered",
        "new_patient": 90,
        "description": "Dental implant to replace missing tooth"
    },
    "whitening": {
        "duration": 90, 
        "price_range": "$300-$800", 
        "insurance": "not covered",
        "new_patient": 60,
        "description": "Professional teeth whitening treatment"
    },
    "invisalign": {
        "duration": 60, 
        "price_range": "$3000-$8000", 
        "insurance": "partial coverage possible",
        "new_patient": 90,
        "description": "Clear aligner orthodontic treatment"
    },
    "veneers": {
        "duration": 120, 
        "price_range": "$1000-$2000", 
        "insurance": "not covered",
        "new_patient": 90,
        "description": "Porcelain veneers for smile makeover"
    },
    "emergency": {
        "duration": 45, 
        "price_range": "$150-$300", 
        "insurance": "varies",
        "new_patient": 30,
        "description": "Emergency dental evaluation"
    },
    "xray": {
        "duration": 15, 
        "price_range": "$50-$150", 
        "insurance": "usually covered",
        "new_patient": 30,
        "description": "Dental x-rays (bitewing or panoramic)"
    }
}

DENTAL_EMERGENCIES = [
    "toothache",
    "tooth pain", 
    "broken tooth",
    "chipped tooth",
    "cracked tooth",
    "lost crown",
    "lost filling",
    "swelling",
    "abscess",
    "bleeding",
    "knocked out tooth",
    "tooth fell out",
    "pain when biting",
    "sensitive to hot cold",
    "gum infection",
    "dry socket",
    "wisdom tooth pain"
]

DENTAL_INSURANCE_CARRIERS = [
    "Delta Dental",
    "Cigna Dental",
    "Aetna Dental",
    "MetLife Dental",
    "Guardian Dental",
    "United Healthcare Dental",
    "Humana Dental",
    "Anthem Dental",
    "Principal Dental",
    "Blue Cross Blue Shield Dental",
    "PPO",
    "HMO"
]

DENTAL_PAYMENT_OPTIONS = [
    "CareCredit",
    "In-house payment plan",
    "HSA (Health Savings Account)",
    "FSA (Flexible Spending Account)",
    "Credit card",
    "Cash discount"
]

DENTAL_QUESTIONS = {
    "new_patient": "Are you a new patient or have you been to our office before?",
    "reason": "What brings you in today?",
    "insurance": "Do you have dental insurance?",
    "which_insurance": "Which insurance carrier do you have?",
    "symptoms": "Can you describe what you're experiencing?",
    "pain_level": "On a scale of 1-10, how would you rate your pain?",
    "when_started": "When did this start?",
    "first_visit": "Is this your first visit with us?"
}
