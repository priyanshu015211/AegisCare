import streamlit as st


def show_emergency_center():
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 28px; font-weight: 700; color: #E2E8F0; margin: 0;">🚨 Emergency Center</h1>
            <p style="font-size: 14px; color: #8892A4; margin: 4px 0 0 0;">High-Risk Patient Monitoring</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Alert banner
    st.markdown(
        """
        <div style="background: rgba(252, 129, 129, 0.15); border: 1px solid rgba(252, 129, 129, 0.3); border-left: 4px solid #FC8181; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px; display: flex; align-items: center;">
            <span style="font-size: 18px; margin-right: 10px;">⚠️</span>
            <div>
                <div style="font-size: 14px; font-weight: 600; color: #FC8181;">Active Emergency</div>
                <div style="font-size: 13px; color: #8892A4;">1 patient requires immediate attention</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Critical Patients", "3", "+1")
    with c2:
        st.metric("Pending Escalations", "5", "+2")
    with c3:
        st.metric("Avg Response Time", "2.1 min", "-0.3 min")

    st.markdown('<hr style="border-color: #2D3548;">', unsafe_allow_html=True)

    # High risk table
    st.markdown(
        '<div style="font-size: 16px; font-weight: 600; color: #E2E8F0; margin-bottom: 12px;">High Risk Patients</div>',
        unsafe_allow_html=True,
    )

    patients = [
        {"id": "P-0987", "score": 85, "status": "Critical", "updated": "2 min ago", "symptoms": "chest pain, shortness of breath"},
        {"id": "P-0991", "score": 79, "status": "Escalated", "updated": "5 min ago", "symptoms": "confusion, severe headache"},
        {"id": "P-0994", "score": 82, "status": "Under Review", "updated": "12 min ago", "symptoms": "breathing difficulty, fever"},
    ]

    status_colors = {
        "Critical": ("#FC8181", "rgba(252, 129, 129, 0.15)"),
        "Escalated": ("#ECC94B", "rgba(236, 201, 75, 0.15)"),
        "Under Review": ("#63B3ED", "rgba(99, 179, 237, 0.15)"),
    }

    for p in patients:
        text_color, bg = status_colors.get(p["status"], ("#8892A4", "#1A1F2E"))
        st.markdown(
            f"""
            <div style="background: #1A1F2E; border: 1px solid #2D3548; border-radius: 10px; padding: 16px 20px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 15px; font-weight: 700; color: #E2E8F0;">{p['id']}</div>
                    <div style="font-size: 12px; color: #8892A4; margin-top: 2px;">{p['symptoms']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 24px; font-weight: 700; color: {text_color};">{p['score']}</div>
                    <div style="display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600; color: {text_color}; background: {bg};">{p['status']}</div>
                    <div style="font-size: 11px; color: #8892A4; margin-top: 4px;">{p['updated']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border-color: #2D3548; margin: 20px 0;">', unsafe_allow_html=True)

    # Escalation queue
    st.markdown(
        '<div style="font-size: 16px; font-weight: 600; color: #E2E8F0; margin-bottom: 12px;">Escalation Queue</div>',
        unsafe_allow_html=True,
    )

    st.info("Patients requiring immediate attention will appear here in real-time once the backend is connected.")
