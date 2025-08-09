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

def log_workout():
    """Log a workout entry."""
    workout = {}
    
    # Automatically use today's date
    workout['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    workout['type'] = input("Enter the type of workout (e.g., Cardio, Strength): ")

    if workout['type'].strip().lower() == "strength":
        muscle_groups = load_muscle_groups()
        workout['muscle'] = input(f"Enter the muscle group worked ({', '.join(muscle_groups)}): ").strip().lower()
        # Validate muscle group
        if workout['muscle'] not in muscle_groups:
            print("Invalid muscle group. Please enter a valid muscle group.")
            return
        config = load_config()
        weight_unit = config['units']['weight']
        workout['weights'] = input(f"Enter the weights used in ({weight_unit}): ")
    workout['notes'] = input("Enter any additional notes: ")
    # For cardio, skip muscle/weight
    # Save the workout to workouts.json
    workouts = load_workouts()
    workouts.append(workout)
    save_workouts(workouts)

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
