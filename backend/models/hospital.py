"""
backend/models/hospital.py

Pydantic schemas for hospitals, departments, and doctors.
Used by the load balancing (Phase 12) and routing systems.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from backend.core.constants import DoctorStatus


# ----------------------------------------------------------
# Hospital
# ----------------------------------------------------------

class HospitalLoad(BaseModel):
    """Real-time capacity snapshot for a hospital."""
    hospital_id: str
    hospital_name: str
    total_capacity: int
    current_occupancy: int
    er_capacity: int
    er_occupancy: int
    ambulances_available: int
    load_percentage: float = Field(ge=0.0, le=100.0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_high_load(self) -> bool:
        return self.load_percentage >= 80.0

    @property
    def is_critical_load(self) -> bool:
        return self.load_percentage >= 95.0


class Hospital(BaseModel):
    """Static profile of a hospital."""
    hospital_id: str
    name: str
    address: str
    city: str
    phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    specialties: list[str] = Field(default_factory=list)
    has_emergency: bool = True
    has_icu: bool = True
    total_beds: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ----------------------------------------------------------
# Doctor
# ----------------------------------------------------------

class DoctorProfile(BaseModel):
    """Persisted doctor profile."""
    doctor_id: str
    full_name: str
    specialty: str
    department: Optional[str] = None
    hospital_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    languages: list[str] = Field(default_factory=list)
    available_slots: list[datetime] = Field(default_factory=list)
    status: DoctorStatus = DoctorStatus.AVAILABLE
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DoctorAvailability(BaseModel):
    """Real-time availability status for a doctor."""
    doctor_id: str
    status: DoctorStatus
    current_patient_id: Optional[str] = None
    next_available_at: Optional[datetime] = None
    queue_length: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)
