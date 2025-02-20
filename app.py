import streamlit as st
from streamlit_extras.app_logo import add_logo

from common.utils import apply_global_styles
from db.db_helper import DBHelper

st.set_page_config(page_title="Live Dashboard", page_icon="⚡", layout="wide")

def main():
    db = DBHelper()
    db.init_db() 
    
    apply_global_styles()
    
if __name__ == "__main__":
    main()
