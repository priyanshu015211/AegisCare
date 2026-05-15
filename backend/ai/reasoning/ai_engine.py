"""
backend/ai/reasoning/ai_engine.py

Core AI Reasoning Engine using Gemini.
Handles symptom analysis, adaptive questioning, and structured responses.
"""

import google.generativeai as genai
from typing import Dict, Any, List, Optional
from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()


class AIEngine:
    def __init__(self):
        self.model = None
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                log.info("Gemini AI Engine initialized successfully")
            except Exception as e:
                log.error(f"Failed to initialize Gemini: {e}")
        else:
            log.warning("GEMINI_API_KEY not found. AI features will be limited.")

    async def analyze_patient(self, patient_state: Dict[str, Any]) -> Dict[str, Any]:
    symptoms = patient_state.get("symptoms", [])
    duration = patient_state.get("duration", "Not specified")

    prompt = f"""
You are a clinical triage assistant.

Symptoms: {', '.join(symptoms)}
Duration: {duration}

Respond **only** in this JSON format:
{{
  "severity": "low" | "medium" | "high" | "critical",
  "reasoning": "short explanation",
  "follow_up_question": "one relevant question"
}}
"""

    response_text = await self.generate_response(prompt)

    # Try to parse JSON from response
    try:
        import json
        # Extract JSON if wrapped in markdown
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response_text

        parsed = json.loads(json_str)
        return {
            "severity": parsed.get("severity", "medium"),
            "reasoning": parsed.get("reasoning", response_text),
            "follow_up_question": parsed.get("follow_up_question", "Can you tell me more?"),
            "raw_response": response_text
        }
    except:
        # Fallback if JSON parsing fails
        return {
            "severity": "medium",
            "reasoning": response_text,
            "follow_up_question": "Can you describe your symptoms in more detail?",
            "raw_response": response_text
        }
            "raw_response": response_text
        }
