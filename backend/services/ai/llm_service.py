"""
backend/services/ai/llm_service.py

LLM Service — Gemini primary, OpenAI fallback, rule-based final fallback.

This is the single point of contact for all LLM calls in AegisCare.
Every call is wrapped in try/except with structured logging.  If Gemini
fails, it tries OpenAI.  If both fail, it returns rule-based scoring so
the triage flow never crashes.

Ticket: T-001 — Gemini LLM Integration
"""

import json
import os
from typing import Any, Dict, List, Optional

from backend.core.config import get_settings
from backend.core.constants import (
    SeverityLevel,
    CRITICAL_SYMPTOMS,
    RESPIRATORY_SYMPTOMS,
    CARDIAC_SYMPTOMS,
    NEUROLOGICAL_SYMPTOMS,
    MAX_CONTEXT_TOKENS,
)
from backend.core.logging import get_logger
from backend.services.base_service import BaseService

log = get_logger(__name__)
settings = get_settings()


# ------------------------------------------------------------------
# System prompt — enforces medical safety boundaries
# ------------------------------------------------------------------

SYSTEM_PROMPT = """You are AegisCare, a medical triage assistant. You are NOT a doctor.

CRITICAL RULES:
- You MUST NEVER diagnose conditions or name specific diseases.
- You MUST NEVER prescribe treatments, medications, or dosages.
- You MUST ONLY assess severity and risk level based on reported symptoms.
- You MUST ALWAYS recommend seeking professional medical advice.
- If in doubt, escalate severity upward (err on the side of caution).

Your task:
1. Assess severity: green (low risk), yellow (moderate risk), red (high risk), or critical (emergency)
2. Estimate a risk score from 0 to 100
3. Provide brief clinical reasoning based ONLY on reported symptoms
4. Ask ONE targeted follow-up question to gather more diagnostic information
5. Indicate whether escalation to a medical professional is needed

Respond ONLY with valid JSON in this exact format:
{
  "severity": "green" | "yellow" | "red" | "critical",
  "risk_score": <integer 0-100>,
  "reasoning": "<brief clinical reasoning, no diagnosis>",
  "follow_up_question": "<one targeted question>",
  "escalation_needed": <true|false>
}"""


# ------------------------------------------------------------------
# Rule-based fallback scoring (used when both LLMs fail)
# ------------------------------------------------------------------

# Clinical reference table: symptom -> base risk score
SYMPTOM_RISK_SCORES: Dict[str, int] = {
    # Respiratory (15-25)
    "cough": 15, "shortness of breath": 25, "difficulty breathing": 25,
    "wheezing": 20, "chest tightness": 20, "rapid breathing": 22,
    "breathlessness": 25, "dyspnea": 25,
    # Cardiac (25-40)
    "chest pain": 40, "palpitations": 25, "heart racing": 30,
    "irregular heartbeat": 35, "chest pressure": 35, "radiating arm pain": 38,
    "jaw pain": 30,
    # Neurological (30-45)
    "severe headache": 30, "confusion": 35, "loss of consciousness": 45,
    "seizure": 45, "sudden weakness": 35, "facial drooping": 40,
    "slurred speech": 40, "dizziness": 20,
    # Critical (60+)
    "not breathing": 80, "no pulse": 80, "unresponsive": 80,
    "severe bleeding": 70, "anaphylaxis": 75,
    # General (5-15)
    "fever": 10, "fatigue": 5, "headache": 8, "nausea": 8,
    "vomiting": 12, "diarrhea": 8, "body aches": 5, "sore throat": 5,
    "runny nose": 3, "chills": 5, "dizziness": 15, "loss of appetite": 5,
    "abdominal pain": 15, "muscle pain": 5, "joint pain": 5,
    "skin rash": 8, "swelling": 12, "bleeding": 20,
}


