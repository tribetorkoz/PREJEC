# 🚀 PROMPT 02 — ONBOARDING & NOTIFICATIONS & EMAIL SYSTEM
## VoiceCore — المهمة الثانية: اجعله موثوقاً

---

## 🎯 هدفك من هذا الملف

تنفيذ **3 أنظمة** تحول المنتج من "يعمل تقنياً" إلى "يمكن بيعه":
1. Onboarding Wizard كامل (5 خطوات) — من التسجيل لأول مكالمة حقيقية
2. Notification System — الشركات تعلم بكل ما يحدث
3. Email System — تسلسل كامل من أول يوم حتى retention

**لا تبدأ هذا الملف قبل إتمام PROMPT_01 بالكامل.**

---

## 📋 قائمة الملفات

```
backend/
├── api/
│   ├── onboarding.py          ← أنشئ من صفر
│   └── notifications.py       ← أنشئ من صفر
├── services/
│   ├── email_service.py       ← أنشئ من صفر (SendGrid)
│   ├── notification_service.py← أنشئ من صفر
│   └── sms_service.py         ← أنشئ من صفر (Twilio SMS)
├── tasks/
│   ├── __init__.py
│   ├── email_tasks.py         ← أنشئ من صفر (Celery)
│   ├── notification_tasks.py  ← أنشئ من صفر
│   └── reminder_tasks.py      ← أنشئ من صفر
└── db/
    └── models.py              ← أضف جداول جديدة

frontend/
├── app/
│   └── onboarding/
│       ├── page.tsx           ← أعد كتابة كاملة
│       ├── steps/
│       │   ├── step1-company.tsx
│       │   ├── step2-agent.tsx
│       │   ├── step3-voice.tsx
│       │   ├── step4-phone.tsx
│       │   └── step5-test.tsx
│       └── components/
│           ├── ProgressBar.tsx
│           ├── VoicePreview.tsx
│           └── TestCallWidget.tsx
└── components/
    └── notifications/
        ├── NotificationBell.tsx
        └── NotificationPanel.tsx
```

---

## 🔧 المهمة 1: Onboarding Wizard

### الخلفية — `backend/api/onboarding.py`

