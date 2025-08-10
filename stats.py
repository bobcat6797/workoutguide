import json
import os
from datetime import datetime, timedelta
from collections import Counter


# Configurable constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSCLE_GROUPS_PATH = os.path.join(BASE_DIR, 'muscle_groups.json' \
'')
MAX_WEEKLY_ENTRIES = 21           # Entry count limit per 7 days before overtraining risk kicks in
OVERTRAIN_RISK_WEIGHT_BASE = 25   # Base risk points if over limit
RISK_DECAY_DAYS = 7               # Days over which risk decays to zero without overtraining
PERF_DECAY_START_DAYS = 3         # Days without workout before performance decay starts
PERF_DECAY_RATE = 3               # Performance points lost per day after decay starts (up to zero)

def calculate_scores(workout_log, current_date=None):
    if current_date is None:
        current_date = datetime.now()

    two_weeks_ago = current_date - timedelta(days=14)
    week_ago = current_date - timedelta(days=7)

    # Filter workouts in the last 7 days and last 14 days
    last_week = [w for w in workout_log if datetime.strptime(w[4], "%Y-%m-%d") >= week_ago]
    last_two_weeks = [w for w in workout_log if datetime.strptime(w[4], "%Y-%m-%d") >= two_weeks_ago]
    entry_count = len(last_week)

    # --- Calculate Performance base (before decay) ---
    performance = min(100, entry_count * 5)

    # --- Calculate Overtraining Risk base ---
    risk = 0
    areas_for_improvement = []

    # Overtraining if entries exceed max weekly entries
    if entry_count > MAX_WEEKLY_ENTRIES:
        over_count = entry_count - MAX_WEEKLY_ENTRIES
        risk += min(50, OVERTRAIN_RISK_WEIGHT_BASE + over_count * 2)
        areas_for_improvement.append(f"{entry_count} entries in last 7 days (limit: {MAX_WEEKLY_ENTRIES})")

    # Muscle focus check for last two weeks
    # muscle_groups must be passed as an argument
    muscle_counts = Counter(w[1] for w in last_two_weeks if w[0] == "strength")
    muscle_groups = globals().get('muscle_groups', [])
    for muscle in muscle_groups:
        if muscle_counts[muscle] == 0:
            areas_for_improvement.append(f"'{muscle}' not targeted in the last two weeks")

    # Check for excessive weight progression
    weight_progression = {}
    for w in last_week:
        if w[0] == "strength" and w[2] is not None:
            muscle = w[1]
            if isinstance(w[2], (int, float)):
                weight = float(w[2])
            elif isinstance(w[2], str):
                try:
                    weight = float(w[2].split()[0])
                except Exception:
                    continue
            else:
                continue
            if muscle not in weight_progression:
                weight_progression[muscle] = []
            weight_progression[muscle].append(weight)

    for muscle, weights in weight_progression.items():
        if len(weights) > 1:
            max_weight = max(weights)
            min_weight = min(weights)
            if max_weight > 1.2 * min_weight:  # Example threshold for excessive progression
                risk += 15
                areas_for_improvement.append(f"Excessive weight progression detected for '{muscle}'")

    # --- Progressive Decay Logic ---
    # Find last workout date
    if workout_log:
        last_workout_date = max(datetime.strptime(w[4], "%Y-%m-%d") for w in workout_log)
        days_since_last = (current_date - last_workout_date).days
    else:
        days_since_last = 1000  # No workouts ever, max decay

    # Performance decay after inactivity threshold
    if days_since_last > PERF_DECAY_START_DAYS:
        decay_days = days_since_last - PERF_DECAY_START_DAYS
        decay_amount = decay_days * PERF_DECAY_RATE
        performance = max(0, performance - decay_amount)

    # Risk decay if no recent overtraining
    if entry_count <= MAX_WEEKLY_ENTRIES and risk > 0:
        # Linearly reduce risk over RISK_DECAY_DAYS
        risk_decay_amount = risk / RISK_DECAY_DAYS
        decay_days = min(days_since_last, RISK_DECAY_DAYS)
        risk = max(0, risk - risk_decay_amount * decay_days)

    # Clamp risk to max 50
    risk = min(50, risk)

    return int(performance), int(risk), areas_for_improvement