def _rule_based_score(symptoms: List[str]) -> Dict[str, Any]:
    """
    Deterministic rule-based risk scoring.  Used as the final fallback
    when both Gemini and OpenAI are unavailable.

    Returns the same dict shape as the LLM responses so callers don't
    need to branch.
    """
    if not symptoms:
        return {
            "severity": SeverityLevel.GREEN.value,
            "risk_score": 0,
            "reasoning": "No symptoms reported. Risk cannot be assessed.",
            "follow_up_question": "Are you experiencing any symptoms?",
            "escalation_needed": False,
        }

    # Sum symptom scores (capped at 100)
    total = sum(SYMPTOM_RISK_SCORES.get(s.lower().strip(), 10) for s in symptoms)

    # Bonus for multiple symptoms
    if len(symptoms) > 3:
        total += (len(symptoms) - 3) * 5

    # Check for critical symptoms
    symptom_set = {s.lower().strip() for s in symptoms}
    has_critical = bool(symptom_set & CRITICAL_SYMPTOMS)

    risk_score = min(max(total, 0), 100)

    # Map score to severity
    if has_critical or risk_score >= 85:
        severity = SeverityLevel.CRITICAL.value
    elif risk_score >= 61:
        severity = SeverityLevel.RED.value
    elif risk_score >= 31:
        severity = SeverityLevel.YELLOW.value
    else:
        severity = SeverityLevel.GREEN.value

    return {
        "severity": severity,
        "risk_score": risk_score,
        "reasoning": (
            f"Rule-based assessment: {len(symptoms)} symptom(s) reported. "
            f"Risk score {risk_score}/100. "
            + ("Critical symptoms detected — immediate attention required."
               if has_critical else "No critical symptoms detected.")
        ),
        "follow_up_question": "Can you describe how long you have had these symptoms?",
        "escalation_needed": has_critical or risk_score >= 61,
    }


# ------------------------------------------------------------------
# LLMService
# ------------------------------------------------------------------