```python
"""
5-Step Onboarding API — يأخذ العميل من التسجيل لأول مكالمة حقيقية.

المبدأ: كل خطوة تُحفظ فوراً. إذا أغلق المستخدم المتصفح → يرجع من حيث توقف.
"""

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])

# ==================== STEP 1: Company Info ====================

@router.post("/step1/company")
async def save_company_info(
    data: CompanyOnboardingStep1,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يحفظ: company name, industry, phone, timezone, website
    يُحدّث: companies.onboarding_step = 1
    يرجع: company_id + next_step URL
    """

# ==================== STEP 2: Agent Setup ====================

@router.post("/step2/agent")
async def setup_agent(
    data: AgentOnboardingStep2,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يحفظ: agent name, language, custom instructions, business hours
    يُنشئ: Agent record في DB
    يُحدّث: onboarding_step = 2

    data يشمل:
    - agent_name: str  (مثال: "Sarah", "Alex")
    - language: str    (en/ar/fr/es/auto)
    - business_hours: Dict  ({"monday": {"open": "09:00", "close": "18:00"}, ...})
    - custom_instructions: str  (ماذا يفعل الوكيل)
    - industry_vertical: Optional[str]  (dental/legal/realty/None)
    """

# ==================== STEP 3: Voice Selection ====================

@router.get("/step3/voices")
async def get_available_voices(
    language: str = "en",
    current_user: User = Depends(get_current_user),
):
    """
    يجلب قائمة أصوات ElevenLabs المتاحة.
    مرتبة حسب: اللغة أولاً، ثم الجنس، ثم الاسم.
    يُخزّن في Redis cache لمدة ساعة.
    """

@router.post("/step3/voice/preview")
async def preview_voice(
    data: VoicePreviewRequest,
    current_user: User = Depends(get_current_user),
):
    """
    يولد عينة صوتية قصيرة (5-10 ثوانٍ) لأي صوت.
    النص الثابت: "Hello, thank you for calling. How can I help you today?"
    يُعيد: audio/mpeg bytes
    يُخزّن الـ preview في Redis لمدة 24 ساعة (لا يعيد التوليد)
    """

@router.post("/step3/voice/select")
async def select_voice(
    data: VoiceSelectionData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يحفظ voice_id المختار على الـ Agent.
    يُحدّث: onboarding_step = 3
    """

# ==================== STEP 4: Phone Number ====================

@router.get("/step4/available-numbers")
async def get_available_phone_numbers(
    area_code: Optional[str] = None,
    country: str = "US",
    current_user: User = Depends(get_current_user),
):
    """
    يجلب أرقام متاحة من Twilio.
    يفلتر بـ area_code إذا طُلب.
    يُعيد: قائمة أرقام مع السعر الشهري.
    """

@router.post("/step4/provision-number")
async def provision_phone_number(
    data: PhoneProvisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    الأهم في كل الـ onboarding.

    يجب أن:
    1. يشتري الرقم من Twilio
    2. يضبط webhook URL تلقائياً على Twilio:
       Voice URL: {base_url}/api/v1/voice/inbound
       Status Callback: {base_url}/api/webhooks/twilio/status
    3. يحفظ الرقم على الشركة في DB
    4. يُحدّث: onboarding_step = 4

    إذا فشل شراء الرقم → يرجع error واضح مع سبب.
    """

@router.post("/step4/use-existing-number")
async def configure_existing_number(
    data: ExistingNumberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    إذا كان لدى العميل رقم Twilio موجود.
    يتحقق من ملكية الرقم.
    يضبط الـ webhooks تلقائياً.
    """

# ==================== STEP 5: Test Call ====================

@router.post("/step5/initiate-test-call")
async def initiate_test_call(
    data: TestCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    أهم خطوة — يسمح للعميل بالاتصال بوكيله قبل الإطلاق الرسمي.

    Flow:
    1. التحقق من أن الشركة لديها: agent + phone number + voice
    2. إطلاق مكالمة Twilio من رقم الشركة إلى data.test_phone
    3. المكالمة تكون مع الوكيل الحقيقي (ليس mock)
    4. حفظ test_call_sid في Redis
    5. إرجاع call_sid للـ frontend يراقب به الحالة

    إذا فشل → خطأ واضح مع تعليمات تصحيح.
    """

@router.get("/step5/test-call-status/{call_sid}")
async def get_test_call_status(
    call_sid: str,
    current_user: User = Depends(get_current_user),
):
    """
    polling endpoint — frontend يسأل كل 2 ثانية.
    يُعيد: initiated/ringing/in-progress/completed/failed
    """

@router.post("/step5/complete-onboarding")
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    يُكمل الـ onboarding ويُعلم الشركة جاهزة.
    يُحدّث: companies.onboarding_completed = True
    يُرسل: welcome email
    يُطلق: "onboarding_completed" event للـ analytics
    يُعيد: redirect URL للـ dashboard
    """
```

---

### الواجهة — `frontend/app/onboarding/`

**المبدأ العام للـ Wizard:**
- Progress bar في الأعلى يُظهر الخطوة الحالية
- كل خطوة تحفظ بمجرد النقر على "Next" (لا "Save" منفصلة)
- إذا أُغلق المتصفح → يرجع من آخر خطوة محفوظة
- الخلفية: `zinc-950`، الكروت: `zinc-900`

**`step5-test.tsx` — الأهم:**

```tsx
"""
خطوة الاختبار — تجربة حقيقية قبل الإطلاق.

الواجهة:
  1. مربع نص لإدخال رقم الهاتف للاختبار
  2. زر "Call Me Now" — يطلق المكالمة
  3. Animated phone icon مع حالة: Calling → Ringing → Connected → Done
  4. بعد انتهاء المكالمة: "How was the experience?" مع تقييم 1-5 نجوم
  5. زر "Go Live" إذا كان راضياً، أو "Adjust Settings" للرجوع

يجب poll كل 2 ثانية لـ /api/v1/onboarding/step5/test-call-status
يُظهر success animation عند Connected
"""
```

**`VoicePreview.tsx`:**

```tsx
"""
مشغل صوتي لمعاينة الأصوات قبل الاختيار.

يُظهر:
  - اسم الصوت + لغته + جنسه
  - زر Play/Stop
  - Loading spinner أثناء جلب الـ audio
  - Selected state واضح (amber-500 border)
  - يُشغل صوتاً واحداً فقط في نفس الوقت (يوقف السابق)
"""
```

