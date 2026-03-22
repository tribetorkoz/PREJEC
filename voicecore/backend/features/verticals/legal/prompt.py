LEGAL_SYSTEM_PROMPT = """
You are {agent_name}, the intake specialist for {firm_name},
a law firm specializing in {practice_areas}.

LEGAL KNOWLEDGE YOU HAVE:
Practice areas you understand:
- Personal Injury: car accidents, slip and fall, medical malpractice
- Criminal Defense: DUI, assault, drug charges, federal crimes
- Family Law: divorce, custody, child support, adoption
- Immigration: visas, green cards, deportation defense, asylum
- Employment: wrongful termination, discrimination, harassment
- Estate Planning: wills, trusts, probate
- Bankruptcy: Chapter 7, Chapter 13

INTAKE QUESTIONS BY CASE TYPE:
Personal Injury:
  1. "When did the incident occur?"
  2. "Were you injured? Are you currently receiving medical treatment?"
  3. "Was a police report filed?"
  4. "Do you have insurance? Does the other party have insurance?"

DUI/Criminal:
  1. "What are the charges?"
  2. "When is your court date, if you have one?"
  3. "Is this your first offense?"

Family Law:
  1. "Are you currently married/separated?"
  2. "Are there children involved?"
  3. "Have any court proceedings started?"

CONFIDENTIALITY RULES — CRITICAL:
- NEVER repeat sensitive information back unnecessarily
- NEVER confirm or deny if someone is a client
- Say "I can't discuss any specific client matters"
- All conversations are confidential — inform callers of this

URGENCY DETECTION:
IMMEDIATE (transfer to on-call attorney):
- "I was just arrested"
- "I'm being deported"
- "My child was taken"
- "I'm in the hospital after an accident"

SAME DAY CONSULTATION:
- Recent accident (within 48 hours)
- Court date within 1 week
- Active custody emergency

PERSONALITY:
- Professional and empathetic — people calling are often in crisis
- Never minimize their situation
- Speak slowly and clearly
- "I understand this is a very stressful situation"

NEVER:
- Give legal advice ("You should sue them" or "You have a case")
- Predict case outcomes
- Discuss fees unless directly asked (then say "The attorney will discuss fees during your consultation")
- Make promises about results
"""

LEGAL_GREETING = "Thank you for calling {firm_name}. This is {agent_name}. I can help schedule a consultation or connect you with our team. What brings you to call us today?"

PRACTICE_AREAS = [
    "Personal Injury",
    "Criminal Defense",
    "Family Law",
    "Immigration",
    "Employment Law",
    "Estate Planning",
    "Bankruptcy",
]

CASE_TYPES = {
    "personal_injury": {
        "name": "Personal Injury",
        "questions": [
            "When did the incident occur?",
            "Were you injured? Are you currently receiving medical treatment?",
            "Was a police report filed?",
            "Do you have insurance? Does the other party have insurance?",
        ],
        "urgency_indicators": [
            "hospital",
            "accident",
            "injured",
            "emergency",
            "just happened",
        ],
    },
    "dui_criminal": {
        "name": "DUI/Criminal Defense",
        "questions": [
            "What are the charges?",
            "When is your court date, if you have one?",
            "Is this your first offense?",
            "Were you arrested?",
        ],
        "urgency_indicators": [
            "arrested",
            "court date",
            "police",
            "charged",
            "ticket",
        ],
    },
    "family_law": {
        "name": "Family Law",
        "questions": [
            "Are you currently married/separated?",
            "Are there children involved?",
            "Have any court proceedings started?",
            "What is the nature of your case?",
        ],
        "urgency_indicators": [
            "custody",
            "divorce",
            "child taken",
            "emergency",
            "abuse",
        ],
    },
    "immigration": {
        "name": "Immigration",
        "questions": [
            "What is your current immigration status?",
            "Have you received any notices from immigration?",
            "Do you have a court date?",
            "Are there any family members involved?",
        ],
        "urgency_indicators": [
            "deportation",
            "detained",
            "raid",
            "asylum",
            "notice",
        ],
    },
    "employment": {
        "name": "Employment Law",
        "questions": [
            "Who was your employer?",
            "When did the incident occur?",
            "Have you spoken to HR?",
            "Do you have any documentation?",
        ],
        "urgency_indicators": [
            "fired",
            "discriminated",
            "harassed",
            "wrongful termination",
            "hostile",
        ],
    },
    "estate_planning": {
        "name": "Estate Planning",
        "questions": [
            "What type of estate planning do you need?",
            "Do you have existing documents?",
            "What is the approximate value of your estate?",
            "Who would you like to designate as beneficiaries?",
        ],
        "urgency_indicators": [],
    },
    "bankruptcy": {
        "name": "Bankruptcy",
        "questions": [
            "What type of debt do you have?",
            "Have you filed for bankruptcy before?",
            "Are you currently employed?",
            "What are your monthly expenses?",
        ],
        "urgency_indicators": [
            "foreclosure",
            "garnishment",
            "lawsuit",
            "debt collector",
        ],
    },
}

URGENT_KEYWORDS = [
    "arrested",
    "deported",
    "taken",
    "hospital",
    "emergency",
    "custody",
    "court date",
]
