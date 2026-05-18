"""
backend/ai/reasoning/drift_engine.py

Dynamic Emergency Drift Detection Engine
"""

from typing import List, Dict, Any
from backend.core.logging import get_logger

log = get_logger(__name__)


class DriftEngine:
    CRITICAL_SYMPTOMS = {
        "breathing difficulty", "chest pain", "shortness of breath",
        "unresponsive", "severe bleeding", "loss of consciousness"
    }

    def detect_drift(
        self,
        previous_symptoms: List[str],
        current_symptoms: List[str],
    ) -> Dict[str, Any]:
        """Compare previous vs current symptoms and return drift analysis."""

        previous_set = set(previous_symptoms)
        current_set = set(current_symptoms)

        new_symptoms = current_set - previous_set
        new_critical = new_symptoms & self.CRITICAL_SYMPTOMS

        drift_score = len(new_critical) * 40 + len(new_symptoms) * 10
        drift_detected = drift_score > 30

        return {
            "drift_detected": drift_detected,
            "drift_score": min(drift_score, 100),
            "escalation_level": "high" if drift_detected else "low",
            "new_symptoms": list(new_symptoms),
            "new_critical_symptoms": list(new_critical),
            "message": "Condition worsening" if drift_detected else "Stable",
        }
