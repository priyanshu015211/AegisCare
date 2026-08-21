# AegisCare — Feature Ticket List

**Version:** 1.0  
**Date:** August 21, 2026  
**Based on:** PRD v1.0  

---

## How to Use These Tickets

Each ticket is written as a **self-contained prompt** you can paste into an AI coding tool (Codebuff, Cursor, Copilot, etc.). The AI should be able to implement the feature with no additional context beyond this ticket.

**Ticket format:**
- **ID:** Unique identifier
- **Name:** Feature name
- **Priority:** MUST-HAVE | SHOULD-HAVE | NICE-TO-HAVE
- **Dependencies:** Other tickets that must be completed first
- **Prompt:** The AI-ready prompt — paste this directly
- **Acceptance Criteria:** How to verify the task is done

---

## Priority Legend

| Priority | Meaning | Launch Impact |
|----------|---------|---------------|
| **MUST-HAVE** | Blocks launch. System doesn't work without it. | Cannot ship |
| **SHOULD-HAVE** | Important for quality. Can launch without it but with workarounds. | Degraded experience |
| **NICE-TO-HAVE** | Enhances the product. Can launch without it entirely. | Nice extra |

---

# MUST-HAVE TICKETS (Block Launch)

---

## T-001: Gemini LLM Integration

**Priority:** MUST-HAVE  
**Dependencies:** None  
**Component:** Backend — AI Layer

### Prompt

```
Implement the Gemini LLM integration for AegisCare. The project uses google-genai>=1.10.0 (NOT the deprecated google-generativeai).

Create `backend/services/ai/llm_service.py` with a class `LLMService` that:

1. Initializes the Gemini client using `google.genai.Client(api_key=os.environ["GEMINI_API_KEY"])`
2. Has an async method `analyze_patient(patient_state: dict) -> dict` that:
   - Builds a system prompt for medical triage (never diagnose, only triage and risk-assess)
   - Sends patient_state as structured JSON context (max 800 tokens)
   - Parses the response to extract: severity, risk_score (0-100), reasoning, follow_up_question, escalation_needed (bool)
   - Returns a dict with those exact keys
3. Has a fallback: if Gemini fails, try OpenAI gpt-4o-mini (if OPENAI_API_KEY is set)
4. Has a final fallback: if both LLMs fail, return rule-based scoring from RiskScoringService
5. Uses config values: gemini_model, openai_model, llm_max_tokens, llm_temperature, llm_timeout_seconds
6. Wraps every LLM call in a try/except with structured logging

The system prompt must include:
- "You are a medical triage assistant, NOT a doctor"
- "Never diagnose conditions or prescribe treatments"
- "Assess severity and risk level based on symptoms"
- "Output JSON with keys: severity, risk_score, reasoning, follow_up_question, escalation_needed"

Wire this service into `backend/api/dependencies/services.py` as a singleton, and update `backend/api/routes/ai.py` to use it instead of any placeholder.
```

### Acceptance Criteria

- [ ] `LLMService` class exists in `backend/services/ai/llm_service.py`
- [ ] `analyze_patient()` returns dict with severity, risk_score, reasoning, follow_up_question, escalation_needed
- [ ] Gemini API key loaded from env var, not hardcoded
- [ ] Fallback to OpenAI works when GEMINI_API_KEY is missing
- [ ] Fallback to rule-based scoring works when both keys are missing
- [ ] System prompt explicitly forbids diagnosis/prescription
- [ ] All LLM calls have try/except with logging
- [ ] Response time < 5 seconds for Gemini calls

---

## T-002: Real Drift Detection Engine

**Priority:** MUST-HAVE  
**Dependencies:** T-001 (LLM for AI-assisted drift reasoning)  
**Component:** Backend — AI Layer

### Prompt

```
Replace the placeholder drift detection in `backend/services/drift_service.py` with a real implementation.

The current file has a placeholder that just checks if "breathing difficulty" or "chest pain" is in the last 2 symptoms. Build a proper engine:

1. Create a new class `DriftDetectionEngine` that extends BaseService
2. The engine should track symptom progression by category:
   - RESPIRATORY: cough, shortness_of_breath, wheezing, chest_tightness, breathing_difficulty
   - CARDIAC: chest_pain, palpitations, heart_racing, irregular_heartbeat, radiating_arm_pain
   - NEUROLOGICAL: severe_headache, confusion, loss_of_consciousness, seizure, slurred_speech
   - CRITICAL: not_breathing, no_pulse, unresponsive, severe_bleeding, anaphylaxis

3. Drift detection rules:
   - NEW_CATEGORY: A symptom appears in a new category (e.g., respiratory → cardiac) = HIGH drift
   - WORSENING_SAME_CATEGORY: Multiple symptoms in the same category = MEDIUM drift
   - CRITICAL_SYMPTOM: Any symptom in CRITICAL set = IMMEDIATE escalation
   - SYMPTOM_COUNT_INCREASE: >3 symptoms total = ELEVATED risk
   - DURATION_EXTENSION: Symptoms lasting >7 days = CHRONIC flag

4. The method `detect_drift(symptoms_history: list[str], previous_severity: str = "green") -> dict` should return:
   - drift_detected: bool
   - drift_type: str (new_category | worsening | critical | count_increase | none)
   - escalation_risk: str (low | medium | high | critical)
   - previous_severity: str
   - new_severity: str
   - reason: str (human-readable explanation)

5. If drift is detected and previous_severity was GREEN or YELLOW, escalate severity one level up.
6. If any CRITICAL symptom is present, always set severity to CRITICAL regardless of other factors.

Wire this into `backend/api/routes/patient.py` so the /update endpoint calls detect_drift after every symptom addition.
```

### Acceptance Criteria

- [ ] `DriftDetectionEngine` class replaces placeholder in `drift_service.py`
- [ ] Detects category changes (respiratory → cardiac = HIGH drift)
- [ ] Detects worsening within same category
- [ ] Any CRITICAL symptom triggers immediate CRITICAL severity
- [ ] Severity escalates progressively (GREEN → YELLOW → RED → CRITICAL)
- [ ] Returns human-readable reason string
- [ ] Integrated into `/api/v1/patient/update` endpoint
- [ ] Unit tests pass for: no drift, same-category drift, cross-category drift, critical symptom

