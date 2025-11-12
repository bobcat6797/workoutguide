import sys
import os
import json
from config import load_config

def program_quit():
    """Exit the program gracefully."""
    print("\nExiting the application\n")
    sys.exit()

def load_muscle_groups(file_path=None):
    """Load muscle groups from a JSON file."""
    if file_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'muscle_groups.json')
    if not os.path.exists(file_path):
        print("\nMuscle groups file not found")
        return []
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            return data.get('muscle_groups', [])
        except json.JSONDecodeError:
            print("\nError decoding JSON from the muscle groups file")
            return []