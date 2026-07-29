"""
backend/multi_tenant_manager.py
Multi-Tenant Facility Cockpit Manager for HydroThermal Nexus-AI Enterprise SaaS.
Tracks and isolates multi-facility thermal plants (Data Center Liquid Cooling, Refineries, Power Plants).
"""

from typing import List, Dict, Any


class MultiTenantFacilityManager:
    """Manages multi-facility tenant isolation, plant status, and aggregate carbon yield."""

    def __init__(self):
        self.facilities = [
            {
                "facility_id": "FAC-IND-01",
                "name": "Noida Data Center Cooling Grid",
                "region": "India-North",
                "plant_type": "Data Center Liquid Cooling",
                "status": "OPERATIONAL",
                "health_score": 96.4,
                "daily_water_saved_l": 14500.0,
                "daily_co2_saved_kg": 420.5
            },
            {
                "facility_id": "FAC-IND-02",
                "name": "Gujarat Hydro-Chemical Refinery",
                "region": "India-West",
                "plant_type": "Chemical Refinery Thermal Tower",
                "status": "OPERATIONAL",
                "health_score": 92.1,
                "daily_water_saved_l": 28900.0,
                "daily_co2_saved_kg": 850.0
            },
            {
                "facility_id": "FAC-IND-03",
                "name": "Bengaluru Thermal Power Auxiliary",
                "region": "India-South",
                "plant_type": "Power Plant Condenser Grid",
                "status": "WARNING",
                "health_score": 81.5,
                "daily_water_saved_l": 9800.0,
                "daily_co2_saved_kg": 310.2
            }
        ]

    def list_facilities(self) -> List[Dict[str, Any]]:

        """Returns list of registered tenant facilities."""
        return self.facilities

    def get_enterprise_aggregate(self) -> Dict[str, Any]:
        """Calculates cross-facility aggregate sustainability impact."""
        total_water = sum(f["daily_water_saved_l"] for f in self.facilities)
        total_co2 = sum(f["daily_co2_saved_kg"] for f in self.facilities)
        avg_health = round(sum(f["health_score"] for f in self.facilities) / len(self.facilities), 1)

        return {
            "total_facilities": len(self.facilities),
            "average_health_score": avg_health,
            "aggregate_daily_water_saved_l": total_water,
            "aggregate_daily_co2_saved_kg": total_co2,
            "annual_co2_reduction_target_tons": round((total_co2 * 365) / 1000.0, 1)
        }
