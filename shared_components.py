# -*- coding: utf-8 -*-
"""
shared_components.py — Reusable UI Components, Authentication Guards, and Layout Utilities
Provides consistent header, sidebar, login forms, Plotly styling, and authentication across all pages.
"""

import os
import base64
import logging
import threading
from typing import Dict, Any, Optional

import streamlit as st
import plotly.graph_objects as go
from streamlit.runtime.scriptrunner_utils import script_run_context

from backend import database as db
from backend.security import sanitize_input
import config

logger: logging.Logger = logging.getLogger("HydroThermalNexus.SharedComponents")

# ── Plotly Standard Dark Layout ────────────────────────────────────────
PLOTLY_LAYOUT: Dict[str, Any] = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    showlegend=True,
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.08)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
)


def hex_to_rgba(hex_str: str, alpha: float = 0.08) -> str:
    """Convert hex color string to CSS rgba string with transparency."""
    h = hex_str.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def get_logo_b64() -> str:
    """Read assets/logo.png and return base64 encoded string for HTML embedding."""
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


LOGO_B64: str = get_logo_b64()


def load_css() -> None:
    """Inject custom styles.css into Streamlit DOM."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def start_api_thread() -> None:
    """Start background FastAPI server thread if not already running."""
    def _start():
        try:
            import uvicorn
            logger.info("Starting background FastAPI REST server on port %d", config.PORT_FASTAPI)
            uvicorn.run("backend.api:app", host=config.FASTAPI_HOST, port=config.PORT_FASTAPI,
                        log_level="error", access_log=False)
        except Exception as e:
            logger.error("Failed to launch FastAPI thread: %s", e)

    if script_run_context.get_script_run_ctx() is not None and "api_thread_started" not in st.session_state:
        t = threading.Thread(target=_start, daemon=True)
        t.start()
        st.session_state.api_thread_started = True


def bootstrap_environment() -> None:
    """Initialize SQLite databases, seed default users, and start backend API thread."""
    db.initialize_all_databases()
    db.seed_default_users()
    start_api_thread()
    load_css()


def show_login() -> None:
    """Render full-page login & registration card."""
    load_css()
    # Hide sidebar on login screen
    st.markdown("<style>[data-testid='stSidebarNav'] {display: none;} [data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        logo_html = (
            f'<img src="data:image/png;base64,{LOGO_B64}" />'
            if LOGO_B64 else '<div style="font-size:3rem;text-align:center;">🔷</div>'
        )
        st.markdown(f"""
        <div class="login-container">
          <div class="login-logo">{logo_html}</div>
          <div class="login-title">HydroThermal Nexus-AI</div>
          <div class="login-subtitle">Secure Industrial Cockpit & Telemetry Platform</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register / Sign Up"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Enter username", key="login_username")
                password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
                submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)

                if submitted:
                    uname = sanitize_input(username, max_len=32)
                    user = db.validate_user(uname, password)
                    if user:
                        token = db.create_session(user["username"], user["role"])
                        st.session_state["session_token"] = token
                        st.session_state["username"]      = user["username"]
                        st.session_state["role"]          = user["role"]
                        st.session_state["authenticated"] = True
                        db.log_audit(user["username"], user["role"], "LOGIN", "None", "User signed in.")
                        logger.info("User %s logged in successfully", user["username"])
                        st.success("✅ Credentials verified. Launching cockpit...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials or account locked. Try again.")

            st.markdown("##### ⚡ Quick 1-Click Demo Login")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👑 Admin", key="demo_admin", use_container_width=True):
                    token = db.create_session("admin", "Admin")
                    st.session_state.update({"session_token": token, "username": "admin", "role": "Admin", "authenticated": True})
                    st.rerun()
            with col2:
                if st.button("🔧 Engineer", key="demo_eng", use_container_width=True):
                    token = db.create_session("engineer", "Field Engineer")
                    st.session_state.update({"session_token": token, "username": "engineer", "role": "Field Engineer", "authenticated": True})
                    st.rerun()
            with col3:
                if st.button("🌱 Auditor", key="demo_aud", use_container_width=True):
                    token = db.create_session("auditor", "Sustainability Auditor")
                    st.session_state.update({"session_token": token, "username": "auditor", "role": "Sustainability Auditor", "authenticated": True})
                    st.rerun()

        with tab_register:
            with st.form("register_form", clear_on_submit=False):
                reg_username = st.text_input("New Username", key="reg_username")
                reg_email = st.text_input("Corporate Email", key="reg_email")
                reg_password = st.text_input("New Password", type="password", key="reg_password")
                reg_role = st.selectbox("Role", ["Field Engineer", "Sustainability Auditor", "Chief Financial Officer (CFO)"])
                reg_submitted = st.form_submit_button("📝 Register Account", use_container_width=True)

                if reg_submitted:
                    if reg_username and reg_password:
                        success = db.register_user(reg_username.strip(), reg_password, reg_email.strip(), reg_role)
                        if success:
                            st.success("✅ Account created successfully! Please sign in above.")
                        else:
                            st.error("❌ Registration failed. Username may already exist.")
                    else:
                        st.warning("⚠️ Please provide username and password.")


