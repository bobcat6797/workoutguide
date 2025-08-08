import json
import sys
from config import load_config, set_weight_unit
from log_workout import log_workout
from stats import display_stats
from workout_manager import manage_workouts

def main():
    config = load_config()
    
    while True:
        print("\nWelcome to the Workout Tracker!")
        print("1. Log a workout")
        print("2. View stats")
        print("3. Manage workouts")
        print("4. Change weight unit")
        print("5. Exit")
        
        choice = input("Please select an option: ")
        
        if choice == '1':
            log_workout()
        elif choice == '2':
            display_stats()
        elif choice == '3':
            manage_workouts()
        elif choice == '4':
            new_unit = input("Enter the new weight unit (kg/lb): ").strip().lower()
            try:
                set_weight_unit(new_unit)
            except ValueError as e:
                print(e)
        elif choice == '5':
            print("Exiting the application. Goodbye!")
            sys.exit()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
