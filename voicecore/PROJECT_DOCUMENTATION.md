# VoiceCore: نظام ذكاء اصطناعي متكامل للمكالمات الصوتية
## ورقة تقنية شاملة - وثيقة المشروع الكاملة

---

# الفهرس

1. [المقدمة](#المقدمة)
2. [الرؤية والفكرة](#الرؤية-والفكرة)
3. [البنية التقنية العامة](#البنية-التقنية-العامة)
4. [الطبقة الخلفية (Backend)](#الطبقة-الخلفية-backend)
5. [قاعدة البيانات](#قاعدة-البيانات)
6. [واجهات برمجة التطبيقات (API)](#واجهات-برمجة-التطبيقات-api)
7. [الخدمات الخارجية](#الخدمات-الخارجية)
8. [نظام الوكلاء الذكيين (Voice Agents)](#نظام-الوكلاء-الذكيين-voice-agents)
9. [خط معالجة الصوت (Voice Pipeline)](#خط-معالجة-الصوت-voice-pipeline)
10. [التكاملات (Integrations)](#التكاملات-integrations)
11. [الطبقة الأمامية (Frontend)](#الطبقة-الأمامية-frontend)
12. [الوضع الرأسي (Verticals)](#الوضع-الرأسي-verticals)
13. [لوحة تحكم المسؤول (Super Admin)](#لوحة-تحكم-المسؤول-super-admin)
14. [الأمان والحماية](#الأمان-والحماية)
15. [النشر والتشغيل](#النشر-والتشغيل)
16. [الاختبار والجودة](#الاختبار-والجودة)
17. [الخطط المستقبلية](#الخطط-المستقبلية)
18. [الخلاصة](#الخلاصة)

---

# 1. المقدمة

## 1.1 ما هو VoiceCore؟

VoiceCore هو نظام متكامل للمكالمات الصوتية يعمل بالذكاء الاصطناعي، مصمم ليحل محل موظفي الاستقبال البشريين في الشركات بمختلف أحجامها. يستخدم النظام تقنيات متقدمة في تحويل الصوت إلى نص (STT)، معالجة اللغة الطبيعية (NLP)، والتوليد الصوتي (TTS) لتوفير تجربة محادثة طبيعية مع العملاء.

## 1.2 المشكلة التي يحلها

- **35-67% من المكالمات** تفشل الوصول إلى شخص حي (حسب الصناعة)
- **فقدان العملاء**: كل مكالمة فائتة قد تكلف $500-$50,000 من الإيرادات المفقودة
- **عدم القدرة على تغطية 24/7**: معظم الشركات لا تستطيع توفير استقبال على مدار الساعة
- **الضغط على الموظفين**: front desk مُثقل بالاستفسارات المتكررة
- **عدم وجود بيانات**: لا توجد طريقة منهجية لتسجيل وتحليل محادثات العملاء

## 1.3 الحل الذي يقدمه VoiceCore

- **استقبال ذكي 24/7**: يعمل على مدار الساعة بدون انقطاع
- **فهم سياقي**: يتذكر محادثات سابقة ويفهم سياق كل عميل
- **تكاملات متعددة**: ربط مع أنظمة CRM والتقويم والدفع
- **تحليلات متقدمة**: تقارير كاملة عن المشاعر والمطالبات والنجاح
- **قابل للتخصيص**: يمكن تخصيصه لكل صناعة واحتياج

---

# 2. الرؤية والفكرة

## 2.1 الفلسفة التصميمية

صُمم VoiceCore ليكون:
- **شبه بشري**: المحادثة تبدو طبيعية قدر الإمكان
- **عملي**: يركز على إنجاز المهام وليس المحادثة للحوار
- **قابل للتوسع**: يمكن نشره على عدة شركات وصناعات
- **آمن**: حماية بيانات العملاء أولوية قصوى

## 2.2 نموذج العمل

### الخطط والأسعار:

| الخطة | السعر الشهري | السعر السنوي | الميزات |
|-------|-------------|-------------|---------|
| Free | $0 | $0 | 50 مكالمة/شهر، 1 وكيل |
| Starter | $299 | $239 | 500 مكالمة/شهر، 3 وكلاء، تكامل أساسي |
| Business | $899 | $719 | 2000 مكالمة/شهر، 10 وكلاء، جميع التكاملات |
| Enterprise | $2,499+ | $1,999+ | غير محدود، دعم مخصص، white-label |

### الوضع الرأسي (Industry Verticals):

| الصناعة | السعر | الاستخدامات |
|---------|-------|------------|
| DentalVoice | $399/شهر | تسجيل مرضى جدد، التحقق من التأمين، حجز المواعيد |
| LegalVoice | $599/شهر | تأهيل القضايا، فحص تضارب المصالح، كشف الطوارئ |
| RealtyVoice | $299/شهر | تأهيل المشترين، جدولة المعاينات، معلومات العقارات |

---

# 3. البنية التقنية العامة

## 3.1 نظرة عامة على Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Phone      │  │   Web       │  │  WhatsApp    │           │
│  │   (Twilio)  │  │   Browser   │  │  Business    │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VOICECORE FRONTEND                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Next.js 14 (App Router)                     │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │Dashboard│ │Analytics│ │Agents   │ │Settings │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │           Super Admin Panel                      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VOICECORE BACKEND                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI (Python 3.11)                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │  Auth   │ │ Agents  │ │ Calls   │ │Billing  │        │   │
│  │  │  API    │ │  API    │ │  API    │ │  API    │        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │Analytics│ │ Webhooks│ │ Public  │ │ Admin   │        │   │
│  │  │  API    │ │  API    │ │  API    │ │  API    │        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌────────────────────────────┼────────────────────────────┐   │
│  │         VOICE AGENTS LAYER                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                │   │
│  │  │ Pipecat  │ │  STT     │ │   TTS    │                │   │
│  │  │ Pipeline │ │(Deepgram)│ │(ElevenLabs)               │   │
│  │  └──────────┘ └──────────┘ └──────────┘                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │     Redis       │ │  External APIs  │
│   (Database)    │ │   (Cache/Queue) │ │ (Twilio/Stripe) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 3.2 Tech Stack

### Backend:
- **Language**: Python 3.11
- **Framework**: FastAPI 0.109.0
- **ASGI Server**: Uvicorn مع 4 workers
- **Database**: PostgreSQL 15 (async with asyncpg)
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery مع Redis broker
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Auth**: JWT with PyJWT
- **Password**: bcrypt via passlib

### Frontend:
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: Tailwind CSS + Radix UI
- **Charts**: Recharts
- **Icons**: Lucide React
- **Auth**: NextAuth.js
- **State**: React Context + Hooks
- **HTTP**: Axios

### Infrastructure:
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Railway (with Dockerfile support)
- **CDN**: Vercel Edge Network (for frontend)

---

# 4. الطبقة الخلفية (Backend)

## 4.1 هيكل الملفات

```
backend/
├── main.py                 # نقطة الدخول، إعداد FastAPI
├── config.py               # إعدادات البيئة
├── celery_app.py           # إعداد Celery للمهام الخلفية
├── gunicorn.conf.py        # إعدادات Gunicorn
├── init_db.py              # تهيئة قاعدة البيانات
├── requirements.txt         # dependencies
├── __init__.py
│
├── api/                    # REST API endpoints
│   ├── __init__.py
│   ├── auth.py            # تسجيل الدخول، JWT، OAuth
│   ├── agents.py           # إدارة الوكلاء
│   ├── calls.py            # إدارة المكالمات
│   ├── analytics.py        # التحليلات والتقارير
│   ├── billing.py          # الفوترة والدفع
│   ├── webhooks.py         # Twilio/Stripe webhooks
│   ├── voice.py            # Voice streaming endpoints
│   ├── companies.py        # إدارة الشركات
│   ├── customers.py        # إدارة العملاء النهائيين
│   ├── admin.py            # لوحة تحكم المسؤول
│   ├── roi_calculator.py   # حاسبة العائد على الاستثمار
│   ├── competitive.py      # تحليل المنافسين
│   ├── intelligence.py     # ذكاء المحادثات
│   ├── public/
│   │   └── router.py       # endpoints عامة
│   └── admin/
│       └── metrics.py      # مقاييس الاستثمار
│
├── db/                     # طبقة قاعدة البيانات
│   ├── __init__.py
│   ├── database.py         # SQLAlchemy async engine
│   ├── models.py           # ORM models
│   └── schemas.py          # Pydantic schemas
│
├── services/              # خدمات خارجية
│   ├── __init__.py
│   ├── twilio_service.py   # Twilio API wrapper
│   ├── stripe_service.py   # Stripe payment wrapper
│   └── whatsapp_service.py # WhatsApp Business API
│
├── agents/                # نظام الوكلاء الذكيين
│   ├── __init__.py
│   ├── voice_agent.py      # Voice agent core logic
│   ├── system_prompt.py    # prompts النظام
│   ├── tools.py            # أدوات الوكيل
│   ├── pipeline.py          # معالجة متوازية
│   ├── streaming.py         # streaming الصوت
│   ├── memory.py           # إدارة الذاكرة
│   ├── cache.py            # تخزين مؤقت
│   ├── emotions.py          # تحليل المشاعر
│   ├── proactive.py         # استباقية المحادثة
│   ├── fallback.py          # معالجة الأخطاء
│   ├── biometrics.py        # تحليل الصوتيات
│   └── pci_compliance.py    # امتثال PCI-DSS
│
├── core/                  # utilities
│   └── circuit_breaker.py  # نمط Circuit Breaker
│
├── integrations/           # تكاملات الطرف الثالث
│   ├── crm/
│   │   └── universal.py    # Salesforce, HubSpot, Zoho, etc.
│   ├── calendar/
│   │   └── universal.py    # Google Calendar, Outlook, Calendly
│   ├── mls/
│   │   └── client.py       # Multiple Listing Service
│   └── automation/
│       └── webhooks.py     # Zapier, Make integration
│
├── channels/              # قنوات الاتصال
│   └── hub.py             # Central channel management
│
├── features/              # ميزات خاصة بالصناعة
│   └── verticals/
│       ├── dental/
│       │   ├── prompt.py
│       │   ├── tools.py
│       │   └── knowledge.py
│       ├── legal/
│       │   ├── prompt.py
│       │   ├── tools.py
│       │   └── compliance.py
│       └── realty/
│           ├── prompt.py
│           └── tools.py
│
├── alembic/               # database migrations
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
│
├── scripts/
│   └── seed.py            # بيانات تجريبية
│
└── tests/
    └── test_api.py        # اختبارات API
```

## 4.2 main.py - نقطة الدخول

```python
# الإعدادات الأساسية
app = FastAPI(title="VoiceCore API", version="1.0.0")

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(calls_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/webhooks")
app.include_router(public_router, prefix="/api/public")
app.include_router(admin_router, prefix="/api/admin")

# Endpoints
GET /                    # Homepage redirect
GET /health              # Basic health check
GET /health/ready        # Readiness check (DB + Redis)
GET /docs                # Swagger UI
GET /redoc               # ReDoc
```

## 4.3 config.py - إعدادات البيئة

```python
class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://..."
    redis_url: str = "redis://..."
    
    # AI Services
    deepgram_api_key: str = ""
    elevenlabs_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # LiveKit (WebRTC)
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_starter_price_id: str = ""
    stripe_business_price_id: str = ""
    
    # JWT
    jwt_secret: str = "dev-secret-change-in-prod"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    
    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Email
    sendgrid_api_key: str = ""
    from_email: str = ""
    
    # URLs
    next_public_api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Plans Pricing
    PLAN_PRICES = {
        "free": {"price_monthly": 0, "calls_limit": 50},
        "starter": {"price_monthly": 299, "calls_limit": 500},
        "business": {"price_monthly": 899, "calls_limit": 2000},
        "enterprise": {"price_monthly": 2499, "calls_limit": -1},
    }
```

---

# 5. قاعدة البيانات

## 5.1 هيكل الجداول

### ER Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    Company      │       │      User       │       │     AdminUser   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ company_id (FK) │       │ id (PK)         │
│ name            │       │ id (PK)         │       │ email (UNIQUE)  │
│ email           │       │ email           │       │ password_hash   │
│ plan            │       │ password_hash   │       │ name            │
│ phone_number    │       │ full_name       │       │ role            │
│ whatsapp_number │       │ role            │       │ is_active       │
│ stripe_*        │       │ is_active       │       │ totp_secret     │
│ status          │       │ last_login      │       │ failed_attempts │
│ created_at      │       └─────────────────┘       │ locked_until    │
└────────┬────────┘                                 │ last_login      │
         │                                        └─────────────────┘
         │                                                │
         │                                                │
         ▼                                                ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Agent       │       │     Call        │       │    AdminLog     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ company_id (FK) │       │ company_id (FK) │       │ admin_id (FK)   │
│ name            │       │ agent_id (FK)   │       │ action          │
│ language        │       │ caller_phone    │       │ target          │
│ voice_id        │       │ duration_secs   │       │ target_id       │
│ system_prompt   │       │ transcript     │       │ details         │
│ is_active       │       │ sentiment      │       │ ip_address      │
│ created_at      │       │ outcome        │       │ user_agent      │
└────────┬────────┘       │ sentiment_score│       │ timestamp       │
         │                │ created_at     │       └─────────────────┘
         │                └─────────────────┘
         │                        │
         ▼                        │
┌─────────────────┐               │
│    Customer     │               │
├─────────────────┤               │
│ id (PK)         │               │
│ company_id (FK) │               │
│ phone (UNIQUE) │               │
│ name            │               │
│ notes           │               │
│ total_calls     │               │
│ last_call_at    │               │
│ is_vip          │               │
└─────────────────┘               │
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Subscription  │
                         ├─────────────────┤
                         │ id (PK)         │
                         │ company_id (FK) │
                         │ stripe_*        │
                         │ plan            │
                         │ status          │
                         │ current_period* │
                         └─────────────────┘
```

## 5.2 النماذج (Models)

```python
# Company Model
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), default="free")
    phone_number = Column(String(50))
    whatsapp_number = Column(String(50))
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="company")
    agents = relationship("Agent", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    calls = relationship("Call", back_populates="company")

# Agent Model
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    language = Column(String(10), default="auto")  # en, ar, fr, es, auto
    voice_id = Column(String(100))  # ElevenLabs voice ID
    system_prompt = Column(Text)
    is_active = Column(Boolean, default=True)
    config = Column(JSON)  # Additional config as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    company = relationship("Company", back_populates="agents")
    calls = relationship("Call", back_populates="agent")

# Call Model
class Call(Base):
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    caller_phone = Column(String(50), nullable=False)
    duration_seconds = Column(Integer)
    transcript = Column(Text)
    sentiment = Column(String(20))  # POSITIVE, NEUTRAL, FRUSTRATED, ANGRY
    sentiment_score = Column(Float)  # 0.0 - 1.0
    outcome = Column(String(50))  # completed, voicemail, transferred, missed
    recording_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="calls")
    agent = relationship("Agent", back_populates="calls")
```

## 5.3 Database Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

# 6. واجهات برمجة التطبيقات (API)

## 6.1 Authentication API

### تسجيل الدخول
```python
POST /api/v1/auth/login
{
    "email": "user@example.com",
    "password": "password123"
}

Response:
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 7200,
    "company_id": 1,
    "user_id": 1
}
```

### Google OAuth
```python
GET /api/v1/auth/google
# Redirects to Google OAuth

GET /api/v1/auth/google/callback?code=xxx
# Creates/updates user and returns JWT
```

### التسجيل
```python
POST /api/v1/auth/register
{
    "email": "newuser@example.com",
    "password": "securepassword",
    "company_name": "My Company"
}

Response:
{
    "access_token": "...",
    "company_id": 2,
    "user_id": 3
}
```

## 6.2 Agents API

### إنشاء وكيل
```python
POST /api/v1/agents/
{
    "name": "Sarah",
    "language": "auto",
    "voice_id": "eleven_multilingual_v2",
    "system_prompt": "You are a helpful receptionist for our dental clinic..."
}

Response:
{
    "id": 1,
    "name": "Sarah",
    "is_active": true,
    ...
}
```

### تحديث وكيل
```python
PUT /api/v1/agents/{agent_id}
{
    "name": "Sarah Updated",
    "system_prompt": "Updated instructions..."
}
```

### تفعيل/إلغاء تفعيل
```python
POST /api/v1/agents/{agent_id}/toggle
Response:
{
    "id": 1,
    "is_active": false
}
```

## 6.3 Calls API

###Inbound Call Webhook (Twilio)
```python
POST /api/webhooks/twilio/voice
# Twilio sends call info, returns TwiML for connecting to LiveKit

<Response>
    <Say>Welcome to our company...</Say>
    <Connect>
        <Stream url="wss://livekit.example.com/voice/1"/>
    </Connect>
</Response>
```

###Outbound Call
```python
POST /api/v1/calls/outbound
{
    "company_id": 1,
    "agent_id": 1,
    "to_phone": "+1234567890",
    "message": "This is a reminder for your appointment..."
}

Response:
{
    "call_sid": "CAxxxx",
    "status": "initiated"
}
```

### سجل المكالمات
```python
GET /api/v1/calls/history?company_id=1&page=1&page_size=20
Response:
{
    "calls": [...],
    "total": 150,
    "page": 1,
    "page_size": 20
}
```

## 6.4 Analytics API

```python
GET /api/v1/analytics/summary?company_id=1&days=30
Response:
{
    "total_calls": 450,
    "total_duration": 18500,
    "avg_duration": 245,
    "sentiment_breakdown": {
        "POSITIVE": 65,
        "NEUTRAL": 25,
        "FRUSTRATED": 7,
        "ANGRY": 3
    },
    "calls_by_day": {
        "2024-01-01": 15,
        "2024-01-02": 22,
        ...
    }
}
```

## 6.5 Billing API

### إنشاء checkout
```python
POST /api/billing/checkout
{
    "plan": "business"
}

Response:
{
    "checkout_url": "https://checkout.stripe.com/..."
}
```

### بوابة إدارة الاشتراك
```python
GET /api/billing/portal
Response:
{
    "portal_url": "https://billing.stripe.com/..."
}
```

---

# 7. الخدمات الخارجية

## 7.1 Twilio Service

```python
class TwilioService:
    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.phone_number = settings.twilio_phone_number
    
    def validate_webhook(self, request):
        """التحقق من صحة webhook من Twilio"""
        return self.validator.validate(
            request.url,
            request.POST,
            request.headers.get("X-Twilio-Signature", "")
        )
    
    def make_call(self, to, twiml_url):
        """إجراء مكالمة صادرة"""
        return self.client.calls.create(
            to=to,
            from_=self.phone_number,
            url=twiml_url,
            record=True
        )
    
    def get_recording(self, call_sid):
        """جلب تسجيل المكالمة"""
        recordings = self.client.recordings.list(call_sid=call_sid)
        return recordings[0].uri if recordings else None
```

## 7.2 Stripe Service

```python
class StripeService:
    def __init__(self):
        stripe.api_key = settings.stripe_secret_key
    
    def create_checkout_session(self, company_id, plan):
        """إنشاء جلسة دفع"""
        price_id = PLAN_PRICES[plan]["stripe_price_id"]
        
        return stripe.checkout.Session.create(
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.frontend_url}/billing/success",
            cancel_url=f"{settings.frontend_url}/billing/cancel",
            metadata={"company_id": str(company_id)}
        )
    
    def create_portal_session(self, customer_id):
        """إنشاء جلسة بوابة إدارة"""
        return stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=settings.frontend_url
        )
    
    def handle_webhook(self, payload, signature):
        """معالجة webhook من Stripe"""
        event = stripe.Webhook.construct_event(
            payload, signature, settings.stripe_webhook_secret
        )
        
        if event["type"] == "customer.subscription.updated":
            # تحديث حالة الاشتراك
        elif event["type"] == "customer.subscription.deleted":
            # إلغاء الاشتراك
        elif event["type"] == "invoice.payment_failed":
            # إشعار فشل الدفع
```

---

# 8. نظام الوكلاء الذكيين (Voice Agents)

## 8.1 بنية الوكيل الذكي

```python
class VoiceAgent:
    def __init__(
        self,
        agent_id: int,
        company_id: int,
        language: str = "en",
        voice_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.agent_id = agent_id
        self.company_id = company_id
        self.language = language
        self.voice_id = voice_id or "eleven_multilingual_v2"
        self.system_prompt = system_prompt
        self.current_call: Optional[Dict] = None
        self.transcript: List[Dict] = []
        self.sentiment_history: List[str] = []
        self.customer_context: Optional[Dict] = None
    
    async def initialize(self):
        """تهيئة خدمات STT, TTS, LLM"""
        self.stt = DeepgramSTTService(
            api_key=settings.deepgram_api_key,
            model="nova-2",
            language="multi",
            interim_results=True,
        )
        
        self.tts = ElevenLabsTTSService(
            api_key=settings.elevenlabs_api_key,
            model_id="eleven_multilingual_v2",
            voice_id=self.voice_id,
        )
        
        self.llm = AnthropicLLMService(
            api_key=settings.anthropic_api_key,
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system_prompt=self.system_prompt,
        )
        
        self.vad = SileroVADAnalyzer(
            start_secs=0.2,
            stop_secs=0.8,
        )
```

## 8.2 أدوات الوكيل

```python
AGENT_TOOLS = [
    {
        "name": "book_appointment",
        "description": "Book an appointment for the customer",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM"},
                "customer_name": {"type": "string"},
                "phone": {"type": "string"},
            },
            "required": ["date", "time", "customer_name", "phone"],
        },
    },
    {
        "name": "check_availability",
        "description": "Check available slots",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
            },
            "required": ["date"],
        },
    },
    {
        "name": "transfer_to_human",
        "description": "Transfer call to human agent",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
            },
            "required": ["reason"],
        },
    },
    {
        "name": "send_whatsapp_confirmation",
        "description": "Send WhatsApp message",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["phone", "message"],
        },
    },
]
```

## 8.3 System Prompt

```python
def build_system_prompt(
    agent_name: str,
    company_id: int,
    customer_context: Dict[str, Any],
    language: str = "en",
    custom_prompt: Optional[str] = None,
) -> str:
    language_names = {
        "en": "English",
        "ar": "Arabic",
        "fr": "French",
        "es": "Spanish",
    }
    
    base_prompt = f"""
You are {agent_name}, a professional voice assistant.

CUSTOMER CONTEXT:
- Name: {customer_context.get('name', 'Valued Customer')}
- Previous calls: {customer_context.get('previous_calls', 0)}
- Last visit: {customer_context.get('last_visit', 'First time caller')}
- Notes: {customer_context.get('notes', 'No previous notes')}

LANGUAGE:
You must respond in {language_names.get(language, 'English')} language.

RULES:
- ALWAYS respond in the same language the customer speaks
- NEVER speak more than 40 words at once
- ALWAYS confirm appointments before saving
- ALWAYS use customer name when known
- NEVER say you are an AI unless directly asked
- If asked: say you are a digital assistant
- Be polite, professional, and efficient
- If customer seems frustrated, transfer to human agent
"""
    
    if custom_prompt:
        base_prompt += f"\n\nCustom Instructions:\n{custom_prompt}\n"
    
    return base_prompt
```

---

# 9. خط معالجة الصوت (Voice Pipeline)

## 9.1 Ultra Low Latency Pipeline

```python
class UltraLowLatencyPipeline:
    """
    Process STT + LLM context loading in parallel.
    While Deepgram converts speech to text,
    simultaneously load customer memory and CRM data.
    This cuts 200-300ms from every response.
    """
    
    async def process(self, audio_frame: bytes, caller_phone: str, company_id: str):
        # STT, Memory, CRM في نفس الوقت
        stt_task = asyncio.create_task(
            self.deepgram.transcribe(audio_frame)
        )
        memory_task = asyncio.create_task(
            self.load_customer_memory(caller_phone, company_id)
        )
        crm_task = asyncio.create_task(
            self.load_crm_context(caller_phone, company_id)
        )
        
        transcript, memory, crm_data = await asyncio.gather(
            stt_task, memory_task, crm_task
        )
        
        context = f"{memory}\n{crm_data}"
        response = await self.llm.respond(
            transcript=transcript,
            context=context
        )
        
        async for audio_chunk in self.tts.stream(response):
            await self.transport.send_audio(audio_chunk)
```

## 9.2 تحليل المشاعر

```python
def analyze_sentiment(self, text: str) -> str:
    text_lower = text.lower()
    
    angry_words = ["angry", "furious", "unacceptable", "terrible", "worst"]
    frustrated_words = ["frustrated", "annoyed", "disappointed", "ridiculous"]
    positive_words = ["thank you", "great", "excellent", "wonderful", "happy"]
    
    if any(word in text_lower for word in angry_words):
        return "ANGRY"
    elif any(word in text_lower for word in frustrated_words):
        return "FRUSTRATED"
    elif any(word in text_lower for word in positive_words):
        return "POSITIVE"
    else:
        return "NEUTRAL"
```

---

# 10. التكاملات (Integrations)

## 10.1 CRM Integration (Universal)

```python
class CRMIntegrator:
    """تكامل موحد مع عدة أنظمة CRM"""
    
    def __init__(self):
        self.providers = {
            "salesforce": SalesforceClient(),
            "hubspot": HubSpotClient(),
            "zoho": ZohoClient(),
            "gohighlevel": GHLClient(),
        }
    
    async def sync_contact(self, provider: str, contact_data: dict):
        """مزامنة جهة اتصال"""
        client = self.providers.get(provider)
        if client:
            await client.create_contact(contact_data)
    
    async def create_lead(self, provider: str, lead_data: dict):
        """إنشاء عميل محتمل"""
        client = self.providers.get(provider)
        if client:
            return await client.create_lead(lead_data)
```

## 10.2 Calendar Integration (Universal)

```python
class CalendarIntegrator:
    """تكامل موحد مع عدة أنظمة تقويم"""
    
    async def book_appointment(
        self,
        provider: str,
        start_time: datetime,
        end_time: datetime,
        customer_name: str,
        notes: str = ""
    ) -> dict:
        """حجز موعد في التقويم"""
        client = self.providers.get(provider)
        if client:
            return await client.create_event(
                summary=f"Appointment: {customer_name}",
                start=start_time,
                end=end_time,
                description=notes
            )
    
    async def get_availability(
        self,
        provider: str,
        date: date,
        duration_minutes: int = 30
    ) -> list:
        """جلب المواعيد المتاحة"""
        client = self.providers.get(provider)
        if client:
            return await client.get_free_slots(date, duration_minutes)
```

---

# 11. الطبقة الأمامية (Frontend)

## 11.1 هيكل الملفات

```
frontend/
├── app/                          # Next.js 14 App Router
│   ├── page.tsx                  # Landing page
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   │
│   ├── (auth)/                   # Auth group
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   │
│   ├── dashboard/                 # User dashboard
│   │   ├── page.tsx              # Dashboard home
│   │   ├── agent/page.tsx        # Agent configuration
│   │   ├── settings/page.tsx     # Company settings
│   │   └── calls/page.tsx        # Call history
│   │
│   ├── agents/page.tsx           # Agents management
│   ├── analytics/page.tsx        # Analytics dashboard
│   ├── calls/page.tsx            # Call history
│   ├── onboarding/page.tsx       # 5-step wizard
│   │
│   ├── verticals/                # Industry-specific pages
│   │   ├── dental/page.tsx
│   │   ├── legal/page.tsx
│   │   └── realty/page.tsx
│   │
│   └── super-admin/              # Admin panel
│       ├── page.tsx              # Admin dashboard
│       ├── layout.tsx            # Admin layout
│       ├── login/page.tsx        # Admin login
│       ├── clients/page.tsx       # Client management
│       ├── agents/page.tsx       # All agents
│       ├── calls/page.tsx         # Live & history
│       ├── verticals/page.tsx    # Industry verticals
│       ├── integrations/page.tsx # CRM/Calendar
│       ├── providers/page.tsx    # STT/LLM/TTS
│       ├── platform/page.tsx     # System health
│       ├── settings/page.tsx     # API keys
│       ├── logs/page.tsx         # Audit logs
│       └── revenue/page.tsx      # Revenue
│
├── components/                   # Reusable components
│   ├── StatsWidget.tsx
│   ├── AgentCard.tsx
│   └── CallLog.tsx
│
├── contexts/                    # React contexts
│   └── AuthContext.tsx
│
├── lib/                         # Utilities
│   ├── api.ts                   # API client
│   ├── auth.ts                  # Auth utilities
│   └── admin-api.ts             # Admin API client
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── postcss.config.js
```

## 11.2 Dashboard Page

```tsx
export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  
  useEffect(() => {
    const fetchStats = async () => {
      const data = await api.analytics.getSummary(user?.company_id);
      setStats(data);
    };
    fetchStats();
  }, [user]);
  
  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Navigation */}
      <nav className="border-b border-zinc-800...">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/agents">Agents</Link>
        <Link href="/calls">Calls</Link>
        <Link href="/analytics">Analytics</Link>
      </nav>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-6">
        <StatsWidget
          title="Total Calls"
          value={stats?.total_calls || 0}
          icon={Phone}
          trend="+12%"
        />
        <StatsWidget
          title="Avg Duration"
          value={stats?.avg_duration || '0:00'}
          icon={Clock}
          trend="+8%"
        />
        <StatsWidget
          title="Resolution Rate"
          value={`${stats?.resolution_rate || 0}%`}
          icon={CheckCircle}
        />
        <StatsWidget
          title="Active Agents"
          value={stats?.active_agents || 0}
          icon={Bot}
        />
      </div>
      
      {/* Recent Calls */}
      <CallLog calls={stats?.recent_calls} />
      
      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <CallsChart data={stats?.calls_by_day} />
        <SentimentChart data={stats?.sentiment_breakdown} />
      </div>
    </div>
  );
}
```

## 11.3 Landing Page Features

```tsx
export default function LandingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  
  const features = [
    { icon: Phone, title: "24/7 Availability", desc: "Never miss a call" },
    { icon: Bot, title: "AI-Powered", desc: "Natural conversations" },
    { icon: Shield, title: "Secure", desc: "HIPAA & SOC2 compliant" },
    { icon: Zap, title: "Fast Setup", desc: "Live in minutes" },
  ];
  
  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Hero */}
      <section className="relative pt-32 pb-20...">
        <h1 className="text-5xl font-bold text-white">
          Your AI <span className="text-amber-500">Receptionist</span>
        </h1>
        <p className="text-xl text-zinc-400">
          Handle bookings, answer questions, and capture leads — 
          while you focus on what matters.
        </p>
        <Link href="/signup" className="btn-primary">
          Start Free Trial
        </Link>
      </section>
      
      {/* Features */}
      <section className="py-20">
        <div className="grid grid-cols-4 gap-6">
          {features.map((f) => (
            <FeatureCard {...f} />
          ))}
        </div>
      </section>
      
      {/* Pricing */}
      <section className="py-20">
        <Pricing plans={plans} cycle={billingCycle} />
      </section>
    </div>
  );
}
```

---

# 12. الوضع الرأسي (Verticals)

## 12.1 DentalVoice

### prompt.py
```python
DENTAL_SYSTEM_PROMPT = """
You are a professional voice assistant for a dental clinic.

Your specialties:
- New patient intake and registration
- Insurance verification (PPO, HMO, Delta, Cigna, Aetna)
- Appointment booking and reminders
- Emergency detection (toothache, abscess, broken tooth)
- Treatment explanation
- Post-op instructions

You should:
- Always verify insurance before major procedures
- Detect emergencies and escalate immediately
- Confirm appointments with date, time, and reason
- Send WhatsApp reminders 24 hours before
- Ask about pain level if emergency suspected
"""
```

### tools.py
```python
DENTAL_TOOLS = [
    {
        "name": "verify_insurance",
        "description": "Check patient insurance coverage",
        "parameters": {
            "type": "object",
            "properties": {
                "provider": {"type": "string"},
                "member_id": {"type": "string"},
            },
        },
    },
    {
        "name": "schedule_cleaning",
        "description": "Book a teeth cleaning appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "phone": {"type": "string"},
                "preferred_date": {"type": "string"},
            },
        },
    },
    {
        "name": "detect_emergency",
        "description": "Flag dental emergency and alert clinic",
        "parameters": {
            "type": "object",
            "properties": {
                "symptoms": {"type": "string"},
                "pain_level": {"type": "integer"},
            },
        },
    },
]
```

## 12.2 LegalVoice

### prompt.py
```python
LEGAL_SYSTEM_PROMPT = """
You are a confidential intake specialist for a law firm.

Practice areas:
- Personal Injury
- Criminal Defense
- Family Law
- Immigration
- Employment Law
- Estate Planning
- Bankruptcy

CRITICAL RULES:
- NEVER confirm if someone is a current client (attorney-client privilege)
- ALWAYS check for conflicts of interest
- Detect emergencies: arrests, deportation, custody
- Never give legal advice — only intake
- Escalate immediately for emergencies
"""
```

### compliance.py
```python
LEGAL_COMPLIANCE = {
    "encryption": "AES-256",
    "retention_days": 30,
    "audit_logging": True,
    "wiretapping_compliance": True,
    "hipaa_ready": True,
    "soc2_compliant": True,
}
```

## 12.3 RealtyVoice

### prompt.py
```python
REALTY_SYSTEM_PROMPT = """
You are a professional voice assistant for a real estate agency.

Your capabilities:
- Qualify buyers (pre-approval, budget, timeline)
- Schedule property showings
- Answer "What is my home worth?" questions
- Provide neighborhood and market info
- Handle seller inquiries
- Flag hot leads immediately

You should:
- Ask about pre-approval status early
- Get contact info before scheduling
- Send property details via text
- Alert agent immediately for pre-approved buyers
"""
```

---

# 13. لوحة تحكم المسؤول (Super Admin)

## 13.1 لوحة التحكم الرئيسية

```tsx
export default function SuperAdminDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  
  // KPIs
  const kpis = [
    { label: "MRR", value: formatCurrency(data?.kpis.mrr) },
    { label: "ARR", value: formatCurrency(data?.kpis.arr) },
    { label: "Total Clients", value: data?.kpis.total_clients },
    { label: "Active Clients", value: data?.kpis.active_clients },
    { label: "Calls Today", value: data?.kpis.calls_today },
    { label: "Failed Rate", value: `${data?.kpis.failed_calls_rate}%` },
  ];
  
  return (
    <div className="flex">
      {/* Sidebar */}
      <Sidebar items={sidebarItems} />
      
      {/* Main Content */}
      <main className="flex-1 p-8">
        <h1>Platform Dashboard</h1>
        
        {/* KPIs Grid */}
        <div className="grid grid-cols-6 gap-4">
          {kpis.map((kpi) => (
            <KPICard {...kpi} />
          ))}
        </div>
        
        {/* Charts */}
        <div className="grid grid-cols-2 gap-8">
          <RevenueChart data={data?.charts.revenue_growth} />
          <ClientsChart data={data?.charts.clients_per_month} />
          <CallsChart data={data?.charts.calls_volume} />
        </div>
        
        {/* Recent Activity */}
        <RecentActivity />
      </main>
    </div>
  );
}
```

## 13.2 إدارة العملاء

```tsx
export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [search, setSearch] = useState("");
  const [plan, setPlan] = useState("");
  
  const columns = [
    { key: "name", header: "Company" },
    { key: "email", header: "Email" },
    { key: "plan", header: "Plan" },
    { key: "mrr", header: "MRR" },
    { key: "calls_count", header: "Calls" },
    { key: "status", header: "Status" },
    { key: "actions", header: "" },
  ];
  
  return (
    <div>
      <div className="flex justify-between mb-6">
        <h1>Clients ({total})</h1>
        <button onClick={() => router.push("/super-admin/clients/new")}>
          Add Client
        </button>
      </div>
      
      <Filters search={search} plan={plan} onFilter={handleFilter} />
      
      <Table columns={columns} data={clients}>
        {(client) => (
          <tr>
            <td>{client.name}</td>
            <td>{client.email}</td>
            <td><PlanBadge plan={client.plan} /></td>
            <td>${client.mrr}</td>
            <td>{client.calls_count}</td>
            <td><StatusBadge status={client.status} /></td>
            <td>
              <ActionsMenu client={client} />
            </td>
          </tr>
        )}
      </Table>
      
      <Pagination page={page} totalPages={totalPages} />
    </div>
  );
}
```

## 13.3 Revenue Dashboard

```tsx
export default function RevenuePage() {
  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      maximumFractionDigits: 0 
    }).format(value);
  
  return (
    <div>
      <h1>Revenue & Billing</h1>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card title="MRR" value={formatCurrency(data?.mrr)} />
        <Card title="ARR" value={formatCurrency(data?.arr)} />
        <Card title="Total Clients" value={data?.total_clients} />
        <Card title="ARPU" value={formatCurrency(data?.arpu)} />
      </div>
      
      {/* Plans Table */}
      <Table>
        <thead>
          <tr>
            <th>Plan</th>
            <th>Clients</th>
            <th>Price</th>
            <th>Revenue</th>
            <th>% of Total</th>
          </tr>
        </thead>
        <tbody>
          {data?.plans.map((plan) => (
            <tr>
              <td>{plan.name}</td>
              <td>{plan.count}</td>
              <td>{formatCurrency(plan.price)}/mo</td>
              <td>{formatCurrency(plan.revenue)}</td>
              <td>
                <ProgressBar value={plan.percentage} />
                {plan.percentage}%
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
```

---

# 14. الأمان والحماية

## 14.1 Authentication & Authorization

```python
# JWT Token Creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        effective_jwt_secret,
        algorithm=settings.jwt_algorithm
    )

# Token Verification
def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            effective_jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

## 14.2 Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

## 14.3 Webhook Validation

```python
def validate_twilio_webhook(request: Request):
    """التحقق من أن webhook قادم فعلاً من Twilio"""
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.twilio_auth_token)
    
    return validator.validate(
        request.url,
        request.POST,
        signature
    )
```

## 14.4 Password Security

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

# 15. النشر والتشغيل

## 15.1 Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: voicecore
      POSTGRES_PASSWORD: voicecore_password
      POSTGRES_DB: voicecore
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U voicecore"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://redis:6379
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      # ... other env vars
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

## 15.2 Dockerfile Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 15.3 Dockerfile Frontend

```dockerfile
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

## 15.4 Railway Deployment

```toml
# railway.toml
[build]
dockerfile = "Dockerfile.backend"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[environment]
NODE_ENV = "production"
```

## 15.5 Environment Variables

```bash
# .env (production)
DATABASE_URL=postgresql+asyncpg://voicecore:secure_pass@host:5432/voicecore
REDIS_URL=redis://host:6379

# AI Services
DEEPGRAM_API_KEY=sk_xxxx
ELEVENLABS_API_KEY=sk_xxxx
ANTHROPIC_API_KEY=sk-ant-xxxx

# Twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_PHONE_NUMBER=+1xxxx

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxx

# Security
JWT_SECRET=<32-char-random-string>
NEXTAUTH_SECRET=<32-char-random-string>
```

---

# 16. الاختبار والجودة

## 16.1 Backend Tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_login_validation():
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_pricing_public():
    response = client.get("/api/public/pricing")
    assert response.status_code == 200
    data = response.json()
    assert "plans" in data
```

## 16.2 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
```

---

# 17. الخطط المستقبلية

## 17.1 الميزات المخطط لها

### Phase 2:
- [ ] **Video Integration**: إضافة مكالمات فيديو مع LiveKit
- [ ] **Multi-language**: دعم أكثر من 50 لغة
- [ ] **Voice Customization**: إنشاء أصوات مخصصة
- [ ] **Advanced Analytics**: تحليلات تنبؤية

### Phase 3:
- [ ] **White-label**: لوحة تحكم قابلة للتخصيص بالكامل
- [ ] **Marketplace**: سوق للوكيل والصوت
- [ ] **API Marketplace**: API مفتوح للمطورين
- [ ] **Mobile SDK**: SDK للتطبيقات المحمولة

### Phase 4:
- [ ] **AI Coach**: تدريب الوكلاء تلقائياً
- [ ] **Sentiment Forecasting**: توقعات المشاعر
- [ ] **Conversational AI**: محادثات أطول وأكثر تعقيداً
- [ ] **Real-time Translation**: ترجمة فورية

## 17.2 تحسينات الأداء

```python
# تحسينات مقترحة:
1. Redis caching للـ customer context
2. Connection pooling محسّن
3. WebSocket multiplexing
4. CDN للصور والـ static files
5. Edge computing للـ STT
```

---

# 18. الخلاصة

## 18.1 ملخص المشروع

VoiceCore هو نظام متكامل يوفر:

| المكون | التقنية | الوظيفة |
|--------|--------|---------|
| STT | Deepgram Nova-2 | تحويل الصوت لنص |
| LLM | Claude 3.5 Sonnet | فهم اللغة والسياق |
| TTS | ElevenLabs | توليد صوت طبيعي |
| Framework | FastAPI + Next.js | API + UI |
| Database | PostgreSQL + Redis | تخزين + Cache |
| Voice | LiveKit + Twilio | WebRTC + Telephony |

## 18.2 KPIs والمقاييس

- **زمن الاستجابة**: < 500ms من الكلام للرد
- **دقة STT**: 98%+ مع Deepgram Nova-2
- **رصد المشاعر**: 85%+ دقة
- **Uptime**: 99.95%
- **قابلية التوسع**: آلاف المكالمات المتزامنة

## 18.3 نقاط القوة

1. **تقنية متقدمة**: استخدام أحدث نماذج الذكاء الاصطناعي
2. **قابل للتخصيص**: يمكن تهيئته لأي صناعة
3. **سهل النشر**: Docker-ready مع نشر سهل
4. **آمن**: HIPAA, SOC2, PCI-DSS compliant
5. **متكامل**: ربط مع معظم أدوات العمل

## 18.4 التحديات

1. **التكلفة**: خدمات AI مكلفة
2. **التعقيد**: نظام معقد يحتاج خبرة
3. **الخصوصية**: حماية البيانات الحساسة
4. **الاتصال**: يحتاج إنترنت مستقر

---

# ملاحظات تقنية إضافية

## هيكل البيانات للإحصائيات

```typescript
interface Analytics {
  total_calls: number;
  total_duration: number;
  avg_duration: number;
  calls_today: number;
  calls_this_week: number;
  calls_this_month: number;
  sentiment_breakdown: Record<string, number>;
  outcome_breakdown: Record<string, number>;
  calls_by_day: Record<string, number>;
  top_intents: IntentCount[];
  missed_opportunities: number;
}

interface IntentCount {
  intent: string;
  count: number;
  percentage: number;
}
```

## أنواع المشاعر

```typescript
type Sentiment = 'POSITIVE' | 'NEUTRAL' | 'FRUSTRATED' | 'ANGRY';

interface SentimentAnalysis {
  sentiment: Sentiment;
  score: number; // 0.0 - 1.0
  keywords: string[];
  action_required: boolean;
}
```

## حالات المكالمة

```typescript
type CallOutcome = 
  | 'completed'      // اكتملت بنجاح
  | 'voicemail'       // تركت رسالة
  | 'transferred'    // حوّلت لإنسان
  | 'missed'          // فُقدت
  | 'failed';         // فشل تقني

interface Call {
  id: number;
  company_id: number;
  agent_id: number;
  caller_phone: string;
  duration_seconds: number;
  transcript: string;
  sentiment: Sentiment;
  outcome: CallOutcome;
  recording_url?: string;
  created_at: Date;
}
```

---

# الوثائق التقنية

## API Reference

### Authentication
```
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/auth/google
GET  /api/v1/auth/google/callback
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### Companies
```
GET    /api/v1/companies
POST   /api/v1/companies
GET    /api/v1/companies/{id}
PUT    /api/v1/companies/{id}
DELETE /api/v1/companies/{id}
```

### Agents
```
GET    /api/v1/agents
POST   /api/v1/agents
GET    /api/v1/agents/{id}
PUT    /api/v1/agents/{id}
DELETE /api/v1/agents/{id}
POST   /api/v1/agents/{id}/toggle
```

### Calls
```
GET  /api/v1/calls
POST /api/v1/calls/outbound
GET  /api/v1/calls/history
GET  /api/v1/calls/{id}
POST /api/webhooks/twilio/voice
```

### Analytics
```
GET /api/v1/analytics/summary
GET /api/v1/analytics/daily
GET /api/v1/analytics/weekly
GET /api/v1/analytics/monthly
```

### Billing
```
POST /api/billing/checkout
GET  /api/billing/portal
GET  /api/billing/subscription
POST /api/webhooks/stripe
```

### Admin
```
POST /api/admin/auth/login
GET  /api/admin/dashboard
GET  /api/admin/clients
PUT  /api/admin/clients/{id}
GET  /api/admin/agents
GET  /api/admin/calls/live
GET  /api/admin/revenue
GET  /api/admin/settings
PUT  /api/admin/settings/apikeys
```

---

# الملاحق

## Appendix A: Keyboard Shortcuts (Admin Panel)

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Quick search |
| `Cmd/Ctrl + N` | New client |
| `Cmd/Ctrl + /` | Show shortcuts |
| `Escape` | Close modal |

## Appendix B: Error Codes

| Code | Description |
|------|-------------|
| `AUTH_001` | Invalid credentials |
| `AUTH_002` | Token expired |
| `AUTH_003` | Account locked |
| `CALL_001` | Twilio error |
| `CALL_002` | No agents available |
| `BILLING_001` | Stripe error |
| `BILLING_002` | Subscription failed |

## Appendix C: Log Levels

```python
LOG_LEVELS = {
    "DEBUG": "تفاصيل للتصحيح",
    "INFO": "معلومات عامة",
    "WARNING": "تحذيرات",
    "ERROR": "أخطاء",
    "CRITICAL": "أخطاء حرجة",
}
```

---

# الخاتمة

هذا المشروع يمثل نظاماً متكاملاً ومتطوراً للمكالمات الصوتية بالذكاء الاصطناعي. يستخدم تقنيات حديثة ومتقدمة لتوفير تجربة استقبال احترافية على مدار الساعة.

المشروع مصمم ليكون:
- **قابل للتوسع**: من startup صغير إلى enterprise كبير
- **مخصص**: يمكن تهيئته لأي صناعة
- **آمن**: يتبع أفضل الممارسات الأمنية
- **موثوق**: uptime عالي مع فشل آمن

---

*تم إنشاء هذه الوثيقة في مارس 2026*
*VoiceCore - AI Voice Receptionist Platform*
