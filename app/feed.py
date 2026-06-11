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
                st.image(f"{image['image_url']}?tr=w-900,h-506,fo-auto", width="stretch")

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

    try:
        search_query = search_query.strip()

        endpoint = (
            f"{BASE_URL}/posts/search/?q={search_query}"
            if search_query
            else f"{BASE_URL}/posts/"
        )

        response = requests.get(endpoint, timeout=10)

        if response.status_code == 404:
            st.info("📭 No posts yet.")
            return

        if response.status_code != 200:
            st.error("Unable to load feed.")
            return

        posts = response.json()
        if not posts:
            st.info("No matching entries found.")
            return

        # Newest entries at the top
        posts.reverse()

        # Render Feed
        for post in posts:
            render_post_card(BASE_URL, post, render_hearts_section, render_comments_section)

            # Admin Actions Engine
            if st.session_state.get("token") and st.session_state.get("is_admin"):
                st.write("") # Micro margin spacing
                
                # Align the delete button neatly to the right edge
                _, delete_col = st.columns([4, 1.2])
                with delete_col:
                    if st.button(
                        "🗑️ Delete Entry",
                        key=f"delete_{post['id']}",
                        use_container_width=True
                    ):
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        delete_response = requests.delete(
                            f"{BASE_URL}/posts/{post['id']}/",
                            headers=headers
                        )

                        if delete_response.status_code == 200:
                            st.success("Post deleted.")
                            st.rerun()
                        else:
                            st.error("Delete failed.")

    except requests.exceptions.ConnectionError:
        st.error("Backend server is offline. Verify FastAPI/Uvicorn is running.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")