# Music School Management System (MSMS) - PST4

## Overview
This project is a modern, Object-Oriented Music School Management System (MSMS) developed for FIT1056. In this iteration (PST4), the system has been upgraded from a text-based console application to a fully interactive web-based Graphical User Interface (GUI) using Streamlit. The application allows front-desk receptionists to easily manage students, teachers, courses, and daily rosters.

## Development Phases (PST4 Fragments)
This GUI was built progressively in three main fragments:
*   **Fragment 4.1: The GUI Entry Point & Main Dashboard**[cite: 3]. We established the main application window and the primary receptionist dashboard[cite: 3]. This serves as the central hub, featuring a sidebar navigation menu that allows seamless switching between different pages[cite: 3]. The `ScheduleManager` is initialized here and preserved using Streamlit's session state[cite: 3].
*   **Fragment 4.2: The Student Management Page**[cite: 4]. We built the GUI page for student management, incorporating a fully functional registration form[cite: 4]. This fragment connects the frontend form directly to the backend `register_student` method[cite: 4].
*   **Fragment 4.3: The Daily Roster & Check-In Page**[cite: 5]. We constructed a visual and interactive page for viewing the daily class schedule and performing real-time student check-ins[cite: 5]. The check-in section calls the backend check-in method and provides appropriate success or error feedback[cite: 5]. *(Note: We also voluntarily expanded this phase to include full Course and Teacher management tabs for a complete application).*

## Project Structure & Component Roles
The project follows a Model-View-Controller (MVC) inspired architecture to ensure a strict separation of concerns between the business logic and the user interface.

*   **`main.py` (The Launcher):** Serves as the single entry point to launch the Streamlit application.
*   **`app/` (The Backend / Controller & Models):**
    *   `schedule.py`: Contains the `ScheduleManager` class, acting as the Controller. It handles all business logic, object instantiation, and JSON file operations.
    *   `student.py`, `teacher.py`, `course.py`, `user.py`: The data models (Classes) that define the attributes and behaviors of the entities within the school.
*   **`gui/` (The Frontend / View):**
    *   `main_dashboard.py`: Configures the main page layout, initializes the session state, and renders the sidebar navigation.
    *   `student_pages.py`: Contains tabbed interfaces for finding, registering, enrolling, and managing students.
    *   `teacher_pages.py`: Contains interfaces for adding, updating, and removing teachers.
    *   `course_pages.py`: Contains interfaces for creating, viewing, and deleting courses.
    *   `roster_pages.py`: Displays the daily schedule and handles real-time student check-ins.
*   **`data/` (The Database):**
    *   `msms.json`: The persistent storage file that saves all entity states and attendance logs.

## Setup and Installation
To run this application, you must have Python installed along with the Streamlit library.

1. Open your terminal and navigate to the root directory of the project (e.g., `cd msms-project`).
2. Install Streamlit if you have not already:
   `pip install streamlit pandas`
3. Launch the application:
   `streamlit run main.py`
4. The application will automatically open in your default web browser at `http://localhost:8501`.

## How to Test the Full Program
You can verify the application's functionality by interacting with the sidebar navigation:

1.  **Test Registration & UI Feedback:** Go to **Student Management > Register**. Attempt to register a student with a blank name to verify the UI validation warnings. Register a valid student and observe the success message and balloons.
2.  **Test Data Relationships (Enrolment):** Go to **Student Management > Enrolment**. Enrol a student in a course, then navigate to **Course Management > All Courses** to verify the enrolled student count has incremented.
3.  **Test State Mutations:** Navigate to **Teacher Management > Update Teacher**. Change a teacher's speciality. Verify the change is reflected in the "All Teachers" tab.
4.  **Test Roster & Check-in:** Go to the **Daily Roster** page. Select a day to view the dynamically loaded schedule table. Use the check-in form to log a student's attendance. You can confirm the timestamp was recorded by checking the `msms.json` file.
5.  **Test Cascading Deletes:** Go to **Course Management > Delete Course**. Delete a course, then check the enrolled students to ensure the course ID was safely removed from their personal records.

## Design Choices & Assumptions

*   **Strict Separation of Concerns:** The Streamlit GUI code never modifies the JSON data directly. It solely collects input and passes it to the `ScheduleManager`. This prevents the GUI from becoming bloated and keeps the backend completely platform-agnostic.
*   **Streamlit Session State:** Streamlit traditionally reruns the entire Python script upon every button click. To prevent the `ScheduleManager` from parsing the JSON file from scratch on every interaction, it is instantiated exactly once and stored inside `st.session_state.manager`.
*   **Defensive UI Dropdowns:** To prevent data collisions where two entities share the same name (e.g., two students named "Bob Williams"), all select box dropdowns dynamically format their labels to include the unique ID: `f"{name} (ID: {id})"`. The GUI then parses the correct integer ID before sending it to the backend.
*   **Robust Deletion Assumption:** It is assumed that deleting an entity should not leave dangling references. The backend methods (`remove_course`, `remove_student`) are designed to scrub the deleted entity's ID from all other related objects in memory before saving to the JSON file.
*   **List Instantiation (The `None` Trap):** In the object constructors, default arguments for lists (like `enrolled_course_ids`) are set to `None` rather than `[]` to prevent the mutable default argument bug, ensuring every object instance gets its own independent list in memory.

