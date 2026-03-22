# 🎤 PROMPT 01 — VOICE PIPELINE & MEMORY SYSTEM
## VoiceCore — المهمة الأولى: اجعله يعمل

---

## 🎯 هدفك من هذا الملف

تنفيذ **3 أنظمة أساسية** يجب أن تعمل قبل أي شيء آخر:
1. Voice Pipeline كامل يعمل end-to-end (مكالمة حقيقية تعمل)
2. Memory System حقيقي مبني على Redis
3. Fallback System عند فشل أي خدمة خارجية

**لا تنتقل للملف الثاني قبل أن تختبر مكالمة حقيقية.**

---

## 📋 قائمة الملفات التي ستنشئها أو تعدلها

```
backend/
├── agents/
│   ├── voice_agent.py         ← أعد كتابة كاملة
│   ├── pipeline.py            ← أعد كتابة كاملة
│   ├── memory.py              ← أنشئ من صفر
│   ├── fallback.py            ← أنشئ من صفر
│   ├── emotions.py            ← أعد كتابة كاملة
│   └── system_prompt.py       ← تحديث
├── api/
│   ├── voice.py               ← أنشئ من صفر
│   └── webhooks.py            ← تحديث
├── core/
│   ├── circuit_breaker.py     ← تحديث
│   └── provider_registry.py   ← أنشئ من صفر
└── tests/
    └── test_voice_pipeline.py ← أنشئ من صفر
```

---

## 🔧 المهمة 1: Memory System (ابدأ هنا)

### الملف: `backend/agents/memory.py`

اكتب class كاملة لإدارة ذاكرة العملاء عبر المكالمات. هذا هو الفرق الأكبر بين VoiceCore وكل المنافسين.

**المتطلبات الكاملة:**

```python
"""
Customer Memory System — Redis-backed persistent memory across calls.

Architecture:
  - Short-term: current call context (TTL: call duration)
  - Medium-term: session memory (TTL: 24 hours)
  - Long-term: customer profile (TTL: 90 days, refreshed on each call)
  - Company-level: shared knowledge across all customers (TTL: 7 days)

Redis Key Schema:
  customer:{company_id}:{phone}:profile     → CustomerProfile (JSON)
  customer:{company_id}:{phone}:history     → List of last 10 call summaries
  customer:{company_id}:{phone}:preferences → Dict of preferences
  session:{call_id}:context                 → Current call context
  company:{company_id}:knowledge            → Company-specific knowledge
"""
```

**يجب أن تنفذ هذه الـ methods بالكامل:**

```python
class CustomerMemoryManager:

    async def get_customer_profile(
        self, phone: str, company_id: int
    ) -> CustomerProfile:
        """
        جلب كامل معلومات العميل من Redis.
        إذا لم يوجد في Redis، جلبه من PostgreSQL وحفظه في cache.
        يشمل: الاسم، تاريخ المكالمات، الملاحظات، VIP status، التفضيلات
        """

    async def update_customer_profile(
        self, phone: str, company_id: int, updates: dict
    ) -> bool:
        """
        تحديث profile العميل بعد كل مكالمة.
        يجب أن يحدث Redis و PostgreSQL في نفس الوقت (async).
        """

    async def save_call_summary(
        self, phone: str, company_id: int, call_id: int,
        summary: str, outcome: str, sentiment: str
    ) -> bool:
        """
        حفظ ملخص المكالمة في list العميل.
        الحد الأقصى: آخر 10 مكالمات.
        يُستخدم في الـ system prompt للمكالمة التالية.
        """

    async def get_call_history_summary(
        self, phone: str, company_id: int, max_calls: int = 3
    ) -> str:
        """
        إرجاع ملخص نصي جاهز للـ system prompt.
        مثال:
        "Customer history:
         - 2024-01-15: Booked dental appointment (POSITIVE)
         - 2024-01-10: Asked about insurance coverage (NEUTRAL)
         - 2024-01-05: Complained about wait time (FRUSTRATED)"
        """

    async def load_context_for_call(
        self, phone: str, company_id: int, call_id: str
    ) -> CallContext:
        """
        تحميل كل السياق اللازم لبدء مكالمة.
        يُستدعى في بداية كل مكالمة.
        Returns: {profile, history_summary, preferences, company_knowledge}
        """

    async def save_session_context(
        self, call_id: str, context: dict, ttl_seconds: int = 3600
    ) -> bool:
        """
        حفظ السياق الحالي للمكالمة الجارية في Redis.
        يُستخدم إذا انقطعت المكالمة وعادت.
        """

    async def mark_customer_vip(
        self, phone: str, company_id: int, reason: str
    ) -> bool:
        """
        تعليم العميل كـ VIP مع سبب التعليم.
        VIP customers get priority treatment in system prompt.
        """

    async def get_or_create_customer(
        self, phone: str, company_id: int,
        name: Optional[str] = None
    ) -> CustomerProfile:
        """
        جلب العميل أو إنشاؤه إذا كانت أول مكالمة.
        يحدث total_calls counter تلقائياً.
        """
```

