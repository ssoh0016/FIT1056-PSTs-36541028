from app.user import User

class TeacherUser(User):
    """Represents a teacher."""
    # TODO: Implement the TeacherUser class, inheriting from User.
    # It should have an additional 'speciality' attribute in its __init__.
    def __init__(self, user_id, name, speciality):
        super().__init__(user_id, name)
        self.speciality = speciality

class Course:
    """Represents a single course offered by the school, linked to a teacher."""
    def __init__(self, course_id, course_name, teacher_id, instrument="", enrolled_student_ids=None, lessons=None):
        self.course_id = course_id
        self.course_name = course_name
        self.instrument = instrument
        self.teacher_id = teacher_id
        # TODO: Initialize two empty lists: 'enrolled_student_ids' and 'lessons'.
        self.enrolled_student_ids = enrolled_student_ids if enrolled_student_ids is not None else []
        self.lessons =  lessons if lessons is not None else [] # This will hold lesson dictionaries