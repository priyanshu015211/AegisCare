import streamlit as st


def render_sidebar():
    with st.sidebar:
        # Brand header
        st.markdown(
            """
            <div style="text-align: center; padding: 8px 0 16px 0;">
                <div style="font-size: 28px; margin-bottom: 4px;">🏥</div>
                <div style="font-size: 22px; font-weight: 700; color: #E2E8F0; letter-spacing: -0.02em;">AegisCare</div>
                <div style="font-size: 12px; color: #8892A4; margin-top: 2px;">Healthcare Coordination Platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<hr style="border-color: #2D3548; margin: 0 0 12px 0;">',
            unsafe_allow_html=True,
        )

        # Navigation
        current = st.session_state.get("current_page", "Dashboard")

        pages = {
            "Dashboard": ("📊", "Operations overview"),
            "Patient Triage": ("🩺", "AI clinical assessment"),
            "Emergency Center": ("🚨", "Critical case monitoring"),
            "Coordination Dashboard": ("📋", "Appointments & scheduling"),
            "Analytics": ("📈", "Trends & insights"),
        }

        page = st.radio(
            label="Navigation",
            options=list(pages.keys()),
            index=list(pages.keys()).index(current) if current in pages else 0,
            label_visibility="collapsed",
            format_func=lambda x: f"{pages[x][0]}  {x}",
        )

        st.session_state["current_page"] = page

        st.markdown(
            '<hr style="border-color: #2D3548; margin: 16px 0 12px 0;">',
            unsafe_allow_html=True,
        )

        # System status
        st.markdown(
            """
            <div style="padding: 0 4px;">
                <div style="font-size: 11px; font-weight: 600; color: #8892A4; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">System Status</div>
                <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(39, 103, 73, 0.15); border: 1px solid rgba(39, 103, 73, 0.3); border-radius: 8px;">
                    <div style="width: 8px; height: 8px; background: #68D391; border-radius: 50%;"></div>
                    <span style="font-size: 13px; color: #68D391; font-weight: 500;">Backend Connected</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return page
