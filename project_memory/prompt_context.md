# AegisCare — Prompt Context (LLM Engineering Reference)

## LLM Usage Rules

AegisCare uses LLMs ONLY for:
1. Generating adaptive follow-up triage questions
2. Explaining a severity assessment in plain language
3. Producing the final doctor handoff report
4. Summarizing patient session history (rolling memory)

LLMs are NOT used for:
- Severity scoring (deterministic rule engine)
- Escalation decisions (threshold-based logic)
- STT / TTS (dedicated models)
- Routing decisions (rule-based)

---

## Token Budget

Target: under 800 tokens per LLM call.

Context sent per call:
1. System prompt (cached, ~150 tokens)
2. PatientState JSON (~120 tokens)
3. Last AI response (~80 tokens)
4. Patient's latest message (~80 tokens)
5. Task instruction (~50 tokens)

Total target: ~480 tokens per call (well under limit).

---

## PatientState JSON (LLM Input)

```json
{
  "patient_id": "uuid",
  "session_id": "uuid",
  "age": 45,
  "gender": "female",
  "symptoms": ["fever", "cough", "chest tightness"],
  "symptom_duration": "3 days",
  "severity": "yellow",
  "risk_score": 58,
  "known_conditions": ["asthma"],
  "current_medications": ["salbutamol inhaler"],
  "allergies": ["penicillin"]
}
```

---

## System Prompt Template (Triage Role)

```
You are AegisCare, a clinical triage assistant supporting healthcare workers.
Your role is to gather precise symptom information, not to diagnose.
Respond in plain, calm English. One question at a time. No emojis.
Current patient state: {patient_state_json}
```

---

## Prompt Roles

| Role      | Purpose                              | Max Output Tokens |
|-----------|--------------------------------------|-------------------|
| triage    | Adaptive follow-up questions         | 150               |
| reasoning | Explain risk to patient              | 200               |
| summary   | Compress session history             | 300               |
| report    | Generate doctor handoff report       | 800               |
