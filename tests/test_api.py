"""
tests/test_api.py
Automated unit test suite for HydroThermal Nexus-AI FastAPI REST endpoints.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.api import app, API_SECRET
from backend import database as db

client = TestClient(app)
AUTH_HEADERS = {"x-api-key": API_SECRET}


@pytest.fixture(autouse=True)
def setup_db():
    db.initialize_all_databases()


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data


def test_unauthorized_access():
    response = client.get("/api/telemetry/live")
    assert response.status_code == 403


def test_live_telemetry_endpoint():
    response = client.get("/api/telemetry/live", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data


def test_telemetry_push():
    payload = {
        "electricity_kwh": 2100.5,
        "water_litres": 3050.0,
        "outdoor_temp_c": 32.1,
        "humidity_pct": 60.5,
        "pressure_psi": 43.2,
        "thermal_temp_c": 67.8
    }
    response = client.post("/api/telemetry/push", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "saved"


def test_ml_metrics_endpoint():
    response = client.get("/api/ml/metrics", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "model_type" in data
    assert data["model_type"] == "IsolationForest"


def test_historical_telemetry_endpoint():
    response = client.get("/api/telemetry/historical?limit=10", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 10


def test_system_score_endpoint():
    response = client.get("/api/system/score", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "health_score" in data
    assert 0 <= data["health_score"] <= 100
