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
        fig.add_vline(x=hours[current_hour], line_width=3, line_dash="dash", line_color="red")
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
    fig.update_layout(**sc.PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)

def render_algae_bioreactor():
    st.markdown('<div class="section-title">🦠 AI-Optimized Microalgae Bioreactor</div>', unsafe_allow_html=True)
    st.markdown("Ultimate Circular Economy: Waste Heat + Waste CO₂ + Wastewater = **Clean Biofuel & Oxygen**.")
    
    c1, c2, c3, c4 = st.columns(4)
    co2_absorbed = round(random.uniform(120.5, 145.2), 1)
    heat_used = round(random.uniform(45.0, 60.5), 1)
    biofuel_yield = round(co2_absorbed * 0.35, 1)
    oxygen_out = round(co2_absorbed * 0.73, 1)
    
    c1.metric("CO₂ Sequestered", f"{co2_absorbed} kg", "Direct Air Capture")
    c2.metric("Waste Heat Utilized", f"{heat_used} kWh", "Symbiosis")
    c3.metric("Biofuel Harvest", f"{biofuel_yield} L", "+2.4 L/hr")
    c4.metric("Oxygen Released", f"{oxygen_out} kg", "Air Purification")

    st.markdown("#### 🧪 Bioreactor Health & Growth Rate")
    time_series = pd.DataFrame({
        "Time": [f"{i}:00" for i in range(1, 13)],
        "Algae Biomass (kg/m3)": np.linspace(1.2, 3.8, 12) + np.random.uniform(-0.1, 0.1, 12),
        "Photosynthesis Efficiency (%)": np.linspace(85, 96, 12) + np.random.uniform(-2, 2, 12)
    })
    
    fig = px.line(time_series, x="Time", y=["Algae Biomass (kg/m3)", "Photosynthesis Efficiency (%)"], title="Live Bioreactor Output")
    fig.update_layout(**sc.PLOTLY_LAYOUT, height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_digital_passport():
    st.markdown('<div class="section-title">🛡️ Cryptographic Digital Product Passports (DPP)</div>', unsafe_allow_html=True)
    st.markdown("Generates verifiable EU-compliant ESG passports for every production batch.")
    
    batch_id = f"BATCH-{random.randint(10000, 99999)}"
    st.markdown(f"**Current Production Run:** `{batch_id}`")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=hydrothermal-nexus-dpp-{batch_id}", width=180)
        st.caption("Scan to verify cryptographic ESG claims.")
    with c2:
        st.success("✅ **Batch verified as 100% Carbon Neutral.**")
        st.info("🔹 Renewable Energy Used: **84%**\n🔹 Recycled Water Used: **92%**\n🔹 Scope 1+2 Carbon Footprint: **0.12 kg CO₂e / unit**")
        st.button("Issue Blockchain Certificate for Batch", type="primary")

def render_biodiversity():
    st.markdown('<div class="section-title">🦅 Biodiversity & Ecosystem Drone Mapping</div>', unsafe_allow_html=True)
    st.markdown("AI simulated drone and satellite analysis of local flora and fauna health near the industrial plant.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Local Aquatic Health Score", "98.4%", "+1.2% (Nominal)")
    c2.metric("Canopy Density Index", "87.1%", "Stable")
    c3.metric("Thermal Plume Impact Risk", "LOW", "Optimal")
    
    st.markdown("#### 🛰️ Simulated Drone Heatmap (Effluent Impact Zone)")
    # Generate a dummy heatmap simulating thermal impact on a river
    z = np.random.normal(25, 2, size=(20, 20))
    # Add a "hotspot" at the discharge pipe (top left)
    for i in range(5):
        for j in range(5):
            z[i][j] += 8 - (i+j)
    
    fig = go.Figure(data=go.Contour(
        z=z, colorscale="Viridis", contours=dict(showlabels=True, labelfont=dict(size=12, color="white"))
    ))
    fig.update_layout(title="River Surface Temperature near Discharge Pipe (°C)", **sc.PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)

def render_carbon_credits():
    st.markdown('<div class="section-title">🪙 Tokenized Carbon Credits (GreenFi)</div>', unsafe_allow_html=True)
    st.markdown("Monetize your emissions reductions by minting verified Carbon Credits and trading them on a decentralized Green Finance (GreenFi) marketplace.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Verified Emissions Reduction", "420.5 tCO₂e", "YTD")
    c2.metric("Minted Carbon Tokens", "420 $C-TKN", "Ready to Trade")
    c3.metric("Estimated Market Value", "$12,194.50", "@ $29/tCO₂e")
    
    st.markdown("#### 📈 Live Carbon Offset Marketplace")
    
    # Generate dummy market data
    dates = pd.date_range(end=datetime.datetime.now(), periods=30, freq='D')
    prices = np.linspace(22, 29, 30) + np.random.uniform(-1.5, 1.5, 30)
    df_market = pd.DataFrame({"Date": dates, "Price per tCO₂e ($)": prices})
    
    fig = px.area(df_market, x="Date", y="Price per tCO₂e ($)", title="Carbon Credit Market Price (30-Day Trend)")
    fig.update_layout(**sc.PLOTLY_LAYOUT, height=280)
    st.plotly_chart(fig, use_container_width=True)
    
    st.button("Mint & Sell 100 $C-TKN on Marketplace", type="primary")

def main():
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔥 Energy & Heat", 
        "💧 Water & Effluent", 
        "🚛 Scope 3",
        "🦠 Algae Bioreactor",
        "🛡️ Digital Passport",
        "🦅 Biodiversity",
        "🪙 Carbon Trading"
    ])
    
    with tab1:
        render_waste_heat_recovery()
        st.markdown("---")
        render_grid_load_shifting()
        
    with tab2:
        render_water_quality()
        
    with tab3:
        render_scope3()
        
    with tab4:
        render_algae_bioreactor()
        
    with tab5:
        render_digital_passport()
        
    with tab6:
        render_biodiversity()
        
    with tab7:
        render_carbon_credits()

if __name__ == "__main__":
    main()
