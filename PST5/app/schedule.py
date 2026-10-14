import csv
import datetime
import json
import logging
import math
import os
import shutil

from app.student import StudentUser
from app.teacher import TeacherUser, Course


class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []
        self.finance_log = []          # PST5: every recorded payment
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_course_id = 1
        self.load_error = None         # PST5: set if the data file was unreadable
        self._load_data()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load_data(self):
        """Loads data from the JSON file and populates the object lists.

        A missing file simply means a fresh start. A damaged file (bad JSON,
        missing keys, wrong types) no longer crashes the app: the problem is
        logged, the damaged file is copied aside, and we start empty.
        """
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)

            for s in data.get("students", []):
                self.students.append(StudentUser(s["id"], s["name"], s.get("enrolled_course_ids", [])))

            for t in data.get("teachers", []):
                self.teachers.append(TeacherUser(t["id"], t["name"], t["speciality"]))

            for c in data.get("courses", []):
                self.courses.append(Course(
                    c.get("course_id", c.get("id")),
                    c.get("course_name", c.get("name")),
                    c["teacher_id"],
                    c.get("instrument", ""),
                    c.get("enrolled_student_ids"),
                    c.get("lessons", [])
                ))

            self.attendance_log = data.get("attendance", [])
            self.finance_log = data.get("finance_log", [])   # old files have no finance_log

            # Load the next-ID counters, but never trust a stored counter that's
            # lower than the highest ID already in use (e.g. a stale hand-edited file) -
            # that would hand out a "new" ID that collides with an existing record.
            self.next_student_id = data.get("next_student_id", 1)
            if self.students:
                self.next_student_id = max(self.next_student_id, max(s.id for s in self.students) + 1)

            self.next_teacher_id = data.get("next_teacher_id", 1)
            if self.teachers:
                self.next_teacher_id = max(self.next_teacher_id, max(t.id for t in self.teachers) + 1)

            self.next_course_id = data.get("next_course_id", 1)
            if self.courses:
                self.next_course_id = max(self.next_course_id, max(c.course_id for c in self.courses) + 1)
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            # json.JSONDecodeError and UnicodeDecodeError are both ValueErrors.
            self._recover_from_bad_data(error)

    def _recover_from_bad_data(self, error):
        """Resets to an empty state after an unreadable data file, keeping a copy of the file."""
        self.students, self.teachers, self.courses = [], [], []
        self.attendance_log, self.finance_log = [], []
        self.next_student_id = self.next_teacher_id = self.next_course_id = 1
        self.load_error = f"{type(error).__name__}: {error}"
        logging.error(f"Could not load {self.data_path}: {self.load_error}")
        print(f"Error: could not read {self.data_path} ({self.load_error}). Starting with a clean state.")
        # Keep the damaged file: the next save would otherwise silently overwrite it.
        try:
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(self.data_path, f"{self.data_path}.corrupt_{stamp}")
        except OSError:
            pass

    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance_log,
            "finance_log": self.finance_log,
            "next_student_id": self.next_student_id,
            "next_teacher_id": self.next_teacher_id,
            "next_course_id": self.next_course_id
        }
        folder = os.path.dirname(self.data_path)
        if folder:
            os.makedirs(folder, exist_ok=True)   # e.g. a brand new install with no data/ folder yet
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print("Data successfully saved.")

    # ------------------------------------------------------------------
    # Enrollment & Scheduling
    # ------------------------------------------------------------------
    def switch_student_course(self, student_id, from_course_id, to_course_id):
        """Moves a student from one course to another, keeping both sides of the
        student/course relationship in sync."""
        student = self.find_student_by_id(student_id)
        from_id_int = int(from_course_id)
        to_id_int = int(to_course_id)

        if not student or from_id_int not in student.enrolled_course_ids:
            return False
        if not self.find_course_by_id(to_id_int):
            return False  # can't switch into a course that doesn't exist

        self.drop_student_course(student_id, from_id_int)
        self.enrol_student(student_id, to_id_int)
        logging.info(f"Student {student_id} switched from course {from_id_int} to course {to_id_int}.")
        return True

    def enrol_student(self, student_id, course_id):
        """Adds a student to a course, updating both the student's and the course's records."""
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)
        if not student or not course:
            return False
        if course.course_id not in student.enrolled_course_ids:
            student.enrolled_course_ids.append(course.course_id)
        if student.id not in course.enrolled_student_ids:
            course.enrolled_student_ids.append(student.id)
        logging.info(f"Student {student_id} enrolled in course {course_id}.")
        return True

    def drop_student_course(self, student_id, course_id):
        """Removes a single course from a student's enrollment, with no replacement course.
        Used directly by the 'Drop a Course' form, and internally by
        switch_student_course as its 'remove the old course' step."""
        student = self.find_student_by_id(student_id)
        if not student or course_id not in student.enrolled_course_ids:
            return False
        student.enrolled_course_ids.remove(course_id)
        course = self.find_course_by_id(course_id)
        if course and student_id in course.enrolled_student_ids:
            course.enrolled_student_ids.remove(student_id)
        logging.info(f"Student {student_id} dropped course {course_id}.")
        return True

    def check_in(self, student_id, course_id):
        """Records a student's attendance for a course after validation.
        The student must exist, the course must exist, and the student must be enrolled."""
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)

        if not student or not course:
            print("Error: Check-in failed. Invalid Student or Course ID.")
            return False
        if course_id not in student.enrolled_course_ids:
            print(f"Error: Check-in failed. {student.name} is not enrolled in {course.course_name}.")
            logging.warning(f"Check-in rejected: student {student_id} is not enrolled in course {course_id}.")
            return False

        timestamp = datetime.datetime.now().isoformat()
        self.attendance_log.append({"student_id": student_id, "course_id": course_id, "timestamp": timestamp})
        self._save_data()
        logging.info(f"Student {student_id} checked in to course {course_id}.")
        print(f"Success: Student {student.name} checked into {course.course_name}.")
        return True

    def get_daily_roster(self, day):
        """Retrieves the courses that have an active (not cancelled) lesson on the given day."""
        roster = []
        for course in self.courses:
            for lesson in course.lessons:
                if lesson.get("cancelled"):
                    continue
                if lesson.get("day", "").strip().lower() == day.strip().lower():
                    roster.append(course)
                    break  # course already added; don't add it twice for a 2nd same-day lesson
        return roster

    def cancel_lesson(self, lesson_id, reason):
        """Marks a lesson as cancelled so it drops off the daily roster.
        The lesson stays on record together with the reason. Returns True on success."""
        reason = str(reason).strip()
        if not reason:
            print("Error: A reason is required to cancel a lesson.")
            return False
        for course in self.courses:
            for lesson in course.lessons:
                if lesson.get("lesson_id") == lesson_id:
                    if lesson.get("cancelled"):
                        print(f"Error: Lesson {lesson_id} is already cancelled.")
                        return False
                    lesson["cancelled"] = True
                    lesson["cancel_reason"] = reason
                    lesson["cancelled_at"] = datetime.datetime.now().isoformat()
                    self._save_data()
                    logging.warning(f"Lesson ID {lesson_id} was cancelled. Reason: {reason}")
                    return True
        print(f"Error: Lesson {lesson_id} not found.")
        return False

    # ------------------------------------------------------------------
    # Student management
    # ------------------------------------------------------------------
    def register_student(self, name, course_id=None):
        """Creates a new student and optionally enrols them in a course right away.
        Returns (student, enrolled): enrolled is True/False if a course_id was given,
        or None if enrollment wasn't attempted at all."""
        new_student = StudentUser(self.next_student_id, name)
        self.students.append(new_student)
        self.next_student_id += 1
        logging.info(f"Registered student '{name}' with ID {new_student.id}.")

        enrolled = None
        if course_id is not None:
            enrolled = self.enrol_student(new_student.id, course_id)
        return new_student, enrolled

    def update_student(self, student_id, name=None):
        """Updates a student's name. Enrolled courses are deliberately NOT editable here -
        they're managed via enrol_student / drop_student_course / switch_student_course,
        which keep the matching Course.enrolled_student_ids lists in sync."""
        student = self.find_student_by_id(student_id)
        if not student:
            return False
        if name:
            student.name = name
            logging.info(f"Student {student_id} renamed to '{name}'.")
        return True

    def remove_student(self, student_id):
        """Removes a student and scrubs their ID from any course rosters they were on.
        Their attendance and payment records are kept (they are historical records)."""
        student = self.find_student_by_id(student_id)
        if not student:
            return False
        self.students.remove(student)
        for course in self.courses:
            if student_id in course.enrolled_student_ids:
                course.enrolled_student_ids.remove(student_id)
        logging.info(f"Removed student {student_id} ('{student.name}').")
        return True

    def print_student_card(self, student_id):
        """Writes a text-file ID badge for a student, listing their courses by name.
        Returns the filename on success, or None if the student wasn't found."""
        student = self.find_student_by_id(student_id)
        if not student:
            return None

        course_names = []
        for cid in student.enrolled_course_ids:
            course = self.find_course_by_id(cid)
            course_names.append(course.course_name if course else f"Unknown course ({cid})")

        filename = f"{student_id}_card.txt"
        with open(filename, 'w') as f:
            f.write("========================\n")
            f.write("  MUSIC SCHOOL ID BADGE\n")
            f.write("========================\n")
            f.write(f"ID: {student.id}\n")
            f.write(f"Name: {student.name}\n")
            f.write(f"Enrolled In: {', '.join(course_names) if course_names else 'Nothing yet'}\n")
        return filename

    # ------------------------------------------------------------------
    # Course management
    # ------------------------------------------------------------------
    def add_course(self, course_name, teacher_id, instrument=""):
        """Creates a new course taught by an existing teacher.
        Returns the new Course, or None if the teacher ID doesn't exist."""
        if not self.find_teacher_by_id(teacher_id):
            return None
        new_course = Course(self.next_course_id, course_name, teacher_id, instrument)
        self.courses.append(new_course)
        self.next_course_id += 1
        logging.info(f"Added course '{course_name}' with ID {new_course.course_id}.")
        return new_course

    def remove_course(self, course_id):
        """Removes a course and scrubs it from every student's enrollment list."""
        course = self.find_course_by_id(course_id)
        if not course:
            return False
        self.courses.remove(course)
        for student in self.students:
            if course_id in student.enrolled_course_ids:
                student.enrolled_course_ids.remove(course_id)
        logging.info(f"Removed course {course_id} ('{course.course_name}').")
        return True

    # ------------------------------------------------------------------
    # Teacher management
    # ------------------------------------------------------------------
    def add_teacher(self, name, speciality):
        """Creates a new teacher and adds them to the system."""
        new_teacher = TeacherUser(self.next_teacher_id, name, speciality)
        self.teachers.append(new_teacher)
        self.next_teacher_id += 1
        logging.info(f"Added teacher '{name}' with ID {new_teacher.id}.")
        return new_teacher

    def update_teacher(self, teacher_id, **fields):
        """Finds a teacher by ID and updates their attributes with the given fields."""
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            return False
        for key, value in fields.items():
            setattr(teacher, key, value)
        logging.info(f"Updated teacher {teacher_id}: {', '.join(fields)}.")
        return True

    def remove_teacher(self, teacher_id):
        """Removes a teacher from the system."""
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            return False
        self.teachers.remove(teacher)
        logging.info(f"Removed teacher {teacher_id} ('{teacher.name}').")
        return True

    # ------------------------------------------------------------------
    # Finance & reporting (PST5 - Fragment 5.1)
    # ------------------------------------------------------------------
    def record_payment(self, student_id, amount, method):
        """Adds a payment record to the finance log. Returns True on success.

        Rejected (returns False, nothing recorded) if the student doesn't exist,
        the amount isn't a positive finite number, or the method is blank.
        """
        if not self.find_student_by_id(student_id):
            print(f"Error: Payment failed. Student {student_id} not found.")
            logging.warning(f"Payment rejected: unknown student ID {student_id}.")
            return False

        try:
            amount = round(float(amount), 2)
        except (TypeError, ValueError):
            amount = float("nan")
        if not math.isfinite(amount) or amount <= 0:
            print("Error: Payment failed. Amount must be a positive number.")
            logging.warning(f"Payment rejected for student {student_id}: invalid amount.")
            return False

        method = str(method).strip()
        if not method:
            print("Error: Payment failed. A payment method is required.")
            logging.warning(f"Payment rejected for student {student_id}: blank method.")
            return False

        payment_record = {
            "student_id": student_id,
            "amount": amount,
            "method": method,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.finance_log.append(payment_record)
        self._save_data()
        logging.info(f"Payment of {amount} recorded for student ID {student_id}.")
        print(f"Payment of {amount} for student {student_id} recorded.")
        return True

    def get_payment_history(self, student_id):
        """Returns a list of all payments for a given student."""
        return [p for p in self.finance_log if p['student_id'] == student_id]

    def export_report(self, kind, out_path):
        """Exports the 'finance' or 'attendance' log to a CSV file. Returns True on success."""
        print(f"Exporting {kind} report to {out_path}...")
        if kind == "finance":
            data_to_export = self.finance_log
            headers = ["student_id", "amount", "method", "timestamp"]
        elif kind == "attendance":
            data_to_export = self.attendance_log
            headers = ["student_id", "course_id", "timestamp"]
        else:
            print("Error: Unknown report type.")
            logging.warning(f"Export rejected: unknown report type '{kind}'.")
            return False

        try:
            folder = os.path.dirname(out_path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(out_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data_to_export)
        except OSError as error:
            print(f"Error: Could not write report ({error}).")
            logging.error(f"Export of {kind} report to {out_path} failed: {error}")
            return False

        logging.info(f"Exported {len(data_to_export)} {kind} rows to {out_path}.")
        return True

    # ------------------------------------------------------------------
    # Search & lookup helpers
    # ------------------------------------------------------------------
    def search(self, term):
        """Searches students by name, and teachers by name or speciality."""
        term_lower = term.lower()
        matched_students = [s for s in self.students if term_lower in s.name.lower()]
        matched_teachers = [t for t in self.teachers
                            if term_lower in t.name.lower() or term_lower in t.speciality.lower()]
        return matched_students, matched_teachers

    def find_student_by_id(self, student_id):
        """Helper to find a student object by their ID."""
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def find_teacher_by_id(self, teacher_id):
        """Helper to find a teacher object by their ID."""
        for teacher in self.teachers:
            if teacher.id == teacher_id:
                return teacher
        return None

    def find_course_by_id(self, course_id):
        """Helper to find a course object by its ID."""
        for course in self.courses:
            if course.course_id == course_id:
                return course
        return None