---

## T-003: Real Risk Scoring Engine

**Priority:** MUST-HAVE  
**Dependencies:** None  
**Component:** Backend — AI Layer

### Prompt

```
Replace the placeholder risk scoring in `backend/services/risk_service.py` with a rule-based + AI hybrid engine.

The current file has a placeholder that adds flat point values. Build a proper scoring system:

1. Create a new class `RiskScoringEngine` that extends BaseService
2. Base scoring rules (applied first, no LLM needed):
   - Each symptom gets a base risk score from a clinical reference table:
     - Respiratory symptoms: 15-25 points each (cough=15, shortness_of_breath=25)
     - Cardiac symptoms: 25-40 points each (chest_pain=40, palpitations=25)
     - Neurological symptoms: 30-45 points each (confusion=35, seizure=45)
     - Critical symptoms: 60+ points each (not_breathing=80, unresponsive=80)
     - General symptoms: 5-15 points each (fever=10, fatigue=5, headache=8)
   - Duration multiplier: <24h=1.0x, 1-3 days=1.1x, 4-7 days=1.2x, >7 days=1.3x
   - Age multiplier: >65=1.2x, >80=1.4x (elderly patients at higher risk)
   - Known conditions bonus: +10 per relevant condition (e.g., diabetes + respiratory symptoms)
   - Symptom count bonus: +5 per symptom beyond the 3rd

3. Severity classification from final score:
   - 0-30: GREEN (low risk)
   - 31-60: YELLOW (moderate risk)
   - 61-84: RED (high risk)
   - 85-100: CRITICAL (emergency)

4. Method signature: `calculate_risk(symptoms: list[str], duration: str = None, known_conditions: list[str] = None, age: int = None) -> dict`
5. Returns: {risk_score: int, severity: str, factors: list[dict], confidence: float}
   - factors: list of {"factor": str, "impact": int, "description": str} explaining each score contribution
   - confidence: 0.0-1.0 based on how many inputs were provided (more data = higher confidence)

6. Wire this into the /patient/analyze endpoint to replace _calculate_placeholder_risk()
```

### Acceptance Criteria

- [ ] Clinical reference table maps every symptom in constants.py to a risk score
- [ ] Duration, age, and known conditions modify the base score
- [ ] Score 0-100 with correct severity thresholds
- [ ] Returns explanatory factors list
- [ ] Confidence score reflects data completeness
- [ ] Unit tests for: single mild symptom, multiple severe symptoms, elderly patient, patient with known conditions
- [ ] Scores are deterministic (same inputs → same output)

---

## T-004: Supabase Database Persistence

**Priority:** MUST-HAVE  
**Dependencies:** None  
**Component:** Backend — Database

### Prompt

```
Wire up Supabase database persistence for all AegisCare tables. The Supabase client is already initialized in `backend/db/supabase_client.py` with two clients: `get_supabase_client()` (anon, read-only) and `get_supabase_admin_client()` (service_role, writes).

Update `backend/db/database_service.py` to implement these operations:

1. Patient operations:
   - `create_patient(data: dict) -> dict` — INSERT into patients table
   - `get_patient(patient_id: str) -> dict | None` — SELECT by patient_id
   - `update_patient(patient_id: str, data: dict) -> dict` — UPDATE by patient_id

2. Session operations:
   - `create_session(patient_id: str, session_data: dict) -> dict` — INSERT into sessions
   - `get_session(session_id: str) -> dict | None` — SELECT by session_id
   - `get_active_session(patient_id: str) -> dict | None` — SELECT most recent session where ended_at IS NULL
   - `update_session(session_id: str, data: dict) -> dict` — UPDATE by session_id
   - `end_session(session_id: str) -> dict` — SET ended_at = now()

3. Symptom operations:
   - `add_symptom(session_id: str, patient_id: str, symptom_data: dict) -> dict` — INSERT into symptom_records
   - `get_symptoms(session_id: str) -> list[dict]` — SELECT all symptoms for a session, ordered by reported_at

4. Escalation operations:
   - `create_escalation(session_id: str, patient_id: str, escalation_data: dict) -> dict` — INSERT into escalations
   - `get_escalations(session_id: str) -> list[dict]` — SELECT escalations for a session
   - `resolve_escalation(escalation_id: str, notes: str = None) -> dict` — SET resolved=true, resolved_at=now()

5. Report operations:
   - `save_handoff_report(session_id: str, patient_id: str, report_content: str) -> dict` — INSERT into reports
   - `get_report(session_id: str) -> dict | None` — SELECT report by session_id

6. Hospital operations:
   - `get_hospitals() -> list[dict]` — SELECT all hospitals
   - `get_hospital_load(hospital_id: str) -> dict | None` — SELECT latest hospital_load record
   - `update_hospital_load(hospital_id: str, load_data: dict) -> dict` — INSERT new hospital_load snapshot

All operations must:
- Use the admin client (service_role) for writes
- Handle Supabase connection errors gracefully (return None/empty list, log warning)
- Return dicts, not Supabase response objects

Then update `backend/api/routes/patient.py` to persist sessions and symptoms to the database on every /analyze and /update call.
```

### Acceptance Criteria

- [ ] All 6 operation groups implemented in database_service.py
- [ ] Every write operation uses `get_supabase_admin_client()`
- [ ] Connection errors return None/empty (no crashes)
- [ ] Sessions are created in DB on /analyze endpoint
- [ ] Symptoms are persisted on every /update call
- [ ] Escalations are logged to DB when drift is detected
- [ ] Handoff reports are saved to DB after generation
- [ ] No Supabase credentials hardcoded anywhere

---

## T-005: Supabase JWT Authentication

**Priority:** MUST-HAVE  
**Dependencies:** T-004 (Supabase persistence)  
**Component:** Backend — Auth

### Prompt

