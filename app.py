import streamlit as st
import requests

# FastAPI Backend Base URL
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Personal Tech Blog", page_icon="🚀", layout="centered")
st.title("💾 Personal Dev Journal")

# --- INITIALIZE SESSION STATE FOR AUTH ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- SIDEBAR: AUTHENTICATION FLOW ---
with st.sidebar:
    if st.session_state.token:
        st.success(f"Logged in as: **{st.session_state.username}**")
        if st.button("Log Out"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
    else:
        auth_mode = st.radio("Choose Action", ["Login", "Register"])
        
        st.subheader(f"{auth_mode} Account")
        username_input = st.text_input("Username", key="auth_user")
        password_input = st.text_input("Password", type="password", key="auth_pass")
        
        if st.button(auth_mode):
            if not username_input or not password_input:
                st.error("Please fill in all fields.")
            else:
                if auth_mode == "Register":
                    # Call FastAPI POST /register/
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
                    # Call FastAPI POST /login/ (Form Data compliant)
                    form_data = {"username": username_input, "password": password_input}
                    response = requests.post(f"{BASE_URL}/login/", data=form_data)
                    
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
# TAB 1: PUBLIC FEED
with tab1:
    st.header("Recent Updates")
    
    # 🔍 Dynamic Search Bar Widget
    search_query = st.text_input("🔍 Search journal entries...", placeholder="Type keywords here...")
    
    try:
        # Route logic based on query input
        if search_query:
            response = requests.get(f"{BASE_URL}/posts/search/?q={search_query}")
        else:
            response = requests.get(f"{BASE_URL}/posts/")
            
        if response.status_code == 200:
            posts = response.json()
            
            if not posts:
                st.info("No matching entries found.")
                
            for post in reversed(posts):
                st.subheader(post["title"])
                st.caption(f"Slug: `{post['slug']}` | Owner ID: {post.get('owner_id', 'Unknown')}")
                
                # 💡 FIXED: Look for 'images' array payload directly instead of image_url
                # Inside your Tab 1 layout container in app.py:
                if "images" in post and post["images"]:
                    for img in post["images"]:
                        image_link = img.get("image_url")
                        if image_link:
                            # 💡 FIX: Set a maximum width instead of expanding to fill the page
                            st.image(image_link, width=300)
                        else:
                            st.error("Error while retrieving individual image asset.")
                
                st.write(post["content"])
                
                # 🗑️ SHOW DELETE BUTTON ONLY IF AUTHENTICATED
                if st.session_state.get("token"):
                    if st.button(f"🗑️ Delete Post", key=f"del_{post['id']}"):
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        # 💡 Ensure the trailing slash matches your FastAPI configuration rule
                        del_response = requests.delete(f"{BASE_URL}/posts/{post['id']}", headers=headers)
                        
                        if del_response.status_code == 200:
                            st.success("Post removed successfully!")
                            st.rerun()
                        else:
                            st.error("Error: Could not delete this entry.")
                            
                st.write("---")
                
        elif response.status_code == 404:
            st.info("Your journal feed is currently empty.")
        else:
            st.error("Could not load posts from backend.")
            
    except requests.exceptions.ConnectionError:
        st.error("Backend server is offline. Make sure Uvicorn is running on port 8000!")

# TAB 2: PRIVATE WRITING DASHBOARD (Requires Auth)
with tab2:
    st.header("Create a New Update")
    
    if not st.session_state.token:
        st.warning("🔒 Please log in from the sidebar to publish updates.")
    else:
        with st.form("post_form", clear_on_submit=True):
            title = st.text_input("Title", placeholder="e.g., Beautiful view of the sunset!")
            content = st.text_area("Content", placeholder="What's the story behind this photo?")
            
            # 🖼️ Added Image Uploader Widget
            uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
            
            submitted = st.form_submit_button("Publish Entry")
            
            if submitted:
                if not title or not content:
                    st.error("Both title and content are required.")
                else:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    
                    # Package text fields as standard Form Data
                    form_data = {
                        "title": title,
                        "content": content
                    }
                    
                    # Package file binary data if user selected an image
                    files = None
                    if uploaded_file is not None:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    
                    # Send multi-part request to your /upload/ endpoint
                    with st.spinner("Uploading media to ImageKit and saving to database..."):
                        post_response = requests.post(
                            f"{BASE_URL}/upload/", 
                            data=form_data,   # Passed as standard form data parameters
                            files=files,      # Handed off as file attachments
                            headers=headers
                        )
                    
                    if post_response.status_code == 200:
                        st.success("🎉 Post and image successfully committed!")
                        st.rerun()
                    else:
                        st.error(f"Failed to post: {post_response.text}")