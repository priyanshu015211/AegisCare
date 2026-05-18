"""
backend/ai/reasoning/ai_engine.py

AegisCare AI Engine — uses google-genai (replaces deprecated google-generativeai).
"""

import json
from typing import Dict, Any

from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()


class AIEngine:
    def __init__(self):
        self.client = None
        self.model_name = settings.gemini_model  # e.g. "gemini-1.5-flash"

        if settings.gemini_api_key:
            try:
                from google import genai  # google-genai package
                self.client = genai.Client(api_key=settings.gemini_api_key)
                log.info(f"Gemini AI Engine initialised (model={self.model_name})")
            except Exception as e:
                log.error(f"Failed to initialise Gemini client: {e}")
        else:
            log.warning("GEMINI_API_KEY not set — AI Engine will use fallback responses")

    # ------------------------------------------------------------------ #
    # Public API                                                            #
    # ------------------------------------------------------------------ #

    async def analyze_patient(self, patient_state: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = patient_state.get("symptoms", [])
        duration = patient_state.get("duration", "Not specified")
        previous_symptoms = patient_state.get("previous_symptoms", [])

        prompt = f"""You are an expert clinical triage AI assistant.

Patient's Current Symptoms: {', '.join(symptoms)}
Duration: {duration}
Previous Symptoms (if any): {', '.join(previous_symptoms) if previous_symptoms else "None"}

Your task:
1. Assess the current severity (low, medium, high, critical)
2. Give short clinical reasoning
3. Suggest one smart follow-up question
4. Estimate risk score from 0 to 100

Respond ONLY in this JSON format:
{{
  "severity": "low" | "medium" | "high" | "critical",
  "risk_score": number between 0-100,
  "reasoning": "short clinical explanation",
  "follow_up_question": "one relevant question",
  "escalation_needed": true or false
}}"""

        if not self.client:
            return self._fallback_response(symptoms)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            text = response.text.strip()

            # Strip markdown fences if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            result = json.loads(text)
            return {
                "severity": result.get("severity", "medium"),
                "risk_score": result.get("risk_score", 50),
                "reasoning": result.get("reasoning", "Symptoms require monitoring."),
                "follow_up_question": result.get(
                    "follow_up_question", "Can you describe your symptoms more?"
                ),
                "escalation_needed": result.get("escalation_needed", False),
                "raw_response": text,
            }

        except Exception as e:
            log.error(f"Gemini error: {e}")
            return self._fallback_response(symptoms)

    # ------------------------------------------------------------------ #
    # Fallback                                                              #
    # ------------------------------------------------------------------ #

    def _fallback_response(self, symptoms: list) -> Dict[str, Any]:
        """Rule-based fallback used when Gemini is unavailable."""
        high_risk = {"breathing difficulty", "chest pain", "shortness of breath"}
        risk_score = 75 if any(s in high_risk for s in symptoms) else 45
        return {
            "severity": "high" if risk_score >= 70 else "medium",
            "risk_score": risk_score,
            "reasoning": "Based on reported symptoms, condition needs attention.",
            "follow_up_question": "Are you experiencing any difficulty in breathing?",
            "escalation_needed": risk_score >= 70,
            "raw_response": "Fallback response used",
        }
