import json
import sys
import os
from config import load_config, set_weight_unit
from log_workout import log_workout
from stats import display_stats
from workout_manager import manage_workouts

def settings_menu(user_dir):
    from config import load_config, set_weight_unit
    # Load about info
    about_path = 'about.json'
    if os.path.exists(about_path):
        with open(about_path, 'r') as f:
            about = json.load(f)
        app_name = about.get('app_name', 'Workout Guide')
        version = about.get('version', '1.0')
    else:
        app_name = 'Workout Guide'
        version = '1.0'
    while True:
        config = load_config(os.path.join(user_dir, 'settings.json'))
        current_unit = config['units']['weight']
        print("\n===========Settings===========")
        print(f"{app_name}")
        print(f"Version: {version}\n")
        print(f"Current weight unit: {current_unit}")
        print("u: Change weight unit")
        print("m: Back to main menu")
        print("==============================")
        choice = input("Select an option (1-2): ")
        if choice == 'u':
            new_unit = 'kg' if current_unit == 'lb' else 'lb'
            confirm = input(f"Change weight unit to {new_unit}? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    set_weight_unit(new_unit, os.path.join(user_dir, 'settings.json'))
                except ValueError as e:
                    print(e)
        elif choice == 'm':
            break
        else:
            print("Invalid option. Try again.")

def main_menu(user_dir):
    from log_workout import log_workout
    from stats import display_stats
    from workout_manager import manage_workouts
    while True:
        print("\n===========MAIN MENU===========")
        print("l: Log a workout")
        print("s: View stats")
        print("m: Manage workouts")
        print("t: Settings")
        print("x: Exit")
        print("u: Back to user menu")
        print("===============================" )
        choice = input("Select an option: ").strip().lower()
        if choice == 'l':
            log_workout(user_dir)
        elif choice == 's':
            display_stats(user_dir)
        elif choice == 'm':
            manage_workouts(user_dir)
        elif choice == 't':
            settings_menu(user_dir)
        elif choice == 'x':
            print("Exiting the application")
            sys.exit()
        elif choice == 'u':
            user_menu()
        else:
            print("Invalid option. Try again.")

def user_menu():
    import datetime
    users_dir = 'users'
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)
    def get_last_login(user_dir):
        last_login_file = os.path.join(user_dir, 'last_login.txt')
        if os.path.exists(last_login_file):
            with open(last_login_file, 'r') as f:
                return f.read().strip()
        return 'Never'
    def set_last_login(user_dir):
        last_login_file = os.path.join(user_dir, 'last_login.txt')
        with open(last_login_file, 'w') as f:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    while True:
        users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
        print("\n=========== User Menu ===========")
        if users:
            print(f"{'#':<3} {'Username':<20} {'Last Login':<20}")
            print('-' * 45)
            for i, u in enumerate(users, 1):
                last_login = get_last_login(os.path.join(users_dir, u))
                print(f"{i:<3} {u:<20} {last_login:<20}")
            print("e: Edit users")
            print("x: Exit")
            print("===============================" )
            choice = input("Enter user number to login, or option: ").strip().lower()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(users):
                    user_dir = os.path.join(users_dir, users[idx])
                    set_last_login(user_dir)
                    return user_dir
                else:
                    print("Invalid user number.")
            elif choice == 'e':
                # Edit users menu
                while True:
                    print("\n--- Edit Users ---")
                    print("d: Delete user")
                    print("r: Rename user")
                    print("u: Back to user menu")
                    edit_choice = input("Enter choice: ")
                    if edit_choice == 'd':
                        idx = input("Enter user number to delete: ")
                        try:
                            idx = int(idx) - 1
                            if 0 <= idx < len(users):
                                user_to_delete = os.path.join(users_dir, users[idx])
                                import shutil
                                shutil.rmtree(user_to_delete)
                                print("User deleted.")
                                break
                            else:
                                print("Invalid user number.")
                        except ValueError:
                            print("Invalid input.")
                    elif edit_choice == 'r':
                        idx = input("Enter user number to rename: ")
                        try:
                            idx = int(idx) - 1
                            if 0 <= idx < len(users):
                                old_user_dir = os.path.join(users_dir, users[idx])
                                new_name = input("Enter new username: ").strip()
                                if not new_name:
                                    print("Username cannot be empty.")
                                    continue
                                new_user_dir = os.path.join(users_dir, new_name)
                                if os.path.exists(new_user_dir):
                                    print("A user with that name already exists.")
                                    continue
                                os.rename(old_user_dir, new_user_dir)
                                print("User renamed.")
                                break
                            else:
                                print("Invalid user number.")
                        except ValueError:
                            print("Invalid input.")
                    elif edit_choice == 'u':
                        break
                    else:
                        print("Invalid option. Try again.")
            elif choice == 'x':
                print("Exiting the application")
                sys.exit()
            else:
                print("Invalid option. Try again.")
        else:
            print("Create a new user to get started")
            username = input("Enter new username or type 'exit' to quit: ").strip()
            if username.lower() in ['exit', 'x']:
                print("Exiting the application")
                sys.exit()
            if not username:
                print("Username cannot be empty.")
                continue
            user_dir = os.path.join(users_dir, username)
            os.makedirs(user_dir, exist_ok=True)
            # Create default settings.json and workouts.json
            settings_path = os.path.join(user_dir, 'settings.json')
            workouts_path = os.path.join(user_dir, 'workouts.json')
            if not os.path.exists(settings_path):
                with open(settings_path, 'w') as f:
                    json.dump({"units": {"weight": "lb", "distance": "km"}}, f, indent=4)
            if not os.path.exists(workouts_path):
                with open(workouts_path, 'w') as f:
                    json.dump([], f, indent=4)
            set_last_login(user_dir)
            print(f"User '{username}' created.")

            return user_dir

if __name__ == "__main__":
    user_dir = user_menu()
    main_menu(user_dir)
