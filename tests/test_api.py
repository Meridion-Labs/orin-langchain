"""Basic API tests for ORIN system."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ORIN AI Agent System"
    assert "features" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_chat_without_auth():
    """Test chat endpoint without authentication."""
    response = client.post("/api/v1/chat", json={"message": "Hello"})
    assert response.status_code == 403  # Forbidden - correct for missing auth


def test_login_endpoint_exists():
    """Test login endpoint exists."""
    response = client.post("/auth/login", data={"username": "test", "password": "test"})
    # The endpoint should exist and return a response
    assert response.status_code in [200, 401, 422]  # Accept success, unauthorized, or validation error