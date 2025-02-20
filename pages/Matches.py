import streamlit as st

from common.utils import apply_global_styles

st.set_page_config(page_title="Matches", page_icon="🏏", layout="wide")
apply_global_styles()

st.title("🏏 Matches")
st.write("View past and upcoming matches here.")