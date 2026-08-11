"""Tests for health and root endpoints."""
from fastapi.testclient import TestClient


def test_root_endpoint_returns_html_ui(client: TestClient):
    """Test GET / returns the Web UI dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Beverage Vision Platform" in response.text


def test_health_check_endpoint(client: TestClient):
    """Test GET /health returns healthy status with connected database."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert "app_name" in data
    assert "version" in data
    assert "timestamp" in data
