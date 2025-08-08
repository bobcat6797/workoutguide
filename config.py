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
    log_file_path = 'workout_log.txt'
    
    if not os.path.exists(log_file_path):
        print("No workout log found.")
        return

    updated_workouts = []
    
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            workout = json.loads(line)
            if 'weights' in workout:
                weight = float(workout['weights'])
                # Convert weight
                converted_weight = weight * conversion_factor
                workout['weights'] = round(converted_weight, 2)  # Round to 2 decimal places
            updated_workouts.append(workout)

    # Write the updated workouts back to the log file
    with open(log_file_path, 'w') as log_file:
        for workout in updated_workouts:
            log_file.write(json.dumps(workout) + '\n')

    print("All weights have been converted to the new unit.")
