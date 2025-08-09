import json
import datetime
import os
from config import load_config

def load_muscle_groups(file_path='muscle_groups.json'):
    """Load muscle groups from a JSON file."""
    if not os.path.exists(file_path):
        print("Muscle groups file not found.")
        return []
    
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            return data.get('muscle_groups', [])
        except json.JSONDecodeError:
            print("Error decoding JSON from the muscle groups file.")
            return []

def log_workout(user_dir):
    """Log a workout entry."""
    workout = {}
    # Automatically use today's date
    workout['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    while True:
        workout_type = input("Enter the type of workout (e.g., Cardio, Strength): ").strip()
        if workout_type:
            workout['type'] = workout_type
            break
        else:
            print("Workout type cannot be blank. Please enter a workout type.")
    if workout['type'].strip().lower() == "strength":
        muscle_groups = load_muscle_groups()
        workout['muscle'] = input(f"Enter the muscle group worked ({', '.join(muscle_groups)}): ").strip().lower()
        # Validate muscle group
        if workout['muscle'] not in muscle_groups:
            print("Invalid muscle group. Please enter a valid muscle group.")
            return
        config = load_config(os.path.join(user_dir, 'settings.json'))
        weight_unit = config['units']['weight']
        workout['weights'] = input(f"Enter the weights used in ({weight_unit}): ")
    workout['notes'] = input("Enter any additional notes: ")
    # Save the workout to the user's workouts.json
    workouts = load_workouts(os.path.join(user_dir, 'workouts.json'))
    workouts.append(workout)
    save_workouts(workouts, os.path.join(user_dir, 'workouts.json'))

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

# Example usage
if __name__ == "__main__":
    log_workout()