**الـ Pydantic models المطلوبة:**

```python
class CustomerProfile(BaseModel):
    phone: str
    company_id: int
    name: Optional[str]
    total_calls: int
    last_call_at: Optional[datetime]
    is_vip: bool
    notes: Optional[str]
    preferences: Dict[str, Any]  # language, communication_style, etc.
    call_history: List[CallSummary]  # آخر 10 مكالمات
    created_at: datetime

class CallSummary(BaseModel):
    call_id: int
    date: datetime
    duration_seconds: int
    outcome: str
    sentiment: str
    summary: str  # ملخص 1-2 جملة

class CallContext(BaseModel):
    customer: CustomerProfile
    history_text: str       # نص جاهز للـ system prompt
    is_returning_customer: bool
    days_since_last_call: Optional[int]
    company_knowledge: Dict[str, Any]
```

**Redis TTL المطلوبة:**
```python
PROFILE_TTL = 90 * 24 * 3600      # 90 يوم
SESSION_TTL = 24 * 3600            # 24 ساعة
COMPANY_KNOWLEDGE_TTL = 7 * 24 * 3600  # 7 أيام
CALL_CONTEXT_TTL = 2 * 3600        # ساعتان
```

---

## 🔧 المهمة 2: Voice Agent الكامل

### الملف: `backend/agents/voice_agent.py`

أعد كتابة كاملة. النسخة الحالية ناقصة ولا تعمل مع مكالمة حقيقية.

**المتطلبات:**

