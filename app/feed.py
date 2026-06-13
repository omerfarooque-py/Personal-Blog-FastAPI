import streamlit as st
import requests
from datetime import datetime

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str


# 1. Isolate the card component into a fragment wrapper
@st.fragment
def render_post_card(BASE_URL, post, render_hearts_section, render_comments_section):
    
    with st.container(border=True):
        # Username dynamically evaluated
        owner_data = post.get("owner")
        if isinstance(owner_data, dict):
            username = owner_data.get("username", "Unknown")
        elif isinstance(owner_data, list) and len(owner_data) > 0:
            username = owner_data[0].get("username", "Unknown")
        else:
            username = "Unknown"

        # Metadata Layout
        st.subheader(post["title"])
        st.caption(f"👤 {username} · 📅 {format_date(post.get('created_at', ''))}")
        
        if post.get("content"):
            st.write(post["content"])

        # Display images safely using updated width attribute
        for image in post.get("images", []):
            if image.get("image_url"):
                st.markdown(
            f"""
            <div style="
                width: 100%; 
                max-height: 500px; 
                background-color: #111217; 
                border-radius: 12px; 
                overflow: hidden; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                margin-bottom: 12px;
            ">
                <img src="{image['image_url']}" style="
                    max-width: 100%; 
                    max-height: 500px; 
                    object-fit: contain;
                ">
            </div>
            """,
            unsafe_allow_html=True
        )
                """
                col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
                with col2:
                  st.image(image["image_url"], width="stretch")
                  """

        # 👑 Isolated Interactions: Clicking these will ONLY rerun THIS card!
        render_hearts_section(BASE_URL, post)
        
        render_comments_section(
            BASE_URL,
            post_id=post["id"],
            token=st.session_state.get("token"),
            post=post
        )
def render_feed_tab(BASE_URL, render_hearts_section, render_comments_section):
    st.subheader("📜 Recent Updates")

    search_query = st.text_input(
        "🔍 Search Journal Entries",
        placeholder="Search by title or content..."
    )

    # 🔢 Track our current DB skip offset in session state
    if "db_post_offset" not in st.session_state:
        st.session_state.db_post_offset = 0

    # 📦 Keep a running collection of loaded posts across pagination cycles
    if "loaded_posts" not in st.session_state or st.button("🔄 Refresh Feed", key="clear_feed_cache"):
        st.session_state.loaded_posts = []
        st.session_state.db_post_offset = 0

    try:
        search_query = search_query.strip()

        # Handle Search vs Standard Paginated Feed Flow
        if search_query:
            endpoint = f"{BASE_URL}/posts/search/?q={search_query}"
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                posts_to_render = response.json()
                posts_to_render.reverse() # Newest first for search results
            else:
                posts_to_render = []
        else:
            # 🚀 Fetch ONLY the 10 posts we need by passing limit and offset to the backend
            endpoint = f"{BASE_URL}/posts/?limit=10&offset={st.session_state.db_post_offset}"
            response = requests.get(endpoint, timeout=10)

            if response.status_code == 404 and not st.session_state.loaded_posts:
                st.info("📭 No posts yet.")
                return
            
            if response.status_code == 200:
                new_posts = response.json()
                
                # Check if this batch is already added to avoid duplication on re-runs
                current_ids = {p["id"] for p in st.session_state.loaded_posts}
                for post in new_posts:
                    if post["id"] not in current_ids:
                        # Append to the bottom so older items render lower down
                        st.session_state.loaded_posts.append(post)
            
            posts_to_render = st.session_state.loaded_posts

        if not posts_to_render:
            st.info("No matching entries found.")
            return

        # Render out the current compiled view list
        for post in posts_to_render:
            render_post_card(BASE_URL, post, render_hearts_section, render_comments_section)

            # Admin Actions Engine
            if st.session_state.get("token") and st.session_state.get("is_admin"):
                st.write("") 
                _, delete_col = st.columns([4, 1.2])
                with delete_col:
                    if st.button("🗑️ Delete Entry", key=f"delete_{post['id']}", use_container_width=True):
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        delete_response = requests.delete(f"{BASE_URL}/posts/{post['id']}/", headers=headers)
                        if delete_response.status_code == 200:
                            st.success("Post deleted.")
                            # Clear states to force full rebuild on next rerun
                            st.session_state.loaded_posts = []
                            st.session_state.db_post_offset = 0
                            st.rerun()

        # 🔽 "Load More" hits the backend to skip what we already have
        if not search_query and response.status_code == 200 and len(new_posts) == 10:
            st.write("") 
            _, center_col, _ = st.columns([1.5, 2, 1.5])
            with center_col:
                if st.button("🔽 Load Older Entries", use_container_width=True):
                    # Increment the offset by 10 to tell FastAPI: "Skip the ones we are looking at!"
                    st.session_state.db_post_offset += 10
                    st.rerun()

    except requests.exceptions.ConnectionError:
        st.error("Backend server is offline. Verify FastAPI/Uvicorn is running.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")