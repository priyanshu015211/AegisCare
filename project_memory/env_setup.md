# AegisCare — Environment Setup Guide

## Prerequisites

- Python 3.11 or higher
- pip 23+
- Git
- Docker + Docker Compose (optional, for containerized dev)
- Node.js not required (no JS build step)

---

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/aegiscare.git
cd aegiscare
```

---

## 2. Python Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate           # Windows
```

---

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Note: PyAudio requires system audio libraries.
On Ubuntu/Debian:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```
On Mac:
```bash
brew install portaudio
```

---

## 4. Environment Variables

```bash
cp .env.example .env
```

Required keys to fill in:
- SUPABASE_URL — from your Supabase project settings
- SUPABASE_ANON_KEY — from Supabase project API settings
- SUPABASE_SERVICE_ROLE_KEY — from Supabase project API settings
- GEMINI_API_KEY — from Google AI Studio
- SECRET_KEY — generate with: python -c "import secrets; print(secrets.token_hex(32))"

Optional (for voice and video features):
- AGORA_APP_ID — from Agora console
- AGORA_APP_CERTIFICATE — from Agora console

---

## 5. Set Up Supabase (Phase 4)

Full SQL migrations will be provided in Phase 4.
For now, create a new Supabase project at https://supabase.com
and note your project URL and keys.

---

## 6. Run Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see the API.

---

## 7. Run Frontend

```bash
streamlit run frontend/app.py
```

Visit http://localhost:8501

---

## 8. Docker (Optional)

```bash
cp .env.example .env   # Fill in your keys first
docker-compose up --build
```

Backend: http://localhost:8000
Frontend: http://localhost:8501

---

## 9. Logs

Logs are written to ./logs/aegiscare.log
and also printed to stdout.

---

## 10. Running Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=backend --cov-report=html
```

---

## Common Issues

### "Module not found: backend"
Run all commands from the repository root, not from inside a subfolder.

### PyAudio install fails
Install system PortAudio library first (see step 3).

### Supabase connection error
Check that SUPABASE_URL and SUPABASE_ANON_KEY are correct in .env.
Make sure .env is in the repository root.

### LLM timeout
Check GEMINI_API_KEY is valid.
Increase LLM_TIMEOUT_SECONDS in .env if needed.
