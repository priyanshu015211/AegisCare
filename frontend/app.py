import streamlit as st
from frontend.styles.theme import apply_custom_css
from frontend.components.sidebar import render_sidebar

# Import pages
from frontend.pages import (
    dashboard,
    patient_triage,
    emergency_center,
    coordination_dashboard,
    analytics
)

st.set_page_config(
    page_title="AegisCare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()
current_page = render_sidebar()

# Page Routing
if current_page == "Dashboard":
    dashboard.show_dashboard()
elif current_page == "Patient Triage":
    patient_triage.show_patient_triage()
elif current_page == "Emergency Center":
    emergency_center.show_emergency_center()
elif current_page == "Coordination Dashboard":
    coordination_dashboard.show_coordination_dashboard()
elif current_page == "Analytics":
    analytics.show_analytics()
