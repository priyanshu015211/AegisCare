"""
backend/schemas/__init__.py

Pydantic schemas for API request/response validation.
Separated from domain models for clean architecture.
"""

from .patient import PatientAnalyzeRequest, PatientUpdateRequest
from .responses import PatientAnalysisResponse, PatientUpdateResponse, APIResponse

__all__ = [
    "PatientAnalyzeRequest",
    "PatientUpdateRequest",
    "PatientAnalysisResponse",
    "PatientUpdateResponse",
    "APIResponse",
]
