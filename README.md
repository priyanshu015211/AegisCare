# AegisCare
## AI Emergency Escalation & Healthcare Coordination System

AegisCare is a production-grade AI-powered healthcare coordination platform built for
overloaded hospitals, rural clinics, and emergency triage environments.

---

## What It Does

- Monitors patient symptom progression in real time
- Detects deterioration through Dynamic Emergency Drift Detection
- Routes patients to appropriate care based on hospital load
- Connects patients with available doctors via video consultation
- Auto-generates structured doctor-ready handoff reports
- Displays a live hospital command center dashboard

## Key Innovation: Dynamic Emergency Drift Detection

Standard healthcare chatbots analyze symptoms at a single point in time.
AegisCare continuously tracks how symptoms evolve during a session.

Example progression:
  fever → cough → breathing difficulty → chest tightness

The system updates severity in real time, escalates risk automatically,
and triggers intervention workflows without waiting for manual input.

Visual indicator: GREEN → YELLOW → RED

---

## Tech Stack

| Layer           | Technology                          |
|----------------|-------------------------------------|
| Frontend        | Streamlit + Plotly                  |
| Backend         | FastAPI + Python 3.11+              |
| Database        | Supabase (PostgreSQL)               |
| AI / LLM        | Gemini 1.5 Flash (GPT-4o-mini fallback) |
| Speech-to-Text  | Faster Whisper                      |
| Text-to-Speech  | XTTS-v2 (Piper fallback)            |
| Video           | Agora SDK                           |
| Auth            | Supabase Auth                       |
| Deployment      | Docker + Streamlit Cloud / Render   |
| Logging         | Loguru                              |

---

## Project Structure

```
aegiscare/
├── backend/              # FastAPI backend
│   ├── api/              # Route handlers and middleware
│   ├── core/             # Config, constants, shared logic
│   ├── models/           # Pydantic schemas and DB models
│   ├── services/         # Business logic (AI, voice, escalation)
│   └── db/               # Supabase client and queries
│
├── frontend/             # Streamlit application
│   ├── pages/            # Multi-page app pages
│   ├── components/       # Reusable UI components
│   ├── assets/           # CSS, icons, static files
│   └── utils/            # Frontend helpers
│
├── voice_pipeline/       # Voice processing
│   ├── stt/              # Faster Whisper STT
│   ├── tts/              # XTTS-v2 / Piper TTS
│   └── audio/            # Audio capture / playback
│
├── project_memory/       # Architecture and handoff docs
├── scripts/              # Dev scripts, migrations, seeds
├── tests/                # Backend and frontend tests
├── docker/               # Dockerfiles and compose configs
└── docs/                 # API docs, diagrams, specs
```

---

## Development Phases

| Phase | Description                                      | Status   |
|-------|--------------------------------------------------|----------|
| 1     | Architecture, planning, repository setup         | Complete |
| 2     | FastAPI backend initialization                   | Pending  |
| 3     | Streamlit frontend initialization                | Pending  |
| 4     | Supabase database integration                    | Pending  |
| 5     | Authentication and session management            | Pending  |
| 6     | Voice pipeline (Whisper + XTTS)                  | Pending  |
| 7     | Structured patient memory system                 | Pending  |
| 8     | AI reasoning pipeline and prompt engineering     | Pending  |
| 9     | Dynamic Emergency Drift Detection engine         | Pending  |
| 10    | Adaptive triage questioning system               | Pending  |
| 11    | Confidence scoring and contradiction detection   | Pending  |
| 12    | Hospital load balancing system                   | Pending  |
| 13    | Appointment scheduling workflow                  | Pending  |
| 14    | Doctor video consultation (Agora)                | Pending  |
| 15    | Doctor handoff report generation                 | Pending  |
| 16    | Live command center dashboard                    | Pending  |
| 17    | Accessibility and multilingual support           | Pending  |
| 18    | Landing page redesign and UX cleanup             | Pending  |
| 19    | Token optimization and performance               | Pending  |
| 20    | Docker, deployment, and production readiness     | Pending  |

---

## Team Ownership

| Developer | Responsibility                                          |
|-----------|---------------------------------------------------------|
| Person 1  | Backend, FastAPI, AI engine, Risk/Escalation engine     |
| Person 2  | Streamlit frontend, Dashboard, UX                       |
| Person 3  | Voice pipeline, Agora, Deployment, Integrations         |

---

## Getting Started

See `docs/setup.md` for full environment setup instructions.
Quick start:

```bash
git clone https://github.com/your-org/aegiscare.git
cd aegiscare
cp .env.example .env          # Fill in your keys
pip install -r requirements.txt
uvicorn backend.main:app --reload    # Start backend
streamlit run frontend/app.py        # Start frontend
```

---

## License

Internal development use only. Not licensed for public distribution.
