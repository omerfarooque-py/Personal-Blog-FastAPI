import streamlit as st
import requests

def render_hearts_section(post):

    hearts_list = post.get("hearts", [])
    total_hearts = len(hearts_list)

    # Check if logged-in user's ID is in the hearts array to color the button
    # For a quick shortcut, we can use a session tracker or let FastAPI return it
    is_hearted_by_me = False 
    # If your backend user profile metadata object is in state, you can check user id matches

    # Create a clean row with columns for the reaction UI
    react_col1, react_col2 = st.columns([1, 5])

    with react_col1:
        # Toggle display based on state
        heart_emoji = "❤️" if is_hearted_by_me else "🤍"
        
        if st.button(f"{heart_emoji} {total_hearts}", key=f"heart_btn_{post['id']}"):
            if not st.session_state.token:
                st.warning("Please login to react.")
            else:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                try:
                    res = requests.post(f"{BASE_URL}/posts/{post['id']}/heart/", headers=headers)
                    if res.status_code == 200:
                        st.rerun() # Refresh to update the count instantly
                    else:
                        st.error("Failed to register reaction.")
                except Exception as e:
                    st.error(f"Error: {e}")