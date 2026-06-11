import streamlit as st
import requests


def render_hearts_section(BASE_URL, post):
    user_id = st.session_state.id  # Assuming the post dictionary contains the owner's user ID
  #  print(f"Current user ID in session: {user_id}")  # Debugging line
    hearts_list = post.get("hearts", [])
    total_hearts = len(hearts_list)

    is_hearted_by_me = any(
        h["user_id"] == user_id for h in hearts_list
    )

    react_col1, _ = st.columns([1, 5])

    with react_col1:

        heart_emoji = "❤️" if is_hearted_by_me else "🤍"

        if st.button(f"{heart_emoji} {total_hearts}", key=f"heart_btn_{post['id']}"):

            if not st.session_state.get("token"):
                st.warning("Please login to react.")
                return

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            try:
                res = requests.post(
                    f"{BASE_URL}/posts/{post['id']}/heart/",
                    headers=headers,
                    timeout=5
                )

                if res.status_code == 200:
                    st.rerun()
                else:
                    st.error("Failed to register reaction.")

            except Exception as e:
                st.error(f"Error: {e}")