```python
class VoiceAgent:
    """
    الوكيل الذكي الكامل لمعالجة المكالمات الصوتية.

    دورة حياة المكالمة:
    1. on_call_start(call_sid, caller_phone, company_id, agent_id)
       - تحميل customer context من memory
       - بناء system prompt مخصص
       - تهيئة STT/TTS/LLM
       - إرسال رسالة ترحيب مخصصة

    2. on_audio_received(audio_frame)
       - UltraLowLatencyPipeline.process()
       - تحليل المشاعر
       - تنفيذ الأدوات إذا طُلب
       - إرسال الرد صوتياً

    3. on_call_end(call_sid)
       - توليد ملخص المكالمة بـ Claude
       - حفظ كل شيء في DB + Redis
       - إرسال notifications إذا لزم
       - حساب outcome النهائي
    """

    def __init__(
        self,
        agent_id: int,
        company_id: int,
        language: str = "auto",
        voice_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        vertical: Optional[str] = None,  # dental/legal/realty/None
    ):
        # يجب تهيئة كل هذه
        self.memory = CustomerMemoryManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fallback_handler = FallbackHandler()
        self.tool_executor = AgentToolExecutor()
        self.current_call: Optional[ActiveCall] = None
        self.sentiment_history: List[str] = []
        self.angry_count: int = 0  # عداد للتحويل التلقائي

    async def on_call_start(
        self, call_sid: str, caller_phone: str,
        company_id: int, agent_id: int
    ) -> str:
        """
        Returns: رسالة الترحيب الأولى (TTS)

        يجب أن:
        1. يحمل customer context من memory
        2. يبني system prompt مخصص بناءً على التاريخ
        3. إذا كان عميل عائد: "Welcome back, [Name]! How can I help you today?"
        4. إذا كان جديد: "Thank you for calling [Company]. I'm [Agent Name]. How can I help?"
        5. يسجل بداية المكالمة في DB
        """

    async def on_audio_received(
        self, audio_frame: bytes
    ) -> Optional[bytes]:
        """
        Returns: audio bytes للرد (TTS) أو None إذا لا يزال يعالج

        يجب أن:
        1. يمرر الصوت للـ pipeline
        2. يحلل المشاعر على كل رد
        3. إذا ANGRY مرتين متتاليتين → ينقل للإنسان تلقائياً
        4. ينفذ الأدوات المطلوبة
        5. يستخدم fallback إذا فشل أي service
        """

    async def on_call_end(self, outcome: str) -> CallSummary:
        """
        outcome: completed/voicemail/transferred/missed/failed

        يجب أن:
        1. يولد ملخص 1-2 جملة بـ Claude
        2. يحفظ transcript في DB
        3. يحدث customer profile في Redis + DB
        4. يحسب sentiment_score النهائي
        5. يُطلق webhook إذا كان outcome مهم
        """

    async def _auto_transfer_if_angry(self) -> bool:
        """
        إذا كان آخر سنتيمنتين ANGRY → نقل للإنسان.
        يسجل السبب في الـ transcript.
        """

    async def _execute_tool(
        self, tool_name: str, parameters: dict
    ) -> dict:
        """
        تنفيذ أدوات الوكيل مع error handling كامل.
        كل tool تأخذ 3 ثوان max، وإلا timeout وfallback message.
        """

    async def _generate_call_summary(self) -> str:
        """
        يستخدم Claude لتوليد ملخص 1-2 جملة من الـ transcript.
        Prompt: "Summarize this call in 1-2 sentences. Include: main topic, outcome, any action items."
        """
```

---

## 🔧 المهمة 3: Ultra Low Latency Pipeline

### الملف: `backend/agents/pipeline.py`

```python
class UltraLowLatencyPipeline:
    """
    هدف: أقل من 500ms من نهاية الكلام لبداية الرد الصوتي.

    التحسينات:
    - STT + Memory + CRM في نفس الوقت (asyncio.gather)
    - TTS streaming بدلاً من انتظار الرد كاملاً
    - Response caching للأسئلة المتكررة
    - Voice Activity Detection دقيق
    """

    async def process(
        self,
        audio_frame: bytes,
        caller_phone: str,
        company_id: str,
        call_id: str,
        conversation_history: List[Dict],
        customer_context: CallContext,
    ) -> AsyncGenerator[bytes, None]:
        """
        Streaming pipeline — يبدأ إرسال الصوت قبل اكتمال الرد.

        STEP 1 — parallel (هذا ما يوفر 200-300ms):
          [STT transcription] + [check response cache] + [update context]

        STEP 2 — sequential:
          Build messages with full context → Claude API (streaming) → ElevenLabs streaming

        STEP 3 — async:
          Save turn to transcript → Update conversation history

        يجب استخدام asyncio.gather() في STEP 1.
        يجب streaming في STEP 2 (لا تنتظر الرد كاملاً).
        """

    async def _check_response_cache(
        self, transcript: str, company_id: str
    ) -> Optional[str]:
        """
        فحص Redis لردود مخزنة على أسئلة متكررة.
        مثال: "What are your hours?" → cached response
        Cache key: sha256(company_id + normalized_question)
        TTL: 24 ساعات
        """

    async def _build_messages(
        self,
        transcript: str,
        history: List[Dict],
        context: CallContext,
        system_prompt: str,
    ) -> List[Dict]:
        """
        بناء messages list لـ Claude API.
        يشمل: system prompt + customer context + conversation history + current transcript.
        history يُقطع إلى آخر 10 turns لتوفير tokens.
        """

    async def _stream_tts(
        self, text_generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[bytes, None]:
        """
        TTS streaming — يبدأ التحدث بمجرد وصول أول جملة.
        يقسم النص على الـ sentence boundaries (. ! ?)
        يرسل كل جملة فور اكتمالها.
        """

    async def _detect_voice_activity(
        self, audio_frame: bytes
    ) -> VoiceActivityResult:
        """
        Silero VAD — يكتشف نهاية الكلام بدقة.
        start_secs: 0.2 — يبدأ الاستماع بسرعة
        stop_secs: 0.8  — ينتظر 800ms صمت قبل المعالجة
        """
```

