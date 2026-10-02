# gui/roster_pages.py
import streamlit as st
import pandas as pd

def show_roster_page(manager):
    """Renders the daily roster and check-in functionality."""
    st.header("Daily Roster")

    # --- View Roster Section (remains the same) ---
    day = st.selectbox("Select a day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    # ... (code to display the dataframe) ...
    try:
        courses = manager.get_daily_roster(day)
        if not courses:
            st.info(f"No lessons scheduled for {day}.")
        else:
            # Displaying data as a sleek Streamlit dataframe
            roster_data = []
            for c in courses:
                roster_data.append({
                    "Course ID": getattr(c, 'course_id', getattr(c, 'id', 'N/A')),
                    "Course Name": getattr(c, 'course_name', getattr(c, 'name', 'N/A')),
                    "Teacher ID": c.teacher_id
                })
            st.dataframe(pd.DataFrame(roster_data), use_container_width=True)
    except AttributeError:
        st.warning("GUI is ready! (Waiting for 'get_daily_roster' from PST3)")
        
    
    # --- Student Check-in Section (now works correctly) ---
    st.subheader("Student Check-in")
    with st.form("check_in_form"):
        try:
            # Dynamically populate dropdowns from manager lists.
            # Labels include the ID so two students/courses that share a name
            # don't collide into the same dict key (and become unreachable).
            student_list = {f"{s.name} (ID: {s.id})": s.id for s in manager.students}
            # Using getattr to safely handle whether your PST3 uses 'name' or 'course_name'
            course_list = {
                f"{getattr(c, 'course_name', getattr(c, 'name', 'Unknown'))} (ID: {getattr(c, 'course_id', getattr(c, 'id', 0))})":
                getattr(c, 'course_id', getattr(c, 'id', 0))
                for c in manager.courses
            }
            
            selected_student_name = st.selectbox("Select Student", list(student_list.keys()))
            selected_course_name = st.selectbox("Select Course", list(course_list.keys()))
        except AttributeError:
            st.info("Dropdowns will populate when PST3 manager data is loaded.")
            selected_student_name, selected_course_name = None, None
            student_list, course_list = {}, {}

        submitted = st.form_submit_button("Check-in Student")

        if submitted:
            if selected_student_name and selected_course_name:
                student_id = student_list[selected_student_name]
                course_id = course_list[selected_course_name]

                try:
                    success = manager.check_in(student_id, course_id)
                    if success:
                        st.success(f"Checked in {selected_student_name} for {selected_course_name}!")
                    else:
                        st.error("Check-in failed. See console for details. (Is the student enrolled in that course?)")
                except AttributeError:
                    st.warning("GUI is ready! (Waiting for 'check_in' from PST3)")
            else:
                st.error("Cannot check in: Student or Course data is missing.")