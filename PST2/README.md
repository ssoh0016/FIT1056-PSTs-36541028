# Music School Management System (MSMS) - PST2

## 1. Project Overview
This repository contains the implementation for **Problem-Solving Task 2 (PST2)** of the Music School Management System (MSMS) for FIT1056. 

The primary objective of PST2 is to resolve the *"Amnesia & Chaos"* problem from PST1 by replacing temporary, in-memory data structures with a robust, persistent JSON file-storage engine (`msms.json`). The application is structured in `pst2_main.py` and provides full CRUD capabilities, attendance check-in, and card generation.

---

## 2. Component & Fragment Breakdown

* **Fragment 2.1: The Core Persistence Engine**
  * `load_data(path)`: Loads the global state from `msms.json`. If the file does not exist, it initializes default data structures (`students`, `teachers`, `attendance`, `next_student_id`, `next_teacher_id`).
  * `save_data(path)`: Serializes and writes the state to `msms.json` using formatted indentation for human readability.

* **Fragment 2.2: Refactoring & Expanding CRUD Operations**
  * Implements dictionary-based records within the centralized `app_data` dictionary.
  * Adds auto-incrementing ID assignment for teachers.
  * Supports dynamic field updating via keyword arguments (`**fields`) for `update_teacher()` and `update_student()`.
  * Implements remove and update utilities: `remove_teacher()` and `update_student()`.

* **Fragment 2.3: Receptionist Features**
  * `check_in(student_id, course_id, timestamp)`: Logs attendance records into `app_data['attendance']` with an ISO-formatted timestamp.
  * `print_student_card(student_id)`: Generates a formatted text file badge (`<student_id>_card.txt`) for the specified student.

* **Fragment 2.4: The Refactored Main Application Loop**
  * Create main() function 
  * Integrates the interactive CLI menu loop.
  * Calls `load_data()` immediately at application startup.
  * Make sure add_teacher, check_in, remove_student, save_data must be called to make the change permanent.

---

## Running the Application
Open your terminal in the project root directory and execute:

## 3. Checkpoint: Commit Your Progress
* Each progress make sure I have save my file and commit the important rule `git add pst2_main.py` and `git commit -m "feat(persistence): Save and load state from JSON"`.



