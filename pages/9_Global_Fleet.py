# -*- coding: utf-8 -*-
"""
pages/9_Global_Fleet.py — Global Multi-Site Fleet Command Map
Interactive map allowing users to select different global facilities and instantly view localized telemetry.
"""

import random
import streamlit as st
import pandas as pd
import plotly.express as px

import shared_components as sc

st.set_page_config(page_title="Global Fleet — HydroThermal Nexus", page_icon="🗺️", layout="wide")

user_info = sc.require_auth()

sc.show_header(title="🗺️ Global Fleet Command", subtitle="Multi-Site Interactive Telemetry Map")
sc.show_sidebar()

# Define global facility locations
facilities = pd.DataFrame([
    {"Region": "Texas HQ (USA)", "lat": 29.7604, "lon": -95.3698, "Status": "Nominal", "Health": 98.4},
    {"Region": "Berlin Plant (EU)", "lat": 52.5200, "lon": 13.4050, "Status": "Warning", "Health": 76.2},
    {"Region": "Tokyo Hub (APAC)", "lat": 35.6762, "lon": 139.6503, "Status": "Critical", "Health": 42.1},
    {"Region": "Mumbai Facility (IN)", "lat": 19.0760, "lon": 72.8777, "Status": "Nominal", "Health": 95.8},
])

st.markdown('<div class="section-title">🌍 Select a Facility to View Local Data</div>', unsafe_allow_html=True)

# Generate the interactive Mapbox scatter plot
fig = px.scatter_mapbox(
    facilities,
    lat="lat",
    lon="lon",
    hover_name="Region",
    hover_data={"lat": False, "lon": False, "Status": True, "Health": True},
    color="Status",
    color_discrete_map={"Nominal": "#00FF88", "Warning": "#FFB800", "Critical": "#FF2D55"},
    size_max=15,
    zoom=1.2,
    height=400
)

fig.update_traces(marker=dict(size=14))
fig.update_layout(
    mapbox_style="carto-darkmatter",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# Render map and capture selection event
selection = st.plotly_chart(fig, on_select="rerun", key="global_map", use_container_width=True)

# Determine the selected region
selected_index = None
if selection and "selection" in selection and "points" in selection["selection"]:
    points = selection["selection"]["points"]
    if len(points) > 0:
        selected_index = points[0]["pointIndex"]

# Default to Texas if no selection is made
if selected_index is None:
    selected_index = 0
    st.info("💡 **Tip:** Click on any marker on the map to instantly switch regions. Currently showing default: **Texas HQ**.")

selected_facility = facilities.iloc[selected_index]
region_name = selected_facility["Region"]
region_status = selected_facility["Status"]

st.markdown("---")
st.markdown(f'<div class="section-title">📍 Localized Telemetry: {region_name}</div>', unsafe_allow_html=True)

# Dynamic data based on region
if region_status == "Nominal":
    pressure = round(random.uniform(40.0, 45.0), 1)
    temp = round(random.uniform(60.0, 75.0), 1)
    alert = "✅ No active anomalies detected."
elif region_status == "Warning":
    pressure = round(random.uniform(35.0, 40.0), 1)
    temp = round(random.uniform(85.0, 95.0), 1)
    alert = "⚠️ Thermal spike detected in cooling tower array."
else:
    pressure = round(random.uniform(10.0, 15.0), 1)
    temp = round(random.uniform(95.0, 110.0), 1)
    alert = "🚨 CRITICAL: Main header pressure loss. Evacuation protocols active."

c1, c2, c3 = st.columns(3)
c1.metric("Site Health Score", f"{selected_facility['Health']}%")
c2.metric("Local Pressure", f"{pressure} PSI")
c3.metric("Core Temperature", f"{temp} °C")

st.markdown("#### 🔔 Regional Alert Status")
if region_status == "Nominal":
    st.success(alert)
elif region_status == "Warning":
    st.warning(alert)
else:
    st.error(alert)

st.markdown("#### 💧 Local Water & ESG Metrics")
w1, w2 = st.columns(2)
w1.metric("Effluent Discharge pH", round(random.uniform(6.8, 7.5), 1))
w2.metric("Renewable Energy Output", f"{round(random.uniform(40, 85))}%")