---

## 🔧 المهمة 4: Fallback System

### الملف: `backend/agents/fallback.py`

```python
"""
Fallback System — يضمن استمرار المكالمة حتى عند فشل الخدمات.

السيناريوهات التي يجب معالجتها:
1. Deepgram فاشل → يستخدم Whisper API كبديل
2. ElevenLabs فاشل → يستخدم Twilio TTS المدمج
3. Claude فاشل → يستخدم pre-built responses للأسئلة الشائعة
4. Redis فاشل → يعمل بدون cache (degraded mode)
5. DB فاشل → يحفظ في memory ويعيد المحاولة بعد المكالمة
6. Twilio فاشل → يسجل للـ retry queue
"""

class FallbackHandler:

    async def stt_with_fallback(
        self, audio_frame: bytes, primary: str = "deepgram"
    ) -> STTResult:
        """
        1. جرب Deepgram (nova-2)
        2. إذا فشل خلال 2 ثانية → جرب OpenAI Whisper
        3. إذا فشل → أرسل "I didn't catch that, could you repeat?"
        يسجل كل فشل في Redis counter للـ monitoring
        """

    async def tts_with_fallback(
        self, text: str, primary_voice_id: str
    ) -> bytes:
        """
        1. جرب ElevenLabs
        2. إذا فشل → جرب ElevenLabs مع voice_id مختلف
        3. إذا فشل → استخدم Twilio TTS المدمج
        4. إذا فشل كل شيء → silence مع log error
        """

    async def llm_with_fallback(
        self, messages: List[Dict], intent: str
    ) -> str:
        """
        1. جرب Claude (claude-3-5-sonnet-20241022)
        2. إذا فشل → جرب مرة ثانية مع exponential backoff
        3. إذا فشل → استخدم pre-built response حسب intent
        4. إذا unknown intent → "Let me transfer you to our team"

        Pre-built responses:
        - "hours": "We're open Monday-Friday 9am-6pm."
        - "location": "We're located at [company address]."
        - "appointment": "I'd be happy to help you schedule. What day works best?"
        - "emergency": "For emergencies, please hang up and call 911."
        - "default": "I'm having trouble processing that. Let me transfer you."
        """

    async def db_with_fallback(
        self, operation: Callable, fallback_storage: dict
    ) -> bool:
        """
        يحاول حفظ في DB.
        إذا فشل → يحفظ في Redis مع flag "pending_sync"
        Celery task يعيد المحاولة كل 5 دقائق
        """


class ProviderHealthMonitor:
    """
    يراقب health كل provider ويُحدّث Redis.
    يُشغَّل كل 60 ثانية بـ Celery beat.
    """

    async def check_all_providers(self) -> Dict[str, ProviderStatus]:
        """
        يختبر: Deepgram, ElevenLabs, Claude, Twilio, Stripe
        يحدث: provider:{name}:status في Redis
        يرسل: alert إذا provider فاشل أكثر من 3 مرات متتالية
        """

    async def get_provider_status(self, name: str) -> ProviderStatus:
        """
        يجلب status من Redis cache (لا يعمل live check في كل request)
        """
```

