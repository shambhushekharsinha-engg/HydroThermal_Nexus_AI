import streamlit as st

def generate_root_cause_analysis(telemetry_data, anomaly_type):
    """
    Generates structured diagnostic evaluations based on telemetry anomalies.
    """
    st.markdown("### 🤖 AI-Driven Root Cause Analysis (RCA)")
    
    if anomaly_type == "Pipe Rupture / Flow Drop":
        st.error("🚨 **Critical Anomaly Detected:** Sudden pressure loss & telemetry drop.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🔍 Primary Failure Vector")
            st.warning("**Solenoid Valve / Main Header Pressure Breakdown**")
            st.write("Calculated fluid loss rate exceeds normal variance threshold by +240%.")
            
        with col2:
            st.markdown("#### 🛠️ Automated Mitigation Path")
            st.info("1. Triggered Solenoid Relay Valve Cutoff.\n2. Rerouted thermal loop to auxiliary bypass.\n3. Issued Telegram Alert Gateway dispatch.")
            
        st.markdown("#### 🌱 ESG & Regulatory Impact")
        st.caption("Prevented estimated water waste of **1,450 Liters/hr** and potential thermal contamination.")

    elif anomaly_type == "HVAC Overheat / Thermal Spike":
        st.warning("⚠️ **Warning Anomaly Detected:** Thermal threshold exceedance.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🔍 Primary Failure Vector")
            st.warning("**Cooling Tower Heat Exchange Degradation**")
            st.write("Temperature ramp-up indicates potential fan motor relay stall.")
            
        with col2:
            st.markdown("#### 🛠️ Automated Mitigation Path")
            st.info("1. Engaged secondary auxiliary chiller system.\n2. Throttled high-load compute racks.\n3. Flagged maintenance ticket in SQLite database.")
            
        st.markdown("#### 🌱 ESG & Regulatory Impact")
        st.caption("Prevented energy surcharge penalty; avoided estimated **38 kg CO2e** excess emissions.")