```
Replace the placeholder shared-secret authentication in `backend/core/auth.py` with real Supabase JWT validation.

The current implementation validates a static bearer token. Replace it with:

1. Keep the existing `get_current_user` function signature but change its implementation
2. Use Supabase's `supabase.auth.get_user(token)` to validate the JWT
3. Return a dict with `user_id`, `email`, and `role` from the validated token
4. If validation fails (expired token, invalid token, user not found), return 401

Implementation:
```python
from backend.db.supabase_client import get_supabase_client

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        client = get_supabase_client()
        if client is None:
            # Fallback for development without Supabase
            return {"user_id": "dev_user", "email": "dev@dev.com", "role": "patient"}
        
        user = client.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "user_id": user.user.id,
            "email": user.user.email,
            "role": user.user.role,
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Auth validation failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")
```

5. Keep the production guard that blocks startup if AEGISCARE_TOKEN is not set
6. Add a `/api/v1/auth/login` endpoint that accepts email+password and returns a Supabase JWT
7. Add a `/api/v1/auth/logout` endpoint that invalidates the token
8. Add a `/api/v1/auth/me` endpoint that returns the current user's profile
9. Update the frontend `api_client.py` to support setting a JWT token after login
```

### Acceptance Criteria

- [ ] `get_current_user` validates JWT against Supabase (not static token)
- [ ] Returns user_id, email, role from validated token
- [ ] Graceful fallback when Supabase is not configured (dev mode)
- [ ] `/auth/login` endpoint returns JWT on valid credentials
- [ ] `/auth/logout` endpoint exists
- [ ] `/auth/me` endpoint returns current user profile
- [ ] Frontend api_client can store and send JWT
- [ ] Expired tokens return 401 with "session expired" message

---

## T-006: Adaptive Triage Questioning Engine

**Priority:** MUST-HAVE  
**Dependencies:** T-001 (LLM), T-003 (Risk Scoring)  
**Component:** Backend — AI Layer

### Prompt

```
Implement the adaptive triage questioning engine in `backend/ai/reasoning/triage_engine.py`.

This engine replaces the static symptom intake with an intelligent conversation that adapts based on patient responses.

Create class `TriageEngine`:

1. State tracking per session:
   - current_severity: str (green/yellow/red/critical)
   - questions_asked: int
   - max_questions: 8 (from TRIAGE_QUESTION_LIMIT constant)
   - symptom_categories_covered: set
   - flagged_concerns: list[str]

2. Method `generate_next_question(patient_state: dict, conversation_history: list[dict]) -> dict`:
   - If this is the first turn: ask "What symptoms are you experiencing?"
   - If <3 symptoms collected: ask follow-ups to gather more symptoms
   - If respiratory symptoms: ask about breathing difficulty, cough duration, fever
   - If cardiac symptoms: ask about chest pain location, radiation, associated symptoms
   - If neurological: ask about onset time, consciousness level, weakness
   - If severity is RED or CRITICAL: skip to "I'm escalating your case immediately"
   - If max_questions reached: generate summary and disposition
   - Returns: {question: str, category: str, urgency: str}

3. Method `process_answer(patient_state: dict, answer: str) -> dict`:
   - Parse the patient's answer
   - Extract any new symptoms mentioned
   - Update symptom categories
   - Re-score risk with RiskScoringEngine
   - Check for drift with DriftDetectionEngine
   - Returns: {new_symptoms: list[str], updated_severity: str, needs_escalation: bool, follow_up: str}

4. Method `generate_disposition(patient_state: dict) -> dict`:
   - If GREEN: return self-care guidance text
   - If YELLOW: return "recommended to visit urgent care" + suggested facility
   - If RED: return "escalating to emergency" + generate handoff report trigger
   - If CRITICAL: return "emergency services notified" + immediate escalation
   - Returns: {severity: str, disposition: str, next_steps: list[str], escalation_needed: bool}

Wire this into the `/api/v1/ai/triage` endpoint and connect it to the frontend patient_triage.py chat interface.
```

### Acceptance Criteria

- [ ] Adaptive questioning adjusts based on symptom category
- [ ] Maximum 8 questions before generating disposition
- [ ] Questions are clinically relevant (not generic)
- [ ] Each answer is parsed for new symptoms
- [ ] Risk is re-scored after every answer
- [ ] Drift detection runs after every answer
- [ ] Disposition matches severity level
- [ ] GREEN gets self-care, YELLOW gets urgent care, RED gets escalation, CRITICAL gets immediate

---

## T-007: Frontend Triage Chat Interface

**Priority:** MUST-HAVE  
**Dependencies:** T-006 (Triage Engine), T-001 (LLM)  
**Component:** Frontend

### Prompt

```
Rebuild `frontend/pages/patient_triage.py` from a static form into a real-time chat interface.

The current page has a basic form with patient_id, duration, and symptoms fields. Replace it with a conversational triage experience:

1. Session initialization:
   - Auto-generate session_id using uuid4()
   - Show patient_id input (default: auto-generated)
   - "Start Triage Session" button begins the conversation

2. Chat interface layout:
   - Left column (60%): Chat messages area + input
   - Right column (40%): Session info panel (patient_id, session_id, severity badge, risk score, time elapsed)

3. Message display:
   - AI messages: left-aligned, light background (#F7FAFC), 14px body text
   - Patient messages: right-aligned, light blue background (#EBF4FF)
   - Each message has timestamp in small muted text below
   - No avatar icons (clinical software, not consumer app)

4. Severity badge (always visible in right panel):
   - Pill-style badge matching severity color from design system
   - GREEN: #F0FFF4 bg, #276749 text — "Low Risk"
   - YELLOW: #FFFBEB bg, #744210 text — "Moderate Risk"
   - RED: #FFF5F5 bg, #9B2C2C text — "High Risk"
   - CRITICAL: #FFF0F0 bg, #63171B text — "Critical"
   - Horizontal progress bar showing risk score (0-100) in severity color

5. Input area:
   - Text input at bottom of chat (full width)
   - Send button to the right
   - Voice input button (microphone icon) to the left of text input

6. Conversation flow:
   - First AI message: "Hello, I'm your triage assistant. What symptoms are you experiencing?"
   - Patient types/speaks symptoms
   - AI responds with adaptive follow-up questions
   - Severity badge updates in real-time
   - When severity hits RED or CRITICAL: show escalation warning banner + "Generate Report" button

7. API calls:
   - Use `api_client.post("/api/v1/ai/triage", json={...})` for each exchange
   - On each response, update severity badge and risk score
   - Store full conversation in session_state

8. End session:
   - "End Session" button (danger style, bottom right)
   - Calls POST /api/v1/patient/update to finalize
   - Shows session summary
```