---

## 🔧 المهمة 2: Notification System

### `backend/services/notification_service.py`

```python
"""
Notification System — الشركات تعلم بكل ما يهمها فوراً.

القنوات المدعومة:
  1. Email (SendGrid) — للأحداث المهمة
  2. SMS (Twilio) — للطوارئ والعملاء الغاضبين
  3. Webhook — للشركات التي تريد Zapier/Slack

الأحداث التي تُرسل notification:
  ANGRY_CUSTOMER      → email + sms فورياً
  MISSED_CALL         → email خلال 5 دقائق
  HOT_LEAD (realty)   → email + sms فورياً
  EMERGENCY (dental)  → sms فورياً
  DAILY_SUMMARY       → email كل يوم 8 صباحاً
  WEEKLY_REPORT       → email كل اثنين
  CALLS_LIMIT_90%     → email تحذيري
  CALLS_LIMIT_100%    → email + disable agent
  PAYMENT_FAILED      → email
"""

class NotificationService:

    async def notify(
        self,
        company_id: int,
        event: NotificationEvent,
        data: dict,
        priority: str = "normal"  # normal/urgent/critical
    ) -> bool:
        """
        الـ dispatcher الرئيسي.
        يجلب notification preferences للشركة.
        يوزع على القنوات المناسبة بناءً على event + preferences.
        يُسجل كل notification في DB.
        """

    async def notify_angry_customer(
        self, company_id: int, call_data: dict
    ) -> bool:
        """
        فوري — priority: critical
        Email: "⚠️ Angry Customer Alert — Immediate Attention Required"
        SMS: "VoiceCore Alert: Angry customer call just ended. Check dashboard."
        يشمل: رقم العميل، وقت المكالمة، آخر ما قاله، رابط التسجيل
        """

    async def notify_missed_call(
        self, company_id: int, caller_phone: str
    ) -> bool:
        """
        بعد 5 دقائق من المكالمة الفائتة (Celery delayed task)
        Email: "📞 Missed Call from [phone]"
        يُذكّر بالاتصال مرة ثانية
        """

    async def send_daily_summary(self, company_id: int) -> bool:
        """
        كل يوم 8:00 صباحاً بتوقيت الشركة.
        يشمل:
        - إجمالي المكالمات أمس
        - توزيع المشاعر
        - المواعيد المحجوزة
        - المكالمات الفائتة
        - أبرز حدث
        """

    async def send_weekly_report(self, company_id: int) -> bool:
        """
        كل اثنين.
        يشمل كل شيء في الـ daily + trends مقارنة بالأسبوع السابق.
        """

    async def check_and_notify_limits(self, company_id: int) -> None:
        """
        يُشغَّل بعد كل مكالمة.
        90% من الحد → email تحذيري
        100% → email + تعطيل الوكيل مؤقتاً + email للعميل عن الترقية
        """
```

---

### جداول جديدة في DB — أضف لـ `backend/db/models.py`

```python
class Notification(Base):
    """سجل كل notification أُرسلت"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    channel = Column(String(20))  # email/sms/webhook
    recipient = Column(String(255))
    subject = Column(String(500))
    content = Column(Text)
    status = Column(String(20), default="sent")  # sent/failed/bounced
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationPreferences(Base):
    """تفضيلات الإشعارات لكل شركة"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True)
    email_angry_customer = Column(Boolean, default=True)
    sms_angry_customer = Column(Boolean, default=False)
    email_missed_call = Column(Boolean, default=True)
    email_daily_summary = Column(Boolean, default=True)
    email_weekly_report = Column(Boolean, default=True)
    webhook_url = Column(String(500))
    webhook_events = Column(JSON, default=[])  # list of events
    notification_email = Column(String(255))  # إذا مختلف عن account email
    notification_phone = Column(String(50))   # للـ SMS
    timezone = Column(String(100), default="America/New_York")
    daily_summary_time = Column(String(5), default="08:00")
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

---

## 🔧 المهمة 3: Email System

### `backend/services/email_service.py`

```python
"""
Email Service بـ SendGrid.
كل email له template محدد — لا strings عشوائية في الكود.
"""

