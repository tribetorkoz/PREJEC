# 💰 PROMPT 03 — COMMERCIAL LAYER
## VoiceCore — المهمة الثالثة: اجعله يبيع

---

## 🎯 هدفك من هذا الملف

تنفيذ **كل ما يحتاجه العميل قبل أن يدفع**:
1. Demo مباشر من المتصفح (بدون تسجيل)
2. Free Trial 14 يوم بدون بطاقة ائتمان
3. Landing Page قوية مع ROI Calculator
4. HIPAA Compliance layer
5. Legal pages (ToS + Privacy Policy)

**لا تبدأ هذا الملف قبل إتمام PROMPT_01 و PROMPT_02.**

---

## 📋 قائمة الملفات

```
backend/
├── api/
│   ├── demo.py               ← أنشئ من صفر
│   ├── public/router.py      ← تحديث كبير
│   └── billing.py            ← تحديث (أضف trial logic)
├── db/
│   └── models.py             ← أضف TrialUsage model
└── services/
    └── compliance_service.py ← أنشئ من صفر

frontend/
├── app/
│   ├── page.tsx              ← أعد كتابة كاملة
│   ├── demo/
│   │   └── page.tsx          ← أنشئ من صفر
│   ├── pricing/
│   │   └── page.tsx          ← أنشئ من صفر
│   ├── legal/
│   │   ├── terms/page.tsx    ← أنشئ من صفر
│   │   ├── privacy/page.tsx  ← أنشئ من صفر
│   │   └── hipaa/page.tsx    ← أنشئ من صفر
│   └── roi/
│       └── page.tsx          ← أنشئ من صفر
└── components/
    ├── landing/
    │   ├── HeroSection.tsx
    │   ├── DemoSection.tsx
    │   ├── PricingSection.tsx
    │   ├── ROICalculator.tsx
    │   ├── TestimonialsSection.tsx
    │   ├── StatsCounter.tsx
    │   └── IndustryCards.tsx
    └── trial/
        └── TrialBanner.tsx
```

---

## 🔧 المهمة 1: Live Demo System

### الأهم — الزائر يجرب الوكيل بدون تسجيل

### `backend/api/demo.py`

```python
"""
Demo System — أي شخص يتصل ويسمع الوكيل فوراً.

طريقتان للـ demo:
  1. Browser Demo: WebRTC مباشر من المتصفح (الأسهل)
  2. Phone Demo: يُدخل رقمه → نتصل به (الأكثر إقناعاً)
"""

router = APIRouter(prefix="/api/public/demo", tags=["demo"])

DEMO_RATE_LIMIT = "5/hour"  # لكل IP

@router.post("/browser-call")
@limiter.limit(DEMO_RATE_LIMIT)
async def start_browser_demo(
    request: Request,
    data: BrowserDemoRequest,
):
    """
    يُنشئ demo session للمتصفح.

    data:
      industry: dental | legal | realty | general

    يُعيد:
      session_token: JWT مؤقت (30 دقيقة)
      websocket_url: للاتصال المباشر
      agent_config: {name, voice_id, greeting}

    يستخدم demo agent محدد مسبقاً لكل industry.
    يُسجل في demo_sessions table للـ analytics.
    """

@router.post("/phone-call")
@limiter.limit(DEMO_RATE_LIMIT)
async def start_phone_demo(
    request: Request,
    data: PhoneDemoRequest,
):
    """
    أقوى أداة تسويقية — نتصل بك الآن.

    data:
      phone: str  (رقم الزائر)
      industry: str

    يُطلق Twilio call من demo number.
    الوكيل يُعرّف نفسه: "Hi! This is a VoiceCore demo call. I'm Sarah,
    your AI receptionist. Ask me anything a dental patient might ask!"

    يُسجل: phone (hashed), industry, duration, outcome في demo_analytics.

    Rate limit مشدد: 2 مكالمات/IP/يوم
    """

@router.get("/session/{session_token}/status")
async def get_demo_status(session_token: str):
    """
    Polling للـ frontend — هل الـ demo session لا تزال صالحة؟
    """

@router.post("/session/{session_token}/end")
async def end_demo_session(
    session_token: str,
    data: DemoEndData,
):
    """
    ينهي الـ demo ويعرض signup CTA.
    يُسجل: was_satisfied, started_signup
    """


# ==================== Demo Agents (Pre-configured) ====================

DEMO_AGENTS = {
    "dental": {
        "name": "Sarah",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # ElevenLabs Rachel
        "greeting": "Hi! I'm Sarah, your AI dental receptionist demo. "
                    "Feel free to ask me about appointments, insurance, or anything "
                    "a dental patient might ask. How can I help you?",
        "system_prompt": DENTAL_DEMO_PROMPT,
    },
    "legal": {
        "name": "Alex",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",  # ElevenLabs Adam
        "greeting": "Hello, this is Alex, demonstrating VoiceCore for law firms. "
                    "Ask me about case intake, scheduling, or any typical client inquiry.",
        "system_prompt": LEGAL_DEMO_PROMPT,
    },
    "realty": {
        "name": "Jessica",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",  # ElevenLabs Elli
        "greeting": "Hi there! I'm Jessica, your real estate AI assistant demo. "
                    "Ask me about property showings, pricing, or buyer qualification.",
        "system_prompt": REALTY_DEMO_PROMPT,
    },
    "general": {
        "name": "Max",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",  # ElevenLabs Josh
        "greeting": "Hello! I'm Max, demonstrating VoiceCore's general receptionist. "
                    "Ask me anything a typical business caller might ask.",
        "system_prompt": GENERAL_DEMO_PROMPT,
    },
}
```