### Acceptance Criteria

- [ ] Chat interface with alternating AI/patient messages
- [ ] Severity badge visible at all times with correct colors
- [ ] Risk score progress bar updates in real-time
- [ ] Voice input button present (can be placeholder until T-009)
- [ ] Adaptive questions from backend appear as AI messages
- [ ] Session info panel shows patient_id, session_id, elapsed time
- [ ] "Generate Report" button appears on RED/CRITICAL
- [ ] "End Session" button ends the triage session
- [ ] Conversation stored in Streamlit session_state
- [ ] No emoji in clinical content

---

## T-008: Handoff Report PDF Generation

**Priority:** MUST-HAVE  
**Dependencies:** T-001 (LLM), T-004 (DB persistence)  
**Component:** Backend — Reports

### Prompt

```
Rebuild `backend/reports/handoff_report.py` to generate real, structured clinician-ready handoff reports using the LLM.

The current file likely has placeholder logic. Replace with:

1. Function `generate_handoff_report(patient_state: dict) -> str`:
   - Builds a structured prompt for the LLM
   - The prompt instructs: "Generate a doctor handoff report in Markdown format"
   - Includes: patient demographics, symptom timeline, risk assessment, escalation history
   - Parses LLM response into Markdown
   - Falls back to template-based report if LLM is unavailable

2. Report structure (must include these sections):
   ```markdown
   # Doctor Handoff Report

   ## Patient Information
   - Patient ID: [id]
   - Age: [age] | Gender: [gender]
   - Known Conditions: [list]
   - Current Medications: [list]
   - Allergies: [list]

   ## Triage Summary
   - Session ID: [id]
   - Duration: [time]
   - Final Severity: [GREEN/YELLOW/RED/CRITICAL]
   - Risk Score: [0-100]

   ## Symptom Timeline
   | Time | Symptom | Category | Severity Note |
   |------|---------|----------|---------------|
   | [timestamp] | [symptom] | [category] | [note] |

   ## Clinical Progression
   [AI-generated narrative of how symptoms evolved during the session]

   ## Risk Factors
   [List of risk factors identified by the system]

   ## Escalation History
   | Time | From → To | Trigger | Action Taken |
   |------|-----------|---------|--------------|
   | [timestamp] | [severity_change] | [trigger] | [action] |

   ## Recommendations
   [AI-generated next steps for the receiving clinician]

   ## System Confidence
   - Overall confidence: [0-100]%
   - Data completeness: [how many data points were collected]
   ```

3. Function `save_report_as_pdf(report_markdown: str, filename: str) -> str`:
   - Convert Markdown to PDF using a simple library (e.g., markdown + weasyprint, or just save as .md)
   - Return the file path

4. Wire into the `/api/v1/report/handoff` endpoint and persist to Supabase using database_service.save_handoff_report()
```

### Acceptance Criteria

- [ ] Report contains all 8 required sections
- [ ] Symptom timeline is chronologically ordered
- [ ] AI narrative describes clinical progression
- [ ] Escalation history shows severity changes
- [ ] Report is saved to Supabase reports table
- [ ] Fallback to template when LLM unavailable
- [ ] Report can be downloaded as Markdown from frontend
- [ ] Report includes system confidence score

---

## T-009: Voice Pipeline — Real Whisper + XTTS Integration

**Priority:** MUST-HAVE  
**Dependencies:** None  
**Component:** Backend — Voice

### Prompt

```
Implement real Faster Whisper STT and XTTS TTS integration in the voice pipeline.

The current voice files (`voice_pipeline/stt/whisper_engine.py` and `voice_pipeline/tts/xtts_engine.py`) likely have placeholder implementations. Replace them:

1. `voice_pipeline/stt/whisper_engine.py` — WhisperEngine:
   - Load Faster Whisper model: `WhisperModel(model_size, device=device, compute_type=compute_type)`
   - Method `transcribe(audio_bytes: bytes, language: str = "en") -> str`:
     - Write audio_bytes to a temp file (WAV)
     - Call model.transcribe(temp_file)
     - Return transcribed text
   - Handle: empty audio, corrupted audio, unsupported format
   - Graceful fallback: if faster-whisper not installed, return "__PLACEHOLDER__" sentinel
   - Config from: WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE

2. `voice_pipeline/tts/xtts_engine.py` — XTTSEngine:
   - Load XTTS model on init (lazy load — first call, not import time)
   - Method `synthesize(text: str, language: str = "en") -> bytes`:
     - Generate speech from text
     - Return audio bytes (WAV format)
   - Graceful fallback: if TTS library not installed, return None
   - Config from: TTS_ENGINE, TTS_MODEL_PATH

3. Both engines must:
   - Be initialized as module-level singletons (NOT per-request)
   - Handle missing dependencies gracefully (log warning, return sentinel)
   - Have is_available property for health checks
   - Clean up temp files after use

4. Wire into `backend/api/routes/voice.py`:
   - /transcribe uses WhisperEngine
   - /respond uses XTTSEngine
   - Both check is_available before processing
   - Return 503 if engine unavailable

5. Update requirements.txt:
   - Uncomment faster-whisper==1.0.3
   - Add TTS dependency (TTS or coqui-tts)
```

### Acceptance Criteria

- [ ] WhisperEngine transcribes real audio files to text
- [ ] XTTSEngine generates real audio from text
- [ ] Both engines are singletons (created once, reused)
- [ ] Both have is_available property
- [ ] Graceful fallback when dependencies not installed
- [ ] Temp files cleaned up after transcription
- [ ] 503 returned when engine unavailable
- [ ] Audio validation (MIME type + magic bytes) still works

