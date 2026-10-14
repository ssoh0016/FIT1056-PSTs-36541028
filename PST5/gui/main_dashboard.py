# gui/main_dashboard.py
import streamlit as st
from app.admin_utils import backup_data
from app.schedule import ScheduleManager
from gui.student_pages import show_student_management_page
from gui.roster_pages import show_roster_page
from gui.course_pages import show_course_management_page
from gui.teacher_pages import show_teacher_management_page
from gui.finance_pages import show_finance_page

def launch():
    """Sets up the main Streamlit application window and navigation."""
    st.set_page_config(layout="wide", page_title="Music School Management System")

    # Instantiate the "brain" of our app ONCE and store it in the session state.
    # This is crucial so the manager object persists as we switch pages.
    if 'manager' not in st.session_state:
        st.session_state.manager = ScheduleManager()
    manager = st.session_state.manager

    if manager.load_error:
        st.error("The data file could not be read, so the app started with empty data. "
                 "A copy of the damaged file was kept next to it (*.corrupt_*), and "
                 "earlier backups are in data/backups.")

    st.sidebar.title("MSMS Navigation")
    # Create a radio button menu in the sidebar for page navigation.
    page = st.sidebar.radio("Go to", [
        "Student Management", "Daily Roster", "Course Management",
        "Teacher Management", "Finance & Payments"
    ])

    # Optional PST5 extra: back up on demand, not just at startup.
    st.sidebar.divider()
    if st.sidebar.button("Backup data now"):
        manager._save_data()   # make sure the file on disk is up to date first
        if backup_data(manager.data_path):
            st.sidebar.success("Backup created in data/backups.")
        else:
            st.sidebar.error("Backup failed. Check msms.log for details.")

    # Use an if/elif block to call the correct function to render the selected page.
    if page == "Student Management":
        show_student_management_page(manager)
    elif page == "Daily Roster":
        show_roster_page(manager)
    elif page == "Course Management":
        show_course_management_page(manager)
    elif page == "Teacher Management":
        show_teacher_management_page(manager)
    elif page == "Finance & Payments":
        show_finance_page(manager)
