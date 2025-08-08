import json
import os

def display_stats():
    """Display workout statistics."""
    log_file_path = 'workout_log.txt'
    
    if not os.path.exists(log_file_path):
        print("No workout log found.")
        return

    total_workouts = 0
    total_duration = 0

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            workout = json.loads(line)
            total_workouts += 1
            total_duration += int(workout.get('duration', 0))

    if total_workouts > 0:
        average_duration = total_duration / total_workouts
        print(f"Total workouts logged: {total_workouts}")
        print(f"Average workout duration: {average_duration:.2f} minutes")
    else:
        print("No workouts logged yet.")

# Example usage
if __name__ == "__main__":
    display_stats()
