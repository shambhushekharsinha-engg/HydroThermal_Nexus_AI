import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import app


class DummyContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def markdown(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def success(self, *args, **kwargs):
        return None

    def metric(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None


class DummyStreamlit:
    def __init__(self):
        self.session_state = {
            "role": "Viewer",
            "username": "tester",
            "current_anomaly": "HVAC Overheat / Thermal Spike",
        }

    def set_page_config(self, *args, **kwargs):
        return None

    def columns(self, spec):
        if isinstance(spec, int):
            return [DummyContainer() for _ in range(spec)]
        return [DummyContainer() for _ in spec]

    def markdown(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def success(self, *args, **kwargs):
        return None

    def metric(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def expander(self, *args, **kwargs):
        return DummyContainer()

    def button(self, *args, **kwargs):
        return False

    def download_button(self, *args, **kwargs):
        return None

    def radio(self, *args, **kwargs):
        return "Multi-Sensor"

    def toggle(self, *args, **kwargs):
        return False

    def selectbox(self, *args, **kwargs):
        return "Nominal / Normal Operations"

    def text_input(self, *args, **kwargs):
        return ""


def test_tab_rca_runs_for_hvac_anomaly(monkeypatch):
    monkeypatch.setattr(app, "st", DummyStreamlit())
    monkeypatch.setattr(app, "has_permission", lambda role, action: False)
    monkeypatch.setattr(
        app.PredictiveMaintenanceEngine,
        "calculate_rul",
        lambda **kwargs: {
            "health_index": 62.5,
            "rul_hours": 1200,
        },
    )
    monkeypatch.setattr(
        app.PredictiveMaintenanceEngine,
        "estimate_downtime_financial_risk",
        lambda rul_hours: {
            "failure_probability_30d": 40.0,
            "risk_weighted_exposure_usd": 4200.0,
        },
    )

    app.tab_rca()
