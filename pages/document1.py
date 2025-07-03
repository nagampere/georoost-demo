import streamlit as st

from components.markdown_loader import load_markdown

st.markdown(load_markdown('README.md'), unsafe_allow_html=True)

# ホームに戻るボタン
if st.button("⬅ Back to Home"): st.switch_page("app.py")