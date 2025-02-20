import streamlit as st

from lib.utils import apply_global_styles

st.set_page_config(page_title="Point Table", page_icon="📊", layout="wide")
apply_global_styles()

st.title("📊 Point Table")
st.write("Check the team rankings and points here.")