class EmailService:

    # ==================== Transactional Emails ====================

    async def send_welcome_email(
        self, to_email: str, company_name: str, user_name: str
    ) -> bool:
        """
        يُرسل فور إكمال التسجيل.
        Subject: "Welcome to VoiceCore, [Name]! Your AI receptionist is ready."
        يشمل:
          - رابط الـ onboarding
          - فيديو تعليمي قصير (YouTube link)
          - رابط الـ documentation
          - "Setup takes only 30 minutes" message
        """

    async def send_onboarding_completed_email(
        self, to_email: str, company_name: str,
        phone_number: str, agent_name: str
    ) -> bool:
        """
        يُرسل بعد إكمال الـ onboarding.
        Subject: "🎉 [Company] is now live on VoiceCore!"
        يشمل:
          - رقم الهاتف المخصص
          - اسم الوكيل
          - رابط الـ dashboard
          - "Share your new number" button
        """

    async def send_call_confirmation(
        self, to_email: str, caller_phone: str,
        appointment_details: dict
    ) -> bool:
        """
        يُرسل للعميل بعد حجز موعد عبر الوكيل.
        Subject: "Your appointment is confirmed ✓"
        """

    async def send_payment_failed_email(
        self, to_email: str, company_name: str,
        amount: float, retry_date: datetime
    ) -> bool:
        """
        Subject: "Action Required: Payment failed for VoiceCore"
        يشمل: رابط تحديث بيانات الدفع + تاريخ المحاولة التالية
        Grace period: الوكيل يستمر 7 أيام
        """

    async def send_subscription_cancelled_email(
        self, to_email: str, company_name: str
    ) -> bool:
        """
        Subject: "Your VoiceCore subscription has been cancelled"
        يشمل: exit survey link + "Reactivate" CTA
        """

    # ==================== Alert Emails ====================

    async def send_angry_customer_alert(
        self, to_email: str, company_name: str,
        call_data: dict
    ) -> bool:
        """
        Subject: "⚠️ Angry Customer Alert — [Company]"
        يشمل:
          - وقت المكالمة
          - رقم العميل (masked: +1-XXX-XXX-1234)
          - آخر ما قاله العميل (quote من الـ transcript)
          - زر "Listen to Recording"
          - زر "Call Back Now"
        """

    async def send_daily_summary_email(
        self, to_email: str, company_name: str,
        stats: DailySummaryStats
    ) -> bool:
        """
        Subject: "📊 Your VoiceCore Daily Summary — [Date]"
        Template HTML كامل مع:
          - 4 KPI cards (calls, duration, sentiment, resolved)
          - Sentiment breakdown bar chart (HTML/CSS فقط)
          - List of missed calls مع زر callback
          - "This week so far" mini stats
        """

    async def send_weekly_report_email(
        self, to_email: str, company_name: str,
        report: WeeklyReport
    ) -> bool:
        """
        Subject: "📈 Your VoiceCore Weekly Report"
        Template أكثر تفصيلاً + trends + مقارنة بالأسبوع السابق
        """

    # ==================== Retention Emails (Celery Tasks) ====================

    async def send_day3_checkin_email(
        self, to_email: str, company_name: str, calls_so_far: int
    ) -> bool:
        """
        اليوم 3 بعد onboarding.
        Subject: "How is [Agent Name] doing?"
        إذا calls_so_far == 0: "Something not working? Let us help."
        إذا calls_so_far > 0: "Your agent has handled X calls already!"
        """

    async def send_churn_risk_email(
        self, to_email: str, company_name: str,
        days_inactive: int
    ) -> bool:
        """
        إذا لم يكن هناك مكالمات لـ 7 أيام.
        Subject: "Is everything OK? We noticed [Agent] has been quiet"
        يعرض: help call booking + troubleshooting guide
        """

    # ==================== Internal ====================

    def _render_template(
        self, template_name: str, context: dict
    ) -> str:
        """
        يُحضّر HTML من Jinja2 templates.
        Templates موجودة في: backend/email_templates/
        كل template تدعم: light mode + mobile responsive
        """

    async def _send_via_sendgrid(
        self, to: str, subject: str, html: str,
        text: str, from_name: str = "VoiceCore"
    ) -> bool:
        """
        يرسل عبر SendGrid API.
        إذا فشل → يُسجل الخطأ ويُضيف للـ retry queue (Celery)
        """
