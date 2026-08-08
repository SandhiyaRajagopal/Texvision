import streamlit as st
from database.session import init_db
from dashboard import home, inspection, history, analytics, settings
import utils.logger as log_utils

logger = log_utils.setup_logger("app")

st.set_page_config(
    page_title="Fabric Defect Inspection",
    layout="wide",
    page_icon="🏭"
)

def main():
    try:
        init_db()
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        st.error("System Initialization Failed. Check logs.")
        
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Inspection", "History", "Analytics", "Settings"])
    
    if page == "Home":
        home.render()
    elif page == "Inspection":
        inspection.render()
    elif page == "History":
        history.render()
    elif page == "Analytics":
        analytics.render()
    elif page == "Settings":
        settings.render()

if __name__ == "__main__":
    main()
