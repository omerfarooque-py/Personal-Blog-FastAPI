import streamlit as st

def render_guide_tab():
    st.header("📱 App Navigation Guide")
    
    # Simple explicit help message for mobile viewports
    with st.expander("👉 Where is the Login / Registration menu?", expanded=True):
        st.markdown("""
        If you are on a **mobile phone or small tablet**, the authentication menu is tucked away into the sidebar:
        1. Look at the **very top left corner** of your screen.
        2. Tap the small arrow icon (**`>`**) to slide out the access panel.
        3. There you can create an account, log in, or toggle your application sessions securely!
        """)
    
    st.markdown("---")
    st.header("🛠️ Engineering Milestone Tracker")
    
    # Structured historical changelog detailing the exact sprint steps
    st.subheader("Version 2.0.0 — Relational Architecture & Control Layer")
    st.caption("Current Stable Build")
    st.markdown("""
    * **June 11, 2026** — Integrated **Alembic Database Migrations** for production-safe cloud schemas on Railway. Added `ON DELETE CASCADE` constraints across tables.
    * **June 10, 2026** — Added interactive, nested asynchronous **Comment Expanders** and implemented **Heart Reactions** tracking unique state constraints per user.
    * **June 09, 2026** — Rolled out public and authenticated comments storage logic linking actions directly to unique user relational profiles.
    * **June 08, 2026** — Refined UI layout with card-based modular layout dividers and real-time custom timezone string timestamp parsers.
    * **June 07, 2026** — Integrated multi-part asset handling allowing live **Image Upload pipelines** bound directly to third-party CDNs (ImageKit).
    * **June 06, 2026** — Created base FastAPI posts generation endpoints with slug configuration parsers.
    """)

