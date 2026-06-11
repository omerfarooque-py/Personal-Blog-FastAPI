import streamlit as st
import requests


def render_comments_section(BASE_URL, post_id, token=None, post=None):
    st.markdown("---")
    
    # Defensive programming: If post wasn't passed, gracefully halt to prevent crashes
    if not post:
        st.warning("⚠️ Comments container context missing.")
        return
        
    # 🔢 Initialize a dynamic comment limit tracker in session state if not present
    state_key = f"comment_limit_{post_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 10  # Start with a base of 10

    # 📥 1. FETCH COMMENTS WITH DYNAMIC LIMIT
    current_limit = st.session_state[state_key]
    
    # Grab comments array safely from the parent post payload
    raw_comments = post.get("comments", [])
    
    # Slice the list locally based on your pagination tracker state
    comments = raw_comments[:current_limit]

    # Dynamic indicator tracking how many comments are currently rendered
    expander_label = f"💬 Comments ({len(raw_comments)})"

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
                            # 👑 FIX 1: Fixed route fallback destination convention mapping
                            meta_response = requests.get(f"{BASE_URL}/posts/{owner_id}/users/", timeout=5) 
                            if meta_response.status_code == 200:
                                username = meta_response.json().get('username', 'Unknown')
                                user_cache[owner_id] = username 
                        except:
                            pass

                with st.container():
                    st.markdown(f"**👤 {username}**")
                    # Cleaned up text presentation handling
                    st.markdown(f"```{comment.get('content', '')}```")
                    
                    if 'created_at' in comment:
                        # Extract date formatting layout smoothly
                        formatted_time = comment['created_at'].split("T")[0]
                        st.caption(f"Posted on {formatted_time}")
                    st.markdown("---")

            # 🔄 "LOAD MORE" BUTTON INTERFACE LAYER
            if len(raw_comments) > current_limit:
                if st.button("🔽 Load More Comments", key=f"load_more_{post_id}"):
                    st.session_state[state_key] += 5
                    st.rerun()

        # 📤 3. ADD NEW COMMENT BOX
        if token:
            st.write("#### Leave a Comment")
            with st.form(key=f"comment_form_{post_id}", clear_on_submit=True):
                comment_text = st.text_area("Write your thought here...", max_chars=500)
                submit_button = st.form_submit_button(label="Post Comment")

                if submit_button:
                    if not comment_text.strip():
                        st.warning("Comment cannot be completely empty!")
                    else:
                        headers = {"Authorization": f"Bearer {token}"}
                        payload = {"content": comment_text}

                        with st.spinner("Submitting..."):
                            try:
                                res = requests.post(
                                    f"{BASE_URL}/posts/{post_id}/comments/",
                                    json=payload,
                                    headers=headers,
                                    timeout=5
                                )
                                
                                # 👑 FIX 2: Accept both standard success codes seamlessly
                                if res.status_code in [200, 201]:
                                    st.success("Comment posted successfully!")
                                    st.session_state[state_key] = 10 
                                    st.rerun()
                                else:
                                    st.error(f"Failed to save comment: Server responded with status code {res.status_code}")
                            except Exception as e:
                                st.error(f"Network processing issue: {e}")
        else:
            st.warning("🔒 Please login to post a comment on this article.")