---

### `frontend/app/demo/page.tsx`

```tsx
"""
صفحة الـ Demo — أهم صفحة في كامل المشروع تجارياً.

Layout:
┌─────────────────────────────────────────────────────┐
│  VoiceCore Live Demo                                │
│  ─────────────────                                  │
│  "Hear your AI receptionist before you sign up"     │
│                                                     │
│  [Select Industry]:                                 │
│  [🦷 Dental] [⚖️ Legal] [🏠 Real Estate] [📱 General]  │
│                                                     │
│  ──────── Choose your demo method ──────────        │
│                                                     │
│  ┌─────────────────┐    ┌─────────────────────┐    │
│  │ 🎤 Try in       │    │ 📞 Call me now       │    │
│  │    Browser      │    │                     │    │
│  │ (No app needed) │    │ [+1 (555) ___-____] │    │
│  │                 │    │ [Call My Phone →]   │    │
│  │ [Start Now →]   │    │                     │    │
│  └─────────────────┘    └─────────────────────┘    │
│                                                     │
│  ── Browser Demo (shows when clicked) ────────────  │
│  ┌─────────────────────────────────────────────┐   │
│  │  🟢 Connected to Sarah (Dental Demo)        │   │
│  │                                             │   │
│  │  [Waveform animation]                       │   │
│  │                                             │   │
│  │  "Go ahead, speak now..."                   │   │
│  │                                             │   │
│  │  [🔴 End Demo]                              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  After demo ends:                                   │
│  "Liked what you heard? Start your free 14-day     │
│   trial — no credit card required."                │
│  [Start Free Trial →]                               │
└─────────────────────────────────────────────────────┘

Technical:
  - Browser demo يستخدم WebRTC (getUserMedia + WebSocket)
  - Waveform animation مع Web Audio API
  - Real-time transcription يظهر أسفل الـ waveform
  - بعد 5 دقائق → auto-end مع CTA

Colors:
  - الصفحة: zinc-950 background
  - Industry buttons: zinc-800 inactive, amber-500 active
  - Demo card: zinc-900 border zinc-700
  - Connected indicator: green-500 pulse animation
  - CTA button: amber-500 hover:amber-400
"""
```

---

## 🔧 المهمة 2: Free Trial System

### `backend/api/billing.py` — تحديث

```python
"""
أضف Trial System للـ billing.

Rules:
  - 14 يوم مجاناً
  - Business plan features
  - بدون بطاقة ائتمان
  - مكالمة تذكير بعد 10 أيام
  - Downgrade تلقائي ليوم 14+1
"""

@router.post("/trial/start")
async def start_free_trial(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يبدأ 14-day free trial.

    يتحقق من:
      - الشركة لم تستخدم trial من قبل (مرة واحدة فقط للأبد)
      - الشركة ليست على plan مدفوع

    يُحدّث:
      companies.plan = "business_trial"
      companies.trial_ends_at = now + 14 days
      companies.trial_used = True

    يُرسل:
      - welcome trial email
      - Celery task مجدول بعد 10 أيام (reminder)
      - Celery task مجدول بعد 14 أيام (downgrade to free)
    """

@router.get("/trial/status")
async def get_trial_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يُعيد:
      is_on_trial: bool
      days_remaining: int
      trial_ends_at: datetime
      can_start_trial: bool
    """


# في `backend/db/models.py` أضف للـ Company model:
# trial_ends_at = Column(DateTime, nullable=True)
# trial_used = Column(Boolean, default=False)
# onboarding_step = Column(Integer, default=0)
# onboarding_completed = Column(Boolean, default=False)
```

