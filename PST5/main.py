# main.py
import streamlit as st
from gui.main_dashboard import launch
from app.admin_utils import init_logger, backup_data

if __name__ == "__main__":
    # Streamlit re-runs this script on every click, so only do the start-up work
    # once per browser session - otherwise every click would create a new backup.
    if "startup_done" not in st.session_state:
        # Initialize the logger as the very first step.
        init_logger()

        # Perform a data backup before starting the application session.
        backup_data()

        st.session_state.startup_done = True

    # Launch the GUI as before.
    launch()
