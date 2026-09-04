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

def switch_course(manager):
    # TODO: Implement the logic to switch a student by calling methods on the manager.
    print("\n--- Switch Course ---")
    try:
        s_id = int(input("Enter Student ID: "))
        from_c = input("Enter current Course ID to drop: ")
        to_c = input("Enter new Course ID to add: ")
        
        # Pass the data to the manager to do the actual work
        if manager.switch_student_course(s_id, from_c, to_c):
            print(f"Success: Student {s_id} switched from {from_c} to {to_c}.")
        else:
            print("Error: Could not switch course. Please check the IDs.")
    except ValueError:
        print("Invalid input. Student ID must be a number.")

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
                c_id = int(input("Enter Course ID: "))
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