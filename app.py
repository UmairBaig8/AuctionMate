import streamlit as st
from streamlit_extras.app_logo import add_logo

from common.utils import apply_global_styles
from db.db_helper import DBHelper

st.set_page_config(page_title="Live Dashboard", page_icon="⚡", layout="wide")

#Load credentials from secrets
USER_CREDENTIALS = st.secrets["USER_CREDENTIALS"]
# Dummy user database with roles
#USER_CREDENTIALS = {
#    "admin": {"password": "admin123", "role": "admin"},
#    "user1": {"password": "user123", "role": "user"},
#}
st.markdown(
    """
    <style>
    #GithubIcon { visibility: hiddeGithubIconn;}


    [data-testid="stSidebarNav"] {{ display: none; }}  /* Hide Sidebar Navigation */
        [data-testid="stSidebar"] {{
            min-width: 10px;
            max-width: 20x;
        }}
        [data-testid="stSidebar"] {{
                display: none;
            }}
        [data-testid="stAppViewContainer"] {
            #background-color: #2C3E50;
            background-image: url("https://images.unsplash.com/photo-1631194758628-71ec7c35137e?q=80&w=3432&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
        }        
        .stButton>button {
            width: 100%;
        }
        .login-container {
            width: 450px;
            height: 400px;
            margin: auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: #f9f9f9;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .guest-button {
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def login():
    
    # Centered layout
    #st.markdown('<div class="login-container">', unsafe_allow_html=True)

    # Guest Button (Above Login)
    if st.button("🎟️ Continue as Guest", key="guest", use_container_width=True):
        st.session_state["authenticated"] = True
        st.session_state["username"] = "Guest"
        st.session_state["role"] = "guest"
        apply_global_styles()
        st.switch_page("pages/Live.py")

    # Login Form
    st.title("DPL Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("🔒 Login", use_container_width=True):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USER_CREDENTIALS[username]["role"]
            st.success(f"Welcome, {username}!")
            apply_global_styles()
            st.switch_page("pages/Live.py")
        else:
            st.error("Invalid username or password")

    # Close container div
    #st.markdown('</div>', unsafe_allow_html=True)

    # # Login Page
    # st.title("DPL Login")
    # username = st.text_input("Username")
    # password = st.text_input("Password", type="password")
    # login_button = st.button("Login")

    # if login_button:
    #     if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
    #         st.session_state["authenticated"] = True
    #         st.session_state["username"] = username
    #         st.session_state["role"] = USER_CREDENTIALS[username]["role"]
    #         st.success(f"Welcome, {username}!")
            
    #         apply_global_styles()
    #         # 🚀 Switch to Live page after successful login
    #         st.switch_page("pages/Live.py")
    #     else:
    #         st.error("Invalid username or password")

def main():
    db = DBHelper()
    db.init_db() 
    apply_global_styles()
    
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