### `frontend/components/trial/TrialBanner.tsx`

```tsx
"""
Banner يظهر في كل صفحات الـ dashboard أثناء الـ trial.

يُظهر:
  - "Free Trial: X days remaining"
  - Progress bar (14 → 0)
  - زر "Upgrade Now" (amber-500)
  - زر X لإخفاء الـ banner مؤقتاً (24 ساعة)

إذا بقي 3 أيام أو أقل:
  - اللون يتغير للـ amber-600
  - "⚠️ Trial ending in X days — Upgrade to keep your agent live"

إذا انتهى الـ trial:
  - Modal لا يمكن إغلاقه: "Your trial has ended. Upgrade to continue."
"""
```

---

## 🔧 المهمة 3: Landing Page كاملة

### `frontend/app/page.tsx` — أعد الكتابة بالكامل

```tsx
"""
Landing page كاملة مع كل الـ sections.

DESIGN RULES:
  - Background: zinc-950 (dark throughout)
  - Primary accent: amber-500
  - Cards: zinc-900 border zinc-800
  - Font: Inter
  - Max width: 1200px centered
  - Mobile first (Tailwind responsive)
"""
```

**Section 1: Hero**

```tsx
"""
Hero Section:

┌──────────────────────────────────────────────────┐
│         [Navbar: Logo | Features | Pricing |      │
│          Verticals | Demo | Login | Start Trial]  │
│                                                   │
│    Your AI Receptionist.                         │
│    Working 24/7. Never tired.                    │
│                                                   │
│    Handle calls, book appointments, capture      │
│    leads — while you focus on what matters.      │
│                                                   │
│    [Start Free Trial →]  [Watch Demo ▶]          │
│                                                   │
│    ─────────────────────────────────────────     │
│    2,400+ calls handled today    98.3% accuracy  │
│    $0 credit card required       14-day free trial│
└──────────────────────────────────────────────────┘

Live Stats Counter:
  - "X calls handled today" — يزيد كل 10 ثوان (fake realtime لكن convincing)
  - يجلب الرقم الحقيقي من: GET /api/public/stats/today

Animated background: subtle grid pattern (CSS only)
"""
```

**Section 2: Demo مباشر في الصفحة**

```tsx
"""
Inline Demo Section (أهم section في الـ landing):

"Try it now — hear your AI receptionist"

┌────────────────────────────────────────────────┐
│  Select your industry:                         │
│  [🦷 Dental] [⚖️ Legal] [🏠 Real Estate] [📱 General] │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │   Sarah — Dental Receptionist Demo       │ │
│  │   ●●●●●● (waveform animation)           │ │
│  │   "Hi! I'm Sarah..."                    │ │
│  │   [🎤 Click to start talking]           │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  Or: [📞 Call my phone instead →]             │
└────────────────────────────────────────────────┘
"""
```

**Section 3: How It Works**

```tsx
"""
3 خطوات بسيطة:

1. Sign up (30 seconds)
2. Configure your agent (10 minutes)
3. Go live (instant)

كل خطوة: icon + title + description + animated arrow
"""
```

**Section 4: Features Grid**

```tsx
"""
6 features في grid:

🧠 Remembers Customers    — "Your AI knows every returning caller"
🌍 Speaks 50+ Languages   — "Auto-detects and responds in customer's language"
📅 Books Appointments     — "Syncs with Google Calendar, Outlook, Calendly"
😊 Detects Emotions       — "Escalates frustrated customers automatically"
📊 Full Analytics         — "Sentiment, intent, conversion — all tracked"
🔒 HIPAA Compliant        — "Safe for medical, legal, financial industries"
"""
```

**Section 5: Industry Verticals**

