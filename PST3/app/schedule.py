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
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                
                for s in data.get("students", []):
                    self.students.append(StudentUser(s["id"], s["name"], s.get("enrolled_in", [])))
                    
                for t in data.get("teachers", []):
                    self.teachers.append(TeacherUser(t["id"], t["name"], t["speciality"]))
                    
                for c in data.get("courses", []):
                    self.courses.append(Course(c["course_id"], c["course_name"], c["teacher_id"]))
                    
                self.attendance_log = data.get("attendance", [])
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")
    
    def switch_student_course(self, student_id, from_course_id, to_course_id):
        """Finds the student, removes the old course, and appends the new one."""
        for student in self.students:
            if student.id == student_id:
                if from_course_id in student.enrolled_in:
                    student.enrolled_in.remove(from_course_id)
                    student.enrolled_in.append(to_course_id)
                    return True
        return False    
    
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

    def find_student_by_id(self, student_id):
        """Helper to find a student object by their ID."""
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def find_course_by_id(self, course_id):
        """Helper to find a course object by its ID."""
        for course in self.courses:
            if course.course_id == course_id:
                return course
        return None
        
    def get_daily_roster(self, day):
        """Retrieves lessons for a specific day."""
        return self.courses

    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance_log,
            "next_student_id": getattr(self, 'next_student_id', 1),
            "next_teacher_id": getattr(self, 'next_teacher_id', 1)
        }
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print("Data successfully saved.")