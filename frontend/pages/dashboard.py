import streamlit as st
import plotly.express as px
import pandas as pd

def show_dashboard():
    st.header("Dashboard")
    st.caption("Hospital Operations Overview")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Current Hospital Load", "72%", "+8%")
    with col2: st.metric("Active Emergencies", "5", "+1")
    with col3: st.metric("Avg Triage Time", "3.8 min", "-0.4 min")

    st.markdown("---")
    st.subheader("Current Risk Distribution")

    risk_data = pd.DataFrame({
        "Risk Level": ["Low", "Medium", "High"],
        "Patients": [28, 12, 7]
    })
    fig = px.pie(risk_data, values="Patients", names="Risk Level")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Patient Activity")
    st.dataframe({
        "Time": ["10:42", "10:38", "10:31"],
        "Patient ID": ["P-1042", "P-1041", "P-1040"],
        "Action": ["Symptom Update", "New Session", "Escalated"],
        "Risk": ["Medium", "Low", "High"]
    }, use_container_width=True, hide_index=True)
