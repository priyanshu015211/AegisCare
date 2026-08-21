# AegisCare — Product Requirements Document

**Version:** 1.0 (MVP)  
**Date:** August 21, 2026  
**Status:** Draft  

---

## 1. What the App Does

AegisCare is an **AI-powered healthcare coordination platform** that continuously monitors patient symptoms in real time, detects clinical deterioration through its proprietary **Dynamic Emergency Drift Detection** engine, and automatically routes patients to appropriate care — from AI-guided triage all the way through to live doctor video consultation.

In plain language: AegisCare is a smart medical triage assistant that listens to your symptoms, watches how they change over time, and gets you to the right level of help — before things get dangerous.

**Key capabilities:**
- Real-time symptom monitoring with severity tracking (GREEN → YELLOW → RED)
- Automated escalation when symptom drift is detected
- Adaptive triage questioning (the AI adjusts its questions based on answers)
- Patient-to-hospital routing based on hospital load
- Video consultation with available doctors (Agora SDK)
- Auto-generated, structured handoff reports for receiving clinicians
- Live hospital command center dashboard for staff

---

## 2. Who It Is For

### Primary Users (Patients)

| Segment | Description |
|---------|-------------|
| **Rural/underserved patients** | People far from hospitals or specialists who need remote triage before traveling |
| **Elderly patients** | Seniors managing chronic conditions who need monitoring between visits |
| **Anxious patients in early symptoms** | People unsure if their symptoms warrant an ER visit — AegisCare gives them a clear answer |
| **Multilingual populations** | Patients who may not speak the dominant language of nearby healthcare facilities |

### Secondary Users (Healthcare Providers)

| Segment | Description |
|---------|-------------|
| **Emergency department staff** | Need to prioritize incoming patients; want pre-sorted, pre-documented cases |
| **Rural clinic doctors** | Overloaded generalists who need AI-assisted decision support |
| **Hospital administrators** | Need visibility into patient flow, load balancing, and resource allocation |
| **Triage nurses** | Front-line screeners who benefit from structured symptom histories |

### Tertiary Users

| Segment | Description |
|---------|-------------|
| **Paramedics / EMS** | Field workers who need to relay structured patient data en route |
| **Insurance / telehealth platforms** | Integration partners (future) |

---

## 3. What Problem It Solves

### The Core Problem

**Healthcare triage is broken.** Patients arrive at hospitals with either too little information (delaying treatment) or too much noise (overwhelming clinicians). Meanwhile, symptom deterioration between initial contact and treatment goes undetected — and that gap kills people.

### Specific Pain Points

| Pain Point | Current Reality | AegisCare Solution |
|------------|-----------------|---------------------|
| **Symptom deterioration goes unseen** | A patient reports a cough at 8am. By noon it\'s become chest pain. Nobody was monitoring the trajectory. | Continuous drift detection tracks symptom evolution in real time and auto-escalates |
| **Triage is subjective and inconsistent** | Different triage nurses score the same symptoms differently. Rush-hour ERs deprioritize serious cases. | Rule-based + AI hybrid engine provides consistent, evidence-informed severity scoring |
| **Patient handoffs are lossy** | Critical context is lost when patients move from triage to ER to specialist. Notes are incomplete or illegible. | Auto-generated structured handoff reports travel with the patient |
| **Rural patients can\'t access specialists** | A rural clinic doctor isn\'t sure if a patient needs a cardiologist. Referral takes weeks. | On-demand video consultation with available specialists via Agora |
| **Hospitals can\'t see the forest** | Admins have no real-time view of patient load across departments or facilities. | Live command center dashboard with load-balancing visibility |

### The Emotional Problem

Patients feel **scared and unheard**. Doctors feel **overwhelmed and unsupported**. AegisCare bridges that gap with continuous AI monitoring that makes patients feel watched-over and gives doctors the structured data they need.

---

## 4. Core Features

