import json
import os

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

    for index, workout in enumerate(workouts):
        print(f"{index + 1}. Date: {workout['date']}, Type: {workout['type']}, Duration: {workout['duration']} minutes, Weights: {workout.get('weights', 'N/A')}")

def edit_workout(index):
    """Edit a specific workout."""
    workouts = load_workouts()
    if index < 0 or index >= len(workouts):
        print("Invalid workout index.")
        return

    workout = workouts[index]
    print(f"Editing workout: {workout}")

    workout['type'] = input("Enter the new type of workout: ")
    workout['duration'] = input("Enter the new duration of the workout (in minutes): ")
    workout['notes'] = input("Enter any new additional notes: ")

    # Ask for weights if the workout type is Weightlifting
    if workout['type'].strip().lower() == "weightlifting":
        workout['weights'] = input("Enter the new weights used: ")

    save_workouts(workouts)

def delete_workout(index):
    """Delete a specific workout."""
    workouts = load_workouts()
    if index < 0 or index >= len(workouts):
        print("Invalid workout index.")
        return

    workouts.pop(index)
    save_workouts(workouts)
    print("Workout deleted successfully.")

def manage_workouts():
    """Manage workouts: view, edit, or delete."""
    while True:
        print("\nWorkout Manager")
        print("1. View workouts")
        print("2. Edit a workout")
        print("3. Delete a workout")
        print("4. Back to main menu")
        
        choice = input("Please select an option: ")
        
        if choice == '1':
            view_workouts()
        elif choice == '2':
            index = int(input("Enter the workout number to edit: ")) - 1
            edit_workout(index)
        elif choice == '3':
            index = int(input("Enter the workout number to delete: ")) - 1
            delete_workout(index)
        elif choice == '4':
            break
        else:
            print("Invalid option. Please try again.")

# Example usage
if __name__ == "__main__":
    manage_workouts()
