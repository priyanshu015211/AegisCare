"""
backend/schemas/patient.py

Pydantic request models for Patient API endpoints.
Strong validation for all incoming patient data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid


class PatientAnalyzeRequest(BaseModel):
    """
    Request body for POST /api/v1/patient/analyze

    session_id isolates concurrent triage sessions for the same patient.
    If the caller does not supply one, a new UUID is generated so that
    PatientMemory objects never collide between independent sessions.
    """
    patient_id: str = Field(
        ...,
        min_length=3,
        max_length=64,
        description="Unique identifier for the patient",
        examples=["pat_abc123"]
    )
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        min_length=3,
        max_length=64,
        description="Unique identifier for this triage session. "
                    "Auto-generated when omitted.",
        examples=["sess_xyz789"]
    )
    symptoms: List[str] = Field(
        ...,
        min_length=1,
        description="List of reported symptoms",
        examples=[["fever", "cough", "fatigue"]]
    )
    duration: Optional[str] = Field(
        None,
        max_length=100,
        description="How long the symptoms have been present (e.g. '2 days', 'since yesterday')",
        examples=["2 days"]
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="Preferred language for response (ISO code)",
        examples=["en", "hi"]
    )

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one symptom is required")
        return [s.lower().strip() for s in v if s.strip()]

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "pat_abc123",
                "session_id": "sess_xyz789",
                "symptoms": ["fever", "cough"],
                "duration": "2 days",
                "language": "en"
            }
        }
    }


class PatientUpdateRequest(BaseModel):
    """
    Request body for POST /api/v1/patient/update
    Used when new symptoms appear during a session.
    """
    patient_id: str = Field(
        ...,
        min_length=3,
        max_length=64,
        description="Unique identifier for the patient"
    )
    new_symptom: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="New symptom reported by the patient"
    )

    @field_validator("new_symptom")
    @classmethod
    def normalize_symptom(cls, v: str) -> str:
        return v.lower().strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "pat_abc123",
                "new_symptom": "breathing difficulty"
            }
        }
    }
