from pathlib import Path

import streamlit as st

from monitoring import monitoring_page
from planner import planner_page

st.set_page_config(page_title="TripMate · India travel planner", page_icon="🧭", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'styles.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)

page = st.navigation(
    [
        st.Page(planner_page, title="Plan a trip", icon="🧭", url_path="plan", default=True),
        st.Page(monitoring_page, title="Monitoring", icon="📈", url_path="monitoring"),
    ],
    position="top",
)
page.run()