---

## 🔧 المهمة 5: Sentiment Analyzer بـ Claude

### الملف: `backend/agents/emotions.py`

**احذف keyword matching. استخدم Claude.**

```python
class SentimentAnalyzer:
    """
    تحليل المشاعر بـ Claude بدلاً من keyword matching.
    يدعم: العربية، الإنجليزية، الفرنسية، الإسبانية.
    """

    async def analyze(
        self, text: str, language: str = "auto"
    ) -> SentimentResult:
        """
        يستخدم Claude لتحليل المشاعر.

        Prompt للـ API:
        "Analyze the sentiment of this customer message.
         Respond with ONLY a JSON object:
         {
           'sentiment': 'POSITIVE|NEUTRAL|FRUSTRATED|ANGRY',
           'score': 0.0-1.0,
           'keywords': ['word1', 'word2'],
           'action_required': true/false,
           'reason': 'brief explanation'
         }
         Message: '{text}'"

        إذا فشل Claude → استخدم keyword fallback البسيط
        Cache النتيجة في Redis لـ 10 دقائق (نفس النص غالباً يتكرر)
        """

    def _keyword_fallback(self, text: str) -> SentimentResult:
        """
        Fallback بسيط إذا فشل Claude.
        يدعم عدة لغات بكلمات مفتاحية أساسية.
        """

    async def analyze_full_call(
        self, transcript: List[Dict]
    ) -> CallSentimentSummary:
        """
        يحلل كامل transcript المكالمة بعد انتهائها.
        يحسب: dominant sentiment, trend, peak_frustration_point
        يُستخدم لحفظ sentiment_score النهائي في DB
        """
```

---

## 🔧 المهمة 6: Voice WebSocket Endpoint

### الملف: `backend/api/voice.py`

```python
"""
WebSocket endpoint لـ LiveKit voice streaming.
يتعامل مع:
- Connection setup
- Audio frame streaming (bidirectional)
- Call state management
- Clean disconnect
"""

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

@router.websocket("/ws/{call_sid}")
async def voice_websocket(
    websocket: WebSocket,
    call_sid: str,
    token: str = Query(...),  # JWT للتحقق
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket handler كامل.

    Flow:
    1. التحقق من الـ JWT token
    2. جلب call info من DB بالـ call_sid
    3. إنشاء VoiceAgent instance
    4. call agent.on_call_start() → إرسال رسالة الترحيب
    5. loop: استقبال audio → معالجة → إرسال رد صوتي
    6. عند disconnect: call agent.on_call_end()

    يجب معالجة:
    - WebSocketDisconnect
    - asyncio.TimeoutError (المكالمة أطول من ساعة)
    - أي exception → سجّل وأغلق نظيفاً
    """


@router.post("/inbound")
async def handle_inbound_call(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Twilio webhook لكل مكالمة واردة.

    يجب أن:
    1. يتحقق من Twilio signature (security)
    2. يجد الشركة من الـ To number
    3. يجد الوكيل الـ active للشركة
    4. ينشئ Call record في DB
    5. يرجع TwiML يوصّل Twilio بـ LiveKit

    TwiML المطلوب:
    <Response>
        <Connect>
            <Stream url="wss://your-server/api/v1/voice/ws/{call_sid}?token={jwt}"/>
        </Connect>
    </Response>

    إذا لم توجد شركة أو وكيل → TwiML بسيط:
    <Response>
        <Say>We're sorry, this number is not in service. Goodbye.</Say>
        <Hangup/>
    </Response>
    """


@router.post("/outbound")
async def initiate_outbound_call(
    call_data: OutboundCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    إطلاق مكالمة صادرة.
    يتحقق من plan limits قبل الإطلاق.
    يستخدم TwilioService.make_call()
    """
```

