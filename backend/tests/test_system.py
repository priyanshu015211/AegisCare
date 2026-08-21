"""
backend/tests/test_system.py

Tests for system status endpoints.
"""

def test_system_status_endpoint(client):
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert "timestamp" in data