```

---

### `backend/tasks/email_tasks.py`

```python
"""
Celery tasks للـ emails المجدولة والمتكررة.
"""

from celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, to: str, template: str, context: dict):
    """
    Generic email task مع retry.
    exponential backoff: 1min, 5min, 15min
    """

@celery_app.task
def send_daily_summaries():
    """
    يُشغَّل كل يوم 8:00 صباحاً UTC.
    يجلب كل الشركات بتوقيتاتها المختلفة.
    يرسل لكل شركة في الوقت الصحيح لمنطقتها الزمنية.
    """

@celery_app.task
def send_weekly_reports():
    """يُشغَّل كل اثنين 8:00 صباحاً UTC."""

@celery_app.task
def check_inactive_companies():
    """
    يُشغَّل كل يوم.
    يجد الشركات التي لم يكن لها مكالمات 7+ أيام.
    يرسل churn risk email.
    """

@celery_app.task
def send_day3_checkins():
    """
    يُشغَّل كل يوم.
    يجد الشركات في يومها الثالث بعد onboarding.
    يرسل checkin email.
    """

@celery_app.task
def retry_failed_notifications():
    """
    يُشغَّل كل 30 دقيقة.
    يُعيد إرسال notifications الفاشلة.
    يحاول 3 مرات max ثم يُعلم الـ admin.
    """
```

---

### `backend/tasks/reminder_tasks.py`

```python
"""
WhatsApp / SMS reminders للعملاء عبر الوكيل.
"""

@celery_app.task
def send_appointment_reminders():
    """
    يُشغَّل كل ساعة.
    يجد كل المواعيد التي ستكون خلال 24 ساعة.
    يرسل WhatsApp reminder أو SMS.

    نص الرسالة:
    "Hi [Name]! Reminder: You have an appointment at [Company] tomorrow
     at [Time]. Reply 'C' to confirm or 'R' to reschedule.
     Powered by VoiceCore."
    """

@celery_app.task
def process_reminder_replies():
    """
    يعالج ردود العملاء على الـ reminders.
    'C' → تأكيد في DB
    'R' → يُعلم الشركة لإعادة الجدولة
    """
```

---

## 🔧 المهمة 4: Notification Bell في الـ Dashboard

### `frontend/components/notifications/NotificationBell.tsx`

```tsx
"""
Notification Bell في header الـ dashboard.

يُظهر:
  - Bell icon مع badge عدد الإشعارات غير المقروءة
  - عند النقر: Dropdown panel مع الإشعارات
  - كل إشعار له: icon حسب النوع، نص، وقت
  - Poll كل 30 ثانية لإشعارات جديدة
  - Mark as read عند رؤيتها

أنواع الإشعارات مع ألوانها:
  ⚠️ angry_customer    → red-500
  📞 missed_call       → amber-500
  🎯 hot_lead          → green-500
  🚨 emergency         → red-600 (flashing)
  📊 daily_summary     → blue-500
  💳 payment_issue     → orange-500
"""
```

---

## 🔧 المهمة 5: Notification Settings Page

### `frontend/app/dashboard/notifications/page.tsx`

```tsx
"""
صفحة إعدادات الإشعارات.

تُظهر toggle switches لكل نوع إشعار:
  ✓ Email me when customer is angry
  ✓ Email me when a call is missed
  ✓ Daily summary email at [time picker]
  ✓ Weekly report every Monday
  ✓ SMS alerts (requires phone number)
  ✗ Webhook (Enterprise plan only)

يشمل:
  - Test button لكل نوع ("Send test email")
  - إدخال بريد إلكتروني مختلف للإشعارات
  - إدخال رقم هاتف للـ SMS
  - Timezone selector
  - Save Changes button مع success toast
"""
```

---

## 🔧 المهمة 6: Email Templates HTML

### أنشئ هذه الملفات في `backend/email_templates/`

```
email_templates/
├── base.html              ← Template أساسي (header + footer لكل الـ emails)
├── welcome.html
├── onboarding_complete.html
├── daily_summary.html
├── weekly_report.html
├── angry_customer_alert.html
├── missed_call.html
├── payment_failed.html
├── day3_checkin.html
└── churn_risk.html
```

**متطلبات `base.html`:**

```html
<!--
Base template يجب أن:
1. يعمل على Gmail, Outlook, Apple Mail
2. Responsive (640px max-width)
3. Dark mode support (prefers-color-scheme)
4. Font: Arial (safe font)
5. Colors:
   - Background: #0A0A0A (dark) / #F5F5F5 (light)
   - Card: #1A1A1A (dark) / #FFFFFF (light)
   - Primary: #F59E0B (amber-500)
   - Text: #FFFFFF (dark) / #1A1A1A (light)

