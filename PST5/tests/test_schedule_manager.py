# tests/test_schedule_manager.py
import csv
import json
import logging

import pytest
from app.schedule import ScheduleManager


# ======================================================================
# Fixtures - each test gets its own clean environment
# ======================================================================
@pytest.fixture
def fresh_manager(tmp_path):
    """A brand-new, empty ScheduleManager saving to a temporary file (never your real data)."""
    return ScheduleManager(data_path=str(tmp_path / "test_data.json"))


@pytest.fixture
def school(fresh_manager):
    """A manager pre-loaded with: 1 teacher, 1 course with two lessons (Mon + Wed),
    and 2 students - Alice (enrolled in the course) and Bob (not enrolled)."""
    m = fresh_manager
    teacher = m.add_teacher("Dr. Keys", "Piano")
    course = m.add_course("Beginner Piano", teacher.id, "Piano")
    course.lessons.append({"lesson_id": 1, "day": "Monday", "start_time": "16:00", "room": "Room A"})
    course.lessons.append({"lesson_id": 2, "day": "Wednesday", "start_time": "16:00", "room": "Room A"})
    m.register_student("Alice", course.course_id)
    m.register_student("Bob")
    return m


@pytest.fixture
def log_records():
    """Collects everything logged at INFO or above during a test, then restores the logger."""
    records = []

    class Collector(logging.Handler):
        def emit(self, record):
            records.append(record)

    root = logging.getLogger()
    handler = Collector()
    old_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    yield records
    root.removeHandler(handler)
    root.setLevel(old_level)


# ======================================================================
# Courses
# ======================================================================
def test_add_course_creates_course(fresh_manager):
    # ARRANGE: a course needs an existing teacher.
    teacher = fresh_manager.add_teacher("Dr. Keys", "Piano")
    # ACT
    course = fresh_manager.add_course("Beginner Piano", teacher.id, "Piano")
    # ASSERT
    assert len(fresh_manager.courses) == 1
    assert fresh_manager.courses[0].course_name == "Beginner Piano"
    assert course.teacher_id == teacher.id


def test_add_course_rejects_unknown_teacher(fresh_manager):
    # ACT: there are no teachers at all, so teacher ID 99 can't exist.
    result = fresh_manager.add_course("Ghost Class", 99, "Piano")
    # ASSERT
    assert result is None
    assert fresh_manager.courses == []


def test_remove_course_scrubs_student_enrolments(school):
    # ARRANGE
    course = school.courses[0]
    alice = school.students[0]
    # ACT
    removed = school.remove_course(course.course_id)
    # ASSERT
    assert removed is True
    assert school.courses == []
    assert alice.enrolled_course_ids == []


# ======================================================================
# Students & enrolment
# ======================================================================
def test_register_student_assigns_incrementing_ids(fresh_manager):
    first, _ = fresh_manager.register_student("First")
    second, _ = fresh_manager.register_student("Second")
    assert (first.id, second.id) == (1, 2)


def test_register_student_with_course_enrols_both_sides(school):
    # ARRANGE
    course = school.courses[0]
    # ACT
    student, enrolled = school.register_student("Cara", course.course_id)
    # ASSERT
    assert enrolled is True
    assert course.course_id in student.enrolled_course_ids
    assert student.id in course.enrolled_student_ids


def test_register_student_with_unknown_course_still_registers(school):
    student, enrolled = school.register_student("Cara", 999)
    assert enrolled is False
    assert student in school.students
    assert student.enrolled_course_ids == []


def test_enrol_student_updates_both_sides(school):
    bob, course = school.students[1], school.courses[0]
    assert school.enrol_student(bob.id, course.course_id) is True
    assert course.course_id in bob.enrolled_course_ids
    assert bob.id in course.enrolled_student_ids


def test_enrol_student_twice_does_not_duplicate(school):
    alice, course = school.students[0], school.courses[0]   # Alice is already enrolled
    school.enrol_student(alice.id, course.course_id)
    assert alice.enrolled_course_ids.count(course.course_id) == 1
    assert course.enrolled_student_ids.count(alice.id) == 1


def test_enrol_unknown_student_returns_false(school):
    assert school.enrol_student(999, school.courses[0].course_id) is False


