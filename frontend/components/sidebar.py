import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("AegisCare")
        st.caption("Healthcare Coordination Platform")

        st.markdown("---")

        # Get current page from session state
        current = st.session_state.get("current_page", "Dashboard")

        page = st.radio(
            label="Navigation",
            options=[
                "Dashboard",
                "Patient Triage",
                "Emergency Center",
                "Coordination Dashboard",
                "Analytics"
            ],
            index=["Dashboard", "Patient Triage", "Emergency Center", "Coordination Dashboard", "Analytics"].index(current)
            if current in ["Dashboard", "Patient Triage", "Emergency Center", "Coordination Dashboard", "Analytics"] else 0,
            label_visibility="collapsed"
        )

        # Save selected page
        st.session_state["current_page"] = page

        st.markdown("---")
        st.subheader("System Status")
        st.success("Backend: Connected", icon="🟢")

        return page
