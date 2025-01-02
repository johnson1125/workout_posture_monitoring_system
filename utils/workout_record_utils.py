from datetime import datetime, timedelta
import json

from . import utils


def generate_exercise_id(exercise_name):
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{exercise_name.upper()}-{current_time}"


def save_workout_set_record(exercise_id, set_number, reps_results, workout_time, mistake_counts, workout_config):
    # Prepare workout set data
    workout_data_file = workout_config["workout_data_directory"]["workout_data"]

    parts = exercise_id.split("-")

    # Extract the date and time from the appropriate parts
    date_str = parts[1]
    time_str = parts[2]
    formatted_datetime = datetime.strptime(date_str + " " + time_str, "%Y%m%d %H%M%S")

    workout_set = {
        "exercise_id": exercise_id,
        "exercise_datetime": formatted_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "set_number": set_number,
        "workout_time": workout_time,
        "mistake_counts": mistake_counts,
        "reps_results": reps_results,
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load existing workout data from JSON file
    try:
        with open(workout_data_file, "r") as file:
            workout_data = json.load(file)
    except FileNotFoundError:
        workout_data = []

    # Append the new workout set data
    workout_data.append(workout_set)

    with open(workout_data_file, "w") as file:
        json.dump(workout_data, file, indent=4)


def load_workout_summary(workout_config,exercise):
    def parse_workout_time(workout_time):
        # Convert "mm:ss" time format to timedelta for summation
        minutes, seconds = map(int, workout_time.split(":"))
        return timedelta(minutes=minutes, seconds=seconds)

    with open(workout_config[exercise]["workout_data_directory"]["workout_data"], "r") as file:
        data = json.load(file)

    summary = {}
    for record in data:
        exercise_id = record["exercise_id"]
        if exercise_id not in summary:
            summary[exercise_id] = {
                "Exercise ID": exercise_id,
                "Exercise DateTime": record["exercise_datetime"],
                "Set": 0,
                "Workout Time": timedelta()
            }
        summary[exercise_id]["Set"] += 1
        summary[exercise_id]["Workout Time"] += parse_workout_time(record["workout_time"])

    # Convert Workout Time back to "mm:ss" format
    for entry in summary.values():
        total_seconds = int(entry["Workout Time"].total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        entry["Workout Time"] = f"{minutes:02}:{seconds:02}"

    # Convert the summary dictionary to a list and sort by Set Number in descending order
    entries = sorted(summary.values(), key=lambda x: x["Exercise ID"], reverse=True)
    return entries

def load_workout_summary_details(workout_config,exercise_id):

    with open(workout_config[ utils.extract_exercise_key(exercise_id)]["workout_data_directory"]["workout_data"], "r") as file:
        data = json.load(file)

    matching_records = [record for record in data if record["exercise_id"] == exercise_id]

    return matching_records

def load_rep_records(workout_config,exercise_id,selected_set):
    _,_,set = selected_set.split("-")
    _,_,set = set.split("_")

    with open(workout_config[utils.extract_exercise_key(exercise_id)]["workout_data_directory"]["workout_data"],
              "r") as file:
        data = json.load(file)
    matching_records = [record for record in data if record["exercise_id"] == exercise_id and record["set_number"] == int(set)]

    return matching_records[0]["reps_results"]
