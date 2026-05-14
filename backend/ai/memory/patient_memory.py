from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.core.logging import get_logger

log = get_logger(__name__)

class PatientMemory:
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.symptoms: List[str] = []
        self.severity: str = "low"
        self.risk_score: int = 0
        self.confidence: float = 0.0
        self.conversation_summary: str = ""
        self.escalation_history: List[Dict] = []
        self.last_updated: datetime = datetime.utcnow()

    def add_symptom(self, symptom: str):
        if symptom.lower() not in [s.lower() for s in self.symptoms]:
            self.symptoms.append(symptom.lower())
            self.last_updated = datetime.utcnow()

    def update_risk(self, risk_score: int, severity: str, confidence: float):
        self.risk_score = risk_score
        self.severity = severity
        self.confidence = confidence
        self.last_updated = datetime.utcnow()

    def get_state(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "symptoms": self.symptoms,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "conversation_summary": self.conversation_summary,
            "last_updated": self.last_updated.isoformat()
        }
