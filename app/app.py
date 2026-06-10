import streamlit as st
import requests
from comments import render_comments_section
from datetime import datetime
from hearts import render_hearts_section

# FastAPI Backend Base URL
BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Personal daily life blog", page_icon="🚀", layout="centered")
st.title("💾 Personal Dev Journal")

# --- INITIALIZE SESSION STATE FOR AUTH ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

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

# --- SIDEBAR: AUTHENTICATION FLOW ---
with st.sidebar:
    if st.session_state.token:
        st.success(f"Logged in as: **{st.session_state.username}**")
        if st.button("Log Out"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
    else:
        auth_mode = st.radio("Choose Action", ["Login", "Register", "admin login"], index=0)
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
                    # ✅ FIXED: Process response and store session state data for standard users
                    response = requests.post(f"{BASE_URL}/login/", data=form_data)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.username = username_input
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                
                elif auth_mode == "admin login":
                    response = requests.post(f"{BASE_URL}/admin/login/", data=form_data)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.username = username_input
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

# --- MAIN CONTENT AREA ---
tab1, tab2 = st.tabs(["📜 Feed", "✍️ Write Post"])

# TAB 1: PUBLIC FEED
with tab1:
    st.header("Recent Updates")
    search_query = st.text_input("🔍 Search journal entries...", placeholder="Search by title or content keywords...")
    
    try:
        if search_query:
            response = requests.get(f"{BASE_URL}/posts/search/?q={search_query}")
        else:
            response = requests.get(f"{BASE_URL}/posts/")
            
        if response.status_code == 200:
            posts = response.json()
            
            if not posts:
                st.info("No matching entries found for your search criteria.")
                
            for post in reversed(posts):
                with st.container(border=True):
                    # Parse timestamp
                    raw_date = post.get("created_at")
                    standard_date = "N/A"
                    if raw_date:
                        try:
                            clean_date_obj = datetime.fromisoformat(raw_date.split(".")[0])
                            standard_date = clean_date_obj.strftime("%B %d, %Y - %I:%M %p")
                        except Exception:
                            pass

                    # Header Row Layout
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(post["title"])
                        
                    owner_id = post.get('owner_id')
                    username = "Unknown"
                    if owner_id:
                        try:
                            meta_response = requests.get(f"{BASE_URL}/users/{owner_id}")
                            if meta_response.status_code == 200:
                                username = meta_response.json().get('username', 'Unknown')
                        except Exception:
                            pass
                            
                    with col2:
                        st.caption(f"👤: {username}")
                        st.caption(f"📅: {standard_date}")
                    
                    st.caption(f"🔗 Slug: `{post['slug']}`")
                    
                    # Image rendering loop
                    if "images" in post and post["images"]:
                        for img in post["images"]:
                            image_link = img.get("image_url")
                            if image_link:
                                optimized_link = f"{image_link}?tr=w-500,c-at_max"
                                st.image(optimized_link, use_container_width=True)
                    
                    # Display the text core entry body content
                    st.write(post["content"])
                    render_hearts_section(post)
                    
                    # ✅ FIXED: Moved comment rendering section completely clear of the image loop
                    # It now displays perfectly under the text content for ALL posts.
                    render_comments_section(post_id=post["id"], token=st.session_state.token)
                    
                    # Action Row: Delete option
                    if st.session_state.get("token") and st.session_state.username == "admin":
                        st.write("") 
                        del_col1, del_col2 = st.columns([5, 1])
                        with del_col2:
                            if st.button("🗑️ Delete", key=f"del_{post['id']}", use_container_width=True):
                                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                del_response = requests.delete(f"{BASE_URL}/posts/{post['id']}/", headers=headers)
                                if del_response.status_code == 200:
                                    st.success("Post removed!")
                                    st.rerun()
                                else:
                                    st.error("Action denied.")
                                    
        elif response.status_code == 404:
            st.info("Your journal feed is currently empty.")
        else:
            st.error("Could not load posts from the backend server.")
            
    except requests.exceptions.ConnectionError:
        st.error("Backend server is offline. Verify Uvicorn is executing on port 8000!")

# TAB 2: PRIVATE WRITING DASHBOARD (Requires Auth)
with tab2:
    st.header("Create a New Update")
    if not st.session_state.token:
        st.warning("🔒 Please log in from the sidebar to publish updates.")
    elif st.session_state.username != "admin":
        st.warning("⚠️ Only admin users can create posts. Please log in with an admin account.")
    else:
        with st.form("post_form", clear_on_submit=True):
            title = st.text_input("Title", placeholder="e.g., Beautiful view of the sunset!")
            content = st.text_area("Content", placeholder="What's the story behind this photo?")
            uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("Publish Entry")
            
            if submitted:
                if not title or not content:
                    st.error("Both title and content are required.")
                else:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    form_data = {"title": title, "content": content}
                    files = None
                    if uploaded_file is not None:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    
                    with st.spinner("Uploading media to ImageKit and saving to database..."):
                        post_response = requests.post(
                            f"{BASE_URL}/upload/", 
                            data=form_data,   
                            files=files,      
                            headers=headers
                        )
                    
                    if post_response.status_code == 200:
                        st.success("🎉 Post and image successfully committed!")
                        st.rerun()
                    else:
                        st.error(f"Failed to post: {post_response.text}")