### Must-Have Features (MVP / V1)

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| F1 | **Symptom Intake Chat** | Patient enters symptoms via conversational AI interface (text + voice). Adaptive questioning adjusts follow-ups based on responses. | P0 — Core |
| F2 | **Dynamic Emergency Drift Detection** | Engine continuously tracks symptom progression within a session. Detects deterioration patterns (e.g., fever → cough → breathing difficulty → chest tightness). Triggers escalation automatically. | P0 — Core (Key Differentiator) |
| F3 | **Severity Scoring & Risk Classification** | Rule-based + AI hybrid assigns real-time risk level: GREEN (monitor), YELLOW (urgent), RED (emergency). Updates dynamically as drift is detected. | P0 — Core |
| F4 | **Automated Escalation Workflows** | When risk escalates: alerts hospital command center, suggests nearest appropriate facility, initiates doctor handoff report. | P0 — Core |
| F5 | **Doctor Handoff Report Generation** | AI generates structured, clinician-ready summary: symptom history, progression timeline, risk assessment, medications, allergies. Exportable as PDF. | P0 — Core |
| F6 | **Patient Memory System** | Structured JSON-based patient context that persists across a session and can be referenced by clinicians. Tracks all symptom entries, vitals, and AI assessments. | P0 — Core |
| F7 | **Hospital Command Center Dashboard** | Real-time view for hospital staff: active patients, severity distribution, escalation queue, hospital load metrics. Built in Streamlit + Plotly. | P0 — Core |
| F8 | **Hospital Load Balancing** | Routes patients to appropriate facilities based on current capacity, specialties available, and geographic proximity. | P0 — Core |
| F9 | **Voice Pipeline (STT + TTS)** | Patients can speak their symptoms (Faster Whisper STT) and hear AI responses (XTTS-v2 TTS). Critical for accessibility and elderly patients. | P0 — Core |
| F10 | **User Authentication** | Supabase Auth integration. Separate flows for patients vs. healthcare providers. Secure session management. | P0 — Core |

### Nice-to-Have Features (V1.1+)

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| F11 | **Video Consultation (Agora SDK)** | Live video calls between patients and doctors. Screen sharing for test results. | P1 — High |
| F12 | **Appointment Scheduling** | Book follow-up appointments based on triage results. Calendar integration. | P1 — High |
| F13 | **Multilingual Support** | Real-time translation for non-native speakers. At minimum: English, Spanish, Mandarin, Hindi. | P1 — High |
| F14 | **Patient History Dashboard** | Longitudinal view of a patient\'s symptom history across multiple sessions. Trend analysis. | P2 — Medium |
| F15 | **Confidence Scoring & Contradiction Detection** | AI flags when patient statements contradict each other or when its own confidence is low. Prompts clarification. | P2 — Medium |
| F16 | **Analytics & Reporting** | Aggregate analytics: average triage times, escalation rates, outcome tracking. For hospital admins. | P2 — Medium |
| F17 | **SMS/Notification Alerts** | Push notifications to patients (medication reminders, appointment confirmations) and staff (escalation alerts). | P2 — Medium |
| F18 | **Insurance / Payer Integration** | Pre-authorization checks, coverage verification. | P3 — Future |
| F19 | **Mobile-First Responsive Design** | Native-feel mobile experience (currently Streamlit desktop-first). React Native or Flutter companion app. | P3 — Future |

---

## 5. User Flow: Start to Finish

### Flow A: Patient Triage Journey

1. **ONBOARDING**: Open app → Create account → Auth via Email/Phone + OTP
2. **SYMPTOM INTAKE**: Patient describes symptoms (text/voice) → AI asks adaptive questions → Patient answers
3. **DRIFT DETECTION (Continuous)**: AI monitors symptom trajectory for worsening patterns. New symptoms? Existing symptoms worse? Vital signs trending?
4. **TRIAGE DISPOSITION**:
   - GREEN → Self-care guidance + follow-up in 24-48h
   - YELLOW → Urgent care recommended: find nearby clinic, book appointment
   - RED → Emergency escalation: alert hospital + generate handoff report + connect to doctor
