# gui/student_pages.py
import streamlit as st
import pandas as pd


def _student_options(manager):
    """Label -> id map for dropdowns. Labels include the ID so two students
    sharing a name (e.g. two 'Bob Williams') don't collide into one option."""
    return {f"{s.name} (ID: {s.id})": s.id for s in manager.students}


def _course_options(manager):
    return {f"{c.course_name} (ID: {c.course_id})": c.course_id for c in manager.courses}


def show_student_management_page(manager):
    """Renders all components for the student management page."""
    st.header("Student Management")

    tab_find, tab_register, tab_enrolment, tab_manage = st.tabs(
        ["Find & List", "Register", "Enrolment", "Update / Remove / Card"]
    )

    # --- Find & List ---
    with tab_find:
        st.subheader("Find a Student or Teacher")
        search_query = st.text_input("Search by name (students) or name/speciality (teachers)")
        if st.button("Search"):
            if search_query.strip():
                matched_students, matched_teachers = manager.search(search_query.strip())
                if not matched_students and not matched_teachers:
                    st.info("No match found.")
                else:
                    if matched_students:
                        st.write("Matched students")
                        st.dataframe(pd.DataFrame([
                            {"ID": s.id, "Name": s.name, "Enrolled in": s.enrolled_course_ids}
                            for s in matched_students
                        ]))
                    if matched_teachers:
                        st.write("Matched teachers")
                        st.dataframe(pd.DataFrame([
                            {"ID": t.id, "Name": t.name, "Speciality": t.speciality}
                            for t in matched_teachers
                        ]))
            else:
                st.warning("Enter something to search for.")

        st.subheader("All Students")
        if not manager.students:
            st.info("No students in the system yet.")
        else:
            st.dataframe(pd.DataFrame([
                {"ID": s.id, "Name": s.name, "Enrolled in": s.enrolled_course_ids}
                for s in manager.students
            ]))

    # --- Register ---
    with tab_register:
        st.subheader("Register New Student")
        with st.form("registration_form"):
            reg_name = st.text_input("New Student Name")
            # In PST3, you register with an optional course ID, not an instrument
            reg_course = st.text_input("Enrol in Course ID (Optional)")
            submitted = st.form_submit_button("Register Student")

            if submitted:
                if not reg_name.strip():
                    st.warning("Please enter a name.")
                else:
                    try:
                        course_id = int(reg_course.strip()) if reg_course.strip() else None
                    except ValueError:
                        st.error("Course ID must be a number, or left blank to skip enrolling.")
                    else:
                        new_student, enrolled = manager.register_student(reg_name, course_id)
                        st.success(f"Successfully registered {new_student.name} as ID {new_student.id}!")
                        st.balloons()
                        if enrolled is True:
                            st.success(f"Enrolled in Course {course_id}.")
                        elif enrolled is False:
                            st.warning(f"Registered, but Course {course_id} was not found.")
                        manager._save_data()  # Save the changes to msms.json

    # --- Enrolment (enrol / drop / switch) ---
    with tab_enrolment:
        student_opts = _student_options(manager)
        course_opts = _course_options(manager)
        no_data = not student_opts or not course_opts
        if no_data:
            st.info("Need at least one student and one course before you can manage enrolment.")

        st.subheader("Enrol Existing Student")
        if not no_data:
            with st.form("enrol_form"):
                s_label = st.selectbox("Student", list(student_opts.keys()), key="enrol_student")
                c_label = st.selectbox("Course", list(course_opts.keys()), key="enrol_course")
                if st.form_submit_button("Enrol"):
                    if manager.enrol_student(student_opts[s_label], course_opts[c_label]):
                        st.success(f"Enrolled {s_label} in {c_label}.")
                        manager._save_data()
                    else:
                        st.error("Could not enrol. Check the student and course exist.")

        st.subheader("Drop a Course")
        if not no_data:
            with st.form("drop_form"):
                s_label = st.selectbox("Student", list(student_opts.keys()), key="drop_student")
                c_label = st.selectbox("Course to drop", list(course_opts.keys()), key="drop_course")
                if st.form_submit_button("Drop course"):
                    if manager.drop_student_course(student_opts[s_label], course_opts[c_label]):
                        st.success(f"Dropped {s_label} from {c_label}.")
                        manager._save_data()
                    else:
                        st.error("Could not drop - that student isn't enrolled in that course.")

        st.subheader("Switch Course")
        if not no_data:
            with st.form("switch_form"):
                s_label = st.selectbox("Student", list(student_opts.keys()), key="switch_student")
                from_label = st.selectbox("From course", list(course_opts.keys()), key="switch_from")
                to_label = st.selectbox("To course", list(course_opts.keys()), key="switch_to")
                if st.form_submit_button("Switch"):
                    ok = manager.switch_student_course(
                        student_opts[s_label], course_opts[from_label], course_opts[to_label]
                    )
                    if ok:
                        st.success(f"Switched {s_label} from {from_label} to {to_label}.")
                        manager._save_data()
                    else:
                        st.error("Could not switch - check the student is enrolled in the 'from' course.")

    # --- Update / Remove / Card ---
    with tab_manage:
        student_opts = _student_options(manager)
        if not student_opts:
            st.info("No students yet.")

        st.subheader("Update Student Name")
        if student_opts:
            with st.form("update_student_form"):
                s_label = st.selectbox("Student", list(student_opts.keys()), key="update_student")
                new_name = st.text_input("New name")
                if st.form_submit_button("Update"):
                    if not new_name.strip():
                        st.warning("Enter a new name first.")
                    elif manager.update_student(student_opts[s_label], name=new_name.strip()):
                        st.success(f"Updated {s_label} to '{new_name.strip()}'.")
                        manager._save_data()
                    else:
                        st.error("Student not found.")

        st.subheader("Print Student Card")
        if student_opts:
            with st.form("print_card_form"):
                s_label = st.selectbox("Student", list(student_opts.keys()), key="card_student")
                if st.form_submit_button("Generate card"):
                    filename = manager.print_student_card(student_opts[s_label])
                    if filename:
                        with open(filename, "r") as f:
                            card_text = f.read()
                        st.text(card_text)
                        st.download_button("Download card", card_text, file_name=filename)
                    else:
                        st.error("Student not found.")

        st.subheader("Remove Student")
        if student_opts:
            with st.form("remove_student_form"):
                s_label = st.selectbox("Student", list(student_opts.keys()), key="remove_student")
                confirm = st.checkbox("I understand this can't be undone")
                if st.form_submit_button("Remove"):
                    if not confirm:
                        st.warning("Please confirm before removing.")
                    elif manager.remove_student(student_opts[s_label]):
                        st.success(f"Removed {s_label}.")
                        manager._save_data()
                    else:
                        st.error("Student not found.")
