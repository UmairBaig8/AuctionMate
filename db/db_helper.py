import sqlite3
from typing import List, Tuple, Dict, Optional

####### FAKE DATA ######
import random
from faker import Faker
import pandas as pd
fake = Faker()
########################
    
class DBHelper:
    def __init__(self, db_name="auction.db"):
        self.db_name = db_name

    def get_db_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                icon TEXT,
                label TEXT,
                page TEXT,
                position INTEGER)''')  # Position helps control the order
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        available TEXT,
                        work_location TEXT,
                        previously_played TEXT,
                        wish_to_be TEXT,
                        player_category TEXT,
                        rating TEXT,
                        gender TEXT,
                        team TEXT,
                        price INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'available')''')  # Status added
        c.execute('''CREATE TABLE IF NOT EXISTS bids (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT,
                        bidder TEXT,
                        bid_amount INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')  # Added timestamp
        c.execute('''CREATE TABLE IF NOT EXISTS current_player (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_id INTEGER,
                        player_name TEXT, 
                        base_price INTEGER DEFAULT 20, 
                        current_bid INTEGER DEFAULT 20, 
                        bidding_team TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS teams (
                        team_name TEXT PRIMARY KEY,
                        owner TEXT,
                        captain TEXT,
                        spend INTEGER DEFAULT 0,
                        budget INTEGER DEFAULT 1000,
                        player_count INTEGER DEFAULT 2,
                        male_count INTEGER DEFAULT 2,
                        female_count INTEGER DEFAULT 2,
                        primary_color TEXT,
                        secondary_color TEXT)''')
        conn.commit()
        conn.close()
        
   # Data loader
    def load_data(self, df, type: str):
        # Drop 'Unnamed: 0' if it exists
        if 'Unnamed: 0' in df.columns:
            df.drop(columns=['Unnamed: 0'], inplace=True)

        if type == 'xl':
            # Full header from Excel
            df.columns = [
                "id", "start_time", "completion_time", "email", "name", "available",
                "work_location", "previously_played", "wish_to_be", "player_category",
                "rating", "gender"
            ]

            # Keep only columns needed for DB
            df = df[[
                "id", "name", "available", "work_location", "previously_played", 
                "wish_to_be", "player_category", "rating", "gender"
            ]]

            # Add missing columns for DB schema
            df["team"] = None
            df["price"] = 0
            df["status"] = "available"

        # Connect to DB and insert
        conn = self.get_db_connection()
        df.to_sql("players", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

        
    # Menu items
    def generate_menu_items(self):
        menu_items = [
            ("./static/Asset 2.svg", "Live", "app.py", 1,),
            ("./static/Asset 3.svg", "Auction", "./pages/Auction.py", 2,),
            ("./static/Asset 4.svg", "Matches", "./pages/Matches.py", 3,),
            ("./static/Asset 5.svg", "Point Table", "./pages/Point_Table.py", 4,),
            ("./static/Asset 6.svg", "Teams", "./pages/Teams.py", 5,),
            ("./static/Asset 6.svg", "Player", "./pages/Players.py", 6,)
        ]
        
        conn = self.get_db_connection()
        c = conn.cursor()
        c.executemany('INSERT INTO menu_items (icon, label, page, position) VALUES (?, ?, ?, ?)', menu_items)
        conn.commit()
        conn.close()
        print("✅ Menu items added.")

    def get_menu_items(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT icon, label, page FROM menu_items ORDER BY position ASC")
        menu_items = c.fetchall()
        conn.close()
        return [{"icon": row[0], "label": row[1], "page": row[2]} for row in menu_items]

    # User Management
    def add_user(self, username: str, password: str, role: str):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()

    def get_user(self, username: str) -> Optional[Tuple]:
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        return user

    # Player Management
    def add_player(self, player_data: Dict):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO players (email, name, available, work_location, previously_played,
                                wish_to_be, player_category, rating, gender, team, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple(player_data.values()))
        conn.commit()
        conn.close()

    def get_players(self) -> List[Dict]:
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
        c = conn.cursor()
        c.execute("SELECT * FROM players")
        players = [dict(row) for row in c.fetchall()]  # Convert rows to dicts
        conn.close()
        return players

    def get_player_by_name(self, player_name: str) -> Optional[Dict]:
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row  # 👈 Enables dict-like access
        c = conn.cursor()
        c.execute("SELECT * FROM players WHERE name = ?", (player_name,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_player_summary(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            COUNT(*) AS total_players,
            COUNT(CASE WHEN Gender = 'Male' THEN 1 END) AS total_male_players,
            COUNT(CASE WHEN Gender = 'Female' THEN 1 END) AS total_female_players,
            COUNT(CASE WHEN team IS NOT NULL AND team != '' THEN 1 END) AS total_sold,
            COUNT(CASE WHEN team IS NULL OR team = '' THEN 1 END) AS total_unsold,
            SUM(price) AS total_spend
        FROM players;
        """

        cursor.execute(query)
        result = cursor.fetchone()
        return result
    
    def get_random_player(self, gender) -> Optional[Dict]:
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row  # Enables fetching rows as dictionaries
        c = conn.cursor()
        c.execute("SELECT * FROM players WHERE gender = ? AND status = 'available' ORDER BY RANDOM() LIMIT 1", (gender,))
        result = c.fetchone()
        conn.close()
        return dict(result) if result else None  # Convert row to dict if found

    def start_auction(self):
        player = self.get_random_player("Female")
        if not player:
            player = self.get_random_player("Male")
        if player:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("DELETE FROM current_player")  # Clear previous auction data
            c.execute("INSERT INTO current_player (player_id, player_name, base_price, current_bid) VALUES (?, ?, ?, ?)",
                    (player['name'], player['name'], 20, 20))  # Storing player ID for reference
            conn.commit()
            conn.close()
        return player
        
    def mark_player_sold(self, player, team, bid_amount: int):
        conn = self.get_db_connection()
        c = conn.cursor()
        
        # Extract name and gender
        player_name = player['name']  
        gender = player['gender']
        
        print(f"Updating: [{player_name}]:{gender}")

        # Mark player as sold and assign them to a team
        c.execute("UPDATE players SET status = 'sold', team = ?, price = ? WHERE name = ?", ( team, bid_amount, player_name))

        # Update team's budget
        c.execute("UPDATE teams SET budget = budget - ?, spend = spend + ? WHERE team_name = ?", 
                (bid_amount, bid_amount, team))

        # Update player count based on gender
        if gender.lower() == "male":
            print(f"Male Updated")
            c.execute("UPDATE teams SET player_count = player_count + 1, male_count = male_count + 1 WHERE team_name = ?", (team,))
        else:
            print(f"Male Updated")
            c.execute("UPDATE teams SET player_count = player_count + 1, female_count = female_count + 1 WHERE team_name = ?", (team,))

        conn.commit()
        conn.close()
        return True  # Successfully marked as sold
    
    def mark_player_unsold(self, player):
        conn = self.get_db_connection()
        c = conn.cursor()
                
        # Mark player as sold and assign them to a team
        c.execute("UPDATE players SET status = 'unsold' WHERE name = ?", (player['name'],))

        conn.commit()
        conn.close()
        return True  # Successfully marked as sold
    
    def get_avg_player_price(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT AVG(price) 
        FROM players 
        WHERE status = 'sold'
        """
        cursor.execute(query)
        result = cursor.fetchone()

        conn.close()
        return round(result[0], 2) if result[0] else 0
    
    def get_most_expensive_player(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT name, price 
        FROM players 
        WHERE price = (SELECT MAX(price) FROM players)
        """
        cursor.execute(query)
        result = cursor.fetchone()

        conn.close()
        return f"{result[0]} ({result[1]} Pts.)" if result else "N/A"


    # Bidding Management
    def get_highest_bid(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        query = "SELECT MAX(bid_amount) FROM bids"
        cursor.execute(query)
        result = cursor.fetchone()

        conn.close()
        return result[0] if result[0] else 0
    
    def record_bid(self, player_name, bidder, bid_amount):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO bids (player_name, bidder, bid_amount) VALUES (?, ?, ?)",
                (player_name, bidder, bid_amount))
        conn.commit()
        conn.close()
        
    def place_bid(self, player_name: str, bidder: str, bid_amount: int):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO bids (player_name, bidder, bid_amount) VALUES (?, ?, ?)", (player_name, bidder, bid_amount))
        c.execute("UPDATE current_player SET current_bid = ?, bidding_team = ? WHERE player_name = ?", (bid_amount, bidder, player_name))
        conn.commit()
        conn.close()
    
    def get_current_player(self) -> Optional[Dict]:
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row  # 👈 Enables dict-like access
        c = conn.cursor()
        c.execute("SELECT * FROM current_player LIMIT 1")
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def set_current_player(self, player_name: str, base_price: int = 20):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM current_player")
        c.execute("INSERT INTO current_player (player_name, base_price, current_bid) VALUES (?, ?, ?)",
                (player_name, base_price, base_price))
        conn.commit()
        conn.close()
        
    def clear_current_player(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM current_player")
        conn.commit()
        conn.close()
    
    

    # Team Management
    
    # Fetch players for a specific team
    def fetch_team_players(self, team: str):
        conn = self.get_db_connection()
        query = "SELECT team, name, player_category, price, status FROM players WHERE team = ?"
        
        # Pass the 'team' parameter as a tuple
        df = pd.read_sql_query(query, conn, params=(team,))
        conn.close()
        return df
    
    # Function to insert data into the database
    def insert_teams(self, df):
        conn = self.get_db_connection()
        c = conn.cursor()

        for _, row in df.iterrows():
            c.execute('''INSERT OR REPLACE INTO teams 
                        (team_name, owner, captain, primary_color, secondary_color) 
                        VALUES (?, ?, ?, ?, ?)''', 
                    (row['team_name'], row['owner'], row['captain'], row['primary_color'], row['secondary_color']))
        conn.commit()
        conn.close()
    
    def add_team(self, team_name: str, owner: str, captain: str):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO teams (team_name, owner, captain) VALUES (?, ?, ?)", (team_name, owner, captain))
        conn.commit()
        conn.close()
        
    def get_teams(self) -> List[Dict]:
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row  # Enables dictionary-like row access
        c = conn.cursor()
        c.execute("SELECT * FROM teams")
        teams = c.fetchall()
        conn.close()
        return [dict(team) for team in teams]  # Convert each row to a dictionary

    def update_team_budget(self, team_name: str, amount: int):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE teams SET budget = budget - ? WHERE team_name = ?", (amount, team_name))
        conn.commit()
        conn.close()

    # Matches & Points Table
    def get_matches(self) -> List[Tuple]:
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM matches")
        matches = c.fetchall()
        conn.close()
        return matches

    def get_point_table(self) -> List[Tuple]:
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM point_table")
        points = c.fetchall()
        conn.close()
        return points

    # Fan Club Management (For future features)
    def add_fan(self, user_id: int, team_name: str):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO fan_club (user_id, team_name) VALUES (?, ?)", (user_id, team_name))
        conn.commit()
        conn.close()

    def get_fans_for_team(self, team_name: str) -> List[Tuple]:
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM fan_club WHERE team_name = ?", (team_name,))
        fans = c.fetchall()
        conn.close()
        return fans
    
    
    
    
    
    
    
    
    ##### FAKE DATA GENERATOR #####
    # Function to insert random users
    def generate_users(self, n):
        conn = self.get_db_connection()
        c = conn.cursor()
        for _ in range(n):
            username = fake.user_name()
            password = fake.password()
            role = random.choice(["owner", "captain", "player"])
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        print(f"✅ {n} users added.")

    def generate_players(self, n, female_count=20):
        conn = self.get_db_connection()
        c = conn.cursor()

        female_added = 0  # Counter for female players

        for _ in range(n):
            email = fake.email()
            name = fake.name()
            available = random.choice(["Yes", "No"])
            work_location = fake.city()
            previously_played = random.choice(["Yes", "No"])
            wish_to_be = random.choice(["Umpire", "Scorer", "Viewer"])
            player_category = random.choice(["Batsman", "Bowler", "All-rounder"])
            rating = str(random.randint(1, 10))

            # Ensure exactly 'female_count' female players
            if female_added < female_count:
                gender = "Female"
                female_added += 1
            else:
                gender = "Male"

            team = None
            price = 0
            status = "available"

            c.execute("""INSERT INTO players (email, name, available, work_location, previously_played,
                        wish_to_be, player_category, rating, gender, team, price, status) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (email, name, available, work_location, previously_played, wish_to_be,
                    player_category, rating, gender, team, price, status))

        conn.commit()
        conn.close()
        print(f"✅ {n} players added ({female_count} Female, {n - female_count} Male).")

    # Function to insert random bids
    def generate_bids(self, n):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM players")
        players = [row[0] for row in c.fetchall()]
        
        c.execute("SELECT username FROM users WHERE role IN ('owner', 'captain')")
        bidders = [row[0] for row in c.fetchall()]

        for _ in range(n):
            if not players or not bidders:
                print("⚠️ Not enough players or bidders to generate bids.")
                return
            player_name = random.choice(players)
            bidder = random.choice(bidders)
            bid_amount = random.randint(50, 500)
            c.execute("INSERT INTO bids (player_name, bidder, bid_amount) VALUES (?, ?, ?)", 
                    (player_name, bidder, bid_amount))
        conn.commit()
        conn.close()
        print(f"✅ {n} bids added.")

    # Function to insert random teams
    def generate_teams(self, n):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role = 'owner'")
        owners = [row[0] for row in c.fetchall()]

        c.execute("SELECT username FROM users WHERE role = 'captain'")
        captains = [row[0] for row in c.fetchall()]

        for _ in range(n):
            if not owners or not captains:
                print("⚠️ Not enough owners or captains to generate teams.")
                return
            team_name = fake.company()
            owner = random.choice(owners)
            captain = random.choice(captains)
            spend = 0
            budget = 1000
            player_count = 2
            female_count = 1 if _ == n-2 else 0
            male_count = 1 if _ == n-2 else 2
            c.execute("""INSERT INTO teams (team_name, owner, captain, spend, budget, 
                        player_count, male_count, female_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (team_name, owner, captain, spend, budget, player_count, male_count, female_count))
        conn.commit()
        conn.close()
        print(f"✅ {n} teams added.")

    # Function to insert random current players for auctions
    def generate_current_player(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name FROM players WHERE status = 'available' ORDER BY RANDOM() LIMIT 1")
        player = c.fetchone()
        
        if player:
            player_id, player_name = player
            base_price = 20
            current_bid = base_price
            bidding_team = None
            c.execute("DELETE FROM current_player")  # Clear previous
            c.execute("""INSERT INTO current_player (player_id, player_name, base_price, current_bid, bidding_team)
                        VALUES (?, ?, ?, ?, ?)""",
                    (player_id, player_name, base_price, current_bid, bidding_team))
            conn.commit()
            print(f"✅ Current player set: {player_name}")
        else:
            print("⚠️ No available players to start auction.")
        conn.close()