def test_drop_student_course_updates_both_sides(school):
    alice, course = school.students[0], school.courses[0]
    assert school.drop_student_course(alice.id, course.course_id) is True
    assert alice.enrolled_course_ids == []
    assert course.enrolled_student_ids == []


def test_drop_student_course_not_enrolled_returns_false(school):
    bob, course = school.students[1], school.courses[0]   # Bob isn't enrolled
    assert school.drop_student_course(bob.id, course.course_id) is False


def test_switch_student_course_moves_enrolment(school):
    # ARRANGE: a second course to switch into.
    alice, old_course = school.students[0], school.courses[0]
    new_course = school.add_course("Intermediate Piano", school.teachers[0].id, "Piano")
    # ACT
    result = school.switch_student_course(alice.id, old_course.course_id, new_course.course_id)
    # ASSERT
    assert result is True
    assert alice.enrolled_course_ids == [new_course.course_id]
    assert alice.id not in old_course.enrolled_student_ids
    assert alice.id in new_course.enrolled_student_ids


def test_switch_to_unknown_course_changes_nothing(school):
    alice, course = school.students[0], school.courses[0]
    result = school.switch_student_course(alice.id, course.course_id, 999)
    assert result is False
    assert alice.enrolled_course_ids == [course.course_id]
    assert alice.id in course.enrolled_student_ids


def test_update_student_changes_name(school):
    assert school.update_student(school.students[0].id, name="Alicia") is True
    assert school.students[0].name == "Alicia"


def test_remove_student_scrubs_course_roster(school):
    alice, course = school.students[0], school.courses[0]
    assert school.remove_student(alice.id) is True
    assert alice not in school.students
    assert alice.id not in course.enrolled_student_ids


def test_remove_unknown_student_returns_false(school):
    assert school.remove_student(999) is False


# ======================================================================
# Daily roster
# ======================================================================
def test_daily_roster_returns_courses_with_a_lesson_that_day(school):
    roster = school.get_daily_roster("Monday")
    assert roster == [school.courses[0]]


def test_daily_roster_is_empty_when_no_lessons_that_day(school):
    assert school.get_daily_roster("Tuesday") == []


def test_daily_roster_ignores_case_and_spaces(school):
    assert school.get_daily_roster("  monday ") == [school.courses[0]]


def test_daily_roster_lists_a_course_once_even_with_two_lessons_that_day(school):
    school.courses[0].lessons.append(
        {"lesson_id": 3, "day": "Monday", "start_time": "18:00", "room": "Room B"})
    assert school.get_daily_roster("Monday") == [school.courses[0]]


# ======================================================================
# Check-in
# ======================================================================
def test_check_in_records_attendance(school):
    alice, course = school.students[0], school.courses[0]
    assert school.check_in(alice.id, course.course_id) is True
    assert len(school.attendance_log) == 1
    record = school.attendance_log[0]
    assert record["student_id"] == alice.id
    assert record["course_id"] == course.course_id
    assert "timestamp" in record


def test_check_in_rejects_student_who_is_not_enrolled(school):
    bob, course = school.students[1], school.courses[0]
    assert school.check_in(bob.id, course.course_id) is False
    assert school.attendance_log == []


def test_check_in_rejects_unknown_ids(school):
    assert school.check_in(999, 999) is False
    assert school.attendance_log == []


# ======================================================================
# Finance (Fragment 5.1)
# ======================================================================
def test_record_payment_and_history(school):
    # ARRANGE: Alice is already a student in the `school` fixture.
    student_id_to_test = school.students[0].id

    # ACT: Record a payment for that student.
    result = school.record_payment(student_id_to_test, 100.00, "Credit Card")

    # ACT 2: Get the payment history.
    history = school.get_payment_history(student_id_to_test)

    # ASSERT: Check the results.
    assert result is True
    assert len(history) == 1
    assert history[0]['amount'] == 100.00
    assert history[0]['method'] == "Credit Card"


def test_get_payment_history_no_results(school):
    # Bob exists but has never paid anything.
    assert school.get_payment_history(school.students[1].id) == []


def test_get_payment_history_only_returns_that_students_payments(school):
    alice, bob = school.students
    school.record_payment(alice.id, 50, "Cash")
    school.record_payment(bob.id, 70, "Cash")
    history = school.get_payment_history(bob.id)
    assert len(history) == 1
    assert history[0]['amount'] == 70


