import pytest
from fastapi.testclient import TestClient
from tachyon.api.server import app

def test_agent_health_endpoint():
    """INT-04: Verify the agent health endpoint."""
    client = TestClient(app)
    # Most agents should be found. Sentinel is a safe bet.
    response = client.get("/api/v1/agents/sentinel/health")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "sentinel"
    assert "status" in data
    assert "total_events" in data

def test_traffic_summary_endpoint():
    """INT-05: Verify the traffic summary endpoint."""
    client = TestClient(app)
    response = client.get("/api/v1/traffic/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "transit" in data
    assert "internal" in data
