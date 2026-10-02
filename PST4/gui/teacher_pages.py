# gui/teacher_pages.py
import streamlit as st
import pandas as pd


def show_teacher_management_page(manager):
    """Renders teacher listing, creation, update, and removal."""
    st.header("Teacher Management")

    tab_list, tab_add, tab_update, tab_remove = st.tabs(
        ["All Teachers", "Add Teacher", "Update Teacher", "Remove Teacher"]
    )

    with tab_list:
        st.subheader("All Teachers")
        if not manager.teachers:
            st.info("No teachers in the system yet.")
        else:
            st.dataframe(pd.DataFrame([
                {"ID": t.id, "Name": t.name, "Speciality": t.speciality}
                for t in manager.teachers
            ]), use_container_width=True)

    with tab_add:
        st.subheader("Add New Teacher")
        with st.form("add_teacher_form"):
            name = st.text_input("Teacher name")
            speciality = st.text_input("Speciality")
            if st.form_submit_button("Add teacher"):
                if not name.strip():
                    st.warning("Enter a name.")
                else:
                    teacher = manager.add_teacher(name.strip(), speciality.strip())
                    st.success(f"Added '{teacher.name}' (ID {teacher.id}).")
                    manager._save_data()

    teacher_opts = {f"{t.name} (ID: {t.id})": t.id for t in manager.teachers}

    with tab_update:
        st.subheader("Update Teacher Info")
        if not teacher_opts:
            st.info("No teachers yet.")
        else:
            with st.form("update_teacher_form"):
                t_label = st.selectbox("Teacher", list(teacher_opts.keys()), key="update_teacher_select")
                new_name = st.text_input("New name (leave blank to skip)")
                new_spec = st.text_input("New speciality (leave blank to skip)")
                if st.form_submit_button("Update"):
                    updates = {}
                    if new_name.strip():
                        updates["name"] = new_name.strip()
                    if new_spec.strip():
                        updates["speciality"] = new_spec.strip()
                    if not updates:
                        st.warning("Nothing to update.")
                    elif manager.update_teacher(teacher_opts[t_label], **updates):
                        st.success(f"Updated {t_label}.")
                        manager._save_data()
                    else:
                        st.error("Teacher not found.")

    with tab_remove:
        st.subheader("Remove Teacher")
        if not teacher_opts:
            st.info("No teachers yet.")
        else:
            with st.form("remove_teacher_form"):
                t_label = st.selectbox("Teacher", list(teacher_opts.keys()), key="remove_teacher_select")
                confirm = st.checkbox("I understand this can't be undone")
                if st.form_submit_button("Remove"):
                    if not confirm:
                        st.warning("Please confirm before removing.")
                    elif manager.remove_teacher(teacher_opts[t_label]):
                        st.success(f"Removed {t_label}.")
                        manager._save_data()
                    else:
                        st.error("Teacher not found.")