def test_record_payment_stores_a_timestamp(school):
    school.record_payment(school.students[0].id, 10, "Cash")
    assert school.finance_log[0]["timestamp"]


def test_record_payment_rounds_amount_to_cents(school):
    school.record_payment(school.students[0].id, 19.999, "Cash")
    assert school.finance_log[0]["amount"] == 20.0


def test_record_payment_rejects_unknown_student(school):
    assert school.record_payment(999, 50, "Cash") is False
    assert school.finance_log == []


def test_record_payment_rejects_invalid_amounts(school):
    alice_id = school.students[0].id
    for bad_amount in [0, -5, "abc", None, float("nan"), float("inf")]:
        assert school.record_payment(alice_id, bad_amount, "Cash") is False
    assert school.finance_log == []


def test_record_payment_rejects_blank_method(school):
    assert school.record_payment(school.students[0].id, 50, "   ") is False
    assert school.finance_log == []


# ======================================================================
# CSV export (Fragment 5.1)
# ======================================================================
def test_export_finance_report_writes_csv(school, tmp_path):
    # ARRANGE
    alice = school.students[0]
    school.record_payment(alice.id, 100, "Cash")
    school.record_payment(alice.id, 25.5, "Credit Card")
    out_file = tmp_path / "finance.csv"
    # ACT
    result = school.export_report("finance", str(out_file))
    # ASSERT
    with open(out_file, newline="") as f:
        rows = list(csv.DictReader(f))
    assert result is True
    assert [row["method"] for row in rows] == ["Cash", "Credit Card"]
    assert float(rows[1]["amount"]) == 25.5
    assert rows[0]["student_id"] == str(alice.id)


