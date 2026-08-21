import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def show_dashboard():
    # Header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 28px; font-weight: 700; color: #E2E8F0; margin: 0;">Dashboard</h1>
            <p style="font-size: 14px; color: #8892A4; margin: 4px 0 0 0;">Hospital Operations Overview</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Top metrics ----
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Active Patients", "23", "+3", delta_color="normal")
    with c2:
        st.metric("Critical Cases", "5", "+1", delta_color="inverse")
    with c3:
        st.metric("Avg Triage Time", "3.8 min", "-0.4 min", delta_color="normal")
    with c4:
        st.metric("Escalation Rate", "12%", "-2%", delta_color="normal")

    st.markdown(
        '<hr style="border-color: #2D3548; margin: 16px 0 24px 0;">',
        unsafe_allow_html=True,
    )

    # ---- Row 2: Risk chart + Activity ----
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(
            '<div style="font-size: 16px; font-weight: 600; color: #E2E8F0; margin-bottom: 12px;">Risk Distribution</div>',
            unsafe_allow_html=True,
        )

        risk_data = pd.DataFrame({
            "Risk Level": ["Low", "Moderate", "High", "Critical"],
            "Patients": [28, 12, 7, 3],
            "Color": ["#48BB78", "#ECC94B", "#FC8181", "#F56565"],
        })

        fig = go.Figure(data=[go.Pie(
            labels=risk_data["Risk Level"],
            values=risk_data["Patients"],
            hole=0.55,
            marker=dict(colors=risk_data["Color"]),
            textinfo="label+percent",
            textfont=dict(size=12, color="#E2E8F0"),
            hovertemplate="<b>%{label}</b><br>%{value} patients<br>%{percent}<extra></extra>",
        )])
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color="#8892A4", size=12)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            annotations=[dict(text="50<br><span style='font-size:12px;color:#8892A4'>Total</span>", x=0.5, y=0.5, font_size=20, font_color="#E2E8F0", showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown(
            '<div style="font-size: 16px; font-weight: 600; color: #E2E8F0; margin-bottom: 12px;">Recent Activity</div>',
            unsafe_allow_html=True,
        )

        activity_data = pd.DataFrame({
            "Time": ["10:42", "10:38", "10:31", "10:25", "10:18"],
            "Patient": ["P-1042", "P-1041", "P-1040", "P-1039", "P-1038"],
            "Event": ["Symptom Update", "New Session", "Escalated", "Resolved", "Triage Started"],
            "Severity": ["Moderate", "Low", "High", "Low", "Moderate"],
        })

        severity_colors = {
            "Low": "🟢",
            "Moderate": "🟡",
            "High": "🔴",
            "Critical": "🚨",
        }

        for _, row in activity_data.iterrows():
            color = severity_colors.get(row["Severity"], "⚪")
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; padding: 10px 12px; margin-bottom: 4px; background: #1A1F2E; border: 1px solid #2D3548; border-radius: 8px; border-left: 3px solid {'#48BB78' if row['Severity'] == 'Low' else '#ECC94B' if row['Severity'] == 'Moderate' else '#FC8181'};">
                    <span style="margin-right: 8px;">{color}</span>
                    <div style="flex: 1;">
                        <span style="font-size: 13px; font-weight: 600; color: #E2E8F0;">{row['Event']}</span>
                        <span style="font-size: 12px; color: #8892A4; margin-left: 8px;">{row['Patient']}</span>
                    </div>
                    <span style="font-size: 12px; color: #8892A4;">{row['Time']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<hr style="border-color: #2D3548; margin: 24px 0 24px 0;">',
        unsafe_allow_html=True,
    )

    # ---- Row 3: Hospital Load ----
    st.markdown(
        '<div style="font-size: 16px; font-weight: 600; color: #E2E8F0; margin-bottom: 12px;">Hospital Load</div>',
        unsafe_allow_html=True,
    )

    hospital_data = pd.DataFrame({
        "Hospital": ["City General", "St. Mary's", "Community Health", "University Medical", "Memorial"],
        "Load": [72, 58, 85, 45, 91],
    })

    colors = ["#48BB78" if v < 60 else "#ECC94B" if v < 80 else "#FC8181" for v in hospital_data["Load"]]

    fig_bar = go.Figure(data=[go.Bar(
        y=hospital_data["Hospital"],
        x=hospital_data["Load"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        text=[f"{v}%" for v in hospital_data["Load"]],
        textposition="auto",
        textfont=dict(color="#E2E8F0", size=12),
        hovertemplate="<b>%{y}</b><br>%{x}% capacity<extra></extra>",
    )])
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", range=[0, 100], gridcolor="#2D3548", tickfont=dict(color="#8892A4")),
        yaxis=dict(tickfont=dict(color="#E2E8F0", size=13)),
        margin=dict(t=10, b=10, l=10, r=10),
        height=220,
    )
    st.plotly_chart(fig_bar, use_container_width=True)
