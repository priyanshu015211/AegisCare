import streamlit as st
import plotly.express as px
import pandas as pd

def show_analytics():
    st.header("Analytics")
    st.caption("Operational Trends & Insights")

    st.subheader("Patient Volume Trend (Placeholder)")
    df = pd.DataFrame({
        "Hour": ["08:00", "10:00", "12:00", "14:00", "16:00"],
        "Patients": [12, 19, 25, 31, 28]
    })
    fig = px.line(df, x="Hour", y="Patients", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Escalation Frequency")
    st.bar_chart({"Low": 45, "Medium": 22, "High": 9})