def test_export_attendance_report_writes_csv(school, tmp_path):
    alice, course = school.students[0], school.courses[0]
    school.check_in(alice.id, course.course_id)
    out_file = tmp_path / "attendance.csv"
    assert school.export_report("attendance", str(out_file)) is True
    with open(out_file, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["course_id"] == str(course.course_id)


def test_export_report_with_no_data_writes_header_only(school, tmp_path):
    out_file = tmp_path / "empty.csv"
    assert school.export_report("finance", str(out_file)) is True
    assert out_file.read_text().strip() == "student_id,amount,method,timestamp"


def test_export_report_creates_missing_folder(school, tmp_path):
    out_file = tmp_path / "reports" / "nested" / "finance.csv"
    assert school.export_report("finance", str(out_file)) is True
    assert out_file.exists()


def test_export_unknown_report_type_returns_false_and_writes_nothing(school, tmp_path):
    out_file = tmp_path / "nope.csv"
    assert school.export_report("salaries", str(out_file)) is False
    assert not out_file.exists()


# ======================================================================
# Persistence & crash-proof loading
# ======================================================================
def test_data_round_trip_restores_everything(school):
    # ARRANGE: these calls save the whole state to the temp file.
    alice, course = school.students[0], school.courses[0]
    school.check_in(alice.id, course.course_id)
    school.record_payment(alice.id, 120.5, "Cash")
    # ACT: load a second manager from the same file.
    reloaded = ScheduleManager(data_path=school.data_path)
    # ASSERT
    assert [s.name for s in reloaded.students] == ["Alice", "Bob"]
    assert reloaded.students[0].enrolled_course_ids == [course.course_id]
    assert [t.name for t in reloaded.teachers] == ["Dr. Keys"]
    assert reloaded.courses[0].course_name == "Beginner Piano"
    assert len(reloaded.courses[0].lessons) == 2
    assert reloaded.attendance_log == school.attendance_log
    assert reloaded.finance_log == school.finance_log


def test_id_counters_survive_reload(school):
    school._save_data()
    reloaded = ScheduleManager(data_path=school.data_path)
    new_student, _ = reloaded.register_student("Cara")
    new_teacher = reloaded.add_teacher("Mr. Fret", "Guitar")
    new_course = reloaded.add_course("Guitar 101", new_teacher.id, "Guitar")
    assert (new_student.id, new_teacher.id, new_course.course_id) == (3, 2, 2)


def test_stale_id_counter_is_repaired_on_load(tmp_path):
    # ARRANGE: counter says 1, but a student with ID 5 already exists.
    path = tmp_path / "stale.json"
    path.write_text(json.dumps({
        "students": [{"id": 5, "name": "Eve", "enrolled_course_ids": []}],
        "next_student_id": 1
    }))
    manager = ScheduleManager(data_path=str(path))
    assert manager.next_student_id == 6


def test_missing_data_file_starts_clean(tmp_path):
    manager = ScheduleManager(data_path=str(tmp_path / "does_not_exist.json"))
    assert manager.students == [] and manager.courses == [] and manager.finance_log == []
    assert manager.load_error is None


def test_old_data_file_without_finance_log_still_loads(tmp_path):
    path = tmp_path / "old.json"
    path.write_text(json.dumps({"students": [], "teachers": [], "courses": [], "attendance": []}))
    manager = ScheduleManager(data_path=str(path))
    assert manager.finance_log == []
    assert manager.load_error is None


def test_corrupt_json_does_not_crash(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{this is not valid json")
    manager = ScheduleManager(data_path=str(path))
    assert manager.students == [] and manager.courses == [] and manager.finance_log == []
    assert manager.load_error is not None


def test_corrupt_json_is_copied_aside(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{this is not valid json")
    ScheduleManager(data_path=str(path))
    copies = list(tmp_path.glob("broken.json.corrupt_*"))
    assert len(copies) == 1
    assert copies[0].read_text() == "{this is not valid json"


def test_json_missing_a_required_key_does_not_crash(tmp_path):
    path = tmp_path / "missing_key.json"
    path.write_text(json.dumps({"students": [{"id": 1}]}))   # no "name"
    manager = ScheduleManager(data_path=str(path))
    assert manager.students == []
    assert "KeyError" in manager.load_error


def test_json_with_wrong_structure_does_not_crash(tmp_path):
    path = tmp_path / "wrong_shape.json"
    path.write_text("[1, 2, 3]")   # valid JSON, but not the object we expect
    manager = ScheduleManager(data_path=str(path))
    assert manager.students == []
    assert manager.load_error is not None


def test_save_creates_missing_data_folder(tmp_path):
    path = tmp_path / "brand_new_folder" / "msms.json"
    manager = ScheduleManager(data_path=str(path))
    manager._save_data()
    assert path.exists()


# ======================================================================
# Lesson cancellation (Fragment 5.2 template)
# ======================================================================
def test_cancel_lesson_removes_it_from_the_roster(school):
    assert school.cancel_lesson(1, "Teacher is ill") is True
    assert school.get_daily_roster("Monday") == []
    assert school.get_daily_roster("Wednesday") == [school.courses[0]]   # other lesson unaffected


def test_cancel_lesson_keeps_the_reason_on_record(school):
    school.cancel_lesson(1, "Teacher is ill")
    lesson = school.courses[0].lessons[0]
    assert lesson["cancelled"] is True
    assert lesson["cancel_reason"] == "Teacher is ill"


def test_cancel_unknown_lesson_returns_false(school):
    assert school.cancel_lesson(999, "No such lesson") is False


def test_cancel_lesson_requires_a_reason(school):
    assert school.cancel_lesson(1, "  ") is False
    assert len(school.get_daily_roster("Monday")) == 1


def test_cancel_lesson_twice_returns_false(school):
    school.cancel_lesson(1, "First time")
    assert school.cancel_lesson(1, "Second time") is False


# ======================================================================
# Logging (Fragment 5.4 integration)
# ======================================================================
def test_record_payment_writes_an_info_log(school, log_records):
    school.record_payment(school.students[0].id, 25, "Cash")
    matches = [r for r in log_records if "Payment of 25.0 recorded for student ID 1" in r.getMessage()]
    assert len(matches) == 1
    assert matches[0].levelno == logging.INFO


def test_register_student_writes_an_info_log(fresh_manager, log_records):
    fresh_manager.register_student("Zoe")
    assert any("Registered student 'Zoe'" in r.getMessage() and r.levelno == logging.INFO
               for r in log_records)


def test_cancel_lesson_writes_a_warning_log(school, log_records):
    school.cancel_lesson(1, "Teacher is ill")
    matches = [r for r in log_records if "Lesson ID 1 was cancelled" in r.getMessage()]
    assert len(matches) == 1
    assert matches[0].levelno == logging.WARNING


def test_rejected_payment_writes_a_warning_log(school, log_records):
    school.record_payment(999, 50, "Cash")
    assert any(r.levelno == logging.WARNING and "unknown student" in r.getMessage()
               for r in log_records)
