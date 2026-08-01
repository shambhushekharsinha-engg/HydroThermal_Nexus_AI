# -*- coding: utf-8 -*-
"""
tests/test_auth.py
Automated unit test suite for HydroThermal Nexus-AI Security, RBAC & Authentication Engine.
"""

import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend import database as db
from backend.security import (
    sanitize_input, validate_username, validate_password_strength,
    has_permission, get_role_badge, get_severity_badge
)


@pytest.fixture(autouse=True)
def setup_auth_db():
    db.initialize_all_databases()
    db.seed_default_users()


def test_password_hashing_and_user_validation():
    raw_password = "Admin@Nexus2026!"
    hashed = db._hash_password(raw_password)

    assert isinstance(hashed, str)
    assert len(hashed) == 64

    user = db.validate_user("admin", raw_password)
    assert user is not None
    assert user["username"] == "admin"
    assert user["role"] == "Admin"

    invalid_user = db.validate_user("admin", "WrongPassword!")
    assert invalid_user is None


def test_input_sanitization():
    dirty_input = "<script>alert('xss')</script>AdminName"
    clean_input = sanitize_input(dirty_input)
    assert "<script>" not in clean_input
    assert "alert" in clean_input


def test_username_validation():
    is_valid, msg = validate_username("admin_user1")
    assert is_valid is True

    is_valid, msg = validate_username("ab")
    assert is_valid is False
    assert "3–32 characters" in msg

    is_valid, msg = validate_username("admin<script>")
    assert is_valid is False


def test_password_strength_validation():
    is_valid, msg = validate_password_strength("Weak1!")
    assert is_valid is False
    assert "at least 8 characters" in msg

    is_valid, msg = validate_password_strength("StrongPassword123!")
    assert is_valid is True


def test_rbac_permissions():
    assert has_permission("Admin", "clear_audit") is True
    assert has_permission("Viewer", "clear_audit") is False
    assert has_permission("Operator", "trigger_anomaly") is True
    assert has_permission("Viewer", "trigger_anomaly") is False


def test_session_creation_and_validation():
    token = db.create_session("admin", "Admin")
    assert isinstance(token, str)
    assert len(token) == 36  # UUID v4 string length

    session_info = db.validate_session(token)
    assert session_info is not None
    assert session_info["username"] == "admin"
    assert session_info["role"] == "Admin"

    db.revoke_session(token)
    assert db.validate_session(token) is None


def test_badges_generation():
    badge_admin = get_role_badge("Admin")
    assert "ADMIN" in badge_admin

    badge_sev = get_severity_badge("CRITICAL")
    assert "CRITICAL" in badge_sev
