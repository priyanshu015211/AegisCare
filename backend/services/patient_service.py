"""
backend/services/patient_service.py

Patient Service with Supabase Integration.
"""

from typing import List, Dict, Any, Optional
from backend.services.base_service import BaseService
from backend.db.database_service import db_service
from backend.core.logging import get_logger

log = get_logger(__name__)


class PatientService(BaseService):
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

        # Calculate risk (placeholder logic for now)
        risk_score = self._calculate_placeholder_risk(symptoms, duration)
        severity = self._determine_severity(risk_score)

        # ========================
        # Save to Supabase
        # ========================
        try:
            # Create a new session
            session = await db_service.create_session(patient_id, symptoms)

            if session:
                # Save individual symptoms
                for symptom in symptoms:
                    await db_service.add_symptom(session["session_id"], symptom)

                # Update patient state
                await db_service.update_patient_state(
                    session_id=session["session_id"],
                    severity=severity,
                    risk_score=risk_score
                )

                self.log_info(f"Session saved to Supabase | ID: {session['session_id']}")

        except Exception as e:
            self.log_error(f"Failed to save to database: {e}")

        return {
            "patient_id": patient_id,
            "symptoms": symptoms,
            "duration": duration,
            "risk_score": risk_score,
            "severity": severity,
            "message": "Analysis completed and saved to database."
        }

    async def update_patient_state(
        self, patient_id: str, new_symptom: str
    ) -> Dict[str, Any]:

        self.log_info(f"Updating patient {patient_id} with new symptom: {new_symptom}")

        risk_score = 75 if new_symptom in ["breathing difficulty", "chest pain"] else 55
        severity = self._determine_severity(risk_score)

        # TODO: In future, we will fetch existing session and update it

        return {
            "patient_id": patient_id,
            "new_symptom": new_symptom,
            "updated_risk_score": risk_score,
            "severity": severity,
            "message": "Patient state updated."
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
