import json
import os
import datetime
from config import get_weight_unit

def load_workouts(file_path):
    """Load workouts from a JSON file."""
    if not os.path.exists(file_path):
        return []
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as file:
        try:
            workouts = json.load(file)
            return workouts
        except json.JSONDecodeError:
            print("Error decoding JSON from the workouts file.")
            return []

def save_workouts(workouts, file_path):
    """Save workouts to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(workouts, file, indent=4)

def view_workouts(user_dir):
    """View all workouts."""
    workouts = load_workouts(os.path.join(user_dir, 'workouts.json'))
    if not workouts:
        return

    # Print header with new order: Type, Date, Muscle, Weights, Notes
    print("\n")
    print(f"{'#':<3} {'Type':<10} {'Date':<18} {'Muscle':<12} {'Weights':<10} {'Notes':<20}")
    print('-' * 75)
    # Get weight unit using config helper
    try:
        weight_unit = get_weight_unit(user_dir)
    except Exception:
        weight_unit = ''
    for index, workout in enumerate(workouts):
        # Format date as 'Aug 8th, 2025'
        try:
            date_obj = datetime.datetime.strptime(workout['date'], "%Y-%m-%d")
            day = date_obj.day
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]
            formatted_date = date_obj.strftime(f"%b {day}{suffix}, %Y")
        except Exception:
            formatted_date = workout['date']
        weights = workout.get('weights', 'N/A')
        if weights != 'N/A' and weight_unit:
            weights = f"{weights} {weight_unit}"
        print(f"{index + 1:<3} {workout['type']:<10} {formatted_date:<18} {str(workout.get('muscle', 'N/A')):<12} {weights:<10} {workout.get('notes', ''):<20}")

def edit_workout(index, user_dir):
    """Edit a specific workout."""
    workouts = load_workouts(os.path.join(user_dir, 'workouts.json'))
    if index < 0 or index >= len(workouts):
        print("Invalid workout index")
        return

    workout = workouts[index]
    print("Current workouts:")
    view_workouts(user_dir)
    print(f"Editing workout #{index + 1}:")
    new_type = input("Enter the new type of workout: ")
    if new_type.strip():
        workout['type'] = new_type
    new_date = input("Enter the new date (YYYY-MM-DD): ")
    if new_date.strip():
        workout['date'] = new_date
    if workout['type'].strip().lower() == "strength":
        try:
            weight_unit = get_weight_unit(user_dir)
        except Exception:
            weight_unit = ''
        while True:
            weights_input = input(f"Enter the weights used in ({weight_unit}): ").strip()
            if not weights_input:
                print("\nInvalid weights. Please enter a number between 0 and 500.")
                continue
            try:
                weights_val = float(weights_input)
                if 0 <= weights_val <= 500:
                    workout['weights'] = weights_input
                    break
                else:
                    print("\nInvalid weights. Please enter a number between 0 and 500.")
            except ValueError:
                print("\nInvalid weights. Please enter a number between 0 and 500.")
    workout['notes'] = input("Enter any notes: ")
    save_workouts(workouts, os.path.join(user_dir, 'workouts.json'))

def delete_workout(index, user_dir):
    """Delete a specific workout."""
    workouts = load_workouts(os.path.join(user_dir, 'workouts.json'))
    print("Current workouts:")
    view_workouts(user_dir)
    if index < 0 or index >= len(workouts):
        print("Invalid workout index")
        return
    workouts.pop(index)
    save_workouts(workouts, os.path.join(user_dir, 'workouts.json'))
    print("Workout deleted successfully.")

def manage_workouts(user_dir):
    """Manage workouts: view, edit, or delete."""
    while True:
        workouts = load_workouts(os.path.join(user_dir, 'workouts.json'))
        if not workouts:
            print("\nNo workouts available")
            break
        print("\n===========WORKOUT MANAGER===========")
        print("v: View workouts")
        print("e: Edit a workout")
        print("d: Delete a workout")
        print("m: Back to main menu")
        print("=====================================")
        choice = input("Select an option: ").strip().lower()
        if choice == 'v':
            view_workouts(user_dir)
        elif choice == 'e':
            view_workouts(user_dir)
            index = int(input("Enter the workout number to edit: ")) - 1
            edit_workout(index, user_dir)
        elif choice == 'd':
            view_workouts(user_dir)
            index = int(input("Enter the workout number to delete: ")) - 1
            delete_workout(index, user_dir)
        elif choice == 'm':
            break
        else:
            print("Invalid option. Try again.")

# Example usage
if __name__ == "__main__":
    print("Please run from main.py")
