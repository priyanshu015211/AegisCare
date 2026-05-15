"""
backend/coordination/appointment_manager.py
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from backend.core.logging import get_logger

log = get_logger(__name__)


class AppointmentManager:
    def __init__(self):
        self.appointments: List[Dict] = []

    async def book_appointment(
        self, 
        patient_id: str, 
        urgency: str = "normal",
        preferred_time: Optional[str] = None
    ) -> Dict[str, Any]:
        
        if urgency == "emergency":
            scheduled_time = datetime.utcnow() + timedelta(minutes=15)
        else:
            scheduled_time = datetime.utcnow() + timedelta(hours=2)

        appointment = {
            "appointment_id": f"APT-{patient_id}-{int(datetime.utcnow().timestamp())}",
            "patient_id": patient_id,
            "scheduled_time": scheduled_time.isoformat(),
            "urgency": urgency,
            "status": "confirmed",
            "doctor": "Dr. Available (Auto-assigned)"
        }

        self.appointments.append(appointment)
        log.info(f"Appointment booked for {patient_id} | Urgency: {urgency}")
        return appointment

    def get_upcoming_appointments(self, patient_id: Optional[str] = None) -> List[Dict]:
        if patient_id:
            return [a for a in self.appointments if a["patient_id"] == patient_id]
        return self.appointments
