from datetime import datetime, timedelta
from typing import Dict, Any, List
from backend.core.logging import get_logger

log = get_logger(__name__)

class AppointmentManager:
    def __init__(self):
        self.appointments = []

    async def book_appointment(self, patient_id: str, urgency: str = "normal"):
        if urgency == "emergency":
            scheduled_time = datetime.utcnow() + timedelta(minutes=15)
        else:
            scheduled_time = datetime.utcnow() + timedelta(hours=2)

        appointment = {
            "appointment_id": f"APT-{patient_id}",
            "patient_id": patient_id,
            "scheduled_time": scheduled_time.isoformat(),
            "urgency": urgency,
            "status": "confirmed"
        }
        self.appointments.append(appointment)
        return appointment
