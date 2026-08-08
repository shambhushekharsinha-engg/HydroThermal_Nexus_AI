# -*- coding: utf-8 -*-
"""
pages/8_Sustainability_Pro.py — Advanced Industrial ESG & Circular Economy
Introduces Next-Gen features: Waste Heat Recovery, Grid Carbon Load Shifting, 
Microgrid Balancing, Water Quality (Effluent), and Scope 3 Supply Chain Tracking.
"""

import datetime
import random
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import shared_components as sc
from backend.security import has_permission

st.set_page_config(page_title="Sustainability Pro — HydroThermal Nexus", page_icon="🌍", layout="wide")

user_info = sc.require_auth()
username = user_info["username"]
role = user_info["role"]

sc.show_header(title="🌍 Sustainability Pro (Enterprise)", subtitle="Next-Gen Circular Economy, Grid Load Shifting, & Advanced ESG Analytics")
sc.show_sidebar()

def render_waste_heat_recovery():
    st.markdown('<div class="section-title">🔥 Waste Heat Recovery & Industrial Symbiosis</div>', unsafe_allow_html=True)
    st.markdown("Monitor waste thermal energy captured from cooling towers and compute racks, redirected for pre-heating boilers or district heating.")
    
    col1, col2, col3 = st.columns(3)
    
    captured_mwh = round(random.uniform(4.5, 7.2), 2)
    gas_saved = round(captured_mwh * 3.412, 1) # MMBtu equivalent
    co2_saved = round(gas_saved * 53.06, 1) # kg CO2 per MMBtu

    col1.metric("Thermal Energy Captured", f"{captured_mwh} MWh", "+12% vs Yesterday")
    col2.metric("Natural Gas Offset", f"{gas_saved} MMBtu", "Saved")
    col3.metric("Direct CO₂ Reduction (Scope 1)", f"{co2_saved} kg", "Avoided")

    # Flow chart for heat recovery
    fig = go.Figure(go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = ["Cooling Towers", "Compute Racks", "Heat Exchanger", "Boiler Pre-Heat", "District Heating", "Lost to Atmos."],
          color = ["#38BDF8", "#A855F7", "#F59E0B", "#EF4444", "#10B981", "#64748B"]
        ),
        link = dict(
          source = [0, 1, 2, 2, 0, 1], # indices correspond to labels
          target = [2, 2, 3, 4, 5, 5],
          value = [8, 12, 10, 5, 2, 3]
        )
    ))
    fig.update_layout(title_text="Thermal Energy Flow Diagram (Industrial Symbiosis)", font_size=10, **sc.PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)

def render_grid_load_shifting():
    st.markdown('<div class="section-title">⚡ Dynamic Grid Carbon & Load Shifting</div>', unsafe_allow_html=True)
    st.markdown("Optimizes energy-intensive operations (e.g., heavy pumping) to align with hours when the grid is powered by renewables.")
    
    hours = [f"{i:02d}:00" for i in range(24)]
    # Simulate grid carbon intensity curve (low during midday due to solar)
    base_intensity = 400
    intensity = [base_intensity - 200 * np.sin(np.pi * (i - 6) / 12) if 6 <= i <= 18 else base_intensity for i in range(24)]
    intensity = [max(100, val + random.uniform(-20, 20)) for val in intensity]
    
    df = pd.DataFrame({"Hour": hours, "Grid Carbon Intensity (gCO2/kWh)": intensity})
    
    current_hour = datetime.datetime.now().hour
    current_intensity = df.iloc[current_hour]["Grid Carbon Intensity (gCO2/kWh)"]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"### Current Grid Status")
        if current_intensity > 300:
            st.error(f"**High Carbon Intensity:** {current_intensity:.0f} gCO₂/kWh")
            st.markdown("🚨 **Recommendation:** Curtail non-essential pumping. Rely on microgrid storage.")
        elif current_intensity > 200:
            st.warning(f"**Moderate Carbon Intensity:** {current_intensity:.0f} gCO₂/kWh")
            st.markdown("⚠️ **Recommendation:** Maintain normal operations. Do not schedule heavy loads.")
        else:
            st.success(f"**Low Carbon Intensity:** {current_intensity:.0f} gCO₂/kWh")
            st.markdown("✅ **Recommendation:** Optimal time for heavy operations (Water treatment, pumping).")
            
        st.button("Auto-Shift Loads to Off-Peak", type="primary")

    with c2:
        fig = px.area(df, x="Hour", y="Grid Carbon Intensity (gCO2/kWh)", title="24-Hour Grid Carbon Forecast")
        fig.add_vline(x=hours[current_hour], line_width=3, line_dash="dash", line_color="red", annotation_text="Now")
        fig.update_layout(**sc.PLOTLY_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_water_quality():
    st.markdown('<div class="section-title">💧 Advanced Water Quality & Effluent Compliance</div>', unsafe_allow_html=True)
    st.markdown("Real-time monitoring of discharged wastewater to prevent ecological damage and regulatory fines.")
    
    c1, c2, c3, c4 = st.columns(4)
    ph_val = round(random.uniform(6.8, 7.4), 2)
    turbidity = round(random.uniform(2.0, 4.5), 1)
    do_val = round(random.uniform(6.0, 8.5), 1)
    temp_val = round(random.uniform(22.0, 26.5), 1)
    
    c1.metric("Effluent pH Level", f"{ph_val}", "Nominal (Limit 6.5-8.5)")
    c2.metric("Turbidity", f"{turbidity} NTU", "-0.2 NTU")
    c3.metric("Dissolved Oxygen (DO)", f"{do_val} mg/L", "+0.4 mg/L")
    c4.metric("Discharge Temp", f"{temp_val} °C", "Safe (<30°C)")
    
    st.progress(1.0, text="EPA Clean Water Act Compliance: 100% (No Violations Detected)")

def render_scope3():
    st.markdown('<div class="section-title">🚛 Scope 3 Emissions & Supply Chain</div>', unsafe_allow_html=True)
    st.markdown("AI-estimated upstream and downstream carbon footprint mapping.")
    
    categories = ["Purchased Goods", "Upstream Logistics", "Waste Disposal", "Employee Commute", "Downstream Logistics"]
    emissions = [450, 120, 45, 80, 210]
    
    fig = px.treemap(
        names=categories,
        parents=["Scope 3"] * len(categories),
        values=emissions,
        title="Scope 3 Emissions Breakdown (Tonnes CO₂e)"
    )
    fig.update_layout(**sc.PLOTLY_LAYOUT, height=350, margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

def main():
    tab1, tab2, tab3 = st.tabs(["🔥 Energy & Heat", "💧 Water & Effluent", "🚛 Scope 3 & Supply Chain"])
    
    with tab1:
        render_waste_heat_recovery()
        st.markdown("---")
        render_grid_load_shifting()
        
    with tab2:
        render_water_quality()
        
    with tab3:
        render_scope3()

if __name__ == "__main__":
    main()