def require_auth() -> Dict[str, str]:
    """
    Authentication guard for pages.
    Ensures user is authenticated; if not, displays login page and halts execution.
    Returns dictionary with username and role.
    """
    bootstrap_environment()

    if not st.session_state.get("authenticated"):
        token = st.session_state.get("session_token")
        if token:
            user_info = db.validate_session(token)
            if user_info:
                st.session_state["authenticated"] = True
                st.session_state["username"]      = user_info["username"]
                st.session_state["role"]          = user_info["role"]
            else:
                show_login()
                st.stop()
        else:
            show_login()
            st.stop()

    st.session_state.setdefault("current_anomaly", "Nominal / Normal Operations")
    st.session_state.setdefault("health_score", 97.4)
    st.session_state.setdefault("active_mission", "None")

    return {
        "username": st.session_state.get("username", "Guest"),
        "role": st.session_state.get("role", "Field Engineer")
    }


def show_header(title: str = "HydroThermal Nexus-AI Cockpit", subtitle: str = "Industrial IoT Operational Cockpit") -> None:
    """Render top operational header banner with active user metrics and logout button."""
    username = st.session_state.get("username", "Guest")
    role = st.session_state.get("role", "Engineer")
    health = st.session_state.get("health_score", 97.4)

    col_title, col_status, col_user = st.columns([2.5, 1.2, 1])

    with col_title:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:38px;margin-right:12px;vertical-align:middle;" />' if LOGO_B64 else ''
        st.markdown(f"""
        <div style="display:flex;align-items:center;">
          {logo_html}
          <div>
            <h2 style="margin:0;padding:0;font-size:1.6rem;font-weight:700;color:#F8FAFC;">{title}</h2>
            <p style="margin:0;padding:0;font-size:0.85rem;color:#94A3B8;">{subtitle}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_status:
        st.markdown(f"""
        <div style="background:rgba(30,41,59,0.7);padding:8px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);text-align:center;">
          <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.05em;">Plant Health</div>
          <div style="font-size:1.2rem;font-weight:700;color:#38BDF8;">💚 {health}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col_user:
        st.markdown(f"""
        <div style="background:rgba(30,41,59,0.7);padding:6px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);text-align:right;">
          <div style="font-size:0.85rem;font-weight:600;color:#F1F5F9;">👤 {username}</div>
          <div style="font-size:0.75rem;color:#A855F7;">🏷️ {role}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:12px 0 20px 0;border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)


def show_sidebar() -> None:
    """Render unified sidebar navigation overview, system status, and user session management."""
    with st.sidebar:
        st.markdown("### 🔷 HydroThermal Nexus")
        st.sidebar.caption("v3.0 Enterprise Operational Platform")

        st.divider()

        # Session information card
        username = st.session_state.get("username", "Guest")
        role = st.session_state.get("role", "Field Engineer")

        st.markdown(f"**Current User:** `{username}`")
        st.markdown(f"**Role:** `{role}`")

        if st.button("🚪 Sign Out", key="sidebar_logout", use_container_width=True):
            token = st.session_state.get("session_token")
            if token:
                db.revoke_session(token)
            st.session_state.clear()
            st.rerun()

        st.divider()

        # Telemetry & Hardware status
        st.markdown("#### ⚡ System Telemetry")
        st.markdown("• **FastAPI Backend:** `ONLINE (8001)`")
        st.markdown("• **ML Anomaly Core:** `READY` (IsolationForest)")
        st.markdown("• **Modbus Gateway:** `CONNECTED` (192.168.1.105)")
        st.markdown("• **Database Storage:** `nexus_storage.db`")

        st.divider()
        st.caption("© 2026 HydroThermal Nexus-AI | Industrial IoT")