```tsx
"""
3 cards بنقر على كل واحدة تفتح details:

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  🦷 Dental   │ │  ⚖️ Legal    │ │  🏠 Realty   │
│  DentalVoice │ │  LegalVoice  │ │  RealtyVoice │
│              │ │              │ │              │
│  $399/mo    │ │  $599/mo    │ │  $299/mo    │
│              │ │              │ │              │
│  - Insurance │ │  - Case      │ │  - Buyer     │
│    verify    │ │    intake    │ │    qualify   │
│  - Emergency │ │  - Conflict  │ │  - Showings  │
│    detect    │ │    check     │ │  - Hot leads │
│              │ │              │ │              │
│ [Learn More] │ │ [Learn More] │ │ [Learn More] │
└──────────────┘ └──────────────┘ └──────────────┘
"""
```

**Section 6: ROI Calculator (الأهم للـ conversion)**

```tsx
"""
ROI Calculator Interactive:

"Calculate your ROI"

Sliders:
  Monthly calls received: [0 ────●──────── 5000]  → 500
  Avg call value ($):     [0 ────●──────── 10000] → 200
  Current miss rate (%):  [0 ────────●──── 100]   → 35%

Results (يتحدث في real-time مع الـ sliders):
┌────────────────────────────────────────┐
│  Currently losing:    $35,000/month    │
│  VoiceCore cost:      $899/month       │
│  Your monthly ROI:    $34,101          │
│  Payback period:      < 1 day          │
│                                        │
│  [Start Free Trial — Risk Free →]      │
└────────────────────────────────────────┘

الحسابات:
  lost_revenue = calls * miss_rate * call_value
  roi = lost_revenue - plan_cost
  payback_days = plan_cost / (lost_revenue / 30)

يُظهر plan المناسب تلقائياً بناءً على عدد المكالمات.
"""
```

**Section 7: Testimonials**

```tsx
"""
3 testimonials (placeholder حقيقي الشكل):

"VoiceCore handled 847 calls last month.
 We recovered $23,000 in appointments we would have missed."
— Dr. Michael Chen, Bright Smile Dental, Chicago

"Our intake process went from 3 days to 4 hours.
 The AI catches everything — conflicts, urgencies, all of it."
— Sarah Kim, Kim & Associates Law Firm

"Closed 12 extra deals last quarter from leads VoiceCore captured
 when we were showing other properties."
— James Rodriguez, Premier Realty Group

كل testimonial: avatar (initials circle), name, company, city, rating (5 stars)
"""
```

**Section 8: Pricing**

```tsx
"""
Pricing Section مع toggle شهري/سنوي:

4 plans مع feature comparison.
Most popular: Business (amber border + badge)
Annual: 20% off مع strikethrough للسعر الأصلي

أسفل كل plan: "Start 14-Day Free Trial"

أسفل الـ pricing:
"All plans include: 24/7 uptime, SSL security, cancel anytime"
"""
```

**Section 9: FAQ**

```tsx
"""
8 أسئلة شائعة Accordion:

Q: How long does setup take?
Q: Do I need technical knowledge?
Q: Can the AI handle multiple calls simultaneously?
Q: What happens when the AI can't answer?
Q: Is it HIPAA compliant?
Q: Can I keep my existing phone number?
Q: What languages are supported?
Q: Can I cancel anytime?
"""
```

**Section 10: Final CTA**

```tsx
"""
Big CTA Section:

"Ready to never miss a call again?"

[Start Free Trial — No Credit Card Required →]

"Join 500+ businesses already using VoiceCore"
(logos row — placeholder companies)
"""
```

---

## 🔧 المهمة 4: Pricing Page منفصلة

### `frontend/app/pricing/page.tsx`

```tsx
"""
صفحة Pricing كاملة ومستقلة (للـ SEO + ads landing).

يشمل كل شيء في pricing section من الـ landing + أكثر:
  - Feature comparison table مفصلة (كل feature مع checkmarks)
  - FAQ عن الأسعار فقط
  - "Talk to Sales" للـ Enterprise
  - Volume discount calculator

Feature Comparison Table:
                         Free  Starter  Business  Enterprise
Monthly calls             50    500     2,000      Unlimited
AI agents                  1      3        10      Unlimited
Languages                  3     10        50+     Unlimited
Voice customization        ✗      ✓         ✓           ✓
CRM integration            ✗      ✗         ✓           ✓
Calendar integration       ✗      ✓         ✓           ✓
Sentiment analysis         ✓      ✓         ✓           ✓
Custom system prompt       ✗      ✓         ✓           ✓
Email notifications        ✓      ✓         ✓           ✓
SMS alerts                 ✗      ✗         ✓           ✓
Analytics dashboard        Basic  Full     Full    Advanced
HIPAA compliance           ✗      ✗         ✓           ✓
White-label                ✗      ✗         ✗           ✓
Dedicated support          ✗      ✗         ✗           ✓
SLA uptime guarantee       ✗      ✗      99.9%       99.99%
"""
```

