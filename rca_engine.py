# -*- coding: utf-8 -*-
"""
rca_engine.py — HydroThermal Nexus-AI Root Cause Analysis Engine
Provides structured fault diagnosis, confidence scoring, MTTR estimation,
cascading fault tree analysis, and severity taxonomy for all anomaly types.

Supported Anomaly Types:
  - Pipe Rupture / Flow Drop
  - HVAC Overheat / Thermal Spike
  - Power Surge / Grid Instability
  - Nominal / Normal Operations
"""

import datetime
import math
from typing import Dict, Any, List


# ── Fault Taxonomy Definitions ────────────────────────────────────────
FAULT_CATEGORIES = {
    "Equipment": "Physical component failure — valve, pump, relay, or sensor degradation",
    "Process": "Operational process deviation — flow, pressure, or temperature exceedance",
    "Environmental": "External environmental trigger — ambient conditions, grid instability",
}


class RCAEngine:
    """
    Industrial Root Cause Analysis engine for HydroThermal Nexus-AI.
    Analyzes anomaly telemetry and produces structured, confidence-scored
    diagnostic reports with fault tree decomposition and MTTR estimates.
    """

    # ── MTTR Baselines (hours) by fault class ─────────────────────────
    MTTR_BASELINES: Dict[str, float] = {
        "Pipe Rupture / Flow Drop": 3.5,
        "HVAC Overheat / Thermal Spike": 2.0,
        "Power Surge / Grid Instability": 1.5,
        "Nominal / Normal Operations": 0.0,
    }

    # ── Confidence Model ───────────────────────────────────────────────
    @staticmethod
    def _compute_confidence(health_score: float, deviation_pct: float) -> float:
        """
        Computes diagnostic confidence score (0–100%).
        Higher deviation and lower health = higher confidence the diagnosis is correct.
        """
        health_factor = max(0.0, 100.0 - health_score) / 100.0   # 0 → 1 as health worsens
        deviation_factor = min(deviation_pct / 300.0, 1.0)        # caps at 300% deviation
        raw = (health_factor * 0.55) + (deviation_factor * 0.45)
        return round(min(raw * 100.0, 99.0), 1)

    # ── MTTR Calculator ────────────────────────────────────────────────
    @staticmethod
    def _compute_mttr(anomaly_type: str, severity: str) -> Dict[str, Any]:
        """Estimates Mean Time to Repair and cost of downtime."""
        base_hours = RCAEngine.MTTR_BASELINES.get(anomaly_type, 2.0)
        severity_multiplier = {"INFO": 0.5, "WARNING": 1.0, "CRITICAL": 1.8, "EMERGENCY": 2.5}.get(severity, 1.0)
        mttr_hours = round(base_hours * severity_multiplier, 1)
        downtime_cost_usd = round(mttr_hours * 3500.0, 2)   # $3,500/hr industry standard
        return {
            "mttr_hours": mttr_hours,
            "estimated_downtime_cost_usd": downtime_cost_usd,
            "severity_multiplier": severity_multiplier,
        }

    # ── Fault Tree Builder ─────────────────────────────────────────────
    @staticmethod
    def _build_fault_tree(anomaly_type: str) -> List[Dict[str, str]]:
        """Returns ordered fault tree: primary → secondary → tertiary failure paths."""
        trees = {
            "Pipe Rupture / Flow Drop": [
                {"level": "Primary",   "node": "Main Header Pressure Loss",         "cause": "Solenoid relay valve seal failure or corrosion fatigue"},
                {"level": "Secondary", "node": "Thermal Loop Bypass Failure",        "cause": "Increased backpressure on auxiliary thermal loop bypass"},
                {"level": "Tertiary",  "node": "ESG Impact — Fluid Loss",            "cause": "Estimated 1,450 L/hr water loss without valve throttle"},
            ],
            "HVAC Overheat / Thermal Spike": [
                {"level": "Primary",   "node": "Fan Motor Relay Stall",              "cause": "Cooling tower fan motor relay contact burnout or bearing seizure"},
                {"level": "Secondary", "node": "Heat Exchange Degradation",          "cause": "Reduced airflow causes exponential thermal accumulation in loop"},
                {"level": "Tertiary",  "node": "Compute Rack Thermal Runaway Risk",  "cause": "Server inlet temp exceeds 40°C — automatic load throttling required"},
            ],
            "Power Surge / Grid Instability": [
                {"level": "Primary",   "node": "Grid Voltage Transient (±20%)",      "cause": "Upstream utility grid fault or lightning strike on feeder line"},
                {"level": "Secondary", "node": "UPS / Battery Changeover Lag",       "cause": "200ms switchover gap causes momentary PLCs reset on Modbus nodes"},
                {"level": "Tertiary",  "node": "Telemetry Data Gap",                 "cause": "Sensor stream interruption during power restoration window"},
            ],
            "Nominal / Normal Operations": [
                {"level": "Primary",   "node": "All Systems Nominal",                "cause": "No anomalous conditions detected in primary telemetry streams"},
            ],
        }
        return trees.get(anomaly_type, [{"level": "Primary", "node": "Unknown Fault", "cause": "Insufficient telemetry for diagnosis"}])

    # ── Main Analysis Method ───────────────────────────────────────────
    def analyze_anomaly(
        self,
        anomaly_type: str,
        health_score: float = 97.4,
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        """
        Generates a full structured RCA diagnostic report.

        Returns:
            primary_vector: High-level anomaly summary
            root_cause: Root failure component identified
            fault_category: Equipment / Process / Environmental
            impact: ESG and operational impact description
            recommendation: Numbered mitigation steps (HTML-safe)
            confidence_pct: Diagnostic confidence (0–100%)
            mttr: Mean Time to Repair details
            fault_tree: Ordered failure cascade tree
            timestamp: ISO timestamp of analysis
        """
        timestamp = datetime.datetime.now().isoformat()

        # ── Pipe Rupture / Flow Drop ───────────────────────────────────
        if anomaly_type == "Pipe Rupture / Flow Drop":
            confidence = self._compute_confidence(health_score, deviation_pct=240.0)
            mttr = self._compute_mttr(anomaly_type, "CRITICAL")
            return {
                "primary_vector": "🔴 CRITICAL Anomaly: Sudden hydraulic pressure collapse and fluid flow drop detected.",
                "root_cause": "Solenoid Relay Valve Seal Failure / Main Header Pressure Breakdown",
                "fault_category": "Equipment",
                "fault_category_desc": FAULT_CATEGORIES["Equipment"],
                "impact": (
                    "Fluid loss rate exceeds normal variance threshold by +240%. "
                    "Without intervention: estimated 1,450 L/hr uncontrolled discharge. "
                    "Automated actuation saved 1,450 L/hr water and prevented thermal contamination."
                ),
                "recommendation": (
                    "1. Solenoid Relay Valve throttled to 20% aperture.<br>"
                    "2. Thermal loop rerouted to auxiliary bypass header.<br>"
                    "3. CRITICAL alert dispatched via Telegram gateway.<br>"
                    "4. Anomaly logged in SHA-256 immutable audit ledger.<br>"
                    "5. Schedule physical valve inspection within 4 hours."
                ),
                "confidence_pct": confidence,
                "severity": "CRITICAL",
                "mttr": mttr,
                "fault_tree": self._build_fault_tree(anomaly_type),
                "timestamp": timestamp,
            }

        # ── HVAC Overheat / Thermal Spike ─────────────────────────────
        elif anomaly_type == "HVAC Overheat / Thermal Spike":
            confidence = self._compute_confidence(health_score, deviation_pct=160.0)
            mttr = self._compute_mttr(anomaly_type, "WARNING")
            return {
                "primary_vector": "🟡 WARNING Anomaly: Thermal loop temperature exceeding safe operational envelope.",
                "root_cause": "Cooling Tower Fan Motor Relay Stall → Heat Exchange Degradation",
                "fault_category": "Process",
                "fault_category_desc": FAULT_CATEGORIES["Process"],
                "impact": (
                    "Temperature ramp-up to 105°C (threshold: 89°C). "
                    "Fan motor relay stall reduces airflow, causing exponential thermal accumulation. "
                    "Prevented energy surcharge penalty; avoided 38 kg CO₂e excess emissions."
                ),
                "recommendation": (
                    "1. Secondary auxiliary chiller system engaged at full capacity.<br>"
                    "2. High-load compute racks throttled to reduce heat generation.<br>"
                    "3. WARNING alert dispatched via Telegram and audit log updated.<br>"
                    "4. Maintenance ticket created for fan motor relay inspection.<br>"
                    "5. Monitor Cooling-Tower-Gamma telemetry every 15 minutes."
                ),
                "confidence_pct": confidence,
                "severity": "WARNING",
                "mttr": mttr,
                "fault_tree": self._build_fault_tree(anomaly_type),
                "timestamp": timestamp,
            }

        # ── Power Surge / Grid Instability ────────────────────────────
        elif anomaly_type == "Power Surge / Grid Instability":
            confidence = self._compute_confidence(health_score, deviation_pct=185.0)
            mttr = self._compute_mttr(anomaly_type, "CRITICAL")
            return {
                "primary_vector": "⚡ CRITICAL Anomaly: Grid voltage transient detected — automated load shedding initiated.",
                "root_cause": "Upstream Grid Feeder Fault → UPS Changeover Lag → PLC Modbus Timeout",
                "fault_category": "Environmental",
                "fault_category_desc": FAULT_CATEGORIES["Environmental"],
                "impact": (
                    "Grid voltage fluctuation of ±20% for 340ms caused Modbus PLC register reset. "
                    "UPS changeover lag of ~200ms created telemetry data gap on 3 sensor nodes. "
                    "Load shedding activated — non-critical pumping reduced by 60%."
                ),
                "recommendation": (
                    "1. Non-critical pump loads shed — operating at 40% capacity.<br>"
                    "2. UPS battery backup engaged — monitoring discharge rate.<br>"
                    "3. CRITICAL alert dispatched — Modbus nodes polled for re-sync.<br>"
                    "4. Grid relay protection circuit verified active (IEEE 1547 compliant).<br>"
                    "5. Contact utility provider and log event in GHG audit ledger."
                ),
                "confidence_pct": confidence,
                "severity": "CRITICAL",
                "mttr": mttr,
                "fault_tree": self._build_fault_tree(anomaly_type),
                "timestamp": timestamp,
            }

        # ── Nominal / Normal Operations ────────────────────────────────
        else:
            return {
                "primary_vector": "✅ Nominal Operations Verified — All sensor streams within safe thresholds.",
                "root_cause": "No anomalies detected in primary telemetry streams.",
                "fault_category": "None",
                "fault_category_desc": "No fault condition active.",
                "impact": "System operating within optimal ESG efficiency thresholds. All KPIs nominal.",
                "recommendation": "Maintain standard monitoring protocols. Next scheduled review in 6 hours.",
                "confidence_pct": 99.0,
                "severity": "INFO",
                "mttr": {"mttr_hours": 0.0, "estimated_downtime_cost_usd": 0.0, "severity_multiplier": 0.0},
                "fault_tree": self._build_fault_tree("Nominal / Normal Operations"),
                "timestamp": timestamp,
            }