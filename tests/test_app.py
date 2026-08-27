# -*- coding: utf-8 -*-
"""
tests/test_app.py
Automated unit test suite for HydroThermal Nexus-AI Main App Entrypoint & Shared Components.
"""

import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import app
import shared_components as sc


class DummyStreamlit:
    def __init__(self):
        self.session_state = {
            "authenticated": True,
            "role": "Admin",
            "username": "admin",
            "session_token": "test_token_123",
            "current_anomaly": "Nominal / Normal Operations",
            "health_score": 97.4,
            "active_facility": "texas_hq",  # pre-set so facility picker is bypassed
        }
        self.sidebar = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def set_page_config(self, *args, **kwargs):
        return None

    def columns(self, spec):
        if isinstance(spec, int):
            return [DummyStreamlit() for _ in range(spec)]
        return [DummyStreamlit() for _ in spec]

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

    def button(self, *args, **kwargs):
        return False

    def divider(self, *args, **kwargs):
        return None

    def text_input(self, *args, **kwargs):
        return ""

    def selectbox(self, *args, **kwargs):
        options = args[1] if len(args) > 1 else kwargs.get("options", [])
        return options[kwargs.get("index", 0)] if options else None

    def toggle(self, *args, **kwargs):
        return False

    def stop(self):
        return None

    def rerun(self):
        return None

    def tabs(self, labels):
        return [DummyStreamlit() for _ in labels]

    def form(self, *args, **kwargs):
        return self

    def form_submit_button(self, *args, **kwargs):
        return False

    def plotly_chart(self, *args, **kwargs):
        return None

    def get(self, key, default=None):
        return self.session_state.get(key, default)


def test_app_main_executes_without_error(monkeypatch):
    monkeypatch.setattr(app, "st", DummyStreamlit())
    monkeypatch.setattr(sc, "st", DummyStreamlit())
    app.main()
