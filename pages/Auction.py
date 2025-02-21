import random
import time
import pandas as pd
import streamlit as st

from db.db_helper import DBHelper
from common.utils import apply_global_styles, get_to_base64

import streamlit.components.v1 as components

st.set_page_config(page_title="A(u)ction", page_icon="⚡", layout="wide")

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1 * 1000, key="live_refresh")  # Refresh every 10s    
    
def show_summary():
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    total_players, total_male, total_female, total_sold, total_unsold, total_spend = db.get_player_summary()
    highest_bid = db.get_highest_bid()
    avg_player_price = db.get_avg_player_price()
    
    # Display metrics in each column
    col1.metric(label="Total Players", value=total_players, border=True)
    col2.metric(label="Total Players(M)", value=total_male, border=True)
    col3.metric(label="Total Players(F)", value=total_female, border=True)
    col4.metric(label="Sold Players", value=total_sold, border=True)
    col5.metric(label="Unsold Players", value=total_unsold, border=True)
    col6.metric(label="Total Spend 💰", value=f"{total_spend} Pts.", border=True)
    col7.metric(label="Highest Bid 💸", value=f"{highest_bid} Pts.", border=True)
    col8.metric(label="Avg. Player Price", value=f"{avg_player_price} Pts.", border=True)

def show_user(col):
    with col:
        current_player = db.get_current_player()
        #st.write(current_player)
        if current_player is None:
            player = db.start_auction()
            current_player = db.get_current_player()
        else:
            player = db.get_player_by_name(current_player['player_name'])    
        #st.write(player)    
        st.markdown(
            f"""
            <br>
            <p style="font-size:32px; color:#000000; background: #FFFFFF;border-radius:15px;text-align:center;"><strong>Current Bid: </strong>{current_player['current_bid']} </p>
            <p style="font-size:32px; color:#000000; background: #FFFFFF;border-radius:15px;text-align:center;"><strong>Team: </strong>{current_player['bidding_team']}</.p> 
            <div class="card" style="height:510px;width:400px;background: linear-gradient(to bottom, #2C39CA 13%, #2C39CA 13%, #2C39CA 63%, #2C39CA 40%);border:none;overflow:hidden;box-shadow:none">
                <img src="{get_to_base64('./static/Male.png' if player['gender'] == 'Male' else './static/Female.png', 'png')}" alt="Team Logo" 
                    style="width:220px; height:220px;">
                <p style="font-size:42px;color:#FFFFFF;font-weight:800">{player['name']}</p>
                <p style="font-size:32px;color:#FFFFFF;">{'★' * int(player['rating'])}</p>
                <p style="font-size:28px; color:#FFFFFF;"><strong>Player Category: </strong>{'🏏' if player['player_category'] in ['All Rounder', 'Batter'] else '🏐'} {player['player_category']}</p>
                <p style="font-size:28px; color:#FFFFFF;"><strong>Available: </strong>{player["available"]}</p>
                <p style="font-size:28px; color:#FFFFFF;"><strong>Previously Played: </strong>{"✅" if player["previously_played"] == "Yes" else "❌"}</p 
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.session_state["role"] == "admin":
            st.markdown("<br>", unsafe_allow_html=True)
            
            _sold, _unsold = st.columns(2)
            with _sold:
                if st.button("Sold", key="sold", type="primary", use_container_width=True):
                    #st.balloons()
                    db.mark_player_sold(player=player, team=current_player['bidding_team'], bid_amount=current_player['current_bid'])
                    db.clear_current_player()
                    st.rerun()
            with _unsold:
                if st.button("Unsold", key="unsold", type="secondary", use_container_width=True):
                    db.mark_player_unsold(player=player)
                    db.clear_current_player()
                    st.rerun()

def show_team(col):

    teams = db.get_teams()
    df = pd.DataFrame(teams)
    
    # 💡 Create Custom Columns
    df["TEAM"] = df["team_name"]
    df["PLAYER"] = df.apply(lambda x: f"{x['player_count']} (F {x['female_count']} | M {x['male_count']})", axis=1)
    df["SPEND"] = df["spend"]
    df["BALANCE"] = df["budget"]
    df["AVAILABLE"] = (14 - df["player_count"]) * 20  # Assuming max 14 players

    # 🎯 Select & Order Columns
    df = df[["TEAM", "PLAYER", "SPEND", "BALANCE", "AVAILABLE"]]

    # 💫 Display the Table
    df = df.set_index("TEAM")
    #col.table(df)
    
    col.markdown(f"""
        <div class="container">
        <ul class="responsive-table">
            <li class="table-header">
                <div class="col col-1">Team</div>
                <div class="col col-2">Player</div>
                <div class="col col-3">Spend</div>
                <div class="col col-4">Budget</div>
                <div class="col col-4">Max. Bid</div>
            </li>
             <li class="table-row" style="background: linear-gradient(90deg, {teams[0]['primary_color']} 0%, {teams[0]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[0]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[0]['player_count']} (F{teams[0]['female_count']} | M{teams[0]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[0]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[0]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[0]["budget"] - ((14 - teams[0]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[1]['primary_color']} 0%, {teams[1]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[1]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[1]['player_count']} (F{teams[1]['female_count']} | M{teams[1]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[1]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[1]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[1]["budget"] - ((14 - teams[1]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[2]['primary_color']} 0%, {teams[2]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[2]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[2]['player_count']} (F{teams[2]['female_count']} | M{teams[2]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[2]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[2]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[2]["budget"] - ((14 - teams[2]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[3]['primary_color']} 0%, {teams[3]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[3]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[3]['player_count']} (F{teams[3]['female_count']} | M{teams[3]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[3]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[3]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[3]["budget"] - ((14 - teams[3]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="color:black;background: linear-gradient(90deg, {teams[4]['primary_color']} 0%, {teams[4]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[4]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[4]['player_count']} (F{teams[4]['female_count']} | M{teams[4]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[4]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[4]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[4]["budget"] - ((14 - teams[4]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[5]['primary_color']} 0%, {teams[5]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[5]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[5]['player_count']} (F{teams[5]['female_count']} | M{teams[5]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[5]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[5]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[5]["budget"] - ((14 - teams[5]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[6]['primary_color']} 0%, {teams[6]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[6]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[6]['player_count']} (F{teams[6]['female_count']} | M{teams[6]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[6]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[6]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[6]["budget"] - ((14 - teams[6]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[7]['primary_color']} 0%, {teams[7]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[7]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[7]['player_count']} (F{teams[7]['female_count']} | M{teams[7]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[7]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[7]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[7]["budget"] - ((14 - teams[7]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[8]['primary_color']} 0%, {teams[8]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[8]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[8]['player_count']} (F{teams[8]['female_count']} | M{teams[8]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[8]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[8]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[8]["budget"] - ((14 - teams[8]["player_count"] - 1) * 20))}</div>
            </li>
            <li class="table-row" style="background: linear-gradient(90deg, {teams[9]['primary_color']} 0%, {teams[9]['secondary_color']} 100%);">
                <div class="col col-1" data-label="Team">{teams[9]['team_name']}</div>
                <div class="col col-2" data-label="Player">{teams[9]['player_count']} (F{teams[9]['female_count']} | M{teams[9]['male_count']})</div>
                <div class="col col-3" data-label="Spend">{teams[9]['spend']}</div>
                <div class="col col-4" data-label="Budget">{teams[9]['budget']}</div>
                <div class="col col-4" data-label="Max. Bid">{max(0, teams[9]["budget"] - ((14 - teams[9]["player_count"] - 1) * 20))}</div>
            </li>
        </ul>
        </div>      
    """, unsafe_allow_html=True)
    
# from streamlit_autorefresh import st_autorefresh

# def show_team(col):
#     count = st_autorefresh(interval=2 * 1000, key="team_refresh")  # Refresh every 10s

#     teams = db.get_teams()
#     df = pd.DataFrame(teams)
    
#     # 💡 Create Custom Columns
#     df["TEAM"] = df["team_name"]
#     df["PLAYER"] = df.apply(lambda x: f"{x['player_count']} (F {x['female_count']} | M {x['male_count']})", axis=1)
#     df["SPEND"] = df["spend"]
#     df["BALANCE"] = df["budget"]
#     #df["AVAILABLE"] = (14 - df["player_count"]) * 20  # Assuming max 14 players
#     df["MAX BID"] = df.apply(lambda x: max(0, x["budget"] - ((14 - x["player_count"] - 1) * 20)), axis=1)
#     ## max(0, df['budget'] - ((14 - df['player_count']) - 1) * 20)

#     # 🎯 Select & Order Columns
#     df = df[["TEAM", "PLAYER", "SPEND", "BALANCE", "MAX BID"]]

#     # 💫 Display the Table
#     df = df.set_index("TEAM")
#     col.table(df)


def auto():
    for _ in range(1, 110):
        time.sleep(10)
        player = db.start_auction()
        teams = db.get_teams()
        print("Acution started...")
        print(f"Player : {player['name']}")
        current_bid = 20
        current_team = ""
                
        for _ in range(1, random.randint(1, 15)):
            #time.sleep(10)
             # 🔄 Move to next random team for bidding
            bidding_team = teams[random.randint(0, len(teams) - 1)]            
            print(f"Team: {bidding_team['team_name']} -- Budget [{bidding_team['budget']}]: Count: {bidding_team['player_count']}(F{bidding_team['female_count']}|M{bidding_team['male_count']})")

            # 💡 Check for female player limit
            if player['gender'] == 'Female' and bidding_team['female_count'] == 2:
                print(f"❌ Team '{bidding_team['team_name']}' already has 2 females. Skipping...")
            elif bidding_team['player_count'] == 14:
                print(f"❌ Team '{bidding_team['team_name']}' already has 14 player. Skipping...")
            elif bidding_team['budget'] > 0:
                available_balance = (15 - bidding_team['player_count']) * 20
                next_bid = current_bid + (5 if current_bid < 50 else 10)
                print(f"Balance {available_balance}, Next Bid {next_bid}")

                if available_balance > next_bid:
                    current_bid = next_bid
                    current_team = bidding_team['team_name']
                    db.place_bid(player_name=player['name'], bidder=current_team, bid_amount=current_bid)
                    print(f"✅ Current Bid: {current_bid}, Team: {current_team}")
        
        #time.sleep(10)
        
        if current_bid > 20 and current_team:
            db.mark_player_sold(player=player, team=current_team, bid_amount=current_bid)
            print(f"Player '{player['name']}' sold to '{current_team}' on price {current_bid}Pts.")
        else:
            db.mark_player_unsold(player=player)
            print(f"Player '{player['name']}' unsold.")

def valid(next_bid, player, bidding_team):
    # 💡 Check for female player limit
    if player['gender'] == 'Female' and bidding_team['female_count'] == 2:
        print(f"❌ Team '{bidding_team['team_name']}' already has 2 females. Skipping...")
        return False
    elif bidding_team['player_count'] == 14:
        print(f"❌ Team '{bidding_team['team_name']}' already has 14 player. Skipping...")
        return False
    elif bidding_team['budget'] > 0:
        available_balance = (14 - bidding_team['player_count']) * 20
        print(f"Balance {available_balance}, Next Bid {next_bid}")
        if available_balance > next_bid:
            return True
    return False

def show_auction_board():
    with st.expander("Bidding..."):
        pass
    
if __name__ == "__main__":
    apply_global_styles()
    db = DBHelper()
    current_player = db.get_current_player()
    current_bid = current_player['current_bid'] if current_player is not None else 20
    current_team = current_player['bidding_team'] if current_player is not None else ""
    
    show_summary()
    
    userCol, detailsCol = st.columns([2, 6])
    show_user(userCol)
    
    show_team(detailsCol)
    
    if st.session_state["role"] == "admin":
    
        with st.expander("Bidding box"):
            # 💡 Arrange Teams into 2 Rows (5 per row)
            
            teams = db.get_teams()
            rows = [teams[:5], teams[5:]]

            st.title("🏏 Team Actions Panel")
            st.success(f"Current Bid: {  current_player['current_bid']}, Team: {current_player['bidding_team']}")
                            
            current_bid = st.number_input(label="Custom bid", value=current_player['current_bid'])
                            
            # Create 10 columns for 10 teams
            cols = st.columns(10)  # 🟦 10 Buttons in a Single Row

            next_bid = current_bid + (5 if current_bid < 50 else 10)

            # Iterate through all teams and place each button in its column
            for idx, team in enumerate(teams):
                with cols[idx]:
                    if st.button(label=team['team_name']):
                        current_bid = current_bid + (5 if current_bid < 50 else 10)
                        current_team = team['team_name']
                        
                        # 💸 Place the bid in the database
                        db.place_bid(player_name=current_player['player_name'], bidder=current_team, bid_amount=current_bid)
                        
                        # 🔄 Fetch updated player info
                        current_player = db.get_current_player()

                            
        
        if st.button("Auto"):
            auto()
