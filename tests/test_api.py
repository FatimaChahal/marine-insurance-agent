import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    response = client.get("/")
    data = response.json()
    assert response.status_code == 200
    assert "Marine Insurance Agent" in data["service"]
    assert "Azure AI Foundry" in data["stack"]

def test_agents_endpoint():
    response = client.get("/agents")
    data = response.json()
    assert response.status_code == 200
    assert "agents" in data
    assert len(data["agents"]) > 0

def test_analyze_requires_auth():
    response = client.post("/analyze", json={})
    assert response.status_code == 401

def test_analyze_invalid_key():
    response = client.post("/analyze",
        json={"email_content": "test"},
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401