---

## T-010: Hospital Command Center Dashboard (Real Data)

**Priority:** MUST-HAVE  
**Dependencies:** T-004 (Supabase persistence)  
**Component:** Frontend

### Prompt

```
Rebuild `frontend/pages/dashboard.py` to show real data from the database instead of hardcoded values.

The current page has hardcoded metrics. Replace with live data:

1. Metric cards (top row, 3 columns):
   - "Active Patients": Count of sessions where ended_at IS NULL
   - "Critical Cases": Count of sessions where severity = 'critical' or 'red'
   - "Avg Triage Time": Average (ended_at - started_at) for sessions ended today

2. Risk Distribution chart (Plotly pie):
   - Query: Count of active sessions grouped by severity
   - Colors: green=#276749, yellow=#D69E2E, red=#E53E3E, critical=#C53030
   - No decorative charts — this must show actionable data

3. Recent Patient Activity table:
   - Last 10 session events (symptom reported, severity change, escalation)
   - Columns: Time, Patient ID (truncated), Action, Severity
   - Sorted by most recent first

4. Hospital Load by Facility (Plotly horizontal bar):
   - Query: Latest hospital_load record per hospital
   - Bars colored by load: green (<60%), yellow (60-80%), red (>80%)
   - Show percentage label on each bar

5. Auto-refresh every 30 seconds using st.rerun() or streamlit-autorefresh

6. API calls:
   - Use api_client to fetch data from backend endpoints
   - Backend endpoints needed:
     - GET /api/v1/system/dashboard-stats (new — returns aggregated stats)
     - GET /api/v1/system/hospital-load (new — returns current load per hospital)
   - Create these endpoints in backend/api/routes/system.py

7. Loading states:
   - Show st.spinner("Loading dashboard data...") while fetching
   - Show st.error("Failed to load data") on failure
```

### Acceptance Criteria

- [ ] Metrics show real counts from database (not hardcoded)
- [ ] Risk distribution pie chart uses real severity data
- [ ] Recent activity table shows actual session events
- [ ] Hospital load bar chart shows real occupancy percentages
- [ ] Auto-refreshes every 30 seconds
- [ ] Graceful error handling when backend is down
- [ ] Loading spinners during data fetch
- [ ] All charts use severity colors from design system

---

# SHOULD-HAVE TICKETS (Important for Quality)

---

## T-011: Hospital Load Balancing Service

**Priority:** SHOULD-HAVE  
**Dependencies:** T-004 (Supabase persistence)  
**Component:** Backend — Coordination

### Prompt

```
Implement the hospital load balancing service that routes patients to the appropriate facility.

Create `backend/services/escalation/load_balancer.py`:

1. Class `HospitalLoadBalancer`:
   - Method `find_best_hospital(symptoms: list[str], patient_location: dict = None) -> dict`:
     - Fetch all hospitals from DB
     - Filter by: has_emergency (if severity=red/critical), specialties (match symptom categories)
     - Sort by: load_percentage ascending (prefer less full hospitals)
     - If patient_location provided: sort by distance (haversine formula)
     - Return top 3 hospitals with: name, address, load_percentage, distance, specialties

   - Method `get_hospital_status(hospital_id: str) -> dict`:
     - Get latest hospital_load record
     - Return: load_percentage, er_occupancy, is_high_load, is_critical_load

   - Method `record_load_snapshot(hospital_id: str, occupancy_data: dict)`:
     - INSERT new row into hospital_load table
     - Timestamp automatically set

2. Load status thresholds (from config):
   - GREEN: load_percentage < 60%
   - YELLOW: load_percentage 60-80%
   - RED: load_percentage 80-95%
   - CRITICAL: load_percentage > 95%

3. Wire into escalation workflow:
   - When severity escalates to RED/CRITICAL, auto-call find_best_hospital()
   - Include recommended hospital in handoff report
```

### Acceptance Criteria

- [ ] Finds hospitals matching symptom specialties
- [ ] Sorts by load (prefer less full)
- [ ] Optional distance-based sorting
- [ ] Returns top 3 recommendations
- [ ] Load thresholds correctly classify hospital status
- [ ] Load snapshots can be recorded
- [ ] Integrated into escalation workflow

---

## T-012: Real-Time Emergency Center

**Priority:** SHOULD-HAVE  
**Dependencies:** T-004 (Supabase), T-002 (Drift Detection)  
**Component:** Frontend

### Prompt

```
Rebuild `frontend/pages/emergency_center.py` to show real-time escalation data.

Replace hardcoded placeholder data with live queries:

1. High Risk Patients table:
   - Query: Sessions WHERE severity IN ('red', 'critical') AND ended_at IS NULL
   - Columns: Patient ID, Risk Score, Severity (with badge), Last Update, Time Since Report
   - Sort by risk_score descending (most critical first)
   - Highlight rows with severity=critical in red background

2. Live Escalation Queue:
   - Query: Escalations WHERE resolved = false, ordered by triggered_at DESC
   - Each entry shows: timestamp, patient_id, severity_at_trigger, action_taken
   - "Resolve" button on each escalation (calls POST /api/v1/escalation/{id}/resolve)

3. Auto-refresh every 15 seconds (more frequent than dashboard — this is the emergency view)

4. Alert banner:
   - If any patient has severity=CRITICAL, show persistent red banner at top
   - Banner: "⚠️ CRITICAL PATIENT: [patient_id] — Immediate attention required"

5. Create backend endpoints:
   - GET /api/v1/patient/high-risk — returns all high-risk active sessions
   - POST /api/v1/escalation/{escalation_id}/resolve — marks escalation resolved
```

### Acceptance Criteria

- [ ] Table shows real high-risk patients from database
- [ ] Escalation queue shows unresolved escalations
- [ ] "Resolve" button works and updates database
- [ ] Auto-refreshes every 15 seconds
- [ ] Critical alert banner appears for CRITICAL patients
- [ ] Row highlighting for critical severity
- [ ] Graceful handling when no high-risk patients exist

