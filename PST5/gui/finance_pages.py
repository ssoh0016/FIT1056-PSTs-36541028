# gui/finance_pages.py
import os
import streamlit as st
import pandas as pd

EXPORT_DIR = "exports"


def show_finance_page(manager):
    """Renders the UI for all financial operations."""
    st.header("Finance & Payments")

    # Labels include the ID so two students with the same name stay distinguishable.
    student_list = {f"{s.name} (ID: {s.id})": s.id for s in manager.students}

    if not student_list:
        st.info("No students registered yet. Register a student before recording payments.")
    else:
        # --- Section 1: Record a Payment ---
        st.subheader("Record New Payment")
        with st.form("payment_form"):
            selected_student_name = st.selectbox(
                "Select Student", list(student_list.keys()), key="payment_student")
            amount = st.number_input("Payment Amount", min_value=0.01, value=50.00, step=1.00, format="%.2f")
            method = st.text_input("Payment Method (e.g., Credit Card, Cash)")

            submitted = st.form_submit_button("Record Payment")
            if submitted:
                if not method.strip():
                    st.warning("Please enter a payment method.")
                elif manager.record_payment(student_list[selected_student_name], amount, method.strip()):
                    st.success(f"Payment of {amount:.2f} for {selected_student_name} recorded.")
                else:
                    st.error("Payment could not be recorded. Check the student and amount.")

        # --- Section 2: View Payment History ---
        st.subheader("View Student Payment History")
        history_student_name = st.selectbox(
            "Select Student to View History", list(student_list.keys()), key="history_student")
        history = manager.get_payment_history(student_list[history_student_name])
        if history:
            df = pd.DataFrame(history)
            st.metric("Total paid", f"{df['amount'].sum():.2f}")
            st.dataframe(df)
        else:
            st.info("This student has no payment history.")

    # --- Section 3: Reports (CSV export) ---
    st.subheader("Export Reports")
    col_finance, col_attendance = st.columns(2)
    for column, kind in ((col_finance, "finance"), (col_attendance, "attendance")):
        with column:
            if st.button(f"Generate {kind} report", key=f"export_{kind}"):
                out_path = os.path.join(EXPORT_DIR, f"{kind}_report.csv")
                if manager.export_report(kind, out_path):
                    with open(out_path, "r", newline="") as f:
                        st.download_button(f"Download {kind}_report.csv", f.read(),
                                           file_name=f"{kind}_report.csv", mime="text/csv",
                                           key=f"download_{kind}")
                else:
                    st.error(f"Could not generate the {kind} report.")
