
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
        **AI Systems & Backend Engineer**
        
        I focus on creating high-performance, secure backend services and private AI systems that extract structured insights from complex datasets.
        
        #### 🛠️ Technical Stack
        * **Backend Frameworks:** Python, FastAPI, SQLAlchemy
        * **Database Version Control:** PostgreSQL, Alembic
        * **Cloud Infrastructure:** Railway Engine Deployments
        * **Intelligent Agents Focus:** Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), FAISS Vector Storages
        """)