---

## T-013: Appointment Scheduling UI

**Priority:** SHOULD-HAVE  
**Dependencies:** T-004 (Supabase), T-011 (Load Balancer)  
**Component:** Frontend + Backend

### Prompt

```
Build the appointment scheduling feature end-to-end.

Backend (`backend/api/routes/appointment.py` — new file):
1. GET /api/v1/appointments — list appointments for current user (patient: own, doctor: assigned)
2. POST /api/v1/appointments — create new appointment
   - Body: {patient_id, doctor_id, scheduled_at, duration_minutes, appointment_type}
   - Validate: doctor is available at that time, slot is not double-booked
3. PATCH /api/v1/appointments/{id}/confirm — doctor confirms appointment
4. PATCH /api/v1/appointments/{id}/cancel — either party cancels
5. GET /api/v1/doctors/available — list doctors with availability status

Frontend (`frontend/pages/coordination_dashboard.py` — rebuild):
1. Three-column layout:
   - Left: Upcoming appointments list (date, patient, type, status)
   - Center: Doctor availability (list with status dots: green=available, yellow=busy, red=offline)
   - Right: Hospital load summary

2. "Book Appointment" flow:
   - Button opens modal
   - Select doctor (filtered by specialty matching triage result)
   - Select date/time (show available slots only)
   - Select type (in-person, video, phone)
   - Confirm booking

3. Appointment cards show: patient name, doctor, time, type, status badge
```

### Acceptance Criteria

- [ ] CRUD endpoints for appointments work
- [ ] Double-booking prevention
- [ ] Doctor availability shown with status dots
- [ ] Booking modal with doctor/date/time selection
- [ ] Appointment status updates (pending → confirmed → completed)
- [ ] Patient sees their own appointments, doctor sees assigned

---

## T-014: Escalation Workflow Automation

**Priority:** SHOULD-HAVE  
**Dependencies:** T-002 (Drift Detection), T-004 (Supabase), T-008 (Report Generation)  
**Component:** Backend — Escalation

### Prompt

```
Build the automated escalation workflow in `backend/services/escalation/escalation_service.py`.

When drift detection triggers an escalation, this service orchestrates the response:

1. Class `EscalationService`:
   - Method `handle_escalation(session_id: str, patient_id: str, drift_result: dict) -> dict`:
     - Create escalation record in DB
     - Determine actions based on severity:
       - RED: alert_doctor + generate_handoff_report
       - CRITICAL: alert_doctor + generate_handoff_report + notify_emergency_contact + find_best_hospital
     - Execute each action
     - Log all actions in the escalation record
     - Return: {escalation_id, actions_taken: list[str], recommended_hospital: dict}

   - Method `alert_doctor(patient_id: str, severity: str, message: str)`:
     - Find assigned doctor for patient
     - Update doctor's notification queue (or log for now)
     - Return: {alerted: bool, doctor_id: str}

   - Method `notify_emergency_contact(patient_id: str, message: str)`:
     - Fetch patient's emergency_contact from DB
     - Log notification (real SMS integration is P2)
     - Return: {notified: bool, contact: str}

   - Method `resolve_escalation(escalation_id: str, resolved_by: str, notes: str = None)`:
     - Mark escalation as resolved
     - Log who resolved it and any notes

2. Wire into DriftDetectionEngine:
   - When drift is detected AND severity escalates, call handle_escalation()
   - Pass the current patient state for context
```

### Acceptance Criteria

- [ ] Escalation records created in DB
- [ ] Actions executed based on severity level
- [ ] Doctor alerting logic works
- [ ] Emergency contact notification (logged for now)
- [ ] Handoff report generated on RED/CRITICAL escalation
- [ ] Hospital recommendation included for CRITICAL
- [ ] Escalation can be resolved with notes
- [ ] All actions logged in escalation record

---

## T-015: Security Hardening — Production Readiness

**Priority:** SHOULD-HAVE  
**Dependencies:** None (already partially done)  
**Component:** Backend — Security

### Prompt

```
Complete the production security hardening for AegisCare. Many pieces are already in place — verify and complete the remaining items:

1. Verify CORS production guard works:
   - Test that ALLOWED_ORIGINS=* crashes on APP_ENV=production
   - Test that valid origins work in production

2. Verify auth production guard works:
   - Test that missing AEGISCARE_TOKEN crashes on APP_ENV=production

3. Deploy the RLS migration:
   - Run backend/db/migrations/002_security_rls.sql against Supabase
   - Verify patients can only see their own data
   - Verify doctors can see assigned patients

4. Test the emergency override endpoint:
   - POST /api/v1/emergency/override with valid token + override code
   - Verify it returns patient data
   - Verify audit log entry is created

5. Test audit logging:
   - Make requests to PHI endpoints
   - Verify audit entries appear in logs/audit.log
   - Verify non-PHI endpoints (health, system) are NOT logged

6. Test data retention:
   - Call DataRetentionService.run_cleanup()
   - Verify it returns a summary without errors

7. Security checklist verification:
   - All secrets in env vars (not in code)
   - HTTPS enforced (Render)
   - Security headers present (check response headers)
   - Rate limiting configured
   - Input validation on all endpoints
```

### Acceptance Criteria

- [ ] CORS guard crashes on wildcard in production
- [ ] Auth guard crashes on missing token in production
- [ ] RLS policies deployed and verified
- [ ] Emergency override returns patient data with audit trail
- [ ] Audit log captures PHI access events
- [ ] Data retention cleanup runs without errors
- [ ] All security headers present in responses

---

## T-016: Supabase Session Persistence for Voice

**Priority:** SHOULD-HAVE  
**Dependencies:** T-004 (Supabase), T-009 (Voice Pipeline)  
**Component:** Backend — Voice

### Prompt