---

## 🔧 المهمة 5: ROI Calculator Page

### `frontend/app/roi/page.tsx`

```tsx
"""
صفحة ROI Calculator مستقلة + مفصلة.

3 tabs:
  Tab 1: Basic Calculator (sliders)
  Tab 2: Industry Calculator (حسب industry)
  Tab 3: Detailed Breakdown (جدول كامل)

Tab 2 — Industry Calculator:
  Dental:
    Input: أعداد المرضى الجدد/شهر، فاتورة الجلسة الأولى
    Output: عائد توقعي من recovery missed calls

  Legal:
    Input: قضايا/شهر، متوسط قيمة القضية
    Output: leads من intake calls + revenue

  Realty:
    Input: leads/شهر، commission rate، avg home price
    Output: deals من hot leads + commission

كل نتيجة مع زر:
"Get this ROI with 14-day free trial →"

يُحفظ الأرقام في URL params للـ sharing.
"""
```

---

## 🔧 المهمة 6: HIPAA Compliance Layer

### `backend/services/compliance_service.py`

```python
"""
HIPAA Compliance Service.

هذا ليس مجرد صفحة — هو نظام حقيقي يُطبق في كل المشروع.
"""

class HIPAAComplianceService:

    # Encryption
    ENCRYPTION_ALGORITHM = "AES-256-GCM"

    def encrypt_pii(self, data: str) -> str:
        """
        تشفير AES-256-GCM لكل PII:
        - أسماء المرضى
        - أرقام الهواتف (في الـ transcripts)
        - تواريخ الميلاد
        - أرقام التأمين
        يستخدم: cryptography library
        Key من: settings.ENCRYPTION_KEY (64-char hex)
        """

    def decrypt_pii(self, encrypted_data: str) -> str:
        """فك التشفير"""

    def mask_phone_in_transcript(self, transcript: str) -> str:
        """
        يستبدل أرقام الهواتف في الـ transcript بـ [PHONE REDACTED]
        Regex يكتشف: +1XXXXXXXXXX, (XXX) XXX-XXXX, XXX-XXX-XXXX
        يُطبق على كل transcript قبل حفظه في DB
        """

    def mask_ssn_in_transcript(self, transcript: str) -> str:
        """يستبدل SSN بـ [SSN REDACTED]"""

    def mask_insurance_in_transcript(self, transcript: str) -> str:
        """يستبدل insurance member IDs بـ [INSURANCE ID REDACTED]"""

    async def log_phi_access(
        self, user_id: int, company_id: int,
        record_type: str, record_id: int, action: str
    ) -> None:
        """
        HIPAA requirement: log كل وصول لـ PHI.
        يُحفظ في: phi_access_logs table
        يُحتفظ به: 6 سنوات (HIPAA requirement)
        """

    async def generate_baa_document(
        self, company_name: str, company_email: str
    ) -> str:
        """
        يُولّد Business Associate Agreement (BAA) PDF.
        Template موجود في: backend/templates/baa_template.txt
        يشمل: company name, date, VoiceCore LLC info
        يُوقَّع رقمياً (checkbox acceptance)
        """

    async def validate_data_retention(self, company_id: int) -> None:
        """
        HIPAA: data retention policy.
        يحذف recordings أقدم من 90 يوم (قابل للتغيير في settings)
        يحذف transcripts أقدم من 1 سنة
        يحتفظ بـ call metadata للـ 7 سنوات
        يُشغَّل كـ Celery task كل يوم
        """


class TranscriptPrivacyFilter:
    """
    يُطبق على كل transcript قبل الحفظ وعند العرض.
    """

    def sanitize_for_storage(self, transcript: str) -> str:
        """
        يُطبق كل الـ masking functions.
        يُعيد transcript آمن للحفظ في DB.
        """

    def sanitize_for_display(
        self, transcript: str, viewer_role: str
    ) -> str:
        """
        viewer_role = "staff" → يُخفي كل PII
        viewer_role = "admin" → يُظهر masked version
        viewer_role = "super_admin" → يُظهر كل شيء
        """
```

