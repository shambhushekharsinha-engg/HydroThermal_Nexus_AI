# -*- coding: utf-8 -*-
"""
pages/9_Global_Fleet.py — Global Multi-Site Fleet Command Center
Interactive world map + text search + fleet table + live facility switching.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import shared_components as sc

st.set_page_config(page_title="Global Fleet — HydroThermal Nexus", page_icon="🗺️", layout="wide")
user_info = sc.require_auth()
fac = sc.get_active_facility()
sc.show_header(
    title=f"🗺️ Global Fleet Command — {fac['flag']} {fac['name']}",
    subtitle="Monitor, search and switch between 17 global facilities in real-time"
)
sc.show_sidebar()

# ── Build facilities DataFrame ───────────────────────────────────────────────
rows = []
for key, f in sc.GLOBAL_FACILITIES.items():
    rows.append({
        "key": key,
        "Facility": f"{f['flag']} {f['name']}",
        "City": f["city"],
        "Country": f["country"],
        "Region": f["region"],
        "Status": f["status"],
        "Health": f["health"],
        "Temp (°C)": f["temp"],
        "Pressure (PSI)": f["pressure"],
        "Energy (kW)": f["energy_kw"],
        "lat": f["lat"],
        "lon": f["lon"],
        "description": f["description"],
        "flag": f["flag"],
        "timezone": f["timezone"],
    })
df = pd.DataFrame(rows)

active_key = st.session_state.get("active_facility", "texas_hq")

# ── Section 1: Map + Search ──────────────────────────────────────────────────
col_map, col_search = st.columns([2.8, 1])

with col_search:
    st.markdown("### 🔍 Find a Facility")
    search_query = st.text_input(
        "", placeholder="Type city, country or region...",
        key="fleet_search", label_visibility="collapsed"
    )

    # Filter
    if search_query:
        mask = df.apply(
            lambda r: any(
                search_query.lower() in str(r[c]).lower()
                for c in ["Facility", "City", "Country", "Region"]
            ),
            axis=1,
        )
        search_results = df[mask]
    else:
        search_results = df

    st.markdown(
        f"<div style='color:#94A3B8;font-size:0.8rem;margin-bottom:8px;'>"
        f"{len(search_results)} facilities found</div>",
        unsafe_allow_html=True,
    )

    for _, row in search_results.iterrows():
        key = row["key"]
        is_active = key == active_key
        status = row["Status"]
        color = "#00FF88" if status == "Nominal" else ("#FFB800" if status == "Warning" else "#FF2D55")
        border = "rgba(100,255,218,0.6)" if is_active else "rgba(255,255,255,0.06)"

        st.markdown(f"""
        <div style="background:rgba(17,34,64,0.8);border:1px solid {border};border-radius:10px;padding:10px 14px;margin-bottom:8px;">
          <div style="font-size:0.95rem;font-weight:700;color:#F8FAFC;">{row['flag']} {row['Facility'].split(' ', 1)[1]}</div>
          <div style="font-size:0.75rem;color:#94A3B8;">{row['City']}, {row['Country']}</div>
          <div style="font-size:0.75rem;margin-top:4px;"><span style="color:{color};font-weight:700;">● {status}</span> &nbsp; Health: {row['Health']}%</div>
        </div>
        """, unsafe_allow_html=True)

        btn_label = "✅ Active" if is_active else "🔌 Switch"
        if not is_active:
            if st.button(btn_label, key=f"search_switch_{key}", use_container_width=True):
                st.session_state["active_facility"] = key
                st.session_state["health_score"] = sc.GLOBAL_FACILITIES[key]["health"]
                st.rerun()
        else:
            st.button(btn_label, key=f"search_active_{key}", use_container_width=True, disabled=True)

with col_map:
    st.markdown("### 🌍 Global Facility Map")
    st.markdown(
        "<div style='color:#94A3B8;font-size:0.82rem;margin-bottom:12px;'>"
        "Markers sized by health score. Use the search panel to switch facilities.</div>",
        unsafe_allow_html=True,
    )

    # Build the interactive scatter map (size by Health column — numeric, 0-100)
    fig_map = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        hover_name="Facility",
        hover_data={
            "lat": False, "lon": False,
            "Status": True, "Health": True,
            "City": True, "Country": True, "Region": True,
        },
        color="Status",
        color_discrete_map={"Nominal": "#00FF88", "Warning": "#FFB800", "Critical": "#FF2D55"},
        size="Health",
        size_max=20,
        zoom=1.2,
        height=520,
    )

    # Highlight the active facility with a larger ring marker
    active_row = df[df["key"] == active_key].iloc[0]
    fig_map.add_trace(go.Scattermap(
        lat=[active_row["lat"]],
        lon=[active_row["lon"]],
        mode="markers+text",
        marker=dict(size=30, color="rgba(100,255,218,0.25)", symbol="circle"),
        text=[f"◉ {active_row['Facility'].split(' ', 1)[1]}"],
        textfont=dict(color="#64FFDA", size=11),
        textposition="top center",
        showlegend=False,
        hoverinfo="skip",
        name="Active",
    ))

    fig_map.update_layout(
        map_style="carto-darkmatter",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            bgcolor="rgba(10,25,47,0.9)",
            bordercolor="rgba(100,255,218,0.2)",
            borderwidth=1,
            font=dict(color="#E2E8F0", size=12),
        ),
    )

    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ── Section 2: Active Facility Snapshot ─────────────────────────────────────
active_fac = sc.get_active_facility()
status = active_fac["status"]
status_color = "#00FF88" if status == "Nominal" else ("#FFB800" if status == "Warning" else "#FF2D55")
health = active_fac["health"]

st.markdown(f"### {active_fac['flag']} Active Facility Snapshot — {active_fac['name']}")
st.markdown(
    f"<span style='color:#94A3B8;font-size:0.85rem;'>"
    f"{active_fac['description']} | {active_fac['timezone']}</span>",
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:16px;'>", unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("🛡️ Health Score", f"{health}%")
m2.metric("🌡️ Temperature", f"{active_fac['temp']} °C")
m3.metric("💧 Pressure", f"{active_fac['pressure']} PSI")
m4.metric("⚡ Energy", f"{active_fac['energy_kw']} kW")
m5.metric("🌱 Grid Carbon", f"{active_fac['grid_carbon']} kg CO₂/kWh")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Section 3: Global Fleet Table ───────────────────────────────────────────
st.markdown("### 📋 Global Fleet Status Dashboard")

# Region filter
regions_list = ["All Regions"] + sorted(df["Region"].unique().tolist())
selected_region = st.selectbox("Filter by Region:", regions_list, key="fleet_region_filter")

display_df = df if selected_region == "All Regions" else df[df["Region"] == selected_region]
display_df = display_df.sort_values("Health", ascending=False)

# Styled fleet table rows
for _, row in display_df.iterrows():
    key = row["key"]
    is_active = key == active_key
    row_status = row["Status"]
    health_val = row["Health"]

    row_status_color = "#00FF88" if row_status == "Nominal" else ("#FFB800" if row_status == "Warning" else "#FF2D55")
    health_color = "#00FF88" if health_val >= 90 else ("#FFB800" if health_val >= 70 else "#FF2D55")
    border_color = "rgba(100,255,218,0.5)" if is_active else "rgba(255,255,255,0.05)"
    bg = "rgba(100,255,218,0.04)" if is_active else "rgba(17,34,64,0.5)"
    bar_width = int(health_val)
    bar_color = "#00FF88" if health_val >= 90 else ("#FFB800" if health_val >= 70 else "#FF2D55")

    col_info, col_metrics, col_bar, col_btn = st.columns([3, 3, 2.5, 1.2])

    with col_info:
        active_tag = (
            " <span style='background:rgba(100,255,218,0.15);color:#64FFDA;"
            "border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;'>ACTIVE</span>"
            if is_active else ""
        )
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border_color};border-radius:10px;padding:12px 16px;">
          <div style="font-size:0.95rem;font-weight:700;color:#F8FAFC;">{row['flag']} {row['Facility'].split(' ', 1)[1]}{active_tag}</div>
          <div style="font-size:0.75rem;color:#94A3B8;">{row['City']}, {row['Country']} · {row['Region']}</div>
          <div style="font-size:0.72rem;color:#64748B;margin-top:3px;">{row['timezone']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_metrics:
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border_color};border-radius:10px;padding:12px 16px;">
          <span style="color:{row_status_color};font-weight:700;">● {row_status}</span>
          <span style="color:#64748B;font-size:0.8rem;"> &nbsp;|&nbsp; 🌡️ {row['Temp (°C)']}°C &nbsp;|&nbsp; 💧 {row['Pressure (PSI)']} PSI &nbsp;|&nbsp; ⚡ {row['Energy (kW)']} kW</span>
        </div>
        """, unsafe_allow_html=True)

    with col_bar:
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border_color};border-radius:10px;padding:12px 16px;">
          <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:6px;">Health: <span style="color:{health_color};font-weight:700;">{health_val}%</span></div>
          <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:8px;overflow:hidden;">
            <div style="background:{bar_color};height:8px;width:{bar_width}%;border-radius:4px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        if not is_active:
            if st.button("🔌 Switch", key=f"table_switch_{key}", use_container_width=True):
                st.session_state["active_facility"] = key
                st.session_state["health_score"] = sc.GLOBAL_FACILITIES[key]["health"]
                st.rerun()
        else:
            st.button("✅ Active", key=f"table_active_{key}", use_container_width=True, disabled=True)

st.markdown("---")

# ── Section 4: Fleet-wide Analytics ─────────────────────────────────────────
st.markdown("### 📊 Fleet-Wide Health Analytics")

fig_bar = go.Figure(go.Bar(
    y=df["Facility"],
    x=df["Health"],
    orientation="h",
    marker_color=[
        "#00FF88" if h >= 90 else "#FFB800" if h >= 70 else "#FF2D55"
        for h in df["Health"]
    ],
    text=[f"{h}%" for h in df["Health"]],
    textposition="outside",
))
fig_bar.update_layout(
    sc.PLOTLY_LAYOUT,
    height=520,
    xaxis_title="Health Score (%)",
    xaxis_range=[0, 115],
    yaxis=dict(autorange="reversed"),
    title="All Facilities — Health Score Ranking",
)
st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
