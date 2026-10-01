# gui/student_pages.py
import streamlit as st

def show_student_management_page(manager):
    """Renders all components for the student management page."""
    st.header("Student Management")

    # --- Search Section (remains the same) ---
    st.subheader("Find a Student")
    search_query = st.text_input("Search by Name or ID")
    if st.button("Search"):
        st.info("Search backend will be conncetd when we plug in your PST3 code")

    # --- Registration Section (now works correctly) ---
    st.subheader("Register New Student")
    with st.form("registration_form"):
        reg_name = st.text_input("New Student Name")
        reg_instrument = st.text_input("First Instrument")
        submitted = st.form_submit_button("Register Student")
        
        if submitted:
            # Check for blank name/instrument before processing
            if reg_name.strip() and reg_instrument.strip():
                try:
                    # This method will be connected to your backend later
                    new_student = manager.register_new_student(reg_name, reg_instrument)
                    if new_student:
                        st.success(f"Successfully registered {reg_name}!")
                        st.balloons() 
                    else:
                        st.error(f"Could not register student. A teacher for {reg_instrument} might not be available.")
                except AttributeError:
                    st.warning("GUI is ready! (Waiting for 'register_new_student' to be added to your PST3 schedule.py)")
            else:
                st.warning("Please enter both a name and an instrument.")