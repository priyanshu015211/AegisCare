"""
backend/services/patient_service.py

Patient Service - Handles patient-related business logic.
This is a placeholder service. Real logic will be added in later phases.
"""

from typing import List, Dict, Any, Optional
from backend.services.base_service import BaseService


class PatientService(BaseService):
    """
    Service responsible for patient data processing and state management.
    """

    def __init__(self):
        super().__init__()

    async def process(self, patient_id: str, symptoms: List[str], **kwargs) -> Dict[str, Any]:
        return await self.analyze_symptoms(patient_id, symptoms, **kwargs)

    async def analyze_symptoms(
        self,
        patient_id: str,
        symptoms: List[str],
        duration: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        self.log_info(f"Analyzing symptoms for patient {patient_id}")

        risk_score = self._calculate_placeholder_risk(symptoms, duration)
        severity = self._determine_severity(risk_score)

        return {
            "patient_id": patient_id,
            "symptoms": symptoms,
            "duration": duration,
            "risk_score": risk_score,
            "severity": severity,
            "message": "Placeholder analysis completed."
        }

    async def update_patient_state(
        self, patient_id: str, new_symptom: str
    ) -> Dict[str, Any]:
        self.log_info(f"Updating patient {patient_id} with new symptom")

        risk_score = 75 if new_symptom in ["breathing difficulty", "chest pain"] else 55
        severity = self._determine_severity(risk_score)

        return {
            "patient_id": patient_id,
            "new_symptom": new_symptom,
            "updated_risk_score": risk_score,
            "severity": severity,
            "message": "Patient state updated (placeholder)."
        }

    def _calculate_placeholder_risk(self, symptoms: List[str], duration: Optional[str]) -> int:
        base = 30
        if any(s in ["breathing difficulty", "chest pain"] for s in symptoms):
            base += 35
        if len(symptoms) >= 3:
            base += 15
        if duration and "day" in duration.lower():
            base += 10
        return min(max(base, 0), 100)

    def _determine_severity(self, risk_score: int) -> str:
        if risk_score >= 75:
            return "high"
        elif risk_score >= 50:
            return "medium"
        return "low"
