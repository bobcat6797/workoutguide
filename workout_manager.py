import json
import os
import datetime

def load_workouts(file_path='workouts.json'):
    """Load workouts from a JSON file."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as file:
        try:
            workouts = json.load(file)
            return workouts
        except json.JSONDecodeError:
            print("Error decoding JSON from the workouts file.")
            return []

def save_workouts(workouts, file_path='workouts.json'):
    """Save workouts to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(workouts, file, indent=4)

def view_workouts():
    """View all workouts."""
    workouts = load_workouts()
    if not workouts:
        print("No workouts found.")
        return

    # Print header with new order: Type, Date, Muscle, Weights, Notes
    print("\n")
    print(f"{'#':<3} {'Type':<10} {'Date':<18} {'Muscle':<12} {'Weights':<10} {'Notes':<20}")
    print('-' * 75)
    # Load weight unit from settings.json
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            weight_unit = settings['units']['weight']
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

def edit_workout(index):
    """Edit a specific workout."""
    workouts = load_workouts()
    if index < 0 or index >= len(workouts):
        print("Invalid workout index.")
        return

    workout = workouts[index]
    print("Current workouts:")
    view_workouts()
    print(f"Editing workout #{index + 1}:")
    new_type = input("Enter the new type of workout: ")
    if new_type.strip():
        workout['type'] = new_type
    new_date = input("Enter the new date (YYYY-MM-DD): ")
    if new_date.strip():
        workout['date'] = new_date
    workout['notes'] = input("Enter any new additional notes: ")
    if workout['type'].strip().lower() == "strength":
        workout['weights'] = input("Enter the weights used: ")
    save_workouts(workouts)

def delete_workout(index):
    """Delete a specific workout."""
    workouts = load_workouts()
    print("Current workouts:")
    view_workouts()
    if index < 0 or index >= len(workouts):
        print("Invalid workout index")
        return
    workouts.pop(index)
    save_workouts(workouts)
    print("Workout deleted successfully.")

def manage_workouts():
    """Manage workouts: view, edit, or delete."""
    while True:
        workouts = load_workouts()
        if not workouts:
            print("No workouts available")
            break
        print("\n===========Workout Manager===========")
        print("1. View workouts")
        print("2. Edit a workout")
        print("3. Delete a workout")
        print("4. Back to main menu")
        print("=====================================")
        choice = input("\nPlease select an option: ")
        if choice == '1':
            view_workouts()
        elif choice == '2':
            view_workouts()
            index = int(input("Enter the workout number to edit: ")) - 1
            edit_workout(index)
        elif choice == '3':
            view_workouts()
            index = int(input("Enter the workout number to delete: ")) - 1
            delete_workout(index)
        elif choice == '4':
            break
        else:
            print("Invalid option. Please try again.")

# Example usage
if __name__ == "__main__":
    manage_workouts()
