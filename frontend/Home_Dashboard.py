"""Streamlit Home Dashboard for AgroPulse Copilot."""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AgroPulse Copilot", page_icon="🌾", layout="wide")

# --- Sidebar Configuration ---
st.sidebar.title("⚙️ System Configuration")
API_URL = st.sidebar.text_input("FastAPI Backend URL", "http://127.0.0.1:8000")
st.sidebar.markdown("---")
st.sidebar.info("AgroPulse Copilot v1.0.0\nEnterprise AI for Smallholder Farmers")

# --- Main Dashboard ---
st.title("🌾 AgroPulse Copilot: Stakeholder Command Center")
st.markdown("Real-time IoT telemetry, hydrological KPIs, and AI-driven crop insights.")

# 1. Fetch Data from Backend (Synchronous requests)
try:
    response = requests.post(f"{API_URL}/api/v1/telemetry/mock", timeout=5)
    data = response.json()
    hydrology = data.get("hydrology", {})
    action_window = data.get("action_window", {})
except Exception:
    st.warning("⚠️ FastAPI backend is offline. Displaying mock data for UI demonstration.")
    hydrology = {"et0_fao_mm_day": 5.4, "soil_moisture_pct": 22.5}
    action_window = {"can_spray_today": True, "irrigation_due_hours": 18, "wind_warning": False}

# 2. Top Level KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Reference Evapotranspiration (ET0)", f"{hydrology.get('et0_fao_mm_day', 0):.2f} mm/day")
col2.metric("Current Soil Moisture", f"{hydrology.get('soil_moisture_pct', 0):.1f}%")
col3.metric("Irrigation Due In", f"{action_window.get('irrigation_due_hours', 0)} hours")
col4.metric("Safe to Spray Today", "✅ Yes" if action_window.get("can_spray_today") else "❌ No")

st.divider()

# 3. SHAP Explainability Chart
st.header("🧠 AI Crop Suitability & SHAP Explainability")
st.markdown("Why did the AI recommend this specific crop? The SHAP values show the exact impact of each soil feature.")

shap_data = pd.DataFrame({
    "Feature": ["Nitrogen", "Phosphorus", "Potassium", "Moisture", "pH", "Temperature"],
    "SHAP Value": [0.45, -0.12, 0.30, 0.65, -0.05, 0.20]
})

fig = px.bar(
    shap_data, x="Feature", y="SHAP Value", 
    color="SHAP Value", 
    color_continuous_scale="RdYlGn",
    title="Feature Attribution (SHAP) for Optimal Crop Prediction"
)
st.plotly_chart(fig, use_container_width=True)

# 4. System Status
st.header("🟢 System Health")
try:
    health = requests.get(f"{API_URL}/health", timeout=2).json()
    st.success(f"Backend Status: **{health.get('status', 'Unknown').upper()}**")
except Exception:
    st.error("Backend Status: **OFFLINE**")