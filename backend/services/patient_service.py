"""
backend/services/patient_service.py

Placeholder Patient Service Layer for AegisCare.

This service contains the business logic for patient analysis and updates.
Currently uses mock/placeholder logic. Will be replaced with real
AI + rule engine in later phases (Phase 8, 9, 11).

Design goals:
- Async ready
- Clean separation from API layer
- Easy to swap mock implementation with real one later
"""

import random
from typing import List
from backend.core.logging import get_logger

log = get_logger(__name__)


class PatientService:
    """
    Service responsible for patient state analysis and risk evaluation.
    """

    async def analyze_patient(
        self,
        patient_id: str,
        symptoms: List[str],
        duration: str | None = None,
        language: str = "en"
    ) -> dict:
        """
        Placeholder analysis logic.
        In future phases this will:
        - Call Gemini / rule engine
        - Run Dynamic Emergency Drift Detection
        - Calculate real confidence + risk
        """
        log.info(f"Analyzing patient {patient_id} with symptoms: {symptoms}")

        # === PLACEHOLDER RISK SCORING LOGIC ===
        base_risk = 30
        symptom_count = len(symptoms)

        # Simple mock scoring (will be replaced)
        if any(s in ["breathing difficulty", "chest pain", "shortness of breath"] for s in symptoms):
            base_risk += 35
        if symptom_count >= 3:
            base_risk += 15
        if duration and ("day" in duration.lower() or "week" in duration.lower()):
            base_risk += 10

        risk_score = min(max(base_risk, 0), 100)

        # Determine severity
        if risk_score >= 75:
            severity = "high"
        elif risk_score >= 50:
            severity = "medium"
        else:
            severity = "low"

        confidence = round(random.uniform(0.65, 0.92), 2)

        return {
            "patient_id": patient_id,
            "severity": severity,
            "risk_score": risk_score,
            "confidence": confidence,
            "message": "Initial assessment completed. (placeholder logic)",
        }

    async def update_patient_condition(
        self,
        patient_id: str,
        new_symptom: str
    ) -> dict:
        """
        Placeholder update workflow.
        Simulates condition drift when new symptoms are reported.
        """
        log.info(f"Updating patient {patient_id} with new symptom: {new_symptom}")

        # Simple mock escalation on new critical symptom
        base_risk = 55
        if new_symptom in ["breathing difficulty", "chest pain", "unresponsive", "severe bleeding"]:
            base_risk = 82
        elif new_symptom in ["fever", "cough"]:
            base_risk = 62

        risk_score = min(base_risk, 100)

        if risk_score >= 75:
            severity = "high"
        elif risk_score >= 50:
            severity = "medium"
        else:
            severity = "low"

        return {
            "patient_id": patient_id,
            "updated_risk_score": risk_score,
            "severity": severity,
            "message": "Patient condition updated based on new symptom. (placeholder)",
        }


# Singleton instance (can be replaced with proper DI later)
patient_service = PatientService()
