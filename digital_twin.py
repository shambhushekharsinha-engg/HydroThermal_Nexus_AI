import streamlit as st
import pydeck as pdk
import pandas as pd

def render_digital_twin():
    st.subheader("🌐 Geo-Spatial Digital Twin (3D Facility Telemetry)")
    
    # Mock telemetry node coordinates around facility assets
    nodes_data = [
        {"node_id": "Hydro-Node-Alpha", "lat": 28.6139, "lon": 77.2090, "status": "Normal", "flow_rate": 120, "temp": 42.5},
        {"node_id": "Thermal-Node-Beta", "lat": 28.6150, "lon": 77.2110, "status": "Warning", "flow_rate": 85, "temp": 68.0},
        {"node_id": "Cooling-Tower-Gamma", "lat": 28.6120, "lon": 77.2070, "status": "Critical", "flow_rate": 30, "temp": 89.2},
    ]
    
    df = pd.DataFrame(nodes_data)
    
    # Status-based RGB color mapping
    color_lookup = {
        "Normal": [0, 200, 100, 160],
        "Warning": [255, 165, 0, 180],
        "Critical": [230, 50, 50, 200]
    }
    df['color'] = df['status'].map(color_lookup)

    # 3D Column Layer for spatial elevation representing thermal output
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="temp",
        elevation_scale=15,
        radius=30,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=28.6139,
        longitude=77.2090,
        zoom=15,
        pitch=45,
    )

    deck = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        tooltip={"text": "Node: {node_id}\nStatus: {status}\nTemp: {temp}°C\nFlow: {flow_rate} L/m"}
    )

    st.pydeck_chart(deck)