"""
predictive_maintenance.py
Predictive Maintenance & Remaining Useful Life (RUL) Forecasting Core.
Calculates component degradation curves, RUL estimation (operating hours),
and financial downtime risk per hour of unscheduled failure.
"""

import math
from typing import Dict, Any, List


class PredictiveMaintenanceEngine:
    """
    Core engine for industrial hydrothermal component degradation forecasting.
    Computes Remaining Useful Life (RUL) and financial failure probability.
    """

    DEFAULT_BASELINE_THRESHOLDS = {
        "vibration_max": 4.5,       # mm/s velocity ISO 10816 Class II threshold
        "bearing_temp_max": 85.0,   # °C thermal alarm threshold
        "pressure_psi_nominal": 45.0
    }

    @classmethod
    def calculate_rul(
        cls,
        vibration_mm_s: float,
        bearing_temp_c: float,
        pressure_psi: float,
        operating_hours_logged: float = 12000.0,
        design_lifespan_hours: float = 40000.0
    ) -> Dict[str, Any]:
        """
        Calculates Remaining Useful Life (RUL) in hours, degradation percentage,
        health index (0-100), and recommended maintenance urgency.
        """
        # Baseline degradation metrics
        vib_ratio = min(max(vibration_mm_s / cls.DEFAULT_BASELINE_THRESHOLDS["vibration_max"], 0.0), 3.0)
        temp_ratio = min(max(bearing_temp_c / cls.DEFAULT_BASELINE_THRESHOLDS["bearing_temp_max"], 0.0), 2.0)
        pressure_dev = abs(pressure_psi - cls.DEFAULT_BASELINE_THRESHOLDS["pressure_psi_nominal"]) / cls.DEFAULT_BASELINE_THRESHOLDS["pressure_psi_nominal"]

        # Combined multi-dimensional degradation factor
        deg_factor = (vib_ratio * 0.5) + (temp_ratio * 0.35) + (pressure_dev * 0.15)
        health_index = max(100.0 - (deg_factor * 35.0), 0.0)

        # Non-linear accelerated wear exponential model
        accelerated_wear_multiplier = math.exp(max(deg_factor - 1.0, 0.0) * 1.2)
        effective_hours_used = operating_hours_logged * accelerated_wear_multiplier

        remaining_hours = max(design_lifespan_hours - effective_hours_used, 0.0)
        rul_percentage = min(max((remaining_hours / design_lifespan_hours) * 100.0, 0.0), 100.0)

        if health_index > 80:
            status = "HEALTHY"
            urgency = "LOW - Routine Inspection"
            action_code = "ACT_MONITOR"
        elif health_index > 50:
            status = "DEGRADING"
            urgency = "MEDIUM - Schedule Preventative Servicing within 14 Days"
            action_code = "ACT_SCHEDULE_MAINT"
        else:
            status = "CRITICAL"
            urgency = "HIGH - Immediate Actuation & Overhaul Required"
            action_code = "ACT_EMERGENCY_SERVICING"

        return {
            "health_index": round(health_index, 1),
            "status": status,
            "urgency": urgency,
            "action_code": action_code,
            "rul_hours": round(remaining_hours, 0),
            "rul_percentage": round(rul_percentage, 1),
            "degradation_factor": round(deg_factor, 3),
            "accelerated_wear_multiplier": round(accelerated_wear_multiplier, 2)
        }

    @classmethod
    def estimate_downtime_financial_risk(
        cls,
        rul_hours: float,
        hourly_downtime_cost_usd: float = 3500.0,
        unplanned_outage_avg_hours: float = 6.0
    ) -> Dict[str, Any]:
        """
        Estimates the monetary risk of unscheduled failure vs proactive servicing cost.
        """
        if rul_hours < 500:
            failure_prob_30d = 0.85
        elif rul_hours < 2000:
            failure_prob_30d = 0.40
        else:
            failure_prob_30d = 0.08

        raw_unplanned_cost = hourly_downtime_cost_usd * unplanned_outage_avg_hours
        risk_weighted_cost = raw_unplanned_cost * failure_prob_30d
        planned_servicing_cost = raw_unplanned_cost * 0.18   # Preventative maintenance costs ~18% of catastrophic outage

        net_savings_by_preventative = max(risk_weighted_cost - planned_servicing_cost, 0.0)

        return {
            "failure_probability_30d": round(failure_prob_30d * 100.0, 1),
            "unplanned_outage_cost_usd": round(raw_unplanned_cost, 2),
            "risk_weighted_exposure_usd": round(risk_weighted_cost, 2),
            "planned_servicing_cost_usd": round(planned_servicing_cost, 2),
            "net_savings_preventative_usd": round(net_savings_by_preventative, 2)
        }
