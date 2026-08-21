"""
backend/schemas/responses.py

Standardized response models for the Patient API.
Ensures consistent JSON structure across all endpoints.
"""

from typing import Any, Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    """
    Timezone-aware UTC datetime.
    Replaces the deprecated datetime.utcnow() (removed in Python 3.12+).
    Use this as the default_factory for all timestamp fields.
    """
    return datetime.now(timezone.utc)


class APIResponse(BaseModel):
    """
    Standardized success response format for all AegisCare APIs.
    All successful responses should follow this structure.
    """
    status: Literal["success"] = "success"
    message: str = "Request completed successfully."
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=_utcnow)


class PatientAnalysisResponse(BaseModel):
    status: Literal["success"] = "success"
    patient_id: str
    session_id: Optional[str] = None
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    message: str
    timestamp: datetime = Field(default_factory=_utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "patient_id": "pat_abc123",
                "severity": "medium",
                "risk_score": 61,
                "confidence": 0.82,
                "message": "Initial assessment completed.",
                "timestamp": "2026-05-15T02:16:00Z"
            }
        }
    }


class PatientUpdateResponse(BaseModel):
    """Response for POST /api/v1/patient/update"""
    status: Literal["success"] = "success"
    patient_id: str
    new_symptom: Optional[str] = None
    updated_risk_score: int = Field(ge=0, le=100)
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    timestamp: datetime = Field(default_factory=_utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "patient_id": "pat_abc123",
                "updated_risk_score": 78,
                "severity": "high",
                "message": "Patient condition updated.",
                "timestamp": "2026-05-15T02:17:00Z"
            }
        }
    }
