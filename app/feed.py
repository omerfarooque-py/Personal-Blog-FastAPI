import streamlit as st
import requests
from datetime import datetime

def render_feed_tab(BASE_URL, render_hearts_section, render_comments_section):
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
                            meta_response = requests.get(f"{BASE_URL}/posts/{owner_id}/users/")
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
                    
                    # Comment rendering section under the text content
                    render_comments_section(post_id=post["id"], token=st.session_state.token)
                    
                    # Action Row: Delete option
                    if st.session_state.get("token") and st.session_state.is_admin:
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