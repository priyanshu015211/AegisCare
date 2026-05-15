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

    async def generate_response(self, prompt: str, max_tokens: int = 512) -> str:
        if not self.model:
            return "AI service is currently unavailable. Please configure Gemini API key."

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=settings.llm_temperature,
                )
            )
            return response.text.strip()
        except Exception as e:
            log.error(f"Gemini generation error: {e}")
            return "I'm having trouble processing your request right now."

    async def analyze_patient(self, patient_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method for analyzing patient symptoms using Gemini.
        """
        symptoms = patient_state.get("symptoms", [])
        duration = patient_state.get("duration", "Not specified")

        prompt = f"""
You are an experienced clinical triage assistant.

Patient Information:
- Symptoms: {', '.join(symptoms)}
- Duration: {duration}

Task:
1. Assess the current severity level (Low / Medium / High / Critical)
2. Give a short clinical reasoning (1-2 sentences)
3. Suggest ONE important follow-up question to ask the patient

Respond in this exact format:
Severity: <Low/Medium/High/Critical>
Reasoning: <your reasoning>
Follow-up Question: <one clear question>
"""

        response_text = await self.generate_response(prompt)

        # Basic parsing (can be improved later)
        severity = "medium"
        reasoning = response_text
        follow_up = "Can you describe your symptoms in more detail?"

        if "Severity:" in response_text:
            try:
                lines = response_text.split("\n")
                for line in lines:
                    if "Severity:" in line:
                        severity = line.split(":")[1].strip().lower()
                    if "Follow-up Question:" in line:
                        follow_up = line.split(":", 1)[1].strip()
            except:
                pass

        return {
            "severity": severity,
            "reasoning": reasoning,
            "follow_up_question": follow_up,
            "raw_response": response_text
        }
