"""
backend/services/risk_service.py

Risk Scoring Service (Placeholder)
Responsible for calculating patient risk scores and severity levels.
"""

from typing import List, Dict, Any, Optional
from backend.services.base_service import BaseService


class RiskScoringService(BaseService):
    """
    Placeholder service for risk scoring logic.
    Will be replaced with more sophisticated rule engine + AI in later phases.
    """

    def __init__(self):
        super().__init__()

    async def process(self, symptoms: List[str], **kwargs) -> Dict[str, Any]:
        return await self.calculate_risk(symptoms, **kwargs)

    async def calculate_risk(
        self,
        symptoms: List[str],
        duration: Optional[str] = None,
        known_conditions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        self.log_info("Calculating placeholder risk score")

        base_score = 30

        critical_symptoms = {"breathing difficulty", "chest pain", "shortness of breath"}
        if any(s in critical_symptoms for s in symptoms):
            base_score += 40

        if len(symptoms) >= 3:
            base_score += 15

        if duration and ("day" in duration.lower() or "week" in duration.lower()):
            base_score += 10

        risk_score = min(max(base_score, 0), 100)
        severity = self._get_severity(risk_score)

        return {
            "risk_score": risk_score,
            "severity": severity,
            "factors": symptoms
        }

    def _get_severity(self, score: int) -> str:
        if score >= 75:
            return "high"
        if score >= 50:
            return "medium"
        return "low"