```
Ensure voice transcriptions are persisted to the database and integrated into the triage session.

1. When /api/v1/voice/transcribe returns a transcription:
   - The frontend should send the transcribed text to /api/v1/ai/triage as a patient message
   - The backend should store the transcription as a symptom record

2. Add voice transcription to patient memory:
   - After transcription, extract symptoms from the text
   - Add to session's symptom history
   - Run risk scoring and drift detection

3. Voice response delivery:
   - After AI generates a response, optionally synthesize it with TTS
   - Return audio URL or bytes to frontend
   - Frontend plays the audio

4. Create a new endpoint: POST /api/v1/voice/triage
   - Accepts: audio file
   - Transcribes → extracts symptoms → runs triage → returns text + audio response
   - All-in-one voice triage flow
```

### Acceptance Criteria

- [ ] Voice transcriptions saved as symptom records
- [ ] Transcribed symptoms run through risk scoring
- [ ] Voice triage endpoint works end-to-end
- [ ] Audio response can be played in frontend
- [ ] Session memory includes voice-reported symptoms

---

# NICE-TO-HAVE TICKETS (Future Enhancements)

---

## T-017: Video Consultation (Agora SDK)

**Priority:** NICE-TO-HAVE  
**Dependencies:** T-005 (JWT Auth), T-013 (Appointments)  
**Component:** Backend + Frontend

### Prompt

```
Implement live video consultation using Agora SDK.

Backend:
1. Create backend/services/video/agora_service.py:
   - Generate Agora token for a channel
   - Method `generate_token(channel_name: str, uid: int, role: str) -> str`
   - Token expiry: AGORA_TOKEN_EXPIRY_SECONDS

2. Create backend/api/routes/video.py:
   - POST /api/v1/video/token — generate Agora token for a session
   - Body: {session_id, channel_name}
   - Returns: {token, app_id, channel_name}

Frontend:
3. Add Agora Web SDK to requirements (agora-rtc-sdk-ng)
4. Create video consultation component:
   - Join channel button
   - Local/remote video elements
   - Mute audio/video buttons
   - Screen sharing button
   - Leave call button

5. Integrate with appointments:
   - When appointment type = "video", show "Join Video Call" button
   - Auto-join Agora channel when clicked
   - End call when appointment is marked completed
```

### Acceptance Criteria

- [ ] Agora tokens generated server-side
- [ ] Video call joins correct channel
- [ ] Local and remote video display
- [ ] Audio/video mute works
- [ ] Screen sharing available
- [ ] Call ends when appointment completed
- [ ] Token expires after configured duration

---

## T-018: Multilingual Support

**Priority:** NICE-TO-HAVE  
**Dependencies:** T-001 (LLM), T-009 (Voice)  
**Component:** Backend + Frontend

### Prompt

```
Add multilingual support for Spanish, Mandarin, and Hindi.

1. Language detection:
   - Add language detection to intake (auto-detect from first message)
   - Allow explicit language selection in UI

2. LLM prompts:
   - Create translated system prompts for each language
   - Include: "Respond in [language]" in system prompt
   - Store language preference in session

3. Voice pipeline:
   - Whisper already supports multilingual transcription
   - Set language parameter in transcribe() call
   - TTS: use language parameter for voice synthesis

4. Frontend:
   - Add language selector to triage page (dropdown: English, Spanish, Mandarin, Hindi)
   - Display all UI text in selected language
   - Handoff report includes original language + English translation

5. Severity/scoring:
   - Symptom mapping: create translated symptom dictionaries
   - "dolor de pecho" = "chest pain" (same risk score)
   - Normalize all input to English for scoring, display in original language
```

### Acceptance Criteria

- [ ] Language auto-detection works
- [ ] Language selector in UI
- [ ] LLM responds in selected language
- [ ] Voice transcription works for all 4 languages
- [ ] Symptom normalization from any language to English
- [ ] Handoff report includes both languages

---

## T-019: Patient History Dashboard

**Priority:** NICE-TO-HAVE  
**Dependencies:** T-004 (Supabase)  
**Component:** Frontend

### Prompt

```
Build a longitudinal patient history view showing all past triage sessions.

Create a new page `frontend/pages/patient_history.py`:

1. Patient search:
   - Search by patient_id or name
   - Show matching patients in a list

2. Patient profile card:
   - Name, age, gender, known conditions, medications, allergies
   - Total sessions count
   - Last session date

3. Session timeline:
   - Vertical timeline of all past sessions
   - Each entry: date, severity badge, risk score, symptoms list
   - Click to expand: see full symptom timeline and handoff report

4. Trend charts (Plotly):
   - Risk score over time (line chart)
   - Severity distribution over time (stacked bar)
   - Symptom frequency (bar chart — which symptoms appear most often)

5. Backend endpoints:
   - GET /api/v1/patient/{id}/history — all sessions for a patient
   - GET /api/v1/patient/{id}/trends — aggregated trend data
```

### Acceptance Criteria

- [ ] Patient search by ID or name
- [ ] Profile card with demographics and conditions
- [ ] Timeline of all past sessions
- [ ] Risk score trend chart
- [ ] Symptom frequency chart
- [ ] Click to view full session details
- [ ] Data from real database queries

---

## T-020: Analytics & Reporting Dashboard

**Priority:** NICE-TO-HAVE  
**Dependencies:** T-004 (Supabase)  
**Component:** Frontend

### Prompt

```
Rebuild `frontend/pages/analytics.py` with real aggregate data.

1. KPI cards (top row):
   - Total Sessions (all time)
   - Average Triage Time (mean session duration)
   - Escalation Rate (% of sessions that triggered escalation)
   - Average Risk Score

2. Charts:
   - Sessions Over Time (line chart, daily/weekly/monthly toggle)
   - Severity Distribution (stacked bar by week)
   - Top Symptom Categories (horizontal bar — respiratory, cardiac, neurological, general)
   - Escalation Outcomes (pie chart — resolved, pending, unresolved)

3. Filters:
   - Date range picker (last 7 days, 30 days, 90 days, custom)
   - Hospital filter (if multi-hospital)
   - Severity filter

4. Backend endpoints:
   - GET /api/v1/analytics/summary — aggregate KPIs
   - GET /api/v1/analytics/trends — time-series data
   - GET /api/v1/analytics/symptoms — symptom category breakdown
   - All queries use SQL aggregations, not Python loops
```

### Acceptance Criteria

