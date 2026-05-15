import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("AegisCare")
        st.caption("Healthcare Coordination Platform")

        st.markdown("---")

        page = st.radio(
            label="Navigation",
            options=[
                "Dashboard",
                "Patient Triage",
                "Emergency Center",
                "Coordination Dashboard",
                "Analytics"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.subheader("System Status")
        st.success("Backend: Connected", icon="🟢")
        st.caption("v0.2.0 • Phase 6+7")

        return page
