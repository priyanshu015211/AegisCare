```markdown
# AegisCare — Prompt Context (Final)

## LLM Usage Rules

**LLMs are used ONLY for:**
- Symptom interpretation
- Adaptive follow-up questions
- Generating explanations
- Creating doctor handoff summaries

**LLMs are NOT used for:**
- Severity scoring
- Escalation decisions
- Risk calculation
- Speech-to-Text / Text-to-Speech

## Patient State (Sent to LLM)

```json
{
  "patient_id": "string",
  "symptoms": ["fever", "cough"],
  "severity": "medium",
  "risk_score": 61,
  "confidence": 0.82,
  "conversation_summary": "..."
}
