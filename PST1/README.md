# PST1 - Music School Management System
This directory contains the PST1 implementation (`MSMS.py`).
Name: Soh Han Yuan
Student ID: 36541028

# Music School Management System (MSMS)

This is a simple Python program. It helps a music school receptionist manage students and teachers. 

---

## Table of Contents
- [Overview]
- [How the Code Works]
- [How to Run the Program]
- [How to Test the Program]
- [Design Choices & Assumptions]

---

## Overview
This program runs in a text window (your terminal). You use a menu to add new students, sign them up for classes, and search for people. 

The data is only saved while the program is open. If you close the program, the data resets.

---

## How the Code Works

The code is broken down into four simple parts:

### 1. Blueprints (Data Models)
* **`Student`**: A blueprint that holds a student's ID number, name, and a list of their instruments.
* **`Teacher`**: A blueprint that holds a teacher's ID number, name, and the instrument they teach.

### 2. Storage (The Database)
* We use two Python lists called `student_db` and `teacher_db` to store the data. 
* The program automatically gives every new student and teacher a unique ID number.

### 3. Actions (The Functions)
* **`add_teacher`**: Adds a new teacher to the system.
* **`front_desk_register`**: Adds a new student and puts them in their first class.
* **`front_desk_enrol`**: Adds a new instrument to an existing student's list.
* **`front_desk_lookup`**: Searches for a name or instrument. It ignores capital letters, so typing "piano" or "Piano" both work.
* **`list_students`** and **`list_teachers`**: Prints a list of everyone currently in the system.

### 4. The Menu (CLI)
* The `main()` function shows a numbered menu on the screen. The user types a number from 1 to 5 to pick what they want to do.

---
### 5. Notes Highlights
* **`def main()`**: encapsulates program execution logic, prevent variable scope leakage and organizing the entry points
* **`if__name__=="__main__"`**: ensures the script runs its main program only when executed directly, allowing it to be imported safety