### جدول جديد — أضف لـ `models.py`

```python
class PHIAccessLog(Base):
    """HIPAA-required audit log for PHI access"""
    __tablename__ = "phi_access_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    record_type = Column(String(50))   # call/customer/transcript
    record_id = Column(Integer)
    action = Column(String(50))        # view/download/export/delete
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    # لا يُحذف أبداً — 6 سنوات minimum retention


class BAA(Base):
    """Business Associate Agreements"""
    __tablename__ = "baas"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True)
    accepted_by_user_id = Column(Integer, ForeignKey("users.id"))
    accepted_at = Column(DateTime)
    ip_address = Column(String(45))
    baa_version = Column(String(20), default="1.0")
    document_url = Column(String(500))
```

---

## 🔧 المهمة 7: Legal Pages

### `frontend/app/legal/terms/page.tsx`

```tsx
"""
Terms of Service — نص قانوني حقيقي (وليس placeholder).

الأقسام:
1. Acceptance of Terms
2. Description of Service
3. Account Registration
4. Subscription and Payment
   - Billing cycles
   - Refund policy (no refunds on monthly, pro-rata on annual cancellation)
   - Failed payment grace period: 7 days
5. Usage Limits and Fair Use
6. Prohibited Uses
7. Privacy and Data Protection
8. Call Recording and Transcription Notice
   - Users must comply with local wiretapping laws
   - Obligation to inform callers
9. Intellectual Property
10. Indemnification
11. Limitation of Liability (IMPORTANT: cap at 3 months subscription)
12. Termination
13. Changes to Terms
14. Governing Law: State of Delaware, USA
15. Contact Information

Format:
  - Dark background (zinc-950)
  - Last updated date واضح في الأعلى
  - Table of contents مع anchor links
  - Print-friendly button
"""
```

### `frontend/app/legal/privacy/page.tsx`

```tsx
"""
Privacy Policy — GDPR + CCPA + HIPAA compliant.

الأقسام:
1. Information We Collect
   - Account data
   - Call data (recordings, transcripts)
   - Usage data
   - Technical data
2. How We Use Information
3. Data Sharing (we NEVER sell data)
4. Data Storage and Security
   - AES-256-GCM encryption
   - SOC2 Type II (in progress)
5. Data Retention
   - Calls: 90 days (configurable)
   - Account data: until deletion request
6. Your Rights (GDPR Article 17 — right to deletion)
7. California Residents (CCPA)
8. Children's Privacy (no users under 18)
9. Contact for Privacy Requests: privacy@voicecore.ai
10. HIPAA Section (for healthcare customers)

أضف: GDPR compliance badge, CCPA badge
"""
```

### `frontend/app/legal/hipaa/page.tsx`

```tsx
"""
HIPAA Compliance Page — أهم صفحة للعملاء في الصحة والقانون.

الأقسام:
1. HIPAA Overview — ما هو وليش مهم
2. How VoiceCore Protects PHI
   - Encryption at rest (AES-256-GCM)
   - Encryption in transit (TLS 1.3)
   - Access controls and audit logging
   - Employee training and policies
3. Business Associate Agreement (BAA)
   - ما هو الـ BAA ولماذا تحتاجه
   - [Sign BAA Online →] button
4. Data Center Security
   - AWS data centers (us-east-1 and us-west-2)
   - SOC 2 Type II certified infrastructure
5. Breach Notification Policy
6. Covered Entities FAQ
7. Contact HIPAA Officer: hipaa@voicecore.ai

Design:
  - Trust badges: HIPAA, SOC2 (coming soon), SSL
  - Green checkmarks للـ compliance items
  - CTA: "Get HIPAA-Ready in Minutes"
"""
```

---

## 🔧 المهمة 8: Public API Endpoints للـ Landing Page

### `backend/api/public/router.py` — تحديث

