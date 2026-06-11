
import streamlit as st


def render_about_tab():
    st.header("Meet the Engineer")
    st.markdown("---")
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image("https://avatars.githubusercontent.com/u/220927412?v=4", caption="Umer Farooque")
        st.markdown("🔗 **Profiles:** [GitHub](https://github.com/omerfarooque-py) | [LinkedIn](https://www.linkedin.com/in/omer-farooque-b04825346/)")
    with col_txt:
       st.markdown("""
        ### Umer Farooque
        **Backend Developer | Aspiring AI Engineer**

        I enjoy building backend systems with Python, FastAPI, and PostgreSQL, focusing on clean APIs, authentication, database design, and scalable application architecture.

        #### 🛠️ Technical Stack
        * **Backend:** Python, FastAPI, SQLAlchemy
        * **Databases:** PostgreSQL, Alembic
        * **Deployment:** Railway
        * **Currently Learning:** LLM Applications, RAG, MCP, Vector Databases
        """)