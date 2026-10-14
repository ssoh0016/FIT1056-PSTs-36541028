# gui/course_pages.py
import streamlit as st
import pandas as pd


def show_course_management_page(manager):
    """Renders course listing, creation, and deletion."""
    st.header("Course Management")

    tab_list, tab_add, tab_delete = st.tabs(["All Courses", "Add Course", "Delete Course"])

    with tab_list:
        st.subheader("All Courses")
        if not manager.courses:
            st.info("No courses in the system yet.")
        else:
            teacher_names = {t.id: t.name for t in manager.teachers}
            st.dataframe(pd.DataFrame([
                {
                    "ID": c.course_id,
                    "Name": c.course_name,
                    "Instrument": c.instrument,
                    "Teacher": teacher_names.get(c.teacher_id, f"Unknown ({c.teacher_id})"),
                    "Enrolled students": len(c.enrolled_student_ids),
                }
                for c in manager.courses
            ]))

    with tab_add:
        st.subheader("Add New Course")
        teacher_opts = {f"{t.name} (ID: {t.id})": t.id for t in manager.teachers}
        if not teacher_opts:
            st.info("Add a teacher first - courses need an existing teacher.")
        else:
            with st.form("add_course_form"):
                course_name = st.text_input("Course name")
                instrument = st.text_input("Instrument")
                teacher_label = st.selectbox("Teacher", list(teacher_opts.keys()))
                if st.form_submit_button("Add course"):
                    if not course_name.strip():
                        st.warning("Enter a course name.")
                    else:
                        course = manager.add_course(
                            course_name.strip(), teacher_opts[teacher_label], instrument.strip()
                        )
                        if course:
                            st.success(f"Added '{course.course_name}' (ID {course.course_id}).")
                            manager._save_data()
                        else:
                            st.error("Could not add course - teacher not found.")

    with tab_delete:
        st.subheader("Delete Course")
        course_opts = {f"{c.course_name} (ID: {c.course_id})": c.course_id for c in manager.courses}
        if not course_opts:
            st.info("No courses to delete.")
        else:
            with st.form("delete_course_form"):
                c_label = st.selectbox("Course", list(course_opts.keys()))
                confirm = st.checkbox("I understand this can't be undone")
                if st.form_submit_button("Delete"):
                    if not confirm:
                        st.warning("Please confirm before deleting.")
                    elif manager.remove_course(course_opts[c_label]):
                        st.success(f"Deleted {c_label}.")
                        manager._save_data()
                    else:
                        st.error("Course not found.")
