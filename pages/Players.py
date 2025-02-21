import pandas as pd
import streamlit as st

from db.db_helper import DBHelper
from common.utils import apply_global_styles

st.set_page_config(page_title="Teams", page_icon="👥", layout="wide")

st.title("👥 Teams")
st.write("Manage teams and view player details.")

def load():
    with st.expander("Upload Team..."):
        uploaded_file = st.file_uploader("Upload Player Data (XLSX or CSV)", type=["xlsx", "csv"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                type = 'xl'
            else:
                df = pd.read_csv(uploaded_file)
                type = 'csv'

            # Save uploaded data to DB
            db.load_data(df,type) 
            st.success("✅ Player data uploaded successfully!")
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    apply_global_styles()
    db = DBHelper()

    load()

    # Fetch player data from DB
    players = db.get_players()
    df = pd.DataFrame(players)

    st.write("### 📋 Player List")
    st.dataframe(df, use_container_width=True)

    # CSV Export Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Export as CSV",
        data=csv,
        file_name="players.csv",
        mime="text/csv"
    )
