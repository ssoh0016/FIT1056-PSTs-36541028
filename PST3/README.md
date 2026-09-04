# Music School Management System (MSMS) - PST3

## 1. Project Overview
This repository contains the implementation of the **Music School Management System (MSMS)** developed as part of **FIT1056 - Problem Solving Task 3 (PST3)**. 

PST3 transitions the application from procedural code to a full **Object-Oriented Programming (OOP)** architecture following the **Model-Controller-View (MCV)** pattern.

---
## Directory & File Structure
```text
FIT1056-PSTs-36541028/
└── PST3/
    ├── app/
    │   ├── __init__.py      # Package initialization
    │   ├── user.py          # Base User model
    │   ├── student.py       # StudentUser class inheriting from User
    │   ├── teacher.py       # TeacherUser and Course classes
    │   └── schedule.py      # ScheduleManager class (Controller/Brain)
    ├── data/
    │   └── msms.json        # JSON database file for persistence
    └── main.py              # Main application entry point (View/Front Desk)

## 2. Component & Fragment Breakdown
* **Fragment 3.1:  The New Blueprints (The Model Layer) `app/`**
  * `app/user.py`:Contains the foundational User base class providing shared attributes (user_id and name).
  * `app/student.py`: Defines `StudentUser` (inherits from User), managing student-specific attributes such as enrolled courses and student status.
  * `app/teacher.py`: Defines `TeacherUser` (inherits from User), managing instructor profiles and assigned courses. `Course` represents individual courses offered by the music school, tracking course IDs, instruments, course name, teacher ID, enrolled student id and lessons.
  * `data/msms.json` Holds the persisted JSON database containing user records, course details, and attendance logs.

* **Fragment 3.2: The "Brain" of the System (The Controller Layer) `app/schedule.py`**
  * `__init__: Explicitly initializes self.attendance_log = [].
  * `_load_data()` Reads raw dictionaries from `data/msms.json` and instantiates them into `StudentUser`, `TeacherUser`, and `Course` class objects. Reads the "attendance" key using `.get()` to safely handle legacy data.
  * `_save_data()` Converts active class instances back into JSON-serializable dictionaries and writes `self.attendance_log` back to `data/msms.json`.

* **Fragment 3.3: Implementing Core Business Logic**
  * `check_in()` Implements validation logic for student check-ins. Updates runtime state and safely appends records to `self.attendance_log` without executing UI/console print commands.
  
* **Fragment 3.4:  The New Front Desk & Main Entry Point (The View Layer)**
  * `main.py` Serves as the user interaction entry point.
  * Instantiates a single `ScheduleManager` object at startup.
  * View functions (e.g., `front_desk_daily_roster(manager, day)`) accept the `manager` instance as a parameter, query its state, and handle all console output formatting.
---

## Running the Application
Open your terminal in the project root directory and execute: cd /FIT1056_works/FIT1056-PSTs-36541028/PST3.

## 3. Checkpoint: Commit Your Progress
**Git Commands to Commit and Push the README:**
```bash
git add README.md PST3/README.md
git commit -m "docs: Add detailed PST3 README outlining architecture, fragments 3.1-3.4, and testing steps"
git push origin individual
