import streamlit as st
import requests


def render_comments_section(BASE_URL, post_id, token=None):
    st.markdown("---")
    
    # 🔢 Initialize a dynamic comment limit tracker in session state if not present
    state_key = f"comment_limit_{post_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 10  # Start with a base of 10

    # 📥 1. FETCH COMMENTS WITH DYNAMIC LIMIT
    comments = []
    current_limit = st.session_state[state_key]
    try:
        # Pass the current limit counter straight to your FastAPI parameter hook
        response = requests.get(f"{BASE_URL}/posts/{post_id}/comments/?limit={current_limit}")
        if response.status_code == 200:
            comments = response.json()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return

    expander_label = f"💬 Comments ({len(comments)})"

    # 📦 2. THE EXPANDER WINDOW
    with st.expander(expander_label, expanded=False):
        
        # DISPLAY COMMENTS
        if not comments:
            st.info("No comments yet. Be the first to share your thoughts!")
        else:
            user_cache = {}
            for comment in comments:
                owner_id = comment.get('owner_id')
                username = "Unknown"
                
                if owner_id:
                    if owner_id in user_cache:
                        username = user_cache[owner_id]
                    else:
                        try:
                            meta_response = requests.get(f"{BASE_URL}/posts/{owner_id}/users/") 
                            if meta_response.status_code == 200:
                                username = meta_response.json().get('username', 'Unknown')
                                user_cache[owner_id] = username 
                        except:
                            pass

                with st.container():
                    st.markdown(f"**👤 {username}**")
                    st.text(comment['content'])
                    if 'created_at' in comment:
                        formatted_time = comment['created_at'].split("T")[0]
                        st.caption(f"Posted on {formatted_time}")
                    st.markdown("---")

            # 🔄 "LOAD MORE" BUTTON INTERFACE LAYER
            # Show the button only if we fetched as many comments as we requested 
            # (which implies there might be more remaining in the database)
            if len(comments) >= current_limit:
                if st.button("🔽 Load 5 More Comments", key=f"load_more_{post_id}"):
                    st.session_state[state_key] += 5
                    st.rerun()

        # 📤 3. ADD NEW COMMENT BOX
        if token:
            st.write("#### Leave a Comment")
            with st.form(key=f"comment_form_{post_id}", clear_on_submit=True):
                comment_text = st.text_area("Write your thought here...", max_chars=500)
                submit_button = st.form_submit_button(label="Post Comment")

                if submit_button:
                    if comment_text.strip() == "":
                        st.warning("Comment cannot be completely empty!")
                    else:
                        headers = {"Authorization": f"Bearer {token}"}
                        payload = {"content": comment_text}

                        with st.spinner("Submitting..."):
                            res = requests.post(
                                f"{BASE_URL}/posts/{post_id}/comments/",
                                json=payload,
                                headers=headers
                            )
                            if res.status_code == 201:
                                st.success("Comment posted successfully!")
                                # Reset back to 10 on new post so they see their new comment at the top
                                st.session_state[state_key] = 10 
                                st.rerun()
                            else:
                                st.error(f"Failed: {res.status_code}")
        else:
            st.warning("🔒 Please login to post a comment on this article.")