def score_description(performance, risk, reasons):
    # Labels & descriptions
    if performance < 60:
        perf_label = "Needs Improvement"
        perf_desc = "Training frequency and/or coverage is low. Aim for more consistent sessions."
    elif performance < 90:
        perf_label = "Healthy Training"
        perf_desc = "You're training regularly and covering most key areas."
    else:
        perf_label = "Optimal"
        perf_desc = "Excellent balance of frequency, coverage, and progression."

    if risk == 0:
        risk_label = "Low Risk"
        risk_desc = "Your training load is within healthy limits."
    elif risk < 20:
        risk_label = "Moderate Risk"
        risk_desc = "Some signs of high load — monitor recovery and rest days."
    else:
        risk_label = "High Risk"
        risk_desc = "Training volume or focus is likely unsustainable. Reduce load."

    def bars(score, max_val):
        filled = score * 20 // max_val
        return "█" * filled + "░" * (20 - filled)

    output = f"""
Performance: {bars(performance, 100)}  {performance}/100   — {perf_label}
Risk Level:  {bars(risk, 50)}  {risk}/50    — {risk_label}

Performance Notes:
   {perf_desc}

Risk Notes:
   {risk_desc}
"""

    if reasons:
        output += "\nAreas for Improvement:\n" + "".join([f"   - {r}\n" for r in reasons])

    return output

def display_stats(user_dir):
    """Display workout statistics with performance and risk analysis."""
    workouts_file = os.path.join(user_dir, 'workouts.json')
    if not os.path.exists(workouts_file):
        print("\nNo workouts found")
        return
    with open(workouts_file, 'r') as file:
        try:
            workouts = json.load(file)
        except json.JSONDecodeError:
            print("\nError decoding JSON from the workouts file")
            return
    total_workouts = len(workouts)
    if total_workouts > 0:
        print(f"\nTotal workouts logged: {total_workouts}")
    else:
        print("No workouts logged")
        return
    # Load muscle groups from muscle_groups.json using absolute path
    muscle_groups = []
    muscle_groups_path = os.path.join(BASE_DIR, 'muscle_groups.json')
    if os.path.exists(muscle_groups_path):
        with open(muscle_groups_path, 'r') as f:
            try:
                data = json.load(f)
                muscle_groups = data.get('muscle_groups', [])
            except Exception:
                muscle_groups = []

    # Convert workouts to the required tuple format: (type, muscle, weights, weight_unit, date)
    workout_log = []
    for w in workouts:
        w_type = w.get('type', None)
        muscle = w.get('muscle', None)
        weights = w.get('weights', None)
        weight_unit = w.get('weight_unit', None)  # Not always present
        date = w.get('date', None)
        # Try to infer weight_unit if not present
        if not weight_unit and weights and isinstance(weights, str):
            parts = weights.split()
            if len(parts) == 2 and parts[0].replace('.', '', 1).isdigit():
                weights, weight_unit = parts
        try:
            weights_val = float(weights) if weights is not None else None
        except Exception:
            weights_val = None
        workout_log.append((w_type, muscle, weights_val, weight_unit, date))

    # Pass muscle_groups to calculate_scores
    globals()['muscle_groups'] = muscle_groups
    perf_score, risk_score, risk_reasons = calculate_scores(workout_log)
    print(score_description(perf_score, risk_score, risk_reasons))

    # --- Areas for Improvement: muscles not targeted in last 14 days ---
    two_weeks_ago = datetime.now() - timedelta(days=14)
    muscles_hit = set(
        w[1] for w in workout_log
        if w[0] == "strength" and w[1] and w[4] and w[1] in muscle_groups and datetime.strptime(w[4], "%Y-%m-%d") >= two_weeks_ago
    )
    missing_muscles = [m for m in muscle_groups if m not in muscles_hit]
    if missing_muscles:
        print("\nAreas for Improvement:")
        for m in missing_muscles:
            print(f"   - '{m}' not targeted in the last two weeks")