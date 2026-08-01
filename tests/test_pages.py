# -*- coding: utf-8 -*-
"""
tests/test_pages.py
Automated module import and structural verification for Streamlit multi-page architecture.
"""

import sys
import os
import importlib
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def test_shared_components_import():
    import shared_components as sc
    assert hasattr(sc, "require_auth")
    assert hasattr(sc, "show_header")
    assert hasattr(sc, "show_sidebar")
    assert hasattr(sc, "load_css")
    assert hasattr(sc, "PLOTLY_LAYOUT")


def test_app_main_import():
    import app
    assert hasattr(app, "main")


def test_pages_modules_importable():
    pages_dir = os.path.join(PROJECT_ROOT, "pages")
    page_files = [
        "1_Dashboard.py",
        "2_Analytics.py",
        "3_Alerts.py",
        "4_DigitalTwin.py",
        "5_Reports.py",
        "6_Settings.py",
        "7_AI_Assistant.py",
    ]

    for pf in page_files:
        full_path = os.path.join(pages_dir, pf)
        assert os.path.exists(full_path), f"Page file {pf} missing from pages/ directory!"

        # Verify python file syntax via compile
        with open(full_path, "r", encoding="utf-8") as f:
            code = f.read()
            compiled = compile(code, full_path, "exec")
            assert compiled is not None, f"Failed to compile {pf}"
