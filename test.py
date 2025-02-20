from db.db_helper import DBHelper
import random


# Run the generator
def generate_stub(db, users=5, players=10, bids=5, teams=3):
    db.generate_users(users)
    db.generate_players(players)
    db.generate_teams(teams)
    #db.generate_bids(bids)
    #db.generate_current_player()    

def auto():
    for _ in range(1, 110):
        player = db.start_auction()
        teams = db.get_teams()
        print("Acution started...")
        print(f"Player : {player['name']}")
        current_bid = 20
        current_team = ""
                
        for _ in range(1, random.randint(1, 15)):
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
        if current_bid > 20 and current_team:
            db.mark_player_sold(player=player, team=current_team, bid_amount=current_bid)
            print(f"Player '{player['name']}' sold to '{current_team}' on price {current_bid}Pts.")
        else:
            db.mark_player_unsold(player=player)
            print(f"Player '{player['name']}' unsold.")

if __name__ == "__main__":
    db = DBHelper()
    db.init_db()
    
    generate_stub(db, users=0, players=110, bids=0, teams=0)  # Change numbers as needed
    
    #auto()

    