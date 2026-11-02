"""Unit tests for the Telemetry Ingestion API."""


from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check() -> None:
    """Test that the API is running and healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ingest_telemetry_success() -> None:
    """Test successful ingestion and hydrology calculation."""
    payload = {
        "timestamp": "2026-10-24T12:00:00Z",
        "farm_id": "test_farm_001",
        "node_id": "node_A",
        "moisture_pct": 28.0,
        "nitrogen_mg_kg": 45.0,
        "phosphorus_mg_kg": 22.0,
        "potassium_mg_kg": 35.0,
        "ph": 7.2,
        "temp_c": 25.0,
    }

    response = client.post("/api/v1/telemetry/ingest", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["farm_id"] == "test_farm_001"
    assert "hydrology" in data
    assert "action_window" in data
    assert "et0_fao_mm_day" in data["hydrology"]
    assert data["hydrology"]["et0_fao_mm_day"] >= 0.0  # ET0 cannot be negative

def test_mock_endpoint() -> None:
    """Test the convenience mock generation endpoint."""
    response = client.post("/api/v1/telemetry/mock")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "action_window" in data
    assert "can_spray_today" in data["action_window"]
    assert "irrigation_due_hours" in data["action_window"]
