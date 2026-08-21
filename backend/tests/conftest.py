"""
backend/tests/conftest.py

Pytest configuration and shared fixtures for AegisCare backend tests.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_patient_analyze_payload():
    return {
        "patient_id": "pat_test_001",
        "symptoms": ["fever", "cough"],
        "duration": "2 days",
        "language": "en"
    }


@pytest.fixture
def sample_patient_update_payload():
    return {
        "patient_id": "pat_test_001",
        "new_symptom": "breathing difficulty"
    }


@pytest.fixture
def invalid_patient_analyze_payload():
    return {
        "patient_id": "pat_test_002",
        "duration": "1 day"
    }
