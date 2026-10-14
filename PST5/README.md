# Music School Management System (MSMS)

A receptionist-facing application for a music school: register students, manage courses and
teachers, view the daily roster, check students in, record payments and export reports.
It was built in five stages (PST1-PST5), each a direct upgrade of the previous one.

| Stage | What it added |
|-------|---------------|
| **PST1** | In-memory console prototype (lists and dictionaries). |
| **PST2** | JSON file storage (`data/msms.json`), input validation, better organisation. |
| **PST3** | Object-oriented redesign: `User` -> `StudentUser` / `TeacherUser`, `Course`, and a `ScheduleManager` controller that owns all business logic. |
| **PST4** | Streamlit GUI in `gui/`, completely separate from the logic in `app/`. |
| **PST5** | Finance and CSV reports, logging, automatic backups, crash-proof loading and an automated pytest suite. |

My PST3/PST4 go beyond the minimum specification (e.g. full course and teacher management pages,
enrol / drop / switch course, student cards), so PST5 is built on that extended version.

## Project structure

```
.
├── app/                      # business logic (no Streamlit in here)
│   ├── user.py               # base User class
│   ├── student.py            # StudentUser(User)
│   ├── teacher.py            # TeacherUser(User) and Course
│   ├── schedule.py           # ScheduleManager - the "brain" (PST3 + finance/logging/etc. from PST5)
│   └── admin_utils.py        # init_logger() and backup_data()          [PST5]
├── gui/                      # Streamlit pages (only call ScheduleManager methods)
│   ├── main_dashboard.py     # layout, sidebar navigation, "Backup data now" button
│   ├── student_pages.py      # search, register, enrol / drop / switch, update, remove, ID card
│   ├── roster_pages.py       # daily roster, check-in, cancel a lesson
│   ├── course_pages.py       # list / add / delete courses
│   ├── teacher_pages.py      # list / add / update / remove teachers
│   └── finance_pages.py      # record payments, payment history, CSV export   [PST5]
├── tests/                    # pytest suite                                  [PST5]
│   ├── test_schedule_manager.py
│   └── test_admin_utils.py
├── data/msms.json            # the database (created/updated automatically)
├── main.py                   # starts logging, takes a backup, launches the GUI
└── requirements.txt
```

## How to run

Run everything from the project root (the folder that directly contains `main.py`, `app/` and `gui/`).

```bash
# 1. create and activate a virtual environment (once)
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)

# 2. install the dependencies inside that environment
pip install -r requirements.txt

# 3. start the app
streamlit run main.py
```

## How to test

```bash
pytest            # runs everything in tests/
pytest -v         # same, listing each test by name
```

The tests never touch your real data: every test builds its own `ScheduleManager` that saves to a
temporary file (pytest's `tmp_path`).

## What each part does

**Student Management** - search students/teachers; register a student (optionally enrolling them
straight away); enrol, drop or switch a student's course; rename or remove a student; generate and
download a printable ID card.

**Daily Roster** - pick a weekday to see which courses have a lesson; check a student in (they must
be enrolled in that course); cancel a lesson with a reason.

**Course Management / Teacher Management** - list, add, update and remove courses and teachers.

**Finance & Payments (PST5)** - record a payment (student, amount, method), view a student's payment
history with a running total, and export the finance or attendance log as a CSV file.

**Sidebar - "Backup data now" (PST5)** - saves and copies the data file into `data/backups/`.

## Data file

`data/msms.json` holds `students`, `teachers`, `courses` (each with its `lessons`), `attendance`,
`finance_log`, and the `next_student_id` / `next_teacher_id` / `next_course_id` counters. Files from
earlier stages without a `finance_log` still load.

## PST5 features in detail

- **Finance engine** (`record_payment`, `get_payment_history`, `export_report`). A payment is rejected
  (nothing recorded, `False` returned) if the student doesn't exist, the amount isn't a positive
  number, or the method is blank. Amounts are rounded to cents.
- **Logging** (`app/admin_utils.py::init_logger`) writes `msms.log` with `timestamp - LEVEL - message`.
  Important business events (registrations, enrolments, payments, removals, exports) are logged at
  INFO; rejected actions and lesson cancellations at WARNING; failures at ERROR.
- **Backups** (`backup_data`) copies `data/msms.json` to `data/backups/msms_backup_<timestamp>.json`
  once when a browser session starts, and on demand from the sidebar button.
- **Crash-proof loading** - a missing data file starts clean; a damaged one (bad JSON, missing keys,
  wrong structure) no longer crashes the app. The problem is logged, a copy of the damaged file is
  kept as `msms.json.corrupt_<timestamp>`, the app starts empty and shows a warning banner.
- **Automated tests** - ~60 pytest tests written Arrange-Act-Assert, each checking one behaviour.

## Design choices and assumptions

- **GUI and logic are separate.** Pages only call `ScheduleManager` methods; all rules live in `app/`.
- **Two-way enrolment.** A student's `enrolled_course_ids` and a course's `enrolled_student_ids` are
  always updated together (enrol, drop, switch, remove student, remove course).
- **IDs are never reused**, even after something is deleted. Stored counters are checked against the
  highest ID in use when loading, so a stale counter can't cause a collision.
- **Check-in requires enrolment.** A student who isn't enrolled in a course can't be checked in to it.
- **`update_student` only changes the name.** Enrolments have their own methods so the two-way link
  can't be broken by a blanket field update.
- **Deleting a student keeps their attendance and payment records.** They are historical/financial
  records; they still appear in the CSV exports.
- **Cancelling a lesson marks it cancelled** (with the reason and time) rather than deleting it. Lessons
  are weekly slots with no calendar date, so a cancellation applies to that weekly slot.
- **Money has no currency symbol** - the school's currency isn't specified, so amounts are plain numbers.
- **Duplicate names are allowed** (two students can both be "Bob Williams"), so every dropdown shows the
  ID as well: `Bob Williams (ID: 3)`.
- **`main.py` only does start-up work once per browser session**, because Streamlit re-runs the script
  on every click; otherwise each click would create a backup.
- Single-user assumption: one receptionist at a time, one data file (no concurrent-edit protection).

## Known limitations

- No login/roles, and no way to add or edit lessons from the GUI (lessons are defined in the data file).
- Old backups are never deleted automatically.
- Cancellation cannot be undone from the GUI.
