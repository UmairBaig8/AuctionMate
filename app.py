import streamlit as st
from streamlit_extras.app_logo import add_logo

from common.utils import apply_global_styles
from db.db_helper import DBHelper

st.set_page_config(page_title="Live Dashboard", page_icon="⚡", layout="wide")

# Dummy user database with roles
USER_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {{
            display: none;
        }}
    [data-testid="stAppViewContainer"] {
        #background-color: #2C3E50;
        background-image: url("https://images.unsplash.com/photo-1631194758628-71ec7c35137e?q=80&w=3432&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def login():

    # Login Page
    st.title("DPL Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USER_CREDENTIALS[username]["role"]
            st.success(f"Welcome, {username}!")
            
            apply_global_styles()
            # 🚀 Switch to Live page after successful login
            st.switch_page("pages/Live.py")
        else:
            st.error("Invalid username or password")

def main():
    db = DBHelper()
    db.init_db() 
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""
    if "role" not in st.session_state:
        st.session_state["role"] = ""
        
    #st.switch_page("app.py")
        
    login()

    
if __name__ == "__main__":
    main()