5. **HANDOFF & COORDINATION**: Auto-generated report (demographics, symptom timeline, drift data, AI assessment, risk factors, allergies, recommended actions) sent to receiving doctor, ER triage, and patient record
6. **POST-CONSULTATION**: Doctor reviews report + consults → Follow-up scheduled → Patient receives summary + next steps

### Flow B: Hospital Staff / Command Center Journey

Login → View Dashboard → See active patients (sorted by severity) → Review incoming escalations → Accept/reassign patients → View hospital load metrics → Generate shift reports

### Flow C: Doctor Consultation Journey

Receive handoff report → Review patient context + drift timeline → Join video call (Agora) → Consult with patient → Update patient record → Prescribe / refer / discharge

---

## 6. MVP Definition

### What ships in V1 (MVP)

**The MVP is a working AI triage system that can:**
1. Accept a patient's symptoms via text and voice
2. Run adaptive triage questioning
3. Detect symptom drift and escalate automatically
4. Generate a doctor-ready handoff report
5. Display a basic hospital command center dashboard
6. Authenticate patients and providers

**In scope:**
- Streamlit frontend (web — functional, not beautiful)
- FastAPI backend with all core services
- Gemini 1.5 Flash for AI reasoning (GPT-4o-mini fallback)
- Supabase for auth + database
- Faster Whisper STT + XTTS-v2 TTS
- Docker deployment
- Static hospital load routing (basic load balancing)

**MVP does NOT include:**
- Video consultation (Agora placeholder only)
- Mobile app (web-only)
- Multilingual support
- Insurance integration
- Patient history across sessions (single-session only for MVP)
- Advanced analytics

### MVP Success Criteria

The MVP is successful if:
- A patient can complete a full triage session and receive a handoff report
- Drift detection triggers escalation at least as accurately as manual triage (pilot testing)
- The command center dashboard updates in real time
- End-to-end latency from symptom input to report generation is < 10 seconds
- System handles 50 concurrent triage sessions without degradation

---

## 7. Success Metrics

### North Star Metric
**Time-to-appropriate-care** — the elapsed time from when a patient first reports symptoms to when they are connected with the right level of clinical care.

### Product Metrics

| Metric | Target (MVP) | Target (6 months) | How Measured |
|--------|-------------|-------------------|--------------|
| **Triage accuracy** | >= 85% agreement with clinician assessment | >= 92% | Pilot study: compare AI triage vs. clinician triage on same patients |
| **Drift detection sensitivity** | >= 80% of deteriorations caught | >= 90% | Retrospective analysis of cases where symptoms worsened |
| **Drift detection false positive rate** | <= 25% | <= 15% | Count of unnecessary escalations |
| **Time to handoff report** | < 10 seconds | < 5 seconds | Backend performance monitoring |
| **Session completion rate** | >= 70% | >= 85% | Analytics: users who start triage and reach a disposition |
| **User satisfaction (patients)** | NPS >= 30 | NPS >= 50 | Post-session survey |
| **User satisfaction (doctors)** | >= 75% find reports "useful" | >= 90% | Provider feedback surveys |
| **Concurrent session capacity** | 50 sessions | 500+ sessions | Load testing + production monitoring |

### Business Metrics (Post-MVP)

| Metric | Target (12 months) |
|--------|-------------------|
| Hospital partners signed | 5 |
| Monthly active patients | 10,000 |
| Monthly triage sessions | 5,000 |
| Average triage time reduction | 30% vs. traditional triage |
| Emergency department diversion rate | 15-20% of low-acuity cases appropriately redirected |

### Guardrail Metrics (Do No Harm)