```python
"""
Public endpoints — بدون authentication.
"""

@router.get("/stats/today")
@cache(expire=300)  # cache 5 دقائق
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """
    يُعيد إحصائيات حقيقية للـ landing page.
    {
        "calls_today": 2847,
        "calls_total": 1250000,
        "companies_active": 523,
        "uptime_percentage": 99.97
    }
    """

@router.post("/roi/calculate")
async def calculate_roi(data: ROICalculatorInput):
    """
    حساب ROI بدون authentication.
    يُسجل الـ calculation في analytics (بدون PII).
    يُعيد: monthly_savings, yearly_savings, payback_days, recommended_plan
    """

@router.get("/pricing")
async def get_pricing():
    """
    Returns all plans with features.
    Cached — لا يحتاج DB query.
    """

@router.post("/demo/request-call")
@limiter.limit("2/day")
async def request_demo_call(request: Request, data: DemoCallRequest):
    """
    Visitor يطلب call demo.
    rate limit مشدد جداً.
    """

@router.post("/contact")
@limiter.limit("3/hour")
async def contact_sales(request: Request, data: ContactRequest):
    """
    Contact form من الـ landing page.
    يُرسل email للـ sales team.
    """
```

---

## 🔧 المهمة 9: Analytics للـ Landing Page

### أضف للـ `backend/db/models.py`

```python
class DemoSession(Base):
    """تتبع كل demo session"""
    __tablename__ = "demo_sessions"

    id = Column(Integer, primary_key=True)
    session_token = Column(String(255), unique=True)
    industry = Column(String(50))
    demo_type = Column(String(20))  # browser/phone
    ip_address = Column(String(45))  # hashed للـ privacy
    country = Column(String(50))
    duration_seconds = Column(Integer)
    converted_to_signup = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketingEvent(Base):
    """تتبع الأحداث التسويقية"""
    __tablename__ = "marketing_events"

    id = Column(Integer, primary_key=True)
    event = Column(String(100))  # roi_calculated, demo_started, pricing_viewed
    properties = Column(JSON)
    session_id = Column(String(255))
    ip_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔧 المهمة 10: Sign BAA Flow

### `backend/api/billing.py` — أضف

```python
@router.post("/baa/sign")
async def sign_baa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يُسجل قبول العميل للـ BAA.

    يتحقق من:
      - الشركة على Business أو Enterprise plan
      - لم يُوقّع BAA من قبل

    يُنشئ:
      - BAA record في DB مع IP + timestamp
      - PDF وثيقة BAA ويحفظها في storage

    يُرسل:
      - Email مع نسخة الـ BAA للعميل

    يُحدّث:
      - companies.hipaa_baa_signed = True
      - companies.hipaa_baa_signed_at = now
    """

@router.get("/baa/document")
async def download_baa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """يُحمّل نسخة الـ BAA الموقّعة"""
```

---

## ✅ معايير الانتهاء

**Demo:**
- [ ] Demo يعمل من المتصفح بدون login (WebRTC)
- [ ] Phone demo يُطلق مكالمة حقيقية
- [ ] Rate limiting يعمل (5/hour)

**Trial:**
- [ ] Signup بدون بطاقة يعطي 14 يوم Business trial
- [ ] Trial banner يظهر مع countdown
- [ ] Downgrade تلقائي بعد انتهاء الـ trial
- [ ] Trial reminder email بعد 10 أيام

**Landing Page:**
- [ ] ROI Calculator يعمل real-time
- [ ] Live stats counter من DB حقيقي
- [ ] Mobile responsive (اختبر على 375px)
- [ ] Page load < 3 ثوان

**Legal:**
- [ ] Terms of Service صفحة كاملة
- [ ] Privacy Policy صفحة كاملة
- [ ] HIPAA page مع BAA signing flow

**HIPAA:**
- [ ] AES-256 encryption على الـ transcripts
- [ ] Phone numbers masked في الـ transcripts
- [ ] PHI access log يُسجل كل وصول
- [ ] BAA flow يعمل ويُرسل PDF

---

## ⚠️ قواعد لا تُكسر

1. **Demo** يجب أن يعمل حتى لو فشلت الـ DB (fallback responses)
2. **ROI Calculator** يعمل 100% client-side — لا API calls
3. **Legal pages** يجب أن تُظهر "Last updated: [date]" واضح
4. **HIPAA** — لا PII في أي log، أي error message، أي Redis key بشكل صريح
5. **BAA** — لا تُفعّل HIPAA features قبل قبول الـ BAA
6. **Trial** — يُستخدم مرة واحدة فقط للأبد (حتى لو أُلغي الحساب وأُعيد)
7. **Demo rate limit** — مشدد جداً لمنع abuse + Twilio cost

---

*PROMPT 03/03 — VoiceCore Build System*
*المرحلة: Commercial — اجعله يبيع*
*الترتيب: PROMPT_01 → PROMPT_02 → PROMPT_03*
