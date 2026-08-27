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


# ── Global Facility Registry ──────────────────────────────────────────
GLOBAL_FACILITIES: Dict[str, Any] = {
    "texas_hq": {
        "name": "Texas HQ", "country": "USA", "city": "Houston", "flag": "🇺🇸",
        "region": "North America", "lat": 29.7604, "lon": -95.3698,
        "status": "Nominal", "health": 98.4,
        "temp": 68.2, "pressure": 42.5, "energy_kw": 128, "flow": 95.2,
        "currency": "USD", "currency_symbol": "$",
        "grid_carbon": 0.42, "timezone": "CST (UTC-6)",
        "description": "Primary hydrothermal operations hub with 4 active nodes.",
    },
    "london_hub": {
        "name": "London Hub", "country": "UK", "city": "London", "flag": "🇬🇧",
        "region": "Europe", "lat": 51.5074, "lon": -0.1278,
        "status": "Nominal", "health": 94.7,
        "temp": 62.1, "pressure": 40.8, "energy_kw": 98, "flow": 88.4,
        "currency": "GBP", "currency_symbol": "£",
        "grid_carbon": 0.23, "timezone": "GMT (UTC+0)",
        "description": "European ops center with renewable energy integration.",
    },
    "berlin_plant": {
        "name": "Berlin Plant", "country": "Germany", "city": "Berlin", "flag": "🇩🇪",
        "region": "Europe", "lat": 52.5200, "lon": 13.4050,
        "status": "Warning", "health": 76.2,
        "temp": 88.5, "pressure": 36.2, "energy_kw": 145, "flow": 72.1,
        "currency": "EUR", "currency_symbol": "€",
        "grid_carbon": 0.35, "timezone": "CET (UTC+1)",
        "description": "Central European plant with thermal spike warning active.",
    },
    "paris_station": {
        "name": "Paris Station", "country": "France", "city": "Paris", "flag": "🇫🇷",
        "region": "Europe", "lat": 48.8566, "lon": 2.3522,
        "status": "Nominal", "health": 91.3,
        "temp": 65.8, "pressure": 41.5, "energy_kw": 112, "flow": 91.0,
        "currency": "EUR", "currency_symbol": "€",
        "grid_carbon": 0.058, "timezone": "CET (UTC+1)",
        "description": "Low-carbon European hub powered primarily by nuclear energy.",
    },
    "moscow_plant": {
        "name": "Moscow Plant", "country": "Russia", "city": "Moscow", "flag": "🇷🇺",
        "region": "Europe", "lat": 55.7558, "lon": 37.6173,
        "status": "Nominal", "health": 87.4,
        "temp": 72.8, "pressure": 39.6, "energy_kw": 182, "flow": 84.1,
        "currency": "RUB", "currency_symbol": "₽",
        "grid_carbon": 0.33, "timezone": "MSK (UTC+3)",
        "description": "East European hub managing Volga Basin thermal grid.",
    },
    "dubai_outpost": {
        "name": "Dubai Outpost", "country": "UAE", "city": "Dubai", "flag": "🇦🇪",
        "region": "Middle East", "lat": 25.2048, "lon": 55.2708,
        "status": "Nominal", "health": 97.3,
        "temp": 69.9, "pressure": 43.5, "energy_kw": 175, "flow": 93.4,
        "currency": "AED", "currency_symbol": "AED",
        "grid_carbon": 0.45, "timezone": "GST (UTC+4)",
        "description": "MENA operations hub with solar-assisted cooling systems.",
    },
    "cairo_facility": {
        "name": "Cairo Facility", "country": "Egypt", "city": "Cairo", "flag": "🇪🇬",
        "region": "Africa", "lat": 30.0444, "lon": 31.2357,
        "status": "Warning", "health": 78.6,
        "temp": 91.5, "pressure": 35.8, "energy_kw": 162, "flow": 68.4,
        "currency": "EGP", "currency_symbol": "E£",
        "grid_carbon": 0.38, "timezone": "EET (UTC+2)",
        "description": "Nile Basin water hub with cooling capacity warning active.",
    },
    "johannesburg_plant": {
        "name": "Johannesburg Plant", "country": "South Africa", "city": "Johannesburg", "flag": "🇿🇦",
        "region": "Africa", "lat": -26.2041, "lon": 28.0473,
        "status": "Nominal", "health": 90.1,
        "temp": 67.3, "pressure": 40.8, "energy_kw": 143, "flow": 87.3,
        "currency": "ZAR", "currency_symbol": "R",
        "grid_carbon": 0.90, "timezone": "SAST (UTC+2)",
        "description": "Sub-Saharan Africa's primary hydrothermal monitoring station.",
    },
    "mumbai_facility": {
        "name": "Mumbai Facility", "country": "India", "city": "Mumbai", "flag": "🇮🇳",
        "region": "South Asia", "lat": 19.0760, "lon": 72.8777,
        "status": "Nominal", "health": 95.8,
        "temp": 71.3, "pressure": 41.0, "energy_kw": 118, "flow": 89.5,
        "currency": "INR", "currency_symbol": "₹",
        "grid_carbon": 0.71, "timezone": "IST (UTC+5:30)",
        "description": "India's largest hydrothermal monitoring facility.",
    },
    "delhi_hub": {
        "name": "Delhi Hub", "country": "India", "city": "New Delhi", "flag": "🇮🇳",
        "region": "South Asia", "lat": 28.6139, "lon": 77.2090,
        "status": "Warning", "health": 81.2,
        "temp": 82.4, "pressure": 38.5, "energy_kw": 155, "flow": 75.3,
        "currency": "INR", "currency_symbol": "₹",
        "grid_carbon": 0.71, "timezone": "IST (UTC+5:30)",
        "description": "Northern India hub monitoring upstream thermal pipeline networks.",
    },
    "beijing_plant": {
        "name": "Beijing Plant", "country": "China", "city": "Beijing", "flag": "🇨🇳",
        "region": "Asia-Pacific", "lat": 39.9042, "lon": 116.4074,
        "status": "Nominal", "health": 88.3,
        "temp": 75.2, "pressure": 40.1, "energy_kw": 198, "flow": 85.2,
        "currency": "CNY", "currency_symbol": "¥",
        "grid_carbon": 0.61, "timezone": "CST (UTC+8)",
        "description": "Large-scale facility managing northern China thermal corridor.",
    },
    "tokyo_hub": {
        "name": "Tokyo Hub", "country": "Japan", "city": "Tokyo", "flag": "🇯🇵",
        "region": "Asia-Pacific", "lat": 35.6762, "lon": 139.6503,
        "status": "Critical", "health": 42.1,
        "temp": 101.2, "pressure": 12.4, "energy_kw": 215, "flow": 38.5,
        "currency": "JPY", "currency_symbol": "¥",
        "grid_carbon": 0.51, "timezone": "JST (UTC+9)",
        "description": "CRITICAL: Main header pressure loss. RCA workflow active.",
    },
    "seoul_plant": {
        "name": "Seoul Plant", "country": "South Korea", "city": "Seoul", "flag": "🇰🇷",
        "region": "Asia-Pacific", "lat": 37.5665, "lon": 126.9780,
        "status": "Nominal", "health": 95.6,
        "temp": 66.4, "pressure": 43.1, "energy_kw": 134, "flow": 92.8,
        "currency": "KRW", "currency_symbol": "₩",
        "grid_carbon": 0.46, "timezone": "KST (UTC+9)",
        "description": "High-efficiency plant with advanced smart-grid integration.",
    },
    "singapore_hub": {
        "name": "Singapore Hub", "country": "Singapore", "city": "Singapore", "flag": "🇸🇬",
        "region": "Asia-Pacific", "lat": 1.3521, "lon": 103.8198,
        "status": "Nominal", "health": 97.9,
        "temp": 63.5, "pressure": 44.2, "energy_kw": 102, "flow": 96.8,
        "currency": "SGD", "currency_symbol": "S$",
        "grid_carbon": 0.41, "timezone": "SGT (UTC+8)",
        "description": "APAC regional command node with fastest anomaly response times.",
    },
    "sydney_station": {
        "name": "Sydney Station", "country": "Australia", "city": "Sydney", "flag": "🇦🇺",
        "region": "Oceania", "lat": -33.8688, "lon": 151.2093,
        "status": "Nominal", "health": 99.1,
        "temp": 61.8, "pressure": 44.8, "energy_kw": 89, "flow": 98.2,
        "currency": "AUD", "currency_symbol": "A$",
        "grid_carbon": 0.45, "timezone": "AEST (UTC+10)",
        "description": "Best performing facility. Zero anomalies in 30 days.",
    },
    "sao_paulo_plant": {
        "name": "São Paulo Plant", "country": "Brazil", "city": "São Paulo", "flag": "🇧🇷",
        "region": "South America", "lat": -23.5505, "lon": -46.6333,
        "status": "Warning", "health": 82.5,
        "temp": 84.1, "pressure": 37.5, "energy_kw": 138, "flow": 79.8,
        "currency": "BRL", "currency_symbol": "R$",
        "grid_carbon": 0.09, "timezone": "BRT (UTC-3)",
        "description": "LATAM hub with thermal spike in secondary cooling loop.",
    },
    "toronto_hub": {
        "name": "Toronto Hub", "country": "Canada", "city": "Toronto", "flag": "🇨🇦",
        "region": "North America", "lat": 43.6510, "lon": -79.3470,
        "status": "Nominal", "health": 96.0,
        "temp": 63.7, "pressure": 42.8, "energy_kw": 108, "flow": 94.5,
        "currency": "CAD", "currency_symbol": "C$",
        "grid_carbon": 0.13, "timezone": "EST (UTC-5)",
        "description": "North American backup command with 99.9% uptime record.",
    },
}


