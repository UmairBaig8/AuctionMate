import pandas as pd
import streamlit as st

from db.db_helper import DBHelper
from common.utils import apply_global_styles

st.set_page_config(page_title="Teams", page_icon="👥", layout="wide")

st.title("👥 Teams")
st.write("Manage teams and view player details.")

def load():
    with st.expander("Upload team..."):
        uploaded_file = st.file_uploader("Upload Player Data (XLSX)", type=["xlsx"])
        if uploaded_file is not None:
            df = db.load_data(uploaded_file)
            st.success("Player data uploaded successfully!")
        

if __name__ == "__main__":
    apply_global_styles()
    db = DBHelper()
    
    load()
    
    players = db.get_players()
    
    df = pd.DataFrame(players)
    
    st.write("### Player List")
    st.dataframe(df, use_container_width=True)