---

## 🔧 المهمة 7: اكتب Alembic Migrations

### الملف: `backend/alembic/versions/001_initial.py`

**اكتب migration كاملة بكل الجداول:**

```python
"""Initial migration — all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-03-01
"""

def upgrade():
    # 1. companies
    op.create_table('companies', ...)

    # 2. users
    op.create_table('users', ...)

    # 3. agents
    op.create_table('agents', ...)

    # 4. customers
    op.create_table('customers', ...)

    # 5. calls
    op.create_table('calls', ...)

    # 6. subscriptions
    op.create_table('subscriptions', ...)

    # 7. admin_users
    op.create_table('admin_users', ...)

    # 8. admin_logs
    op.create_table('admin_logs', ...)

    # Indexes المطلوبة (مهمة جداً للأداء):
    op.create_index('idx_calls_company_created', 'calls', ['company_id', 'created_at'])
    op.create_index('idx_calls_caller_phone', 'calls', ['caller_phone'])
    op.create_index('idx_customers_phone_company', 'customers', ['phone', 'company_id'], unique=True)
    op.create_index('idx_agents_company_active', 'agents', ['company_id', 'is_active'])

def downgrade():
    # عكس كل شيء بالترتيب الصحيح
    ...
```

---

## 🔧 المهمة 8: Tests

### الملف: `backend/tests/test_voice_pipeline.py`

```python
"""
اكتب هذه الـ tests بالكامل — لا تتركها فارغة.
"""

async def test_memory_get_customer_new():
    """عميل جديد → ينشئ profile فارغ"""

async def test_memory_get_customer_existing():
    """عميل موجود → يجلب من Redis"""

async def test_memory_save_call_summary():
    """حفظ ملخص → يظهر في history"""

async def test_memory_max_10_calls():
    """11 مكالمة → الأولى تُحذف"""

async def test_pipeline_parallel_execution():
    """STT + Memory يعملان بالتوازي → أسرع من sequential"""

async def test_fallback_stt_deepgram_fails():
    """Deepgram يفشل → Whisper يعمل"""

async def test_fallback_tts_elevenlabs_fails():
    """ElevenLabs يفشل → Twilio TTS يعمل"""

async def test_sentiment_angry_triggers_transfer():
    """سنتيمنت ANGRY مرتين → transfer تلقائي"""

async def test_voice_websocket_full_flow():
    """مكالمة كاملة: connect → welcome → audio → response → disconnect"""

async def test_inbound_webhook_twilio_signature():
    """webhook بدون signature صحيح → 403"""
```

---

## ✅ معايير الانتهاء (Definition of Done)

قبل أن تعتبر هذا الملف منتهياً، تأكد من:

- [ ] `python -m pytest backend/tests/test_voice_pipeline.py -v` يمر بالكامل
- [ ] مكالمة تجريبية حقيقية عبر Twilio تعمل (حتى 30 ثانية)
- [ ] Redis يحفظ customer profile بعد المكالمة
- [ ] إذا أوقفت Deepgram service → المكالمة تستمر مع Whisper
- [ ] `alembic upgrade head` يعمل بدون errors
- [ ] لا يوجد `# TODO` أو `pass` في الكود

---

## ⚠️ قواعد لا تُكسر

1. **كل** async operation داخل try/except مع logging
2. **لا** تحفظ أي PII (phone, name) في logs
3. **كل** Twilio webhook يتحقق من `X-Twilio-Signature`
4. **الـ** sentiment analysis يستخدم Claude أولاً، keyword fallback ثانياً
5. **الـ** memory system يحدث Redis و DB معاً (لا consistency issues)
6. **الـ** pipeline لا تنتظر الـ LLM response كاملاً — TTS streaming إلزامي

---

*PROMPT 01/03 — VoiceCore Build System*
*المرحلة: Foundation — اجعله يعمل*
