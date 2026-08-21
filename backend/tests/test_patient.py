"""
backend/tests/test_patient.py

Tests for Patient API endpoints.
"""

def test_analyze_patient_success(client, sample_patient_analyze_payload):
    response = client.post("/api/v1/patient/analyze", json=sample_patient_analyze_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "risk_score" in data
    assert 0 <= data["risk_score"] <= 100


def test_update_patient_success(client, sample_patient_update_payload):
    response = client.post("/api/v1/patient/update", json=sample_patient_update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_analyze_patient_missing_symptoms(client, invalid_patient_analyze_payload):
    response = client.post("/api/v1/patient/analyze", json=invalid_patient_analyze_payload)
    assert response.status_code == 422


def test_analyze_patient_empty_symptoms(client):
    payload = {"patient_id": "pat_test_empty", "symptoms": []}
    response = client.post("/api/v1/patient/analyze", json=payload)
    assert response.status_code == 422


def test_update_patient_missing_new_symptom(client):
    payload = {"patient_id": "pat_test_003"}
    response = client.post("/api/v1/patient/update", json=payload)
    assert response.status_code == 422


def test_analyze_patient_malformed_json(client):
    response = client.post(
        "/api/v1/patient/analyze",
        data="this is not json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code in [422, 400]
