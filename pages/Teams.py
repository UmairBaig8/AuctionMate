import re
import pandas as pd
import streamlit as st

from db.db_helper import DBHelper
from common.utils import apply_global_styles

st.set_page_config(page_title="Teams", page_icon="👥", layout="wide")

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=2 * 1000, key="live_refresh")  # Refresh every 10s  

st.title("👥 Teams")
st.write("Manage teams and view player details.")


def upload():
    with st.expander("Upload teams..."):
        uploaded_file = st.file_uploader("Teams", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            db.insert_teams(df)
            st.success("Player data uploaded successfully!")

def show_team(teams):
    # Loop through teams in batches of 5
    for i in range(0, len(teams), 5):
        cols = st.columns(5)  # Create 5 columns for the current row

        for j in range(5):
            if i + j < len(teams):  # Ensure we don't exceed the list length
                team = teams[i + j]
                
                with cols[j]:
                    st.markdown(
                        f"""
                        <div class="card" style="background: 
                                linear-gradient(90deg, {team['primary_color']} 0%, {team['secondary_color']} 100%) top,
                                linear-gradient(to bottom, #FFFFFF 50%, #FFFFFF 50%);
                            background-size: 100% 50%, 100% 100%;
                            background-repeat: no-repeat;
                            border:none; height: 220px; width: 250px; text-align:left; padding-left:20px;padding-top:10px;margin:15px;"
                        ">
                            <h3 style="color: { "black" if team['team_name'] == 'Digi<br> Super Kings' else 'white' };margin-top:15px;">{ re.sub(r'\s', '<br>', team['team_name'], count=1)}</h3>
                            <p style="color:black"><strong>🏆 Owner:</strong> {team['owner']}</p>
                            <p style="color:black"><strong>👑 Captain:</strong> {team['captain']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


if __name__ == "__main__":
    apply_global_styles()
    db = DBHelper()
    
    # Fetch all teams
    teams = db.get_teams()
    
    upload()
    # with st.expander("Teams..."):
    #     show_team(teams=teams)
    
    # Extract team names for tab creation
    available_teams = [team['team_name'] for team in teams]

    # Create tabs for each team
    tabs = st.tabs([f"🏆 {team}" for team in available_teams])

    # Loop through each tab and display team players
    for i, team_name in enumerate(available_teams):
        with tabs[i]:
            # Fetch players for the current team
            df = db.fetch_team_players(team_name)

            # Get team details from the existing 'teams' list
            team_info = next((team for team in teams if team['team_name'] == team_name), {})
            primary_color = team_info.get('primary_color', '#FFFFFF')
            secondary_color = team_info.get('secondary_color', '#F0F0F0')
            owner = team_info.get('owner', 'N/A')
            captain = team_info.get('captain', 'N/A')

            # Inject custom CSS for background
            st.markdown(f"""
                <style>
                div[data-baseweb="tab-panel"]:nth-of-type({i+3}) {{
                    background: 
                        linear-gradient(90deg, {primary_color} 0%, {secondary_color} 100%) 0% 0% / 100% 110px no-repeat,
                        linear-gradient(to bottom, #FFFFFF 50%, #FFFFFF 50%);
                    border-radius: 10px;
                    padding: 10px;
                    min-height: 600px;
                }}
                </style>
            """, unsafe_allow_html=True)


            # 🏆 Display Team Info: Team Name (Left) | Owner & Captain (Right)
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 20px; padding: 5px 10px;">
                    <div style="font-size:42px;color:{ '#000000' if i == 4 else '#FFFFFF'}">🏆 <strong>{team_name}</strong></div>
                    <div>
                        👑 <strong>Owner:</strong> {owner} &nbsp;&nbsp; | &nbsp;&nbsp; 🧢 <strong>Captain:</strong> {captain}
                    </div>
                </div>
                <br><br>
            """, unsafe_allow_html=True)



            # Prepare DataFrame for display
            team_df = df.rename(columns={
                "name": "Player Name", 
                "player_category": "Player Category", 
                "price": "Price", 
                "status": "Status"
            }).set_index("Player Name")

            # Display the DataFrame
            st.dataframe(team_df, use_container_width=True)
