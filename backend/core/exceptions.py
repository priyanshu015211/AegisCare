"""
backend/core/exceptions.py

Custom exceptions for AegisCare backend.
These provide semantic meaning and can be caught by the global exception handler.
"""

from fastapi import HTTPException, status


class AegisCareException(Exception):
    """Base exception for all AegisCare-specific errors."""
    def __init__(self, message: str, error_code: str = "AEGIS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PatientNotFoundException(AegisCareException):
    """Raised when a patient cannot be found."""
    def __init__(self, patient_id: str):
        super().__init__(f"Patient with id '{patient_id}' not found", "PATIENT_NOT_FOUND")


class InvalidSymptomException(AegisCareException):
    """Raised for invalid or empty symptom input."""
    def __init__(self, detail: str = "Invalid symptom provided"):
        super().__init__(detail, "INVALID_SYMPTOM")


class ServiceUnavailableException(AegisCareException):
    """Raised when a downstream service (LLM, DB, etc.) is unavailable."""
    def __init__(self, service_name: str):
        super().__init__(f"{service_name} service is currently unavailable", "SERVICE_UNAVAILABLE")
