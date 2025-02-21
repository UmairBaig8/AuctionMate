import bcrypt
import pandas as pd
import sqlite3

import streamlit as st

import base64

from db.db_helper import DBHelper

def get_to_base64(svg_path, type:str):
    with open(svg_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return f"data:image/{type};base64,{encoded}"

def apply_global_styles():
    """Applies custom global styles to all pages."""
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.switch_page("app.py")
    
    
    css = f"""
    <style>
        [data-testid="stHeader"]{{
            #background-image: url({get_to_base64('./static/wallpaper.png','png')});
            #background-repeat: no-repeat;
            #height: 190px;
            #background-size: cover;
            #background-position: top;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            display: block;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px; /* Adjust the height as needed */
            #background-color: #2C3E50;
            background-image: url({get_to_base64('./static/wallpaper.png','png')});
            background-size: cover;
            #background-position: center;
            #background-repeat: no-repeat;
            z-index: 9999;
        }}
        [data-testid="stSidebarNav"] {{ display: none; }}  /* Hide Sidebar Navigation */
        [data-testid="stSidebar"] {{
            min-width: 180px;
            max-width: 200px;
        }}
        
        [data-testid="stHeaderActionElements"] {{
            display: none;
        }}
        
        [data-testid="stMainBlockContainer"]{{
            #padding-left: .1rem;
            #padding-right: .5rem;
        }}
        
        # [data-testid="stMetricLabel"] {{
        #     color: #2C39CA;
        #     font-size: 18px;
        # }}
        # [data-testid="stMetricValue"] {{
        #     color: #F25697;
        #     font-size: 42px;
        # }}
        
        # [data-testid="stMetric"]{{
        #     border-radius: 15px;
        #     padding: 20px;
        #     margin: 10px;
        #     background: #FFFFFF;
        #     width: 200px;
        #     box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
        #     transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        # }}
        # [data-testid="stMetric"]:hover {{
        #     transform: scale(1.05); /* Increase size slightly */
        #     box-shadow: 4px 4px 15px rgba(0, 0, 0, 0.3); /* Enhanced shadow */
        # }}
        
        [data-testid="stVerticalBlockBorderWrapper"]{{
            padding: 0px;
        }}
        
        .card {{
            position: relative;
            #background: linear-gradient(to bottom, #F25697 50%, white 50%);
            background: #FFFFFF;
            border-radius: 15px;
            text-align: center;
            
        }}

        .card img {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-top: 10px;
            transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        }}
        .card img:hover {{
            transform: scale(1.1); /* Increase size slightly */
        }}

        .card h3, .card p {{
            margin: 5px 0;
            color: black;
        }}
        .card .team-info {{
            margin-top: 10px;
        }}
        .card .team-info p {{
            margin: 5px 0;
        }}
        
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
            .responsive-table {
            li {
                border-radius: 3px;
                padding: 15px 30px;
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }
            .table-header {
                
                background-color: #F25697;
                text-transform: uppercase;
                letter-spacing: 0.03em;
                font: normal normal 800 24px/26px sans serif;
            }
            .table-row {
                background-color: #2C39CA;
                font: normal normal 800 24px/26px sans serif;
                border-bottom: 1px solid #ddd;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
            }
            .col-1 {
                flex-basis: 35%;
            }
            .col-2 {
                flex-basis: 20%;
            }
            .col-3 {
                flex-basis: 15%;
                text-align:center;
            }
            .col-4 {
                flex-basis: 15%;
                text-align:center;
            }
            .col-5 {
                flex-basis: 15%;
                text-align:center;
            }
            
            @media all and (max-width: 767px) {
                .table-header {
                    display: none;
                }
                .table-row{
                }
                li {
                    display: block;
                }
                .col {
                    flex-basis: 100%;
                }
                .col {
                    display: flex;
                    padding: 10px 0;
                    &:before {
                        color: #2C39CA;
                        padding-right: 10px;
                        content: attr(data-label);
                        flex-basis: 50%;
                        text-align: right;
                    }
                }
            }
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.logo("./static/Group 40174.png")
    st.sidebar.image("./static/Group 40174@2x.png")

    if st.session_state["authenticated"]:    
        st.sidebar.divider()

    db = DBHelper()

    # 🚀 Streamlit Sidebar Rendering
    menu_items = db.get_menu_items()
    
    if st.session_state["authenticated"] and len(menu_items) < 4:
        db.generate_menu_items()
        menu_items = db.get_menu_items()
        
    # Role-based Menu Filtering
    if st.session_state["role"] == "admin":
        filtered_menu = menu_items  # Admin gets all pages
    else:
        # Guests get only Live, Teams, and Players
        # Filter for guest users (only Live, Teams, and Player)
        filtered_menu = [item for item in menu_items if item["label"] in ["Live", "Teams", "Player"]]

    if st.session_state["authenticated"]:
        for item in filtered_menu:
            col1, col2 = st.sidebar.columns([1, 4])
            col1.image(item["icon"], use_container_width=True)
            col2.page_link(item["page"], label=item["label"])
    
        st.sidebar.divider()
    
    
        if st.sidebar.button(label="Logout", key="logout",type="tertiary"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = ""
            st.switch_page("app.py")
