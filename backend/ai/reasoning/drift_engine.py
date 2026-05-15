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
        current_symptoms: List[str]
    ) -> Dict[str, Any]:
        
        previous_critical = set(previous_symptoms) & self.CRITICAL_SYMPTOMS
        current_critical = set(current_symptoms) & self.CRITICAL_SYMPTOMS

        new_critical_symptoms = current_critical - previous_critical
        drift_detected = len(new_critical_symptoms) > 0

        escalation_level = "high" if drift_detected else "low"

        return {
            "drift_detected": drift_detected,
            "escalation_level": escalation_level,
            "new_critical_symptoms": list(new_critical_symptoms),
            "message": (
                "Patient condition appears to be worsening." 
                if drift_detected else 
                "No significant deterioration detected."
            )
        }
