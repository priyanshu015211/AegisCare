# AegisCare — Technical Architecture Document

**Version:** 1.0  
**Date:** August 21, 2026  
**Status:** Draft  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Tech Stack & Reasoning](#2-tech-stack--reasoning)
3. [Complete File & Folder Structure](#3-complete-file--folder-structure)
4. [Database Schema](#4-database-schema)
5. [API Architecture](#5-api-architecture)
6. [Authentication & Security](#6-authentication--security)
7. [Environment Variables & Configuration](#7-environment-variables--configuration)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Data Flow](#9-data-flow)
10. [Performance & Scaling Notes](#10-performance--scaling-notes)

---

## 1. Architecture Overview

AegisCare follows a **clean three-tier architecture** with strict separation of concerns:

```
┌──────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Streamlit Frontend (Python)                             │    │
│  │  Pages: Triage │ Dashboard │ Emergency Center │ Analytics │    │
│  │  Components: Cards │ Layout │ Sidebar                     │    │
│  │  Talks to backend via HTTP (httpx)                       │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                              │ HTTP REST
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                         │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐      │
│  │  API Layer   │  │ Service Layer│  │    AI Layer       │      │
│  │  (FastAPI)   │  │ (Business    │  │  (Gemini/GPT-4o)  │      │
│  │              │──│  Logic)      │──│                   │      │
│  │  /api/v1/*   │  │              │  │  Reasoning Engine │      │
│  │  Middleware:  │  │ PatientSvc   │  │  Drift Detection  │      │
│  │  - CORS      │  │ DriftSvc     │  │  Risk Scoring     │      │
│  │  - Timing    │  │ RiskSvc      │  │  Prompt Builder   │      │
│  │  - Logging   │  │ Escalation   │  │  Memory Manager   │      │
│  │  - Security  │  │ Voice        │  │                   │      │
│  │  - Errors    │  │ AI           │  └───────────────────┘      │
│  └─────────────┘  └──────────────┘                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Voice Pipeline                                          │    │
│  │  Faster Whisper (STT) → Text → AI → Text → XTTS (TTS)  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Coordination Layer                                      │    │
│  │  Appointment Manager │ Load Balancer │ Handoff Reports   │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────────────────────┐     │
│  │  Supabase         │  │  In-Memory State                 │     │
│  │  (PostgreSQL)     │  │  PatientState (Pydantic models)  │     │
│  │                   │  │  Session Memory (JSON)           │     │
│  │  - patients       │  │  Drift History (per-session)     │     │
│  │  - sessions       │  └──────────────────────────────────┘     │
│  │  - symptom_records│                                         │
│  │  - escalations    │  ┌──────────────────────────────────┐     │
│  │  - appointments   │  │  File System                     │     │
│  │  - doctors        │  │  - logs/ (Loguru rotation)       │     │
│  │  - hospitals      │  │  - voice_pipeline/tts/models/    │     │
│  │  - hospital_load  │  │  - generated PDF reports         │     │
│  │  - reports        │  └──────────────────────────────────┘     │
│  └──────────────────┘                                           │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Service Layer Pattern** — Business logic lives in `backend/services/`, never in route handlers. Routes validate input and delegate to services.
2. **Dependency Injection** — FastAPI `Depends()` wires services as singletons via `backend/api/dependencies/`. Services are testable and swappable.
3. **Token-Optimized Patient State** — The `PatientState` Pydantic model is the ONLY context sent to the LLM (max ~200 tokens). Never the full conversation.
4. **Rule + AI Hybrid** — Escalation decisions use a rule-based engine for speed and determinism, with AI for nuanced reasoning. Rules gate the AI, not the other way around.
5. **Fail-Safe Defaults** — If Supabase is down, the app degrades gracefully (no crash). If Gemini is down, it falls back to GPT-4o-mini. If both are down, rule-based triage still works.

---

## 2. Tech Stack & Reasoning

### Backend

| Technology | Version | Why |
|-----------|---------|-----|
| **Python** | 3.11+ | Required by FastAPI, Streamlit, and the entire ML/AI ecosystem. 3.11 gives structural pattern matching and better error messages. |
| **FastAPI** | 0.111.0 | Async-first, auto-generates OpenAPI docs, native Pydantic v2 validation, built-in dependency injection. The best Python web framework for APIs that need both speed and developer ergonomics. |
| **Uvicorn** | 0.29.0 | ASGI server. Production-grade, supports multiple workers for horizontal scaling. |
| **Pydantic v2** | 2.10.6 | Data validation, serialization, and settings management. v2 is 5-50x faster than v1 due to Rust core. Used for ALL data contracts. |
| **Pydantic Settings** | 2.7.0 | Environment variable loading with type validation. Fails fast on missing/invalid config. |
| **Loguru** | 0.7.2 | Structured logging with rotation, retention, and format control. Far cleaner than stdlib `logging`. |
| **httpx** | 0.24+ | Async HTTP client for frontend-to-backend communication. Modern `requests` replacement. |

### AI / LLM

| Technology | Version | Why |
|-----------|---------|-----|
| **Google Gemini 1.5 Flash** | via `google-genai>=1.10.0` | Primary LLM. Fast inference, large context window, cost-effective for triage. The `google-genai` SDK replaces the deprecated `google-generativeai`. |
| **GPT-4o-mini** | via OpenAI SDK (optional) | Fallback LLM if Gemini is unavailable. Kept as a secondary option for reliability. |
| **Rule-Based Engine** | Custom (Python) | Deterministic escalation logic that runs without any LLM. Always executes first — AI is for nuance, not for safety-critical decisions. |

**Why not GPT-4 as primary?** Cost. At ~$0.15/1M input tokens for Gemini Flash vs ~$2.50/1M for GPT-4o, Gemini Flash is 16x cheaper for a high-volume triage system. The quality difference is negligible for structured symptom analysis.

### Database

| Technology | Version | Why |
|-----------|---------|-----|
| **Supabase** | 2.4+ | Managed PostgreSQL with built-in auth, RLS, real-time subscriptions, and auto-generated REST API. Eliminates the need for a separate ORM, auth service, and API layer for database operations. Free tier handles MVP. |
| **PostgreSQL** | 14+ (via Supabase) | The gold standard for relational data. JSONB support for flexible patient state storage. |

**Why not MongoDB?** Patient data is relational (patients → sessions → symptoms → escalations). SQL gives us ACID transactions, JOINs for reporting, and RLS for security. MongoDB would require manual transaction handling and lacks RLS.

**Why not raw PostgreSQL + SQLAlchemy?** Supabase gives us auth, RLS policies, and a dashboard for free. SQLAlchemy adds complexity without benefit when Supabase handles the ORM layer.

### Frontend

| Technology | Version | Why |
|-----------|---------|-----|
| **Streamlit** | 1.35+ | Rapid prototyping for data-heavy dashboards. Python-native (no context-switching from backend). Built-in session state, file upload, and charting. Perfect for MVP. |
| **Plotly** | 5.20+ | Interactive charts for the command center dashboard and analytics. Used by Streamlit's `st.plotly_chart()`. |
| **Pandas** | 2.0+ | Data manipulation for dashboard aggregations and analytics views. |

**Why not React/Next.js?** MVP velocity. The team already knows Python. Streamlit lets us build a functional dashboard in days, not weeks. We accept the tradeoff (less UI flexibility, harder to customize) because the product value is in the AI engine, not the UI polish.

### Voice

| Technology | Version | Why |
|-----------|---------|-----|
| **Faster Whisper** | 1.0.3 | Open-source STT. Runs server-side on CPU (no GPU required for `base` model). 4x faster than original Whisper with comparable accuracy. |
| **XTTS-v2** | Coqui TTS | High-quality TTS with voice cloning capability. Produces natural-sounding medical responses. |
| **Piper** | Fallback | Lightweight TTS for environments where XTTS is too heavy. Falls back automatically. |

### Infrastructure

| Technology | Version | Why |
|-----------|---------|-----|
| **Docker** | 24+ | Consistent dev/prod environments. Two Dockerfiles: one for backend, one for frontend. |
| **Docker Compose** | 3.9 | Local development orchestration. Spins up backend + frontend with shared networking. |
| **Render** | PaaS | Hosted deployment. Free tier for MVP, scales to paid tiers. Native Python support. |

**Why not AWS/GCP directly?** Too much ops overhead for a 3-person team at MVP stage. Render handles SSL, health checks, auto-deploys, and logging. We can migrate to cloud infra when we need fine-grained control.

---

## 3. Complete File & Folder Structure

```
aegiscare/
│
├── backend/                          # FastAPI backend application
│   ├── __init__.py
│   ├── main.py                       # App entrypoint, middleware stack, lifespan
│   │
│   ├── ai/                           # AI/LLM layer
│   │   ├── memory/                   # Patient memory management
│   │   │   └── patient_memory.py     # In-memory session state, summarization
│   │   ├── prompts/                  # Prompt templates for each LLM role
│   │   │   ├── triage.py             # Adaptive questioning prompts
│   │   │   ├── reasoning.py          # Differential analysis prompts
│   │   │   ├── report.py             # Handoff report generation prompts
│   │   │   └── summary.py            # Memory summarization prompts
│   │   └── reasoning/               # AI reasoning engine
│   │       ├── triage_engine.py      # Adaptive questioning logic
│   │       └── differential.py       # Symptom analysis engine
│   │
│   ├── api/                          # API layer
│   │   ├── __init__.py
│   │   ├── api_v1.py                 # Route aggregator, auth wiring
│   │   ├── dependencies/             # FastAPI dependency injection
│   │   │   ├── __init__.py
│   │   │   └── services.py           # Service singletons (Patient, Risk, Drift, AI, Voice)
│   │   ├── middleware/               # Request processing middleware
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py      # Global exception handling
│   │   │   ├── request_logger.py     # Request/response logging
│   │   │   ├── security_headers.py   # Security headers (CSP, HSTS, etc.)
│   │   │   └── timing.py             # Request duration tracking
│   │   └── routes/                   # Endpoint definitions
│   │       ├── __init__.py
│   │       ├── ai.py                 # AI reasoning endpoints
│   │       ├── health.py             # Public health check endpoints
│   │       ├── patient.py            # Patient CRUD + analysis
│   │       ├── report.py             # Handoff report generation
│   │       ├── system.py             # System status (uptime, version)
│   │       └── voice.py              # Voice pipeline endpoints
│   │
│   ├── core/                         # Shared configuration & utilities
│   │   ├── __init__.py
│   │   ├── auth.py                   # Bearer token authentication
│   │   ├── config.py                 # Pydantic Settings (all env vars)
│   │   ├── constants.py              # Enums, symptom sets, thresholds
│   │   ├── error_responses.py        # Standardized error response formats
│   │   ├── exceptions.py             # Custom exception classes
│   │   └── logging.py                # Loguru setup & logger factory
│   │
│   ├── coordination/                 # Healthcare coordination
│   │   └── appointment_manager.py    # Scheduling, availability, booking
│   │
│   ├── db/                           # Database layer
│   │   ├── __init__.py
│   │   ├── database_service.py       # High-level DB operations
│   │   ├── supabase_client.py        # Supabase client initialization
│   │   └── migrations/               # SQL migration files
│   │       ├── 001_initial_schema.sql
│   │       └── 002_rls_policies.sql
│   │
│   ├── models/                       # Pydantic domain models
│   │   ├── __init__.py
│   │   ├── api_schemas.py            # API request/response models
│   │   ├── hospital.py               # Hospital, Doctor, Load models
│   │   └── patient.py                # PatientState, Session, Symptom models
│   │
│   ├── reports/                      # Report generation
│   │   └── handoff_report.py         # Doctor handoff PDF generation
│   │
│   ├── schemas/                      # API request schemas
│   │   ├── __init__.py
│   │   ├── patient.py                # PatientAnalyzeRequest, PatientUpdateRequest
│   │   └── responses.py              # PatientAnalysisResponse, PatientUpdateResponse
│   │
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── base_service.py           # Base class with logging & error handling
│   │   ├── drift_service.py          # Emergency Drift Detection engine
│   │   ├── patient_service.py        # Patient analysis & state management
│   │   ├── risk_service.py           # Risk scoring & severity classification
│   │   ├── ai/                       # AI-specific services
│   │   │   └── llm_service.py        # Gemini/GPT-4o client wrapper
│   │   ├── escalation/               # Escalation engine
│   │   │   └── escalation_service.py # Alert routing, hospital notification
│   │   └── voice/                    # Voice-specific services
│   │       ├── stt_service.py        # Faster Whisper wrapper
│   │       └── tts_service.py        # XTTS/Piper wrapper
│   │
│   ├── voice/                        # Voice pipeline
│   │   └── __init__.py
│   │
│   └── tests/                        # Backend unit tests
│       └── __init__.py
│
├── frontend/                         # Streamlit frontend application
│   ├── __init__.py
│   ├── app.py                        # Streamlit entrypoint, page routing
│   │
│   ├── components/                   # Reusable UI components
│   │   ├── __init__.py
│   │   ├── cards.py                  # Patient cards, severity badges
│   │   ├── layout.py                 # Page layout & spacing utilities
│   │   └── sidebar.py                # Navigation sidebar
│   │
│   ├── pages/                        # Streamlit pages (multi-page app)
│   │   ├── __init__.py
│   │   ├── analytics.py              # Analytics & reporting views
│   │   ├── coordination_dashboard.py # Appointment & scheduling view
│   │   ├── dashboard.py              # Main hospital command center
│   │   ├── emergency_center.py       # Live escalation queue
│   │   └── patient_triage.py         # Patient triage session UI
│   │
│   ├── styles/                       # Custom CSS
│   │   └── healthcare_theme.css      # Medical-grade color palette
│   │
│   └── utils/                        # Frontend helpers
│       ├── __init__.py
│       ├── api_client.py             # httpx wrapper for backend calls
│       └── formatters.py             # Date/time/number formatting
│
├── voice_pipeline/                   # Voice processing
│   ├── __init__.py
│   ├── audio/                        # Audio capture & playback
│   │   ├── __init__.py
│   │   ├── recorder.py               # Audio input handling
│   │   └── player.py                 # Audio output handling
│   ├── stt/                          # Speech-to-Text
│   │   ├── __init__.py
│   │   └── whisper_engine.py         # Faster Whisper integration
│   └── tts/                          # Text-to-Speech
│       ├── __init__.py
│       ├── xtts_engine.py            # XTTS-v2 engine
│       ├── piper_engine.py           # Piper fallback engine
│       └── models/                   # Pre-downloaded TTS model weights
│
├── project_memory/                   # Architecture & handoff docs
│   ├── api_contracts.md              # API endpoint contracts
│   ├── architecture.md               # High-level architecture decisions
│   ├── current_progress.md           # Phase completion status
│   ├── database_schema.md            # Full DB schema documentation
│   ├── developer_handoff.md          # Onboarding guide for new devs
│   ├── env_setup.md                  # Environment setup instructions
│   ├── feature_status.md             # Feature completion tracking
│   ├── future_tasks.md               # Backlog & roadmap
│   ├── known_issues.md               # Bug tracker & technical debt
│   ├── prompt_context.md             # LLM prompt context docs
│   └── ui_guidelines.md              # UI/UX design guidelines
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── backend/                      # Backend tests
│   │   ├── __init__.py
│   │   ├── test_risk_service.py      # Risk scoring unit tests
│   │   ├── test_drift_service.py     # Drift detection unit tests
│   │   ├── test_patient_api.py       # Patient endpoint integration tests
│   │   └── test_auth.py              # Authentication unit tests
│   └── frontend/                     # Frontend tests
│       └── __init__.py
│
├── docker/                           # Dockerfiles
│   ├── Dockerfile.backend            # Backend container
│   └── Dockerfile.frontend           # Frontend container
│
├── deployment/                       # Deployment configs
│   └── render.yaml                   # Render deployment manifest
│
├── docs/                             # Documentation
│   ├── PRD.md                        # Product Requirements Document
│   ├── TECHNICAL_ARCHITECTURE.md     # This document
│   └── setup.md                      # Setup instructions
│
├── scripts/                          # Dev scripts
│   ├── seed_hospitals.py             # Seed hospital data
│   └── run_migrations.py             # Run SQL migrations
│
├── .env.example                      # Environment variable template
├── .gitignore                        # Git ignore rules
├── docker-compose.yml                # Local dev orchestration
├── LICENSE                           # Project license
├── pytest.ini                        # Pytest configuration
├── render.yaml                       # Render deployment (root copy)
├── requirements.txt                  # Python dependencies
├── runtime.txt                       # Python runtime version
└── README.md                         # Project overview
```

---

## 4. Database Schema

All tables live in Supabase (PostgreSQL). UUIDs are primary keys throughout. Timestamps use `timestamptz` (timezone-aware).

### Entity Relationship Diagram

```
auth.users (Supabase Auth)
    │
    ├─── patients.user_id
    │        │
    │        ├─── sessions.patient_id
    │        │        │
    │        │        ├─── symptom_records.session_id
    │        │        ├─── escalations.session_id
    │        │        ├─── reports.session_id
    │        │        └─── appointments.session_id
    │        │
    │        ├─── symptom_records.patient_id
    │        ├─── escalations.patient_id
    │        ├─── reports.patient_id
    │        └─── appointments.patient_id
    │
    └─── doctors.user_id
             │
             ├─── appointments.doctor_id
             └─── doctors.hospital_id
                      │
                      ├─── hospitals.hospital_id
                      │        └─── hospital_load.hospital_id
                      └─── doctors.hospital_id
```

### Table: `patients`

Stores demographic and medical history for each patient. Linked to Supabase Auth via `user_id`.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `patient_id` | `uuid` | PK, default `gen_random_uuid()` | Unique patient identifier |
| `full_name` | `text` | | Patient's full name |
| `age` | `integer` | | Patient's age |
| `gender` | `text` | | Gender (male/female/other) |
| `phone` | `text` | | Contact phone number |
| `emergency_contact` | `text` | | Emergency contact name/phone |
| `known_conditions` | `text[]` | | Array of chronic conditions (e.g., `{"diabetes", "hypertension"}`) |
| `current_medications` | `text[]` | | Array of current medications |
| `allergies` | `text[]` | | Array of known allergies |
| `user_id` | `uuid` | FK → `auth.users` | Links to Supabase Auth user |
| `created_at` | `timestamptz` | default `now()` | Record creation time |
| `updated_at` | `timestamptz` | default `now()` | Last update time |

**Plain English:** One row per patient. Contains everything a doctor needs to know before seeing them — who they are, what conditions they have, what drugs they take, and what they're allergic to. Each patient has a Supabase Auth account for login.

---

### Table: `sessions`

One row per triage session. A session starts when a patient begins reporting symptoms and ends when a disposition is reached.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `session_id` | `uuid` | PK, default `gen_random_uuid()` | Unique session identifier |
| `patient_id` | `uuid` | FK → `patients` | Which patient this session belongs to |
| `started_at` | `timestamptz` | default `now()` | When the session began |
| `ended_at` | `timestamptz` | nullable | When the session ended (null if active) |
| `turn_count` | `integer` | default `0` | Number of patient-AI exchanges |
| `severity` | `text` | | Current severity: `green`, `yellow`, `red`, `critical` |
| `risk_score` | `integer` | | Current risk score (0-100) |
| `summary` | `text` | | LLM-generated rolling summary of the session |
| `state_json` | `jsonb` | | Serialized `PatientState` — the full in-memory state snapshot |

**Plain English:** Each time a patient starts a triage conversation, a session row is created. As the conversation progresses, `severity` and `risk_score` update in real time. The `summary` field holds an AI-generated summary that shrinks the conversation into a few sentences. The `state_json` field stores the complete patient state as JSON — this is what gets sent to the LLM on each turn.

---

### Table: `symptom_records`

Individual symptom entries within a session. Multiple rows per session.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Record identifier |
| `session_id` | `uuid` | FK → `sessions` | Which session this symptom belongs to |
| `patient_id` | `uuid` | FK → `patients` | Denormalized for query performance |
| `symptom` | `text` | | Symptom name (e.g., "chest pain") |
| `duration` | `text` | nullable | How long the symptom has persisted |
| `severity_note` | `text` | nullable | Patient's own description of severity |
| `category` | `text` | nullable | Symptom category (respiratory/cardiac/neurological/general) |
| `reported_at` | `timestamptz` | default `now()` | When this symptom was reported |

**Plain English:** Every time the patient mentions a symptom, a row is inserted here. This creates a chronological timeline of symptoms — critical for drift detection. The `category` field enables rule-based fast-pathing (e.g., if a cardiac symptom appears after respiratory symptoms, that's a red flag).

---

### Table: `escalations`

Audit log of every escalation event. Created when severity crosses a threshold.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `escalation_id` | `uuid` | PK | Unique escalation identifier |
| `session_id` | `uuid` | FK → `sessions` | Which session triggered this |
| `patient_id` | `uuid` | FK → `patients` | Denormalized for query performance |
| `triggered_at` | `timestamptz` | default `now()` | When the escalation was triggered |
| `severity_at_trigger` | `text` | | Severity level at time of escalation |
| `risk_score_at_trigger` | `integer` | | Risk score at time of escalation |
| `action_taken` | `text` | | What action was taken (alert_doctor, book_appointment, etc.) |
| `symptoms_at_trigger` | `text[]` | | Snapshot of all symptoms at escalation time |
| `resolved` | `boolean` | default `false` | Whether the escalation was resolved |
| `resolved_at` | `timestamptz` | nullable | When it was resolved |
| `notes` | `text` | nullable | Clinician notes on the escalation |

**Plain English:** This is the audit trail. Every time the system escalates a patient (e.g., from GREEN to RED), a row is recorded here with a complete snapshot of what the patient's symptoms were at that moment. This is critical for medical-legal compliance and for retrospective analysis.

---

### Table: `appointments`

Scheduled appointments between patients and doctors.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `appointment_id` | `uuid` | PK | Unique appointment identifier |
| `patient_id` | `uuid` | FK → `patients` | Patient being seen |
| `doctor_id` | `uuid` | FK → `doctors` | Doctor seeing the patient |
| `session_id` | `uuid` | FK → `sessions` | Nullable — the triage session that led to this appointment |
| `scheduled_at` | `timestamptz` | | Appointment date/time |
| `duration_minutes` | `integer` | default `15` | Length of appointment |
| `status` | `text` | | pending, confirmed, in_progress, completed, cancelled, no_show |
| `appointment_type` | `text` | | in_person, video, phone |
| `agora_channel` | `text` | nullable | Agora channel name for video appointments |
| `notes` | `text` | nullable | Appointment notes |
| `created_at` | `timestamptz` | default `now()` | When the appointment was created |

**Plain English:** When a patient needs follow-up care, an appointment is booked here. The `session_id` links back to the triage session so the doctor can review the full history before the appointment. For video appointments, `agora_channel` stores the Agora channel name for the video call.

---

### Table: `doctors`

Doctor profiles and availability status.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `doctor_id` | `uuid` | PK | Unique doctor identifier |
| `full_name` | `text` | | Doctor's full name |
| `specialty` | `text` | | Medical specialty (e.g., "cardiology") |
| `department` | `text` | nullable | Hospital department |
| `hospital_id` | `uuid` | FK → `hospitals` | Hospital they work at |
| `phone` | `text` | nullable | Contact number |
| `email` | `text` | nullable | Contact email |
| `languages` | `text[]` | | Languages spoken (for multilingual matching) |
| `status` | `text` | | available, busy, on_call, offline |
| `user_id` | `uuid` | FK → `auth.users` | Links to Supabase Auth account |
| `created_at` | `timestamptz` | default `now()` | Record creation time |

**Plain English:** One row per doctor. Contains their specialty, which hospital they're at, and their current availability status. The `languages` field is used for future multilingual matching — pairing patients who speak Spanish with doctors who speak Spanish.

---

### Table: `hospitals`

Static hospital profiles. Used for load balancing and routing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `hospital_id` | `uuid` | PK | Unique hospital identifier |
| `name` | `text` | | Hospital name |
| `address` | `text` | | Full address |
| `city` | `text` | | City |
| `phone` | `text` | | Main phone number |
| `latitude` | `float8` | nullable | GPS latitude (for distance calculation) |
| `longitude` | `float8` | nullable | GPS longitude (for distance calculation) |
| `specialties` | `text[]` | | Available specialties |
| `has_emergency` | `boolean` | default `true` | Has emergency department |
| `has_icu` | `boolean` | default `true` | Has ICU |
| `total_beds` | `integer` | | Total bed capacity |
| `created_at` | `timestamptz` | default `now()` | Record creation time |

**Plain English:** Static hospital directory. The `latitude`/`longitude` fields enable proximity-based routing ("find me the nearest hospital with a cardiology department"). The `specialties` array is matched against patient symptoms to route to the right facility.

---

### Table: `hospital_load`

Time-series snapshots of hospital capacity. New row inserted every 5-15 minutes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `uuid` | PK | Snapshot identifier |
| `hospital_id` | `uuid` | FK → `hospitals` | Which hospital |
| `total_capacity` | `integer` | | Total bed capacity |
| `current_occupancy` | `integer` | | Current number of occupied beds |
| `er_capacity` | `integer` | | Emergency department capacity |
| `er_occupancy` | `integer` | | Current ER patients |
| `ambulances` | `integer` | | Ambulances currently available |
| `load_percentage` | `float8` | | Calculated load (occupancy/capacity * 100) |
| `recorded_at` | `timestamptz` | default `now()` | When this snapshot was taken |

**Plain English:** This is a time-series table. Every few minutes, the system snapshots each hospital's current capacity. The `load_percentage` field is what the load balancer uses to decide where to route patients — it always picks the hospital with the lowest load that has the right specialties.

---

### Table: `reports`

Generated doctor handoff reports. One per completed session.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `report_id` | `uuid` | PK | Report identifier |
| `session_id` | `uuid` | FK → `sessions` | Which session generated this report |
| `patient_id` | `uuid` | FK → `patients` | Denormalized for query performance |
| `generated_at` | `timestamptz` | default `now()` | When the report was generated |
| `report_markdown` | `text` | | Full report content in Markdown format |
| `severity_at_close` | `text` | | Final severity level when session ended |
| `risk_score` | `integer` | | Final risk score |

**Plain English:** When a triage session ends, the AI generates a structured report summarizing everything — symptom timeline, drift data, risk assessment, and recommended actions. The report is stored here in Markdown format (easily convertible to PDF) and is sent to the receiving doctor.

---

### Indexes

| Table | Index | Purpose |
|-------|-------|---------|
| `sessions` | `idx_sessions_patient_id` | Fast lookup of all sessions for a patient |
| `sessions` | `idx_sessions_started_at DESC` | Recent sessions first (dashboard) |
| `symptom_records` | `idx_symptom_records_session_id` | Fast lookup of symptoms in a session |
| `escalations` | `idx_escalations_session_id` | Fast lookup of escalations in a session |
| `appointments` | `idx_appointments_patient_scheduled` | Patient's upcoming appointments |
| `hospital_load` | `idx_hospital_load_recorded` | Most recent load snapshot per hospital |

### Row Level Security (RLS)

| Table | Policy | Effect |
|-------|--------|--------|
| `patients` | Owner can read/write their own row | Patients see only their own data |
| `sessions` | Owner can read/write their own sessions | Patients see only their own sessions |
| `doctors` | Read-only to authenticated patients | Patients can view doctor profiles |
| `hospitals` | Read-only to all authenticated users | Everyone sees hospital directory |
| `escalations` | Patient owner + doctors at that hospital | Doctors see escalations for their hospital |
| `reports` | Patient owner + assigned doctor | Only the patient and their doctor see the report |

---

## 5. API Architecture

All endpoints live under `/api/v1/`. Protected routes require a `Bearer` token in the `Authorization` header.

### Endpoint Map

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Backend health check |
| `GET` | `/api/v1/system/status` | No | System status (version, uptime) |
| `GET` | `/api/v1/system/uptime` | No | Server uptime in seconds |
| `POST` | `/api/v1/patient/analyze` | Yes | Initial symptom analysis (creates session) |
| `POST` | `/api/v1/patient/update` | Yes | Add new symptom (runs drift detection) |
| `POST` | `/api/v1/ai/triage` | Yes | AI triage questioning |
| `POST` | `/api/v1/ai/reason` | Yes | Differential reasoning |
| `POST` | `/api/v1/voice/transcribe` | Yes | Audio → text (Whisper STT) |
| `POST` | `/api/v1/voice/synthesize` | Yes | Text → audio (XTTS TTS) |
| `GET` | `/api/v1/report/generate/{session_id}` | Yes | Generate handoff report |

### Request/Response Flow

```
Client (Streamlit)                   Server (FastAPI)
      │                                    │
      │  POST /api/v1/patient/analyze      │
      │  Body: {patient_id, symptoms,      │
      │         duration}                   │
      │───────────────────────────────────▶│
      │                                    │
      │                    ┌───────────────┤
      │                    │ 1. Validate   │
      │                    │    request    │
      │                    │ 2. RiskSvc    │
      │                    │    .calculate │
      │                    │ 3. PatientSvc │
      │                    │    .analyze   │
      │                    │ 4. Create     │
      │                    │    session    │
      │                    │ 5. Persist to │
      │                    │    Supabase   │
      │                    └───────────────┤
      │                                    │
      │  Response: {patient_id,            │
      │    session_id, severity,           │
      │    risk_score, confidence,         │
      │    message}                        │
      │◀───────────────────────────────────│
```

### Middleware Stack (Order Matters)

1. **SecurityHeadersMiddleware** — Adds CSP, HSTS, X-Frame-Options headers
2. **RequestLoggerMiddleware** — Logs method, path, status code, duration
3. **TimingMiddleware** — Adds `X-Process-Time` header to responses
4. **CORSMiddleware** — Handles cross-origin requests from frontend
5. **ErrorHandlerMiddleware** — Catches unhandled exceptions, returns structured JSON errors

---

## 6. Authentication & Security

### Current Implementation (Placeholder)

AegisCare currently uses a **shared-secret Bearer token** (`AEGISCARE_TOKEN` env var). The backend validates the token using `hmac.compare_digest` (constant-time comparison to prevent timing attacks).

```
Client sends:  Authorization: Bearer <AEGISCARE_TOKEN>
Server checks: hmac.compare_digest(token, expected_token)
```

**This is a placeholder.** It works for development and demo but is not production-grade authentication.

### Planned Implementation (Supabase JWT)

The architecture is designed to swap in Supabase JWT validation with zero changes to route handlers:

```python
# backend/core/auth.py (planned)
from supabase import create_client

async def get_current_user(credentials = Depends(bearer_scheme)):
    user = supabase.auth.get_user(credentials.credentials)
    if not user or user.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": user.user.id, "role": user.user.role}
```

The `get_current_user` dependency is applied at the **router level** in `api_v1.py`, so every protected route gets auth automatically without individual `Depends()` annotations.

### Security Measures

| Layer | Measure | Status |
|-------|---------|--------|
| Transport | HTTPS (via Render/Supabase) | Production only |
| Authentication | Shared-secret Bearer token | Placeholder |
| Authentication | Supabase JWT validation | Planned |
| Authorization | Row Level Security (RLS) | Defined, needs deployment |
| API | Rate limiting (60 req/min) | Configured |
| Secrets | No hardcoded values, all via env vars | Implemented |
| Logging | No PHI in logs (symptoms only, no names) | Implemented |
| CORS | Configurable allowed origins | Implemented |
| Headers | Security headers (CSP, HSTS, X-Frame) | Implemented |
| Token comparison | Constant-time `hmac.compare_digest` | Implemented |

---

## 7. Environment Variables & Configuration

All configuration is managed via environment variables, loaded by Pydantic Settings from `.env`. The app **fails fast** on missing required values in production.

### Required Variables (Must Set)

| Variable | Example | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `a3f8c2...` (64 hex chars) | App secret key. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `AEGISCARE_TOKEN` | `b7d1e4...` (64 hex chars) | Bearer token for API auth. Same value for frontend and backend. |
| `SUPABASE_URL` | `https://xyz.supabase.co` | Supabase project URL |
| `SUPABASE_ANON_KEY` | `eyJhbG...` | Supabase anonymous/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbG...` | Supabase service role key (bypasses RLS). **Never expose to frontend.** |
| `GEMINI_API_KEY` | `AIzaSy...` | Google Gemini API key |
| `ALLOWED_ORIGINS` | `https://app.aegiscare.io` | Comma-separated list of frontend domains |

### Optional Variables (Have Defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | `development`, `staging`, `production` |
| `DEBUG` | `false` | Enable debug mode (Swagger docs, verbose errors) |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `BACKEND_PORT` | `8000` | Backend server port |
| `BACKEND_WORKERS` | `1` | Uvicorn worker processes (2x CPUs + 1 rule of thumb) |
| `PRIMARY_LLM` | `gemini` | `gemini` or `openai` |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |
| `OPENAI_MODEL` | `gpt-4o-mini` | Fallback OpenAI model |
| `OPENAI_API_KEY` | (empty) | Only needed if using OpenAI as primary or fallback |
| `LLM_TEMPERATURE` | `0.3` | Lower = more deterministic (good for medical) |
| `LLM_MAX_TOKENS` | `1024` | Max tokens per LLM response |
| `LLM_TIMEOUT_SECONDS` | `30` | LLM request timeout |
| `WHISPER_MODEL_SIZE` | `base` | `tiny`, `base`, `small`, `medium`, `large` |
| `WHISPER_DEVICE` | `cpu` | `cpu` or `cuda` (GPU) |
| `TTS_ENGINE` | `xtts` | `xtts` or `piper` |
| `AGORA_APP_ID` | (empty) | Agora video SDK app ID |
| `AGORA_APP_CERTIFICATE` | (empty) | Agora video SDK certificate |
| `ESCALATION_GREEN_THRESHOLD` | `30` | Risk score 0-30 = GREEN |
| `ESCALATION_YELLOW_THRESHOLD` | `60` | Risk score 31-60 = YELLOW |
| `ESCALATION_RED_THRESHOLD` | `61` | Risk score 61+ = RED |
| `ESCALATION_CRITICAL_THRESHOLD` | `85` | Risk score 85+ = auto-alert |
| `MAX_HOSPITAL_CAPACITY` | `100` | Default max beds per hospital |
| `SESSION_EXPIRY_HOURS` | `24` | Session TTL before auto-cleanup |
| `PATIENT_MEMORY_MAX_TURNS` | `20` | Max conversation turns before summarization |
| `MEMORY_SUMMARY_TRIGGER` | `15` | Summarize after this many turns |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `60` | Per-client rate limit |

### Configuration Hierarchy

```
.env file (local dev)
    ↓
Environment variables (production / Render dashboard)
    ↓
Pydantic Settings (type validation + defaults)
    ↓
get_settings() (cached singleton, called once)
```

**Important:** The `SECRET_KEY` validator will **raise an error in production** if set to `changeme`, `secret`, or empty. In development, it emits a warning instead.

---

## 8. Deployment Architecture

### Local Development

```
┌─────────────────────────────────────┐
│  docker-compose up --build          │
│                                     │
│  ┌──────────────┐ ┌──────────────┐ │
│  │ Backend       │ │ Frontend     │ │
│  │ FastAPI       │ │ Streamlit    │ │
│  │ :8000         │ │ :8501        │ │
│  └──────┬───────┘ └──────┬───────┘ │
│         │                 │         │
│         └────────┬────────┘         │
│                  │                  │
│         ┌────────▼────────┐         │
│         │ Supabase Cloud  │         │
│         │ (hosted)        │         │
│         └─────────────────┘         │
└─────────────────────────────────────┘
```

### Production (Render)

```
┌─────────────────────────────────────────────────────┐
│                    Render PaaS                       │
│                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │ aegiscare-backend    │  │ aegiscare-frontend   │  │
│  │ Web Service          │  │ Web Service          │  │
│  │ Python 3.11          │  │ Python 3.11          │  │
│  │ uvicorn (1 worker)   │  │ Streamlit            │  │
│  │ Port: $PORT (auto)   │  │ Port: $PORT (auto)   │  │
│  │                      │  │                      │  │
│  │ Health: /health      │  │ Health: /_stcore/    │  │
│  │                      │  │        health        │  │
│  └──────────┬──────────┘  └──────────┬──────────┘  │
│             │                         │              │
│             └────────────┬────────────┘              │
│                          │                           │
│              ┌───────────▼───────────┐              │
│              │    Supabase Cloud     │              │
│              │  - PostgreSQL DB      │              │
│              │  - Auth (JWT)         │              │
│              │  - RLS Policies       │              │
│              │  - Realtime (future)  │              │
│              └───────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

### Docker Configuration

**Backend Dockerfile** — Installs Python deps, copies source, runs uvicorn:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** — Installs Python deps, copies source, runs Streamlit:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 9. Data Flow

### Patient Triage Session (End-to-End)

```
Patient                          Frontend                    Backend                     AI/DB
  │                                │                           │                           │
  │  1. "I have a fever and       │                           │                           │
  │     cough for 2 days"         │                           │                           │
  │──────────────────────────────▶│                           │                           │
  │                                │  POST /patient/analyze    │                           │
  │                                │  {symptoms, duration}     │                           │
  │                                │──────────────────────────▶│                           │
  │                                │                           │  RiskSvc.calculate_risk() │
  │                                │                           │──────────────────────────▶│
  │                                │                           │  ◀── {risk_score: 45}     │
  │                                │                           │                           │
  │                                │                           │  PatientSvc.analyze()     │
  │                                │                           │──────────────────────────▶│
  │                                │                           │  ◀── {severity: "yellow"} │
  │                                │                           │                           │
  │                                │                           │  Supabase INSERT session  │
  │                                │                           │──────────────────────────▶│
  │                                │  ◀── {severity, risk,     │                           │
  │  ◀── "I see. Based on your   │     confidence, message}   │                           │
  │  symptoms, I rate this as     │                           │                           │
  │  YELLOW. Let me ask a few     │                           │                           │
  │  more questions..."           │                           │                           │
  │                                │                           │                           │
  │  2. "Now my chest hurts too"  │                           │                           │
  │──────────────────────────────▶│                           │                           │
  │                                │  POST /patient/update     │                           │
  │                                │  {new_symptom: "chest     │                           │
  │                                │   pain"}                  │                           │
  │                                │──────────────────────────▶│                           │
  │                                │                           │  DriftSvc.detect_drift()  │
  │                                │                           │  [fever, cough,           │
  │                                │                           │   chest pain]             │
  │                                │                           │  → DRIFT DETECTED         │
  │                                │                           │  → Severity: YELLOW→RED   │
  │                                │                           │                           │
  │                                │                           │  Supabase INSERT          │
  │                                │                           │  escalation record        │
  │                                │                           │──────────────────────────▶│
  │                                │                           │                           │
  │                                │                           │  ReportSvc.generate()     │
  │                                │                           │  [full patient state →    │
  │                                │                           │   LLM → structured report]│
  │                                │                           │                           │
  │  ◀── "⚠️ ESCALATION: Your    │  ◀── {severity: "red",    │                           │
  │  condition has worsened. A    │   escalation: true,       │                           │
  │  handoff report has been      │   report: "## Handoff     │                           │
  │  generated for your doctor." │    Report..."}             │                           │
  │                                │                           │                           │
```

---

## 10. Performance & Scaling Notes

### Current Capacity (MVP)

| Metric | Value | How |
|--------|-------|-----|
| Concurrent sessions | ~50 | Limited by Gemini API rate limits |
| LLM response time | 1-3 seconds | Gemini Flash average |
| Voice STT latency | 2-5 seconds | Whisper `base` model on CPU |
| Voice TTS latency | 3-8 seconds | XTTS-v2 on CPU |
| DB query latency | < 50ms | Supabase PostgreSQL, < 1000 rows per table |
| Report generation | 3-5 seconds | LLM + markdown rendering |

### Scaling Considerations

| Bottleneck | When It Hits | Solution |
|-----------|--------------|----------|
| Gemini API rate limits | > 100 concurrent sessions | Add API key rotation or request queuing |
| Supabase connection pool | > 50 concurrent DB writes | Upgrade Supabase plan (connection pooling) |
| Voice pipeline CPU | > 10 concurrent voice sessions | GPU instances or dedicated voice microservice |
| Uvicorn single worker | > 200 req/sec | Increase `BACKEND_WORKERS` (2x CPUs + 1) |
| Supabase free tier | > 50K rows total | Upgrade to Supabase Pro ($25/mo) |
| Render free tier | 15 min sleep, 512MB RAM | Upgrade to Render paid tier ($7/mo+) |

### Cost Estimates (Per Month at Scale)

| Service | Free Tier | 1K Patients | 10K Patients |
|---------|-----------|-------------|--------------|
| Supabase | $0 (50K rows) | $25 (Pro) | $75 (Pro+) |
| Gemini API | $0 (60 RPM) | ~$15 | ~$120 |
| Render | $0 (512MB) | $7 (Starter) | $25 (Standard) |
| Agora (video) | $0 (10K min) | ~$5 | ~$40 |
| **Total** | **$0** | **~$52** | **~$260** |

---

*This document should be updated as the architecture evolves. Last updated: August 21, 2026.*
