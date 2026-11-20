# -*- coding: utf-8 -*-
"""
pages/4_DigitalTwin.py — Geo-Spatial 3D Digital Twin & Actuator Controls
Renders interactive PyDeck 3D spatial map, facility telemetry nodes, and edge hardware actuator controls.
"""

import logging
from typing import Dict, Any, List

import streamlit as st
import pandas as pd
import pydeck as pdk

import shared_components as sc
from backend.security import has_permission
from actuators import AutomatedMitigationManager

logger: logging.Logger = logging.getLogger("HydroThermalNexus.PageDigitalTwin")

st.set_page_config(page_title="Digital Twin — HydroThermal Nexus", page_icon="🌐", layout="wide")

user_info: Dict[str, str] = sc.require_auth()
username: str = user_info["username"]
role: str = user_info["role"]

fac = sc.get_active_facility()
sc.show_header(
    title=f"🌐 3D Digital Twin — {fac['flag']} {fac['name']}",
    subtitle=f"Spatial Topology & Edge Actuator Controls · {fac['city']}, {fac['country']}"
)
sc.show_sidebar()


def render_3d_spatial_twin() -> None:
    """Render 3D PyDeck spatial map and telemetry nodes calibrated to the active facility."""
    fac = sc.get_active_facility()
    c_lat, c_lon = fac["lat"], fac["lon"]

    st.markdown(f'<div class="section-title">🌐 3D Facility Spatial Topology — {fac["flag"]} {fac["name"]}</div>', unsafe_allow_html=True)
    st.caption(f"3D Column Height = Node Temperature (°C). Color Code = Operational Health Status. Site: {fac['city']}, {fac['country']} ({c_lat:.4f}°N, {c_lon:.4f}°E).")

    anomaly = st.session_state.get("current_anomaly", "Nominal / Normal Operations")

    base_t = fac["temp"]
    nodes: List[Dict[str, Any]] = [
        {"node_id": f"{fac['name']}-Node-Alpha",   "lat": c_lat + 0.0008, "lon": c_lon - 0.0008, "status": "Normal",   "flow_rate": 120, "temp": base_t * 0.65},
        {"node_id": f"{fac['name']}-Node-Beta",    "lat": c_lat + 0.0012, "lon": c_lon + 0.0010, "status": "Warning" if fac["status"] == "Warning" else "Normal",  "flow_rate": 85,  "temp": base_t},
        {"node_id": f"{fac['name']}-Tower-Gamma",  "lat": c_lat - 0.0010, "lon": c_lon - 0.0012, "status": "Critical" if fac["status"] == "Critical" else "Normal", "flow_rate": 30 if fac["status"] == "Critical" else 95,  "temp": base_t * 1.3 if fac["status"] == "Critical" else base_t * 0.85},
        {"node_id": f"{fac['name']}-Relay-Delta",  "lat": c_lat - 0.0005, "lon": c_lon + 0.0008, "status": "Normal",   "flow_rate": 100, "temp": base_t * 0.55},
    ]

    if anomaly == "Pipe Rupture / Flow Drop":
        nodes[0]["status"] = "Critical"
        nodes[0]["flow_rate"] = 10
    elif anomaly == "HVAC Overheat / Thermal Spike":
        nodes[1]["status"] = "Critical"
        nodes[1]["temp"] = 105.0
    elif anomaly == "Power Surge / Grid Instability":
        nodes[3]["status"] = "Critical"
        nodes[3]["temp"] = 58.0
        nodes[3]["flow_rate"] = 0
        nodes[1]["status"] = "Warning"
        nodes[1]["temp"] = 72.0

    df_nodes = pd.DataFrame(nodes)
    color_map = {
        "Normal": [0, 255, 136, 200],
        "Warning": [255, 184, 0, 210],
        "Critical": [255, 45, 85, 230],
    }
    df_nodes["color"] = df_nodes["status"].map(color_map)

    layer = pdk.Layer(
        "ColumnLayer",
        data=df_nodes,
        get_position=["lon", "lat"],
        get_elevation="temp",
        elevation_scale=22,
        radius=40,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    view = pdk.ViewState(latitude=c_lat, longitude=c_lon, zoom=15, pitch=55)
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style="light",
        tooltip={"text": "📍 {node_id}\nStatus: {status}\n🌡️ {temp:.1f}°C\n💧 {flow_rate} L/m"}
    ))

    st.markdown('<div class="section-title" style="margin-top:1rem;">📋 Node Telemetry Status Cards</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, node in zip([c1, c2, c3, c4], nodes):
        s = node["status"]
        c = {"Normal": "#00FF88", "Warning": "#FFB800", "Critical": "#FF2D55"}.get(s, "#aaa")
        with col:
            st.markdown(f"""
            <div class="kpi-card {'green' if s=='Normal' else 'yellow' if s=='Warning' else 'red'}">
              <div class="kpi-label">{node['node_id']}</div>
              <div class="kpi-value" style="font-size:1.4rem;color:{c};">{s}</div>
              <div style="margin-top:0.4rem;font-size:0.8rem;color:#64748B;">
                🌡️ {node['temp']}°C &nbsp;·&nbsp; 💧 {node['flow_rate']} L/m
              </div>
            </div>""", unsafe_allow_html=True)


def render_actuator_controls() -> None:
    """Render edge hardware actuator override panel."""
    st.markdown("---")
    st.markdown('<div class="section-title">🔧 Edge Actuator & Solenoid Control Panel</div>', unsafe_allow_html=True)

    mitigation_mgr = AutomatedMitigationManager()

    if has_permission(role, "actuate_hardware"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 💧 Solenoid Valve Aperture Override")
            aperture = st.slider("Valve Aperture (%)", 0, 100, 100, 5, key="actuator_solenoid_slider")
            if st.button("Apply Solenoid Aperture", key="btn_apply_solenoid", use_container_width=True):
                st.success(f"✅ Solenoid Valve updated to {aperture}% aperture.")
                logger.info("Solenoid valve manually set to %d%% by %s", aperture, username)

        with col2:
            st.markdown("##### 🌡️ HVAC Relay Mode")
            hvac_mode = st.selectbox("HVAC Circuit Relay Mode", [
                "OPTIMIZED AUTO-MODULATION",
                "SAFETY LOAD SHEDDING ACTIVE",
                "EMERGENCY MAXIMUM COOLING"
            ], key="actuator_hvac_select")
            if st.button("Update Relay Mode", key="btn_apply_hvac", use_container_width=True):
                st.success(f"✅ HVAC Relay state updated to: {hvac_mode}")
                logger.info("HVAC Relay updated to %s by %s", hvac_mode, username)
    else:
        st.info("🔒 Field Engineer or Admin role required for hardware actuation overrides.")


def main() -> None:
    render_3d_spatial_twin()
    render_actuator_controls()


if __name__ == "__main__":
    main()
