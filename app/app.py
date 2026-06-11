import streamlit as st
import requests
from comments import render_comments_section
from datetime import datetime
from hearts import render_hearts_section

# FastAPI Backend Base URL
BASE_URL = "https://lavish-solace-production-099a.up.railway.app"

st.set_page_config(page_title="Personal daily life blog", page_icon="🚀", layout="centered")
st.title("💾 Personal Dev Journal")

# --- INITIALIZE SESSION STATE FOR AUTH ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False  # 👑 Initialized fallback state flag

# --- SIDEBAR: PROJECT INFO ---
with st.sidebar:
    st.divider()
    st.markdown("### 🛠️ Project Info")
    st.caption("An Intelligent Journal & Newsletter Aggregator built with FastAPI, PostgreSQL, and Streamlit.")
    
    with st.container(border=True):
        st.markdown(
            """
            **Developed by:**
            🚀 [Omer farooque](https://github.com/omerfarooque-py)
            
            **Stack:**
            * Python 3.12 / FastAPI
            * SQLAlchemy / Alembic
            * Streamlit Frontend
            * ImageKit Optimization
            """
        )
    st.caption("© 2026 All Rights Reserved.")

# --- SIDEBAR: AUTHENTICATION FLOW ---# --- SIDEBAR: AUTHENTICATION FLOW ---
with st.sidebar:
    if st.session_state.token:
        # Dynamically display the correct label based on their table attributes
        role_label = "👑 Admin" if st.session_state.is_admin else "👤 Standard User"
        st.success(f"Logged in as: **{st.session_state.username}**\n\nRole: `{role_label}`")
        
        if st.button("Log Out"):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()
    else:
        # 🟢 Cleaned up action choices: admin login option is no longer needed here!
        auth_mode = st.radio("Choose Action", ["Login", "Register"], index=0)
        st.subheader(f"{auth_mode} Account")
        username_input = st.text_input("Username", key="auth_user")
        password_input = st.text_input("Password", type="password", key="auth_pass")
        
        if st.button(auth_mode):
            if not username_input or not password_input:
                st.error("Please fill in all fields.")
            else:
                form_data = {"username": username_input, "password": password_input}
                
                if auth_mode == "Register":
                    response = requests.post(
                        f"{BASE_URL}/register/",
                        json={"username": username_input, "password": password_input}
                    )
                    if response.status_code == 200:
                        st.success("Account created! Please switch to Login.")
                    else:
                        detail = response.json().get("detail", "Registration failed")
                        st.error(f"Error: {detail}")
                        
                elif auth_mode == "Login":
                    response = requests.post(f"{BASE_URL}/login/", data=form_data)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # 🟢 Capture both the token and the database role flag instantly!
                        st.session_state.token = data["access_token"]
                        st.session_state.username = username_input
                        st.session_state.is_admin = data.get("is_admin", False) 
                        
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")


# --- 4-TAB NAVIGATION BAR (Solves Mobile Sidebar Invisibility) ---
from feed import render_feed_tab
from write_post import render_write_tab
from guide import render_guide_tab
from about import render_about_tab

tab_feed, tab_write, tab_guide, tab_about = st.tabs([
    "📜 Feed", 
    "✍️ Write Post", 
    "🛠️ How to Use & System Logs",
    "👤 Meet the Engineer"
])

with tab_feed:
    render_feed_tab(BASE_URL, render_hearts_section, render_comments_section)


with tab_write:
    render_write_tab(BASE_URL)


with tab_guide: 
    render_guide_tab()

with tab_about: 
    render_about_tab()