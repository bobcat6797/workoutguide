import json
import os

def display_stats():
    """Display workout statistics."""
    workouts_file = 'workouts.json'
    if not os.path.exists(workouts_file):
        print("No workouts found")
        return
    with open(workouts_file, 'r') as file:
        try:
            workouts = json.load(file)
        except json.JSONDecodeError:
            print("Error decoding JSON from the workouts file.")
            return
    total_workouts = len(workouts)
    if total_workouts > 0:
        print("\n")
        print(f"Total workouts logged: {total_workouts}")
    else:
        print("\n")
        print("No workouts logged")

# Example usage
if __name__ == "__main__":
    display_stats()
