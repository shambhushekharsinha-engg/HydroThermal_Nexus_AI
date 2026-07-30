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


def test_modbus_status_endpoint():
    response = client.get("/api/modbus/status", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert "telemetry" in data


def test_tenant_facilities_endpoint():
    response = client.get("/api/tenants/facilities", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "facilities" in data
    assert len(data["facilities"]) >= 3


def test_tenant_aggregate_endpoint():
    response = client.get("/api/tenants/aggregate", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "total_facilities" in data
    assert data["total_facilities"] >= 3
    assert "annual_co2_reduction_target_tons" in data


def test_quick_login_endpoint():
    payload = {"role": "Admin"}
    response = client.post("/api/auth/quick-login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"
    assert data["username"] == "admin"
    assert "session_token" in data


def test_currency_rates_endpoint():
    response = client.get("/api/currency/rates", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["base_currency"] == "USD"
    assert "currencies" in data
    assert "INR" in data["currencies"]
    assert "EUR" in data["currencies"]
    assert "GBP" in data["currencies"]
    assert "JPY" in data["currencies"]


def test_currency_convert_endpoint():
    payload = {"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"}
    response = client.post("/api/currency/convert", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.0
    assert data["from_currency"] == "USD"
    assert data["to_currency"] == "EUR"
    assert data["converted_amount"] == 92.0
    assert "€" in data["formatted"]


def test_currency_calculate_savings_endpoint():
    payload = {
        "water_litres": 2000.0,
        "energy_kwh": 1000.0,
        "co2_kg": 500.0,
        "water_cost_per_l": 0.05,
        "energy_cost_per_kwh": 8.0,
        "carbon_price_per_tonne_usd": 15.0,
        "input_currency": "INR",
        "target_currency": "USD"
    }
    response = client.post("/api/currency/calculate-savings", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["target_currency"] == "USD"
    assert data["total_savings"] > 0
    assert "total_savings_formatted" in data



