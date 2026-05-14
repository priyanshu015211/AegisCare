from typing import List, Dict
from backend.core.logging import get_logger

log = get_logger(__name__)

class DriftEngine:
    CRITICAL_SYMPTOMS = {"breathing difficulty", "chest pain", "shortness of breath"}

    def detect_drift(self, previous: List[str], new_symptoms: List[str]) -> Dict:
        new_critical = [s for s in new_symptoms if s in self.CRITICAL_SYMPTOMS]
        drift = len(new_critical) > 0
        return {
            "drift_detected": drift,
            "escalation_level": "high" if drift else "low",
            "message": "Condition worsening" if drift else "Stable"
        }
