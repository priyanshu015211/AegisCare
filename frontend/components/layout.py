import streamlit as st

def section_header(title: str, description: str = ""):
    st.subheader(title)
    if description:
        st.caption(description)
    st.markdown("---")
