import json
import os

def load_config(file_path='settings.json'):
    """Load configuration settings from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file '{file_path}' not found.")
    
    with open(file_path, 'r') as file:
        try:
            config = json.load(file)
            return config
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON from the configuration file.")

def set_weight_unit(unit, file_path='settings.json'):
    """Set the weight unit in the configuration file and convert existing weights."""
    config = load_config(file_path)
    if unit not in ['kg', 'lb']:
        raise ValueError("Weight unit must be 'kg' or 'lb'.")
    
    current_unit = config['units']['weight']
    
    if current_unit != unit:
        convert_weights(current_unit, unit)

    config['units']['weight'] = unit
    
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)
    print(f"Weight unit set to {unit}.")

def convert_weights(current_unit, new_unit):
    """Convert all logged weights from current unit to new unit."""
    conversion_factor = 2.20462 if new_unit == 'lb' else 0.453592
    workouts_file = 'workouts.json'
    if not os.path.exists(workouts_file):
        print("No workouts found.")
        return
    with open(workouts_file, 'r') as file:
        try:
            workouts = json.load(file)
        except json.JSONDecodeError:
            print("Error decoding JSON from the workouts file.")
            return
    for workout in workouts:
        if 'weights' in workout:
            weight = float(workout['weights'])
            converted_weight = weight * conversion_factor
            workout['weights'] = round(converted_weight, 2)
    with open(workouts_file, 'w') as file:
        json.dump(workouts, file, indent=4)
    print("All weights have been converted to the new unit.")
