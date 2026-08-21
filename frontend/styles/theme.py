import streamlit as st

def apply_custom_css():
    with open("frontend/styles/main.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
