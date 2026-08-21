# AegisCare — Security and Access Document

**Version:** 1.0  
**Date:** August 21, 2026  
**Audience:** Non-technical founders, developers, and compliance reviewers  
**Status:** Draft  

---

## What This Document Is

This document explains how AegisCare keeps patient data safe, who can do what in the system, what happens when things go wrong, and what edge cases we need to handle before launch. Everything is written in plain English.

**The bottom line:** AegisCare handles sensitive medical data. One mistake can mean a HIPAA violation, a lawsuit, or — worst of all — a patient getting the wrong care. This document is the rulebook that prevents that.

---

## Table of Contents

1. [Authentication — Who Are You?](#1-authentication--who-are-you)
2. [User Roles — What Can Each Person Do?](#2-user-roles--what-can-each-person-do)
3. [Row-Level Security — Who Sees What Data?](#3-row-level-security--who-sees-what-data)
4. [Data Protection — How We Keep Information Safe](#4-data-protection--how-we-keep-information-safe)
5. [Error Handling — What Happens When Things Go Wrong](#5-error-handling--what-happens-when-things-go-wrong)
6. [Edge Cases — Scenarios You Must Handle Before Launch](#6-edge-cases--scenarios-you-must-handle-before-launch)
7. [Compliance Checklist](#7-compliance-checklist)
8. [Incident Response](#8-incident-response)

---

## 1. Authentication — Who Are You?

Authentication is the process of verifying someone is who they say they are. Think of it like checking an ID at the door.

### How It Works Today (Placeholder)

Right now, AegisCare uses a **shared secret** — a long random password that both the frontend and backend know. Every request from the frontend to the backend includes this secret in the header.

**How it works:**
1. The frontend includes the secret in every API call: `Authorization: Bearer <secret>`
2. The backend checks: "Is this the correct secret?"
3. If yes → the request goes through
4. If no → 401 Unauthorized (rejected)

**The secret is stored in:** The `AEGISCARE_TOKEN` environment variable — a long random string like `b7d1e4f8a2c3...` (64 characters).

**Why this is a placeholder:** Everyone who has this secret can access everything. If it leaks (e.g., someone commits it to GitHub), the entire system is compromised. It's like giving every employee the master key to the building.

### How It Will Work in Production (Planned)

We will replace the shared secret with **Supabase JWT authentication**. Here's what that means in plain English:

**JWT = JSON Web Token.** It's like a temporary ID badge that expires.

**How it works:**
1. Patient logs in with email/password
2. Supabase verifies the credentials
3. Supabase gives the patient a temporary token (like a wristband at a hospital)
4. The patient includes this token in every request
5. The backend checks: "Is this token valid? Has it expired? Does it belong to this patient?"
6. If all checks pass → the request goes through
7. If any check fails → 401 Unauthorized

**The key difference:** Each patient gets their own unique token. If one token leaks, only that one patient's data is at risk — not everyone's.

### Authentication Rules

| Rule | What It Means | Why It Matters |
|------|---------------|----------------|
| **Every protected endpoint requires a token** | You can't access patient data, AI analysis, voice, or reports without logging in | Prevents unauthorized access |
| **Tokens expire after 24 hours** | Patients must re-login daily | Limits damage if a token is stolen |
| **Tokens are checked with constant-time comparison** | The system takes the same amount of time to check a wrong token as a right one | Prevents "timing attacks" where hackers guess the token by measuring response speed |
| **Health check endpoints are public** | `/health` and `/api/v1/system/status` don't need a token | Load balancers and monitoring tools need to check if the system is running |
| **Doctor accounts require admin approval** | Doctors can't self-register | Prevents fake doctors from accessing patient data |

### What the Token Looks Like

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The long string after "Bearer" is the JWT. It contains:
- **Who you are** (patient ID, role)
- **When it expires** (24 hours from login)
- **A signature** (to prove it wasn't tampered with)

---

## 2. User Roles — What Can Each Person Do?

AegisCare has four types of users. Each role has specific permissions — what they CAN do and what they CANNOT do.

### Role: Patient

**Who they are:** People using AegisCare to report symptoms and get triaged.

| CAN Do | CANNOT Do |
|--------|-----------|
| Create an account | See other patients' data |
| Start a triage session | Modify their own medical records |
| Report symptoms | Cancel another patient's appointment |
| View their own session history | Access the hospital command center |
| View their own handoff reports | See hospital load data |
| Book an appointment | Modify escalation records |
| View their own appointment history | Generate reports for other patients |
| Receive voice responses | Access AI model configuration |
| Cancel their own appointment | See system logs |

**Why these restrictions matter:** Patient data is protected health information (PHI). A patient should never be able to see another patient's symptoms, diagnosis, or treatment — that's a HIPAA violation.

### Role: Doctor

**Who they are:** Licensed healthcare providers who review triage results and consult with patients.

| CAN Do | CANNOT Do |
|--------|-----------|
| View handoff reports for their assigned patients | See patients assigned to other doctors |
| Update patient records during consultation | Delete patient records |
| View their own schedule | Modify hospital load data |
| Accept or decline appointments | Access AI model configuration |
| Add clinical notes to patient records | Create new patient accounts |
| Initiate video consultations | View system logs |
| View escalation queue for their hospital | Modify escalation thresholds |
| Mark appointments as completed | See other doctors' schedules |

**Why these restrictions matter:** Doctors should only see patients they're responsible for. A cardiologist shouldn't see the psychiatric records of a patient they're not treating — that's the "minimum necessary" rule in healthcare.

### Role: Hospital Administrator

**Who they are:** Hospital staff who manage operations, not direct patient care.

| CAN Do | CANNOT Do |
|--------|-----------|
| View the command center dashboard | View individual patient symptoms |
| View hospital load metrics | Access handoff reports |
| View aggregate analytics | Modify patient records |
| View escalation statistics (numbers only) | Initiate video consultations |
| View doctor availability | Book appointments directly |
| View appointment statistics | Access AI model configuration |
| Export aggregate reports | See individual patient identities |
| Configure hospital settings | Delete any records |

**Why these restrictions matter:** Administrators need to see the big picture (how busy is the hospital?) but not the details (what symptoms does patient P-1043 have?). This is the difference between "the ER is at 80% capacity" and "Patient X has chest pain" — the admin needs the first, not the second.

### Role: System Administrator (Internal)

**Who they are:** The AegisCare development team. This role is NOT available in the app — it's for backend operations only.

| CAN Do | CANNOT Do |
|--------|-----------|
| View system logs | Modify patient data directly |
| Monitor API performance | Bypass audit logging |
| Update system configuration | Access production databases without approval |
| Review security events | Disable RLS policies |
| Manage API keys | Share credentials outside the team |

### Role Permission Matrix (Summary)

| Action | Patient | Doctor | Admin | Sysadmin |
|--------|---------|--------|-------|----------|
| Report symptoms | YES | NO | NO | NO |
| View own data | YES | NO | NO | YES |
| View assigned patients | NO | YES | NO | YES |
| View all patients | NO | NO | NO | YES |
| Generate handoff reports | NO | YES | NO | YES |
| View hospital load | NO | YES | YES | YES |
| View aggregate analytics | NO | YES | YES | YES |
| View individual patient data | NO | YES | NO | YES |
| Modify patient records | NO | YES | NO | YES |
| Book appointments | YES | YES | NO | YES |
| View system logs | NO | NO | NO | YES |
| Modify system config | NO | NO | NO | YES |

---

## 3. Row-Level Security — Who Sees What Data?

Row-Level Security (RLS) is a database-level rule that says: "Even if someone has a valid login, they can only see the rows they're allowed to see."

Think of it like this: **Authentication** checks if you're allowed in the building. **RLS** checks which rooms you can enter once you're inside.

### How RLS Works

Every table in the database has rules attached to it. When someone queries the database, the database automatically filters the results based on who's asking.

**Example:**
- Patient P-1043 logs in and queries "Show me my sessions"
- The database returns: Only sessions where `patient_id = P-1043`
- Patient P-1043 tries to query "Show me all sessions"
- The database returns: Only sessions where `patient_id = P-1043` (same result — RLS blocks everything else)

### RLS Rules for Each Table

#### Table: `patients`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Owner read/write | Patients | A patient can only read and update their own row |
| Doctor read | Doctors | A doctor can read patients assigned to them (via appointments) |
| Admin read | Admins | Can see all patients for operational purposes |

**Plain English:** If Patient A tries to look up Patient B's medical history, the database returns nothing. Patient A can only see their own data.

#### Table: `sessions`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Owner read/write | Patients | A patient can only see their own triage sessions |
| Assigned doctor read | Doctors | A doctor can see sessions for patients they're assigned to |
| Admin aggregate read | Admins | Can see session counts and statistics (not content) |

**Plain English:** If Patient A is in a triage session, Patient B can't see it. Only Patient A and the doctor assigned to Patient A can see what symptoms were reported and what the AI recommended.

#### Table: `symptom_records`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Owner read | Patients | A patient can only see their own symptom records |
| Assigned doctor read | Doctors | A doctor can see symptoms for their assigned patients |

**Plain English:** The actual symptoms a patient reported (e.g., "chest pain", "difficulty breathing") are only visible to that patient and their doctor. Nobody else.

#### Table: `escalations`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Owner read | Patients | A patient can see their own escalation events |
| Hospital doctor read | Doctors | Any doctor at the same hospital can see escalations (for awareness) |
| Admin read | Admins | Can see all escalations for reporting |

**Plain English:** When a patient's condition is escalated, their doctor can see it. Other doctors at the same hospital can also see it (in case they need to help). But doctors at a different hospital cannot see it.

#### Table: `appointments`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Owner read/write | Patients | A patient can see and manage their own appointments |
| Assigned doctor read/write | Doctors | A doctor can see and update appointments they're assigned to |
| Admin read | Admins | Can see all appointments for scheduling purposes |

**Plain English:** Patient A can see their appointment with Dr. Smith. Patient B cannot see Patient A's appointment. Dr. Smith can see all their appointments. The hospital admin can see all appointments to manage scheduling.

#### Table: `doctors`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Read-only (all authenticated) | Everyone | All logged-in users can view doctor profiles |

**Plain English:** Doctor profiles (name, specialty, availability) are visible to everyone who's logged in. This is necessary so patients can choose a doctor and see who's available.

#### Table: `hospitals`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Read-only (all authenticated) | Everyone | All logged-in users can view hospital directory |

**Plain English:** Hospital information (name, address, specialties) is public to all logged-in users. Patients need this to find nearby hospitals. Doctors need it to see their workplace.

#### Table: `hospital_load`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Read-only (all authenticated) | Everyone | All logged-in users can view current hospital load |

**Plain English:** Current hospital capacity (how many beds are available) is visible to everyone. This is needed for the load-balancing system to route patients to the right hospital.

#### Table: `reports`

| Rule | Who It Applies To | What It Does |
|------|-------------------|--------------|
| Owner read | Patients | A patient can only see their own handoff reports |
| Assigned doctor read | Doctors | A doctor can only see reports for their assigned patients |

**Plain English:** Handoff reports contain detailed medical information. Only the patient and their doctor can see them. No one else.

### RLS Summary

| Table | Patients See | Doctors See | Admins See |
|-------|-------------|-------------|------------|
| `patients` | Own row only | Assigned patients | All patients |
| `sessions` | Own sessions | Assigned patient sessions | Counts only |
| `symptom_records` | Own symptoms | Assigned patient symptoms | No content |
| `escalations` | Own escalations | Hospital escalations | All escalations |
| `appointments` | Own appointments | Assigned appointments | All appointments |
| `doctors` | All profiles | All profiles | All profiles |
| `hospitals` | All | All | All |
| `hospital_load` | All | All | All |
| `reports` | Own reports | Assigned reports | No content |

---

## 4. Data Protection — How We Keep Information Safe

### 4.1 Data at Rest (Stored Data)

| Measure | What It Means | Status |
|---------|---------------|--------|
| **Encryption at rest** | All data stored in Supabase is encrypted on disk | Provided by Supabase (AES-256) |
| **No hardcoded secrets** | API keys, database passwords, and tokens are never in the code | Implemented |
| **Environment variables** | All secrets are stored in env vars, never committed to git | Implemented |
| **Log sanitization** | Patient names are never logged — only symptom descriptions | Implemented |

### 4.2 Data in Transit (Data Moving Between Systems)

| Measure | What It Means | Status |
|---------|---------------|--------|
| **HTTPS everywhere** | All communication between frontend and backend is encrypted | Render provides SSL |
| **Supabase SSL** | Database connections use TLS encryption | Provided by Supabase |
| **Security headers** | Every response includes headers that prevent browser attacks | Implemented |

**Security headers currently set:**

| Header | Value | What It Prevents |
|--------|-------|-----------------|
| `X-Content-Type-Options` | `nosniff` | Browser "guessing" file types (prevents MIME confusion attacks) |
| `X-Frame-Options` | `DENY` | Other websites embedding AegisCare in an iframe (prevents clickjacking) |
| `X-XSS-Protection` | `1; mode=block` | Browser-level XSS filter activation |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Prevents leaking URLs to external sites |
| `Content-Security-Policy` | `default-src 'self'` | Only allows loading resources from the same domain |

### 4.3 API Security

| Measure | What It Means | Status |
|---------|---------------|--------|
| **Rate limiting** | 60 requests per minute per client | Configured |
| **Request size limits** | Audio uploads limited to 25 MB | Implemented |
| **Input validation** | All inputs validated with Pydantic schemas | Implemented |
| **File type validation** | Audio files validated by MIME type AND magic bytes | Implemented |
| **CORS** | Only allowed origins can make cross-origin requests | Configurable via `ALLOWED_ORIGINS` |

### 4.4 What We Log (and What We Don't)

| We LOG | We DON'T Log |
|--------|-------------|
| Request method, path, status code | Patient names |
| Request duration | Patient IDs in plain text (only prefix) |
| Error messages (generic) | Full error stack traces (production) |
| Symptom descriptions (for debugging) | Bearer tokens (only first 4 chars) |
| Escalation events | LLM prompt content |
| System health metrics | Database query results |

**Why this matters:** If our logs are ever accessed by an unauthorized person, they should not contain enough information to identify patients or reconstruct their medical data.

### 4.5 Voice Data Handling

| Stage | Protection |
|-------|-----------|
| **Upload** | Audio files are validated (MIME type + magic bytes + size limit) |
| **Processing** | Audio is transcribed to text, then the original audio is discarded |
| **Storage** | Audio files are NOT stored — only the text transcription is saved |
| **Transcription** | Stored as a symptom record, same protection as all patient data |

**Plain English:** When a patient speaks their symptoms, the system converts the audio to text, then throws away the audio file. The text is treated like any other patient data — protected by RLS and encryption.

---

## 5. Error Handling — What Happens When Things Go Wrong

### 5.1 The Error Response Format

Every error in AegisCare follows the same format, so frontend developers and users always know what happened:

```json
{
    "code": "error",
    "message": "Something went wrong",
    "detail": "More specific information (only in development mode)",
    "error_id": "ERR-1692640000",
    "timestamp": "2026-08-21T14:30:00Z"
}
```

| Field | What It Means | Who Sees It |
|-------|---------------|-------------|
| `code` | Always "error" for errors | Frontend developer |
| `message` | Human-readable description | End user |
| `detail` | Technical details (e.g., stack trace) | Developer (only in dev mode) |
| `error_id` | Unique identifier for this specific error | Support team (for tracking) |
| `timestamp` | When the error occurred (UTC) | Everyone |

**Why `detail` is hidden in production:** In development, we show detailed error messages to help developers fix bugs. In production, those details could leak internal information (database structure, file paths, API keys) to attackers.

### 5.2 Common Errors and What They Mean

#### Authentication Errors

| HTTP Status | Error | What Happened | What the User Sees | What to Do |
|-------------|-------|---------------|--------------------|-----------|
| **401** | `Authentication required` | No token sent | "Please log in to continue" | Log in again |
| **401** | `Invalid or expired token` | Wrong token or token expired | "Your session has expired. Please log in again" | Log in again |
| **403** | `Forbidden` | Valid token but not enough permissions | "You don't have permission to do this" | Contact support |

**Why 401 vs 403 matters:** 401 means "I don't know who you are" (authentication failure). 403 means "I know who you are, but you can't do this" (authorization failure). The user needs different information for each.

#### Validation Errors (Bad Input)

| HTTP Status | Error | What Happened | Example |
|-------------|-------|---------------|---------|
| **422** | `Validation error` | Missing required field | Sent empty symptoms list |
| **422** | `Validation error` | Field too short/long | Patient ID is only 2 characters |
| **422** | `Validation error` | Invalid format | Duration is not a string |

**What the user sees:** "Please check your input. [specific field] is required / too short / invalid."

**What the developer does:** Check the Pydantic schema in `backend/schemas/patient.py` to see the exact validation rules.

#### Client Errors (Wrong Request)

| HTTP Status | Error | What Happened | What to Do |
|-------------|-------|---------------|-----------|
| **404** | `Not found` | Requested resource doesn't exist | Check the ID is correct |
| **400** | `Bad request` | Malformed request | Check request body format |
| **400** | `Unsupported content type` | Wrong file type uploaded | Use WAV, MP3, OGG, FLAC, or M4A |
| **400** | `Audio file is empty` | Uploaded an empty file | Re-record the audio |
| **400** | `Audio file too large` | File > 25 MB | Record a shorter clip |

#### Server Errors (Our Fault)

| HTTP Status | Error | What Happened | What to Do |
|-------------|-------|---------------|-----------|
| **500** | `An unexpected error occurred` | Something broke on our end | Check logs with error_id |
| **500** | `AI analysis failed` | Gemini API call failed | Check GEMINI_API_KEY, retry |
| **500** | `Failed to generate handoff report` | Report generation failed | Check LLM service, retry |
| **503** | `Speech-to-text engine not available` | Whisper not installed | Install faster-whisper |
| **503** | `Text-to-speech engine not available` | XTTS not loaded | Check TTS model path |

#### Rate Limiting

| HTTP Status | Error | What Happened | What to Do |
|-------------|-------|---------------|-----------|
| **429** | `Rate limited` | Too many requests (>60/min) | Wait 1 minute, then retry |

### 5.3 Error Handling Architecture

The system has **three layers** of error handling:

```
Layer 1: Individual Route Handlers
    ↓ (catch expected errors, return specific messages)
Layer 2: ErrorHandlerMiddleware
    ↓ (catch unhandled exceptions, return generic messages)
Layer 3: Global Exception Handlers
    ↓ (catch everything else, return "Internal server error")
```

**Layer 1 (Route Handlers):** Each endpoint catches specific errors it expects. For example, the patient analyze endpoint catches invalid symptom errors and returns a helpful message like "At least one symptom is required."

**Layer 2 (ErrorHandlerMiddleware):** If an error slips past the route handler, this middleware catches it. It logs the full error details (for developers) but returns a generic message to the user (for security).

**Layer 3 (Global Exception Handlers):** The last resort. If something truly unexpected happens, this catches it and returns "Internal server error" with an error ID that support can use to look up what happened.

### 5.4 What NOT to Do with Errors

| Don't | Why |
|-------|-----|
| Don't show stack traces to users | They reveal internal code structure |
| Don't show database error messages | They reveal table/column names |
| Don't show file paths | They reveal server directory structure |
| Don't show API keys or tokens | They give attackers access |
| Don't ignore 500 errors | They indicate something is broken |
| Don't retry infinitely | Can cause cascading failures |

---

## 6. Edge Cases — Scenarios You Must Handle Before Launch

These are the "what if" scenarios that can break the system or create security vulnerabilities. Every one of these must be handled before AegisCare goes live.

### 6.1 Authentication Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **Patient tries to access another patient's data** | Data breach, HIPAA violation | RLS blocks this. Frontend never displays other patients' data. |
| **Token expires mid-session** | Patient loses their triage session | Frontend detects 401, prompts re-login, preserves session state |
| **Token is stolen** | Attacker impersonates patient | Tokens expire in 24h. RLS limits damage to that patient's data. Invalidate on logout. |
| **User logs in from two devices simultaneously** | Session conflict | Allow it — multiple sessions per patient is valid (phone + laptop) |
| **Patient account deleted but sessions remain** | Orphaned data | CASCADE delete: deleting a patient deletes their sessions, symptoms, escalations |
| **Supabase auth service is down** | Nobody can log in | Show "Authentication service unavailable" message. Don't bypass auth. |
| **Admin changes AEGISCARE_TOKEN in production** | All frontend sessions break | Frontend detects 401, shows "Session expired, please refresh" |

### 6.2 Data Integrity Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **Patient reports the same symptom twice** | Duplicate data, confusing timeline | Allow it — the symptom may have worsened. Log timestamp for each occurrence. |
| **Patient reports contradictory symptoms** | AI confusion, incorrect triage | AI confidence scoring flags contradictions. Doctor review for ambiguous cases. |
| **Patient provides empty symptom list** | API error, empty session | Reject with 422 "At least one symptom is required" |
| **Patient provides extremely long symptom text** | Token overflow, slow LLM | Truncate at 500 characters per symptom, max 10 symptoms |
| **Patient ID contains special characters** | SQL injection, parsing errors | Pydantic validation: alphanumeric + hyphens only, 3-64 chars |
| **Symptom contains medical jargon the AI doesn't recognize** | AI gives poor response | Fall back to rule-based scoring. Log unrecognized symptoms for training. |
| **Session crashes mid-triage** | Patient loses progress | Session state persisted to Supabase on every turn. Resume from last save. |
| **Database write fails but LLM already responded** | Data inconsistency | Retry database write. Log failure. Frontend shows "Your response was received but we couldn't save it." |

### 6.3 AI / LLM Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **Gemini API is down** | No AI analysis possible | Fall back to GPT-4o-mini. If both down, use rule-based scoring only. |
| **Gemini returns garbage/incoherent response** | Bad triage advice | Validate response format. If invalid, fall back to rules. Log for review. |
| **Gemini returns a diagnosis** | Regulatory violation (AI can't diagnose) | System prompt explicitly forbids diagnosis. Post-response filter checks for diagnostic language. |
| **LLM response takes >30 seconds** | Patient abandoned, session timeout | Show "Analyzing your symptoms..." spinner. If timeout, retry once, then use rules. |
| **Patient uses the system for non-medical purposes** | Wasted resources, bad data | No special handling — the system triages whatever symptoms are reported. |
| **Patient reports a symptom in a language the AI doesn't support** | Poor quality response | Detect language, show "We don't support [language] yet" message. Don't guess. |
| **LLM generates a harmful or offensive response** | Reputational damage, patient harm | Post-response filter checks for inappropriate content. Replace with safe fallback. |

### 6.4 Voice Pipeline Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **Audio file is corrupted** | Whisper crashes or returns garbage | Validate magic bytes before processing. Return 400 "File appears corrupted." |
| **Audio is too quiet / too loud** | Poor transcription quality | Whisper handles this reasonably. If confidence is low, ask patient to repeat. |
| **Patient speaks a language Whisper doesn't support** | Gibberish transcription | Detect language. If unsupported, show "Voice input in [language] is not supported yet." |
| **Audio file is actually video** | Whisper rejects it | MIME type validation catches this. Accept `video/mp4` but only process audio track. |
| **Patient uploads a non-audio file** | Whisper crashes | Magic byte validation catches non-audio files. Return 400. |
| **Microphone permission denied** | Can't record | Show "Please allow microphone access" with instructions. |
| **Network drops during upload** | Incomplete audio file | Check file size > 0 before processing. Frontend retries. |
| **XTTS model fails to load** | TTS unavailable | Show "Voice response not available" message. Triage continues with text only. |

### 6.5 Drift Detection Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **Patient's condition worsens rapidly** | Delayed escalation | Drift detection runs on EVERY symptom update. Critical symptoms trigger immediate RED escalation. |
| **Patient's condition improves** | Over-escalation | Severity can decrease. If risk score drops below threshold, severity updates accordingly. |
| **Patient leaves mid-session without ending** | Orphaned escalation | Session auto-expires after 24 hours. Final state saved. |
| **Multiple patients escalate at the same time** | Hospital overwhelmed | Load balancer routes to less-full hospitals. Queue escalations if all are full. |
| **Drift detection triggers on a false positive** | Unnecessary emergency alert | Doctor can resolve escalation with notes. False positive rate tracked for tuning. |
| **Patient reports a critical symptom but then says "just kidding"** | System still escalated | Once escalated, only a doctor can resolve it. Patient can add a note but can't un-escalate. |

### 6.6 Deployment Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **Render free tier sleeps after 15 min inactivity** | First request after sleep takes 30+ seconds | Show "Waking up the server..." message. Consider paid tier for production. |
| **Supabase free tier hits row limit** | New data can't be saved | Monitor row count. Alert at 80% capacity. Upgrade plan before hitting limit. |
| **Gemini API quota exhausted** | No more AI calls this month | Fall back to OpenAI. If both exhausted, use rules only. Monitor usage daily. |
| **SSL certificate expires** | Browser shows "Not Secure" | Render auto-renews. Monitor certificate expiry. |
| **Docker image build fails** | Can't deploy updates | Test Docker builds locally before pushing. Keep rollback version ready. |
| **Environment variable missing in production** | App crashes on startup | Pydantic Settings validates required vars at startup. Fail fast with clear error. |

### 6.7 Medical Safety Edge Cases

| Edge Case | Risk | How to Handle |
|-----------|------|---------------|
| **AI recommends treatment instead of triage** | Regulatory violation | System prompt says "You are a triage assistant, not a doctor. Never diagnose or prescribe." |
| **Patient with no symptoms wants to use the app** | Empty triage session | Require at least one symptom to start a session. |
| **Patient reports a life-threatening emergency** | System delay could be fatal | CRITICAL_SYMPTOMS set triggers immediate escalation. Show "Call 911" prominently. |
| **System says "You're fine" but patient is actually dying** | Missed escalation | Guardrail: any symptom in CRITICAL_SYMPTOMS auto-escalates to RED regardless of other factors. |
| **Doctor ignores an escalation** | Patient deterioration | Re-alert after 15 minutes. Re-alert after 30 minutes. Notify hospital admin after 45 minutes. |
| **Handoff report contains inaccurate information** | Doctor makes wrong decision based on bad data | Report includes confidence score. Doctor is responsible for verifying information. |

---

## 7. Compliance Checklist

### HIPAA Readiness (Required Before Handling Real Patient Data)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Encryption at rest | Done (Supabase) | AES-256 provided by Supabase |
| Encryption in transit | Done (HTTPS via Render) | All traffic encrypted |
| Access controls (RLS) | Defined, needs deployment | RLS policies written, need to be applied |
| Audit logging | Partial | Request logging done. Need dedicated audit trail for PHI access. |
| Business Associate Agreement (BAA) | Needed with Supabase | Supabase offers BAA on Pro plan ($25/mo+) |
| BAA with Render | Needed | Render offers BAA on paid plans |
| Data retention policy | Not defined | Need to define: how long to keep patient data |
| Right to deletion | Not implemented | Need: patient can request full data deletion |
| Incident response plan | This document | Section 8 below |
| Minimum necessary access | Done (RLS) | Each role sees only what it needs |
| No PHI in logs | Done | Patient names not logged |
| Automatic session timeout | Done (24h) | Tokens expire after 24 hours |

### What "Minimum Necessary" Means

This is a HIPAA rule: **only access the minimum amount of patient data needed to do the job.**

- A patient needs to see their own symptoms → they can
- A patient needs to see other patients' symptoms → they can't
- A doctor needs to see their assigned patients → they can
- A doctor needs to see patients at other hospitals → they can't
- An admin needs to see "the ER is busy" → they can
- An admin needs to see "Patient X has chest pain" → they can't

---

## 8. Incident Response

### If You Suspect a Data Breach

**Step 1: Don't panic, but act fast.**

| Step | Action | Who |
|------|--------|-----|
| 1 | **Isolate:** Disable the compromised API key or token immediately | System Admin |
| 2 | **Assess:** What data was accessed? Which patients? How much? | System Admin |
| 3 | **Notify:** Tell your team, then your legal counsel | Founder |
| 4 | **Document:** Write down exactly what happened, when, and what was affected | System Admin |
| 5 | **Report:** If PHI was exposed, notify affected patients within 60 days (HIPAA requirement) | Legal |
| 6 | **Fix:** Patch the vulnerability, rotate all credentials | Developer |
| 7. | **Review:** How did this happen? What can prevent it next time? | Full team |

### If the System Goes Down

| Severity | Definition | Response Time | Action |
|----------|-----------|---------------|--------|
| **Critical** | Patients can't access triage | < 15 minutes | All hands on deck. Check Render status, Supabase status, Gemini status. |
| **High** | One feature broken (voice, reports) | < 1 hour | Fix the broken feature. Other features continue working. |
| **Medium** | Slow performance (>5s response) | < 4 hours | Check database connections, LLM latency, server resources. |
| **Low** | Cosmetic issue, non-blocking | < 24 hours | Fix in next development cycle. |

### Emergency Override

In a true medical emergency, the system must **never block access to care.** If the authentication system is down, there should be a documented manual override process for hospital staff to access patient data. This override must:

1. Require two-person authorization (doctor + admin)
2. Be logged with full audit trail
3. Be reviewed within 24 hours
4. Never be automated

**Plain English:** If the login system breaks and a patient is dying, a doctor and an admin together can override the system to access the patient's data. But every override is recorded and reviewed.

---

## Appendix A: Security Checklist Before Launch

| # | Check | Status |
|---|-------|--------|
| 1 | All secrets in environment variables, not in code | DONE |
| 2 | `SECRET_KEY` is a strong random value (not "changeme") | DONE (validated at startup) |
| 3 | `AEGISCARE_TOKEN` is a strong random value (not "dev-token") | DONE (validated at startup, blocks in production) |
| 4 | `ALLOWED_ORIGINS` set to actual frontend domain (not "*") | DONE (validated at startup, blocks in production) |
| 5 | Supabase RLS policies deployed | DONE (migration script written: `002_security_rls.sql`) |
| 6 | Supabase BAA signed (Pro plan) | NEEDS ACTION (requires Supabase Pro subscription) |
| 7 | Render BAA signed (paid plan) | NEEDS ACTION (requires Render paid tier) |
| 8 | Auth upgraded from shared token to Supabase JWT | NEEDS ACTION (architecture ready, placeholder token works) |
| 9 | HTTPS enforced on all endpoints | DONE (Render) |
| 10 | Security headers set on all responses | DONE |
| 11 | Rate limiting configured | DONE |
| 12 | Input validation on all endpoints | DONE |
| 13 | Error messages don't leak internal details | DONE |
| 14 | Logs don't contain PHI | DONE |
| 15 | Session timeout configured (24h) | DONE |
| 16 | CORS configured for production domains only | DONE (validated at startup, blocks wildcard in production) |
| 17 | Audit logging for PHI access | DONE (AuditLoggerMiddleware created) |
| 18 | Data retention policy defined | DONE (DataRetentionService created, configurable via env vars) |
| 19 | Incident response plan documented | DONE (this document) |
| 20 | Emergency override process documented | DONE (Section 8 + /api/v1/emergency/override endpoint) |
| 21 | Emergency override endpoint implemented | DONE (two-person auth: Bearer token + override code) |
| 22 | Audit log table created | DONE (migration script: `002_security_rls.sql`) |
| 23 | Data retention cleanup utility | DONE (`data_retention.py` service) |
| 24 | Production startup validation | DONE (blocks on missing SECRET_KEY, AEGISCARE_TOKEN, wildcard CORS) |

---

## Appendix B: Security Terms Glossary

| Term | Plain English |
|------|--------------|
| **Authentication** | Proving you are who you say you are (like showing ID) |
| **Authorization** | Determining what you're allowed to do (like which rooms your key opens) |
| **JWT** | A temporary digital ID badge that proves you're logged in |
| **RLS** | Database rules that automatically filter what each user can see |
| **PHI** | Protected Health Information — anything that identifies a patient and their medical data |
| **HIPAA** | US law that protects patient health information. Violations can result in fines of $100-$50,000 per violation. |
| **BAA** | Business Associate Agreement — a legal contract saying a vendor (Supabase, Render) will protect your patient data |
| **CORS** | Rules that say which websites can talk to your API |
| **Rate Limiting** | Limits on how many requests a single user can make per minute |
| **Encryption** | Scrambling data so only authorized people can read it |
| **TLS/SSL** | Encryption for data moving over the internet (the "S" in HTTPS) |
| **CSP** | Content Security Policy — rules that prevent malicious code from running in the browser |
| **CSRF** | Cross-Site Request Forgery — an attack where a malicious website tricks your browser into making requests |
| **XSS** | Cross-Site Scripting — an attack where malicious code is injected into a web page |
| **Timing Attack** | An attack where a hacker measures how long authentication takes to guess the secret |
| **Cascade Delete** | When you delete a parent record (patient), all child records (sessions, symptoms) are also deleted |

---

*This document should be reviewed and updated quarterly, or whenever a security incident occurs. Last updated: August 21, 2026.*