def get_active_facility() -> Dict[str, Any]:
    """Get the currently active facility profile from session state."""
    key = st.session_state.get("active_facility", "texas_hq")
    return GLOBAL_FACILITIES.get(key, GLOBAL_FACILITIES["texas_hq"])


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


def _show_facility_picker() -> None:
    """Show a full-page facility selection screen after login."""
    load_css()
    st.markdown("""
    <style>
    .fac-card {
        background: rgba(17, 34, 64, 0.8);
        border: 1px solid rgba(100, 255, 218, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 12px;
    }
    .fac-card:hover { border-color: rgba(100,255,218,0.6); }
    .fac-title { font-size: 1.05rem; font-weight: 700; color: #F8FAFC; }
    .fac-sub { font-size: 0.78rem; color: #94A3B8; margin-top: 2px; }
    .fac-badge-nominal { background: rgba(0,255,136,0.15); color:#00FF88; border-radius:6px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
    .fac-badge-warning { background: rgba(255,184,0,0.15); color:#FFB800; border-radius:6px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
    .fac-badge-critical { background: rgba(255,45,85,0.15); color:#FF2D55; border-radius:6px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;color:#64FFDA;margin-bottom:4px;'>🌍 Select Your Facility</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#94A3B8;margin-bottom:30px;'>Choose a facility to begin monitoring. You can switch at any time from the sidebar.</p>", unsafe_allow_html=True)

    # Search box
    search = st.text_input("🔍 Search by city, country or region", placeholder="e.g. Tokyo, India, Europe...", key="fac_picker_search")

    # Filter facilities
    filtered = {
        k: v for k, v in GLOBAL_FACILITIES.items()
        if not search or any(
            search.lower() in v[f].lower()
            for f in ["name", "city", "country", "region"]
        )
    }

    # Group by region
    regions: Dict[str, list] = {}
    for k, v in filtered.items():
        regions.setdefault(v["region"], []).append((k, v))

    for region, items in sorted(regions.items()):
        st.markdown(f"<h4 style='color:#64FFDA;margin-top:24px;margin-bottom:12px;'>📌 {region}</h4>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, (key, fac) in enumerate(items):
            with cols[idx % 3]:
                status = fac["status"]
                badge_cls = "nominal" if status == "Nominal" else ("warning" if status == "Warning" else "critical")
                st.markdown(f"""
                <div class="fac-card">
                  <div class="fac-title">{fac['flag']} {fac['name']}</div>
                  <div class="fac-sub">{fac['city']}, {fac['country']} · {fac['timezone']}</div>
                  <div style="margin-top:8px;">
                    <span class="fac-badge-{badge_cls}">{status}</span>
                    <span style="color:#64748B;font-size:0.78rem;margin-left:8px;">Health: {fac['health']}%</span>
                  </div>
                  <div style="color:#94A3B8;font-size:0.76rem;margin-top:6px;">{fac['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🚀 Launch {fac['name']}", key=f"pick_{key}", use_container_width=True):
                    st.session_state["active_facility"] = key
                    st.session_state["health_score"] = fac["health"]
                    st.rerun()


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

    # If facility not yet selected, show a facility selection screen
    if "active_facility" not in st.session_state:
        _show_facility_picker()
        st.stop()

    return {
        "username": st.session_state.get("username", "Guest"),
        "role": st.session_state.get("role", "Field Engineer")
    }



def show_header(title: str = "HydroThermal Nexus-AI Cockpit", subtitle: str = "Industrial IoT Operational Cockpit") -> None:
    """Render top operational header banner with active user metrics and logout button."""
    username = st.session_state.get("username", "Guest")
    role = st.session_state.get("role", "Engineer")
    health = st.session_state.get("health_score", 97.4)
    fac = get_active_facility()

    col_title, col_loc, col_status, col_user = st.columns([2, 1.5, 1.2, 0.9])

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

    with col_loc:
        st.markdown(f"""
        <div style="background:rgba(30,41,59,0.7);padding:8px 14px;border-radius:8px;border:1px solid rgba(100,255,218,0.2);text-align:center;">
          <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.05em;">Active Facility</div>
          <div style="font-size:1rem;font-weight:700;color:#64FFDA;">{fac['flag']} {fac['name']}</div>
          <div style="font-size:0.72rem;color:#64748B;">{fac['city']}, {fac['country']}</div>
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

        # ── Facility Switcher ─────────────────────────────────────────
        st.markdown("#### 🌍 Active Facility")
        fac = get_active_facility()
        active_key = st.session_state.get("active_facility", "texas_hq")
        st.markdown(f"**{fac['flag']} {fac['name']}**  \n`{fac['city']}, {fac['country']}`")

        options = list(GLOBAL_FACILITIES.keys())
        labels = [f"{v['flag']} {v['name']}" for v in GLOBAL_FACILITIES.values()]
        current_idx = options.index(active_key) if active_key in options else 0

        selected_label = st.selectbox(
            "Switch Facility:",
            labels,
            index=current_idx,
            key="sidebar_fac_switch",
            label_visibility="collapsed"
        )
        if selected_label != labels[current_idx]:
            new_key = options[labels.index(selected_label)]
            new_fac = GLOBAL_FACILITIES[new_key]
            st.session_state["active_facility"] = new_key
            st.session_state["health_score"] = new_fac["health"]
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
