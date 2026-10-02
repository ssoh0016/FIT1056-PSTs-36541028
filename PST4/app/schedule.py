import json
import datetime
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
        self.next_student_id = 1
        self.next_teacher_id = 1
        self.next_course_id = 1
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
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

    # --- Enrollment & Scheduling ---

    def switch_student_course(self, student_id, from_course_id, to_course_id):
        """Moves a student from one course to another, keeping both sides of the
        student/course relationship in sync."""
        from_id_int = int(from_course_id)
        to_id_int = int(to_course_id)

        if not self.find_course_by_id(to_id_int):
            return False  # can't switch into a course that doesn't exist
        if not self.drop_student_course(student_id, from_id_int):
            return False  # student doesn't exist, or wasn't enrolled in from_course_id

        self.enrol_student(student_id, to_id_int)
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
        return True

    def drop_student_course(self, student_id, course_id):
        """Removes a student from a single course, keeping both sides of the
        student/course relationship in sync. Unlike switch_student_course, this
        doesn't enrol the student anywhere else afterward."""
        student = self.find_student_by_id(student_id)
        if not student or course_id not in student.enrolled_course_ids:
            return False

        student.enrolled_course_ids.remove(course_id)
        course = self.find_course_by_id(course_id)
        if course and student_id in course.enrolled_student_ids:
            course.enrolled_student_ids.remove(student_id)
        return True

    def check_in(self, student_id, course_id):
        """Records a student's attendance for a course after validation."""
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)
        
        if not student or not course:
            print("Error: Check-in failed. Invalid Student or Course ID.")
            return False
            
        timestamp = datetime.datetime.now().isoformat()
        check_in_record = {"student_id": student_id, "course_id": course_id, "timestamp": timestamp}
        
        self.attendance_log.append(check_in_record)
        self._save_data() 
        print(f"Success: Student {student.name} checked into {course.course_name}.")
        return True

    def get_daily_roster(self, day):
        """Retrieves the courses that have a lesson scheduled on the given day."""
        roster = []
        for course in self.courses:
            for lesson in course.lessons:
                if lesson.get("day", "").strip().lower() == day.strip().lower():
                    roster.append(course)
                    break  # course already added; don't add it twice for a 2nd same-day lesson
        return roster

    # --- Student Management (ported from PST2, adapted to enrol by course_id) ---

    def register_student(self, name, course_id=None):
        """Creates a new student and optionally enrols them in a course right away.
        Returns (student, enrolled): enrolled is True/False if a course_id was given,
        or None if enrollment wasn't attempted at all."""
        new_student = StudentUser(self.next_student_id, name)
        self.students.append(new_student)
        self.next_student_id += 1

        enrolled = None
        if course_id is not None:
            enrolled = self.enrol_student(new_student.id, course_id)
        return new_student, enrolled

    def update_student(self, student_id, **fields):
        """Finds a student by ID and updates their attributes with the given fields."""
        student = self.find_student_by_id(student_id)
        if not student:
            return False
        for key, value in fields.items():
            setattr(student, key, value)
        return True

    def remove_student(self, student_id):
        """Removes a student and scrubs their ID from any course rosters they were on."""
        student = self.find_student_by_id(student_id)
        if not student:
            return False
        self.students.remove(student)
        for course in self.courses:
            if student_id in course.enrolled_student_ids:
                course.enrolled_student_ids.remove(student_id)
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

    # --- Teacher Management (ported from PST2) ---

    def add_teacher(self, name, speciality):
        """Creates a new teacher and adds them to the system."""
        new_teacher = TeacherUser(self.next_teacher_id, name, speciality)
        self.teachers.append(new_teacher)
        self.next_teacher_id += 1
        return new_teacher

    def update_teacher(self, teacher_id, **fields):
        """Finds a teacher by ID and updates their attributes with the given fields."""
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            return False
        for key, value in fields.items():
            setattr(teacher, key, value)
        return True

    def remove_teacher(self, teacher_id):
        """Removes a teacher from the system."""
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            return False
        self.teachers.remove(teacher)
        return True

    # --- Course Management ---

    def add_course(self, course_name, teacher_id, instrument=""):
        """Creates a new course taught by the given teacher, auto-assigning a course ID.
        Returns the new Course, or None if the teacher_id doesn't exist."""
        if not self.find_teacher_by_id(teacher_id):
            return None
        new_course = Course(self.next_course_id, course_name, teacher_id, instrument)
        self.courses.append(new_course)
        self.next_course_id += 1
        return new_course

    def remove_course(self, course_id):
        """Removes a course and scrubs it from every enrolled student's course list."""
        course = self.find_course_by_id(course_id)
        if not course:
            return False
        self.courses.remove(course)
        for student in self.students:
            if course_id in student.enrolled_course_ids:
                student.enrolled_course_ids.remove(course_id)
        return True

    # --- Search & Lookup helpers ---

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

    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance_log,
            "next_student_id": self.next_student_id,
            "next_teacher_id": self.next_teacher_id,
            "next_course_id": self.next_course_id
        }
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print("Data successfully saved.")