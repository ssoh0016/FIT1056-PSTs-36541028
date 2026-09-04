# main.py - The View Layer
from app.schedule import ScheduleManager


def front_desk_daily_roster(manager, day):
    """Displays a pretty table of all lessons on a given day."""
    print(f"\n--- Daily Roster for {day} ---")
    # Notice: This code does not need to change. It doesn't care where the Course class lives.
    # It only talks to the manager.
    # TODO: Call a method on the manager to get the day's lessons and print them.
    lessons = manager.get_daily_roster(day)
    
    if not lessons:
        print("No lessons schduled for this day.")
    else:
        for lesson in lessons:
            print(f"Course: {lesson.course_name} (ID: {lesson.course_id}) | Teacher ID: {lesson.teacher_id}")

def switch_course(manager, student_id, from_course_id, to_course_id):
    # TODO: Implement the logic to switch a student by calling methods on the manager.
    success = manager.switch_student_course(student_id, from_course_id, to_course_id)
    
    if success:
        print(f"Success: Student {student_id} switched from {from_course_id} to {to_course_id}.")
    else:
        print(f"Error: Could not switch process. Please verify the IDs and ensure the student is enrolled in the original course.")

def main():
    """Main function to run the MSMS application."""
    manager = ScheduleManager() # Create ONE instance of the application brain.
    
    while True:
        print("\n===== MSMS v3 (Object-Oriented) =====")
        # TODO: Create a menu for the new PST3 functions.
        # Get user input and call the appropriate view function, passing 'manager' to it.
        print("1. View Daily Roster")
        print("2. Check-in Student")
        print("3. Switch Course")
        print("q. Quit and Save")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            day = input("Enter day (e.g., Monday): ")
            front_desk_daily_roster(manager, day)
            
        elif choice == '2':
            try:
                s_id = int(input("Enter Student ID: "))
                c_id = input("Enter Course ID: ")
                # Manage handles the actual check-in logic
                manager.check_in(s_id, c_id)
            except ValueError:
                print ("Invalid input.")
                
        elif choice == '3':
            switch_course(manager)
        
        elif choice == 'q':
            print("Saving and exiting...")
            manager._save_data()
            break
        
        
if __name__ == "__main__":
    main()