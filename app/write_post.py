import streamlit as st
import requests

def render_write_tab(BASE_URL):
    st.header("Create a New Update")
    if not st.session_state.token:
        st.warning("🔒 This section is locked.")
        st.info("💡 **Mobile User Notice:** Click on the top-left sidebar arrow (`>`) to log in or register your account.")
    elif not st.session_state.is_admin:
        st.warning("⚠️ Access Denied.")
        st.error("Only workspace administrators can write entries. Your account does not have sufficient privileges.")
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