- [ ] KPIs show real aggregated data
- [ ] All charts use real data from database
- [ ] Date range filter works
- [ ] Charts use Plotly with healthcare color scheme
- [ ] No hardcoded data anywhere
- [ ] Queries are efficient (SQL aggregations)

---

## T-021: SMS/Notification Alerts

**Priority:** NICE-TO-HAVE  
**Dependencies:** T-014 (Escalation Workflow)  
**Component:** Backend — Notifications

### Prompt

```
Implement SMS notification alerts for patients and staff.

1. Create backend/services/notification_service.py:
   - Use Twilio or similar SMS API (configurable)
   - Method `send_sms(to: str, message: str) -> bool`
   - Method `send_escalation_alert(patient_id: str, severity: str)`
   - Method `send_appointment_reminder(appointment_id: str)`
   - Method `send_appointment_confirmation(appointment_id: str)`

2. Notification templates:
   - Escalation: "AegisCare Alert: Your condition has been escalated to [severity]. Please seek immediate medical attention."
   - Appointment reminder: "AegisCare Reminder: You have an appointment with Dr. [name] at [time]."
   - Appointment confirmation: "AegisCare: Your appointment with Dr. [name] has been confirmed for [date/time]."

3. Integration points:
   - On escalation: send alert to patient + assigned doctor
   - 24h before appointment: send reminder
   - On appointment creation: send confirmation

4. Config:
   - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
   - NOTIFICATION_ENABLED=true/false
```

### Acceptance Criteria

- [ ] SMS sending works via Twilio
- [ ] Escalation alerts sent automatically
- [ ] Appointment reminders sent 24h before
- [ ] Confirmation sent on booking
- [ ] Notifications can be disabled via config
- [ ] Failed sends are logged (not silent failures)

---

## T-022: Confidence Scoring & Contradiction Detection

**Priority:** NICE-TO-HAVE  
**Dependencies:** T-001 (LLM), T-006 (Triage Engine)  
**Component:** Backend — AI

### Prompt

```
Add AI-powered confidence scoring and contradiction detection to the triage system.

1. In the LLM prompt, add instruction: "Rate your confidence in this assessment from 0-100"
2. Parse confidence from LLM response
3. Contradiction detection:
   - After each patient answer, check if it contradicts previous answers
   - Example: patient says "no chest pain" then later says "chest hurts"
   - If contradiction detected: flag it, ask patient to clarify
4. Low confidence handling:
   - If confidence < 50: add note to handoff report "AI confidence is low — verify with patient"
   - If confidence < 30: trigger doctor alert for manual review
5. Store confidence score in session state and display in UI
```

### Acceptance Criteria

- [ ] Confidence score parsed from LLM response
- [ ] Contradictions detected and flagged
- [ ] Patient prompted to clarify contradictions
- [ ] Low confidence noted in handoff report
- [ ] Very low confidence triggers doctor alert
- [ ] Confidence displayed in session info panel

---

## T-023: Mobile-Responsive Frontend

**Priority:** NICE-TO-HAVE  
**Dependencies:** None  
**Component:** Frontend

### Prompt

```
Make the Streamlit frontend responsive for mobile devices.

1. Add responsive CSS to `frontend/styles/main.css`:
   - Media queries for screens < 768px
   - Stack columns vertically on mobile
   - Increase touch target sizes (min 44px)
   - Full-width cards on mobile
   - Sidebar collapses to hamburger menu

2. Triage page mobile layout:
   - Full-width chat interface
   - Severity badge moves to top of screen (sticky)
   - Input area at bottom with larger touch targets

3. Dashboard mobile layout:
   - Single-column layout
   - Metric cards stack vertically
   - Charts full-width
   - Tables scroll horizontally

4. Test on:
   - iPhone Safari
   - Android Chrome
   - Tablet (iPad)
```

### Acceptance Criteria

- [ ] All pages usable on mobile
- [ ] No horizontal scroll on text content
- [ ] Touch targets >= 44px
- [ ] Chat interface works on mobile
- [ ] Severity badge always visible
- [ ] Charts readable on small screens

---

# TICKET DEPENDENCY MAP

```
T-001 (LLM Integration)
  ├── T-002 (Drift Detection)
  │     └── T-012 (Emergency Center)
  ├── T-003 (Risk Scoring)
  │     └── T-006 (Triage Engine)
  │           ├── T-007 (Frontend Chat)
  │           └── T-022 (Confidence Scoring)
  ├── T-008 (Handoff Reports)
  │     └── T-014 (Escalation Workflow)
  │           └── T-021 (SMS Notifications)
  └── T-018 (Multilingual)

T-004 (Supabase Persistence)
  ├── T-005 (JWT Auth)
  │     └── T-017 (Video Consultation)
  ├── T-010 (Dashboard Real Data)
  ├── T-011 (Load Balancing)
  │     └── T-013 (Appointment Scheduling)
  │           └── T-017 (Video Consultation)
  └── T-019 (Patient History)

T-009 (Voice Pipeline)
  ├── T-016 (Voice + Session Persistence)
  └── T-018 (Multilingual)

T-015 (Security Hardening) — independent, can start anytime
T-023 (Mobile Responsive) — independent, can start anytime
T-020 (Analytics) — independent after T-004
```

---

## Sprint Planning Suggestion

### Sprint 1 (Week 1-2): Foundation
- T-001: LLM Integration
- T-003: Risk Scoring
- T-004: Supabase Persistence

### Sprint 2 (Week 3-4): Core Engine
- T-002: Drift Detection
- T-006: Triage Engine
- T-008: Handoff Reports
- T-009: Voice Pipeline

### Sprint 3 (Week 5-6): Frontend
- T-007: Frontend Chat Interface
- T-010: Dashboard Real Data
- T-012: Emergency Center

### Sprint 4 (Week 7-8): Integration
- T-005: JWT Auth
- T-011: Load Balancing
- T-014: Escalation Workflow
- T-015: Security Hardening

---

*Each ticket prompt is designed to be self-contained. Paste the "Prompt" section directly into an AI coding tool for implementation.*