| Metric | Threshold |
|--------|-----------|
| Critical symptom missed (false negative) | 0 tolerance — any miss triggers incident review |
| System downtime during peak hours | < 1 hour/month |
| PHI data exposure incidents | 0 |
| Average AI response latency | < 3 seconds per interaction |

---

## 8. What We Are NOT Building in V1

This section is as important as what we are building. Every "not now" is a deliberate decision to stay focused.

| Excluded Feature | Why It's Out | When It Comes Back |
|-----------------|--------------|---------------------|
| **Mobile app (iOS/Android)** | Streamlit web app is functional for MVP. Native mobile is a massive effort. | V2 — Consider React Native or Flutter |
| **Video consultation (Agora)** | Requires significant integration + HIPAA compliance for video streams. Placeholder architecture exists. | V1.1 — After core triage is validated |
| **Patient history across sessions** | MVP is single-session. Cross-session memory requires complex data model + privacy considerations. | V1.1 — Build longitudinal patient profiles |
| **Multilingual support** | Requires translation infrastructure, medical terminology mapping, and regulatory review per language. | V1.2 — Start with Spanish + Mandarin |
| **Insurance / payer integration** | Requires partner relationships, compliance reviews, and billing infrastructure. | V2 — Business model phase |
| **EHR integration (Epic, Cerner)** | HL7/FHIR integration is complex and requires hospital IT partnerships. | V2 — After hospital adoption |
| **AI diagnosis / treatment recommendations** | **Regulatory boundary.** AI cannot diagnose or prescribe. Triage and risk assessment only. | Never — regulatory boundary |
| **Real-time vital sign monitoring (IoT)** | Requires hardware partnerships (pulse oximeters, BP cuffs, etc.) | V2+ — If wearable API standard emerges |
| **Advanced analytics dashboard** | Full analytics suite requires significant data pipeline work. Basic command center is MVP. | V1.1 — After data accumulates |
| **Drug interaction checking** | Requires pharmaceutical database licensing and medical accuracy validation. | V2 — Partner with drug DB provider |
| **Patient-to-patient community features** | Social features in healthcare require careful moderation and regulatory compliance. | Never or V3 — Out of core scope |
| **Offline mode** | Healthcare triage requires connectivity for AI inference. Offline would severely limit functionality. | Never — core constraint |
| **Gamification / patient engagement hooks** | Inappropriate for emergency healthcare context. | Never — wrong tone for the product |

---

## Appendix A: Technical Constraints

| Constraint | Detail |
|------------|--------|
| AI Model | Gemini 1.5 Flash (primary), GPT-4o-mini (fallback). Must support both. |
| Frontend Framework | Streamlit (MVP). Plan migration path for V2. |
| Database | Supabase (PostgreSQL). Schema must support multi-tenant hospital deployment. |
| Voice | Faster Whisper (STT) + XTTS-v2 (TTS). Must work on server-side (no client-side GPU). |
| Deployment | Docker-first. Target Render or similar PaaS for MVP hosting. |
| Compliance | HIPAA considerations from Day 1 (encryption at rest, audit logging, BAA with Supabase). |
| Cost | Gemini Flash is cost-effective. Budget: < $0.01 per triage session for AI inference. |

## Appendix B: Competitive Landscape

| Competitor | What They Do | How We Differentiate |
|-----------|-------------|---------------------|
| Ada Health | Symptom checker → possible conditions | We track drift over time; they snapshot once |
| Babylon Health | AI triage + telehealth | We focus on hospital coordination, not direct-to-consumer |
| Current Health | Remote patient monitoring | We're acute triage, not chronic monitoring |
| Chief Medicine | Clinical decision support for doctors | We serve patients AND providers in one loop |

**Our moat: Dynamic Emergency Drift Detection.** No competitor continuously monitors symptom evolution within a session and auto-escalates based on trajectory.

---

*This PRD is a living document. Update as validated learnings come from MVP usage.*