يشمل:
  - VoiceCore logo في header (SVG text فقط)
  - Company name + timestamp
  - Footer مع: Unsubscribe, Privacy Policy, Company address
  - UTM parameters على كل link للـ tracking
-->
```

---

## 🔧 المهمة 7: Celery Configuration

### `backend/celery_app.py` — تحديث كامل

```python
"""
Celery configuration مع:
  - Redis broker
  - Beat scheduler للـ periodic tasks
  - 3 queues: default, high_priority, scheduled
  - Proper serialization
  - Error handling + logging
"""

from celery import Celery
from celery.schedules import crontab

app = Celery('voicecore')

app.conf.update(
    broker_url=settings.redis_url,
    result_backend=settings.redis_url,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # 3 queues مختلفة
    task_queues={
        'default': {'routing_key': 'default'},
        'high_priority': {'routing_key': 'high'},
        'scheduled': {'routing_key': 'scheduled'},
    },
    task_default_queue='default',

    # Angry customer → high priority queue
    task_routes={
        'tasks.notification_tasks.send_angry_alert': {'queue': 'high_priority'},
        'tasks.notification_tasks.send_emergency_alert': {'queue': 'high_priority'},
        'tasks.email_tasks.send_daily_summaries': {'queue': 'scheduled'},
        'tasks.email_tasks.send_weekly_reports': {'queue': 'scheduled'},
    },

    # Beat schedule
    beat_schedule={
        'daily-summaries': {
            'task': 'tasks.email_tasks.send_daily_summaries',
            'schedule': crontab(hour=8, minute=0),
        },
        'weekly-reports': {
            'task': 'tasks.email_tasks.send_weekly_reports',
            'schedule': crontab(day_of_week=1, hour=8, minute=0),
        },
        'check-inactive': {
            'task': 'tasks.email_tasks.check_inactive_companies',
            'schedule': crontab(hour=9, minute=0),
        },
        'appointment-reminders': {
            'task': 'tasks.reminder_tasks.send_appointment_reminders',
            'schedule': crontab(minute=0),  # كل ساعة
        },
        'retry-notifications': {
            'task': 'tasks.email_tasks.retry_failed_notifications',
            'schedule': crontab(minute='*/30'),  # كل 30 دقيقة
        },
        'provider-health-check': {
            'task': 'tasks.notification_tasks.check_provider_health',
            'schedule': crontab(minute='*/5'),  # كل 5 دقائق
        },
    }
)
```

---

## ✅ معايير الانتهاء

- [ ] Onboarding wizard يعمل 5 خطوات كاملة دون أخطاء
- [ ] رقم Twilio يُشترى ويُضبط تلقائياً من خطوة 4
- [ ] Test call في خطوة 5 يعمل فعلاً (مكالمة حقيقية)
- [ ] Email يصل بعد إكمال التسجيل (check spam folder)
- [ ] Angry customer alert يُرسل خلال 60 ثانية من انتهاء المكالمة
- [ ] Daily summary email يصل في الوقت الصحيح
- [ ] `celery -A celery_app worker --loglevel=info` يعمل بدون errors
- [ ] `celery -A celery_app beat --loglevel=info` يعمل بدون errors
- [ ] لا يوجد `# TODO` في أي ملف

---

## ⚠️ قواعد لا تُكسر

1. **كل email** يجب أن يعمل على mobile (640px max-width)
2. **كل notification** تُحفظ في DB (للـ audit trail)
3. **Angry customer alert** يُرسل على **high_priority queue** — لا تأخير
4. **Celery tasks** تُنفذ async — لا تحجب الـ API
5. **Email templates** بـ HTML فقط — لا Jinja2 logic معقد
6. **Unsubscribe link** إلزامي في كل email (GDPR compliance)

---

*PROMPT 02/03 — VoiceCore Build System*
*المرحلة: Reliability — اجعله موثوقاً*
