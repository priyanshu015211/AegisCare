import google.generativeai as genai
from typing import Dict, Any
from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()

class AIEngine:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        else:
            self.model = None

    async def generate_response(self, prompt: str) -> str:
        if not self.model:
            return "AI service unavailable."
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            log.error(f"Gemini error: {e}")
            return "Error processing request."

    async def analyze_symptoms(self, patient_state: Dict) -> Dict:
        prompt = f"Patient symptoms: {patient_state.get('symptoms')}. Assess severity and suggest next question."
        response = await self.generate_response(prompt)
        return {"assessment": response, "confidence": 0.75}