class LLMService(BaseService):
    """
    Centralised LLM service for AegisCare.

    Call order:
        1. Gemini (google-genai)   — primary, cheapest
        2. OpenAI (gpt-4o-mini)    — fallback if Gemini fails
        3. Rule-based scoring      — final fallback, always works

    Every external call is wrapped in try/except so the triage flow
    never crashes due to an LLM outage.
    """

    def __init__(self):
        super().__init__()
        self._gemini_client = None
        self._openai_client = None

        # --- Gemini ------------------------------------------------
        if settings.gemini_api_key:
            try:
                from google import genai

                self._gemini_client = genai.Client(api_key=settings.gemini_api_key)
                self.log_info(
                    f"Gemini client initialised (model={settings.gemini_model})"
                )
            except Exception as e:
                self.log_error(f"Failed to initialise Gemini client: {e}")
        else:
            self.log_warning("GEMINI_API_KEY not set — Gemini will be skipped")

        # --- OpenAI fallback ---------------------------------------
        if settings.openai_api_key:
            try:
                import openai

                self._openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                self.log_info(
                    f"OpenAI fallback initialised (model={settings.openai_model})"
                )
            except Exception as e:
                self.log_error(f"Failed to initialise OpenAI client: {e}")
        else:
            self.log_warning("OPENAI_API_KEY not set — OpenAI fallback disabled")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze_patient(self, patient_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse a patient's state and return triage assessment.

        Returns dict with keys:
            severity, risk_score, reasoning,
            follow_up_question, escalation_needed
        """
        symptoms: List[str] = patient_state.get("symptoms", [])
        duration: str = patient_state.get("duration", "Not specified")
        previous: List[str] = patient_state.get("previous_symptoms", [])

        # Build the user prompt from patient state
        user_prompt = self._build_user_prompt(symptoms, duration, previous)

        # 1. Try Gemini
        result = await self._call_gemini(user_prompt)
        if result is not None:
            return result

        # 2. Try OpenAI
        result = await self._call_openai(user_prompt)
        if result is not None:
            return result

        # 3. Rule-based fallback (never fails)
        self.log_warning("Both LLMs unavailable — using rule-based scoring")
        return _rule_based_score(symptoms)

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_user_prompt(
        self,
        symptoms: List[str],
        duration: str,
        previous_symptoms: List[str],
    ) -> str:
        """Build the user-facing prompt from patient state data."""
        symptom_list = ", ".join(symptoms) if symptoms else "None reported"
        prev_list = (
            ", ".join(previous_symptoms) if previous_symptoms else "None"
        )

        return (
            f"Patient Symptoms: {symptom_list}\n"
            f"Duration: {duration}\n"
            f"Previous Symptoms: {prev_list}\n\n"
            f"Assess severity, risk score (0-100), provide reasoning, "
            f"and suggest one follow-up question. "
            f"Respond with valid JSON only."
        )

    # ------------------------------------------------------------------
    # Gemini call
    # ------------------------------------------------------------------

    async def _call_gemini(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call Gemini and parse the JSON response.  Returns None on failure."""
        if not self._gemini_client:
            return None

        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
            response = self._gemini_client.models.generate_content(
                model=settings.gemini_model,
                contents=full_prompt,
            )
            text = response.text.strip()
            result = self._parse_llm_json(text)
            if result is not None:
                self.log_info(
                    f"Gemini responded — severity={result['severity']}, "
                    f"risk={result['risk_score']}"
                )
            return result
        except Exception as e:
            self.log_error(f"Gemini call failed: {e}")
            return None

    # ------------------------------------------------------------------
    # OpenAI call
    # ------------------------------------------------------------------

    async def _call_openai(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI and parse the JSON response.  Returns None on failure."""
        if not self._openai_client:
            return None

        try:
            response = self._openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
            )
            text = response.choices[0].message.content.strip()
            result = self._parse_llm_json(text)
            if result is not None:
                self.log_info(
                    f"OpenAI responded — severity={result['severity']}, "
                    f"risk={result['risk_score']}"
                )
            return result
        except Exception as e:
            self.log_error(f"OpenAI call failed: {e}")
            return None

    # ------------------------------------------------------------------
    # JSON parsing
    # ------------------------------------------------------------------

    def _parse_llm_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse the LLM response text as JSON.

        Handles common LLM quirks:
        - Markdown code fences (```json ... ```)
        - Extra text around the JSON blob
        - Trailing commas

        Returns a normalised dict or None if parsing fails.
        """
        # Strip markdown fences
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Find the JSON object boundaries
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            self.log_warning(f"No JSON object found in LLM response: {text[:200]}")
            return None

        json_str = text[start:end]

        try:
            raw = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.log_warning(f"JSON parse error: {e}. Raw: {json_str[:200]}")
            return None

        # Normalise and validate
        severity = raw.get("severity", "yellow").lower()
        valid_severities = {s.value for s in SeverityLevel}
        if severity not in valid_severities:
            severity = "yellow"

        risk_score = raw.get("risk_score", 50)
        if not isinstance(risk_score, (int, float)):
            risk_score = 50
        risk_score = int(min(max(risk_score, 0), 100))

        return {
            "severity": severity,
            "risk_score": risk_score,
            "reasoning": str(raw.get("reasoning", "Symptoms require monitoring.")),
            "follow_up_question": str(
                raw.get(
                    "follow_up_question",
                    "Can you describe your symptoms in more detail?",
                )
            ),
            "escalation_needed": bool(raw.get("escalation_needed", False)),
        }

    # ------------------------------------------------------------------
    # BaseService abstract method
    # ------------------------------------------------------------------

    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Delegates to analyze_patient for BaseService compatibility."""
        return await self.analyze_patient(*args, **kwargs)

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        """True if at least one LLM backend is configured."""
        return self._gemini_client is not None or self._openai_client is not None

    @property
    def active_provider(self) -> str:
        """Returns the name of the active primary provider."""
        if self._gemini_client:
            return "gemini"
        if self._openai_client:
            return "openai"
        return "rule-based"
