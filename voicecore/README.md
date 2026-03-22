# 🎙️ VoiceCore - Enterprise AI Voice Platform

<div align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success" alt="Production Ready" />
  <img src="https://img.shields.io/badge/Framework-Next.js%2014-blue" alt="Next.js" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-green" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Security-A%2B-brightgreen" alt="Security A+" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-blue" alt="PostgreSQL" />
</div>

<br/>

**VoiceCore** is an enterprise-grade highly scalable B2B platform that provides smart AI conversational agents capable of conducting human-like calls asynchronously over the phone or WhatsApp.

---

## 🔥 Enterprise Features

- **Robout Automated Call Center**: Replaces manual receptionist work with powerful autonomous AI nodes that learn from the company's knowledge base.
- **Bank-Level Security**: Fully encrypted JWT-based authentication system, bcrypt hashed credentials, and advanced REST API Cross-Origin security.
- **DDoS Mitigation**: Engineered with automatic robust Rate-Limiting capabilities via `SlowAPI` safeguarding all public/private endpoints.
- **Self-Healing Auto-Migrations**: Includes an intelligent `init_db.py` layer ensuring that your schema is up to date dynamically without downtime.
- **Enterprise Deep Analytics**: Offers a completely data-driven UI rendering granular real-time statistics out of user call trends and behaviors.
- **Streamlined Configuration**: Instantly handles deployments across complex environments with a sophisticated 1-click startup automation script `start.bat`.

---

## 🛠️ Technology Stack

**Frontend Layer**
- React 18 / Next.js (App Router paradigm)
- Enterprise Typography (`Outfit` & `Inter`)
- Custom React Hooks Contextual Authentication (`AuthContext`)
- Tailwind CSS w/ custom global variable theming
- Recharts (Rich UI Visualization)

**Backend Architecture**
- FastAPI (High-performance API operations)
- SQLAlchemy 2.0 (ORM) 
- PyJWT Authentication
- Structlog (Enterprise-grade asynchronous logging standard)
- Uvicorn (Lightning-fast ASGI interface)

---

## 🚀 Quick Start Guide (Windows)

We have streamlined the setup pipeline specifically for Windows environments via our autonomous engine execution standard.

1. **Clone the Source Code**
2. **Execute the Smart Startup Batch:**
   Double-click the `start.bat` file in the root directory.
   
The magic startup script will automatically:
- Construct a pristine Python Virtual Environment (`venv`).
- Intermittently install all required Backend / UI dependencies.
- Engage backend databases and auto-migrate them seamlessly.
- Expose the Backend and Frontend on concurrent processes.

### Service Ports
- **Application Portal:** `http://localhost:3000`
- **FastAPI Operations Hub:** `http://localhost:8000/docs`

---

## 🔐 Advanced System Administration

If you need to configure custom API keys for conversational engines:
1. Copy `.env.example` to `.env` inside the root directory.
2. Complete your `DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY` and Twilio endpoints.
3. The platform natively restricts CORS access exclusively to your specified `FRONTEND_URL` environment string. 

<br/>

### *Designed for scale, perfected for humans.*
