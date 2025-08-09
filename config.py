def get_weight_unit(user_dir):
    """Return the current weight unit for the user."""
    config = load_config(user_dir)
    return config['units']['weight']
import json
import os


def load_config(user_dir):
    user_dir = user_dir.rstrip('/')
    file_path=os.path.join(user_dir, 'settings.json')
    """Load configuration settings from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"\nConfiguration file '{file_path}' not found.")
    
    with open(file_path, 'r') as file:
        try:
            config = json.load(file)
            return config
        except json.JSONDecodeError:
            raise ValueError("\nError decoding JSON from the configuration file.")

def set_weight_unit(unit, file_path='settings.json'):
    """Set the weight unit in the configuration file and convert existing weights."""
    config = load_config(file_path)
    if unit not in ['kg', 'lb']:
        raise ValueError("\nWeight unit must be 'kg' or 'lb'.")
    current_unit = config['units']['weight']
    if current_unit != unit:
        user_dir = os.path.dirname(file_path)
        convert_weights(current_unit, unit, os.path.join(user_dir, 'workouts.json'))
    config['units']['weight'] = unit
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)
    print("\n")
    print(f"Weight unit set to {unit}.")

def convert_weights(current_unit, new_unit, workouts_file):
    """Convert all logged weights from current unit to new unit."""
    conversion_factor = 2.20462 if new_unit == 'lb' else 0.453592
    if not os.path.exists(workouts_file):
        print("\nNo workouts found")
        return
    with open(workouts_file, 'r') as file:
        try:
            workouts = json.load(file)
        except json.JSONDecodeError:
            print("\nError decoding JSON from the workouts file.")
            return
    for workout in workouts:
        if 'weights' in workout:
            weight = float(workout['weights'])
            converted_weight = weight * conversion_factor
            workout['weights'] = round(converted_weight, 2)
    with open(workouts_file, 'w') as file:
        json.dump(workouts, file, indent=4)
    print("\nAll weights have been converted to the new unit.")
