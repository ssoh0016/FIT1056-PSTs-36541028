# pst2_main.py - The Persistent Application

import json
import datetime

DATA_FILE = "msms.json"
app_data = {} # This global dictionary will hold ALL our data.

# --- Core Persistence Engine ---
def load_data(path=DATA_FILE):
    """Loads all application data from a JSON file."""
    global app_data
    try:
        with open(path, 'r') as f:
            # TODO: Use json.load(f) to load the file's content into the global 'app_data' variable.
            app_data = json.load(f)
            print("Data loaded successfully.")
    except FileNotFoundError:
        print("Data file not found. Initializing with default structure.")
        # TODO: If the file doesn't exist, initialize 'app_data' with a default dictionary.
        # It should have keys like: "students", "teachers", "attendance", "next_student_id", "next_teacher_id".
        # The lists should be empty and the IDs should start at 1.
        app_data = {
            "students": [],
            "teachers": [],
            "attendance": [],
            "next_student_id": 1,
            "next_teacher_id": 1
        }

def save_data(path=DATA_FILE):
    """Saves all application data to a JSON file."""
    # TODO: Open the file at 'path' in write mode ('w').
    # Use json.dump() to write the global 'app_data' dictionary to the file.
    # Use the 'indent=4' argument in json.dump() to make the file readable.
    with open(path, 'w') as f:
        json.dump(app_data, f, indent=4)
    print("Data saved successfully.")
    
    
# --- Full CRUD for Core Data ---
# Note: We are now working with lists of dictionaries, not lists of objects.

def add_teacher(name, speciality):
    """Adds a teacher dictionary to the data store."""
    # TODO: Get the next teacher ID from app_data['next_teacher_id'].
    teacher_id = app_data['next_teacher_id']
    # TODO: Create a new teacher dictionary with 'id', 'name', and 'speciality' keys.
    new_teacher = {"id": teacher_id, "name": name, "speciality": speciality}
    # TODO: Append the new dictionary to the app_data['teachers'] list.
    app_data['teachers'].append(new_teacher)
    # TODO: Increment the 'next_teacher_id' in app_data.
    app_data['next_teacher_id'] += 1
    print(f"Core: Teacher '{name}' added.")

def update_teacher(teacher_id, **fields):
    """Finds a teacher by ID and updates their data with provided fields."""
    # TODO: Loop through the app_data['teachers'] list.
    for teacher in app_data['teachers']:
        # TODO: If a teacher's 'id' matches teacher_id:
        if teacher['id'] == teacher_id:
            # Use the .update() method on the teacher dictionary to apply the 'fields'.
            teacher.update(fields)
            print(f"Teacher {teacher_id} updated.")
            return 
    print(f"Error: Teacher with ID {teacher_id} not found.")
    
    
def remove_teacher(teacher_id):
    """Removes a teacher from the data store."""
    initial_count = len(app_data['teachers'])
    app_data['taechers'] = [t for t in app_data['taechers'] if t['id'] != teacher_id]
    if len(app_data['teachers']) < initial_count:
            print(f"Teacher {teacher_id} removed.")
            return 
    print(f"Error: Student with ID {teacher_id} not found.")
    
def add_student(name, enrolled_in=None):
    """Adds a student dictionary to the data store."""
    if enrolled_in is None:
        enrolled_in = []
    student_id = app_data['next_student_id']
    new_student = {"id": student_id, "name": name, "enrolled_in": enrolled_in}
    app_data['students'].append(new_student)
    app_data['next_student_id'] += 1
    print(f"Core: Student '{name}' added.")
    
def update_student(student_id, **fields):
    """Finds a student by ID and updates their data with provided fields."""
    # TODO: Loop through the app_data['student'] list.
    for student in app_data['student']:
        # TODO: If a student's 'id' matches student_id:
        if student['id'] == student_id:
            # Use the .update() method on the student dictionary to apply the 'fields'.
            student.update(fields)
            print(f"Teacher {student_id} updated.")
            return 
    print(f"Error: Teacher with ID {student_id} not found.")

def remove_student(student_id):
    """Removes a student from the data store."""
    # TODO: Find the student dictionary in app_data['students'] with the matching ID.
    initial_count = len(app_data['students'])
    app_data['students'] = [s for s in app_data['students'] if s['id'] != student_id]
    # If found, use the .remove() method on the list to delete it.
    # A list comprehension is a clean way to do this:
    # app_data['students'] = [s for s in app_data['students'] if s['id'] != student_id]
    if len(app_data['students']) < initial_count:
        print(f"Student {student_id} removed.")
        return 
    print(f"Error: Student with ID {student_id} not found.")
    
    
# TODO: Implement remove_teacher() and update_student() using the patterns above.