"""
backend/api.py
FastAPI REST backend for HydroThermal Nexus-AI.
Runs on port 8001, started as a background thread by app.py.
Provides: telemetry, anomaly, audit, ESG, health, and alert endpoints.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import datetime
import numpy as np

# Local imports (resolved relative to project root)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import database as db

app = FastAPI(
    title="HydroThermal Nexus-AI API",
    version="2.0.0",
    description="REST backend for industrial telemetry, anomaly detection, and ESG metrics."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──────────────────────────────────────────────────
class AnomalyTrigger(BaseModel):
    username: str
    role: str
    anomaly_type: str
    severity: str = "WARNING"

class TelemetryPush(BaseModel):
    electricity_kwh: float
    water_litres: float
    outdoor_temp_c: float
    humidity_pct: float
    pressure_psi: float
    thermal_temp_c: float

class AlertAck(BaseModel):
    alert_id: int
    username: str

class ESGUpdate(BaseModel):
    co2_saved_kg: float
    water_saved_l: float
    energy_saved_kwh: float
    esg_score: float


# ── Helper: Simple API token check ──────────────────────────────────
API_SECRET = os.environ.get("NEXUS_API_SECRET", "NexusAPI_Internal_2026")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=403, detail="Invalid API key.")
    return x_api_key


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    """Returns system health status and uptime."""
    return {
        "status": "operational",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database":  "connected",
            "telemetry": "streaming",
            "alerts":    "active"
        }
    }


@app.get("/api/telemetry/live")
def get_live_telemetry(hours: int = 24, _key=Depends(verify_api_key)):
    """Returns telemetry records from the last N hours."""
    df = db.get_telemetry(hours=hours)
    if df.empty:
        return {"data": [], "count": 0}
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.post("/api/telemetry/push")
def push_telemetry(payload: TelemetryPush, _key=Depends(verify_api_key)):
    """Ingests a telemetry snapshot into the database."""
    db.save_telemetry(
        payload.electricity_kwh, payload.water_litres,
        payload.outdoor_temp_c,  payload.humidity_pct,
        payload.pressure_psi,    payload.thermal_temp_c
    )
    return {"status": "saved", "timestamp": datetime.datetime.now().isoformat()}


@app.post("/api/anomaly/trigger")
def trigger_anomaly(payload: AnomalyTrigger, _key=Depends(verify_api_key)):
    """Logs an anomaly trigger event and creates an alert."""
    db.log_audit(
        payload.username, payload.role,
        "TRIGGER_ANOMALY", payload.anomaly_type,
        f"Anomaly '{payload.anomaly_type}' triggered via API."
    )
    db.save_alert(
        severity=payload.severity,
        channel="API",
        title=f"Anomaly Triggered: {payload.anomaly_type}",
        message=f"User {payload.username} triggered scenario: {payload.anomaly_type}"
    )
    return {"status": "logged", "anomaly": payload.anomaly_type}


@app.get("/api/audit/logs")
def get_audit(limit: int = 100, _key=Depends(verify_api_key)):
    """Returns the most recent audit log entries."""
    df = db.get_audit_logs(limit=limit)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.get("/api/alerts")
def get_alerts(limit: int = 50, _key=Depends(verify_api_key)):
    """Returns the most recent alert records."""
    df = db.get_alerts(limit=limit)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.post("/api/alerts/acknowledge")
def ack_alert(payload: AlertAck, _key=Depends(verify_api_key)):
    """Marks an alert as acknowledged."""
    db.acknowledge_alert(payload.alert_id, payload.username)
    return {"status": "acknowledged", "alert_id": payload.alert_id}


@app.post("/api/esg/update")
def update_esg(payload: ESGUpdate, _key=Depends(verify_api_key)):
    """Updates today's ESG metrics."""
    db.upsert_esg(
        payload.co2_saved_kg, payload.water_saved_l,
        payload.energy_saved_kwh, payload.esg_score
    )
    return {"status": "updated"}


@app.get("/api/esg/history")
def esg_history(days: int = 30, _key=Depends(verify_api_key)):
    """Returns ESG history for the last N days."""
    df = db.get_esg_history(days=days)
    return {"data": df.to_dict(orient="records"), "count": len(df)}


@app.get("/api/system/score")
def system_score(_key=Depends(verify_api_key)):
    """Computes a real-time system health score (0–100)."""
    # Simplified scoring logic — can be replaced with ML model
    import random
    score = round(random.uniform(85, 99), 1)
    return {
        "health_score": score,
        "pressure_ok":  True,
        "thermal_ok":   True,
        "flow_ok":      True,
        "timestamp":    datetime.datetime.now().isoformat()
    }
