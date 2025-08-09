import json
import sys
from config import load_config, set_weight_unit
from log_workout import log_workout
from stats import display_stats
from workout_manager import manage_workouts

def settings_menu():
    while True:
        config = load_config()
        current_unit = config['units']['weight']
        print("\n===========Settings===========")
        print(f"Current weight unit: {current_unit}")
        print("1. Change weight unit")
        print("2. Back to main menu")
        print("==============================")
        choice = input("Select an option (1-2): ")
        if choice == '1':
            new_unit = 'kg' if current_unit == 'lb' else 'lb'
            confirm = input(f"Change weight unit to {new_unit}? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    set_weight_unit(new_unit)
                except ValueError as e:
                    print(e)
        elif choice == '2':
            break
        else:
            print("Invalid option. Try again.")

def main():
    while True:
        print("\n===========Workout Guide===========")
        print("1. Log a workout")
        print("2. View stats")
        print("3. Manage workouts")
        print("4. Settings")
        print("5. Exit")
        print("===================================")
        choice = input("Select an option(1-5): ")
        if choice == '1':
            log_workout()
        elif choice == '2':
            display_stats()
        elif choice == '3':
            manage_workouts()
        elif choice == '4':
            settings_menu()
        elif choice == '5':
            print("Exiting the application")
            sys.exit()
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
