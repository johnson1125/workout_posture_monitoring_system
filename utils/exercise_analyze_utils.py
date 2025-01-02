import random
from config import workout_configurations  # Ensure config.py is in the same directory or adjust the import path accordingly


def analyze_exercise_sets(set_records, exercise):
    """
    Analyzes a list of exercise set records to generate intuitive comments and recommendations based on exercise type.

    Parameters:
        set_records (list): A list of dictionaries, each containing details of an exercise set.
        exercise_type (str): The type of exercise (e.g., "squat", "bicep_curl").

    Returns:
        dict: A dictionary containing the aggregated analysis, comments, and recommendations.
    """
    # Fetch exercise configuration
    workout_config = workout_configurations.get(exercise)
    if not workout_config:
        raise ValueError(f"Exercise type '{exercise}' is not defined in the configuration.")

    # Define actual mistake types (excluding proper form labels like "proper_squat" or "proper_curl")
    actual_mistakes = workout_config.get("mistake_types", [])

    # Initialize per-set analysis list
    per_set_analysis = []

    for set_record in set_records:
        # Extract relevant data
        exercise_id = set_record.get("exercise_id", "Unknown")
        set_number = set_record.get("set_number", "Unknown")
        workout_time = set_record.get("workout_time", "Unknown")
        mistake_counts = set_record.get("mistake_counts", {})
        reps_results = set_record.get("reps_results", [])

        # Initialize set-specific analysis variables
        total_reps = len(reps_results)
        total_mistakes = sum(mistake_counts.get(mistake, 0) for mistake in actual_mistakes)
        # Assume that "proper_<exercise>" is the key for correct reps, e.g., "proper_squat"
        proper_label = f"proper_{exercise}"
        correct_reps = mistake_counts.get(proper_label, 0)

        # Identify the most frequent mistake
        if mistake_counts:
            most_frequent_mistake = max(actual_mistakes, key=lambda x: mistake_counts.get(x, 0))
        else:
            most_frequent_mistake = None

        # Analyze mistake trends for the set
        mistake_trends = {}
        for mistake in actual_mistakes:
            count = mistake_counts.get(mistake, 0)
            if count > 0:
                mistake_trends[mistake] = {
                    "count": count,
                    "severity": categorize_severity(count)
                }

        # Generate comments based on analysis
        comments = generate_comments(
            total_mistakes, most_frequent_mistake, mistake_trends,correct_reps, exercise
        )

        # Generate recommendations based on analysis
        recommendations = generate_recommendations(
            mistake_trends, exercise
        )

        # Append set-specific analysis
        set_analysis = {
            "Exercise ID": exercise_id,
            "Set Number": set_number,
            "Workout Time": workout_time,
            "Total Reps": total_reps,
            "Correct Reps": correct_reps,
            "Total Mistakes": total_mistakes,
            "Mistake Counts": mistake_counts,
            "Most Frequent Mistake": most_frequent_mistake,
            "Mistake Trends": mistake_trends,
            "Comments": comments,
            "Recommendations": recommendations
        }
        per_set_analysis.append(set_analysis)


    return per_set_analysis


def categorize_severity(count):
    """
    Categorizes the severity of a mistake based on its count.

    Parameters:
        count (int): The number of times a mistake occurred.

    Returns:
        str: The severity category.
    """
    if count >= 10:
        return "High"
    elif count >= 5:
        return "Moderate"
    elif count >= 1:
        return "Low"
    else:
        return "None"

def generate_comments(total_mistakes, most_frequent_mistake, mistake_trends, correct_reps, exercise_type):
    """
    Generates comments based on the analysis of mistakes and feedback.

    Parameters:
        total_mistakes (int): Total number of mistakes in the set.
        most_frequent_mistake (str): The most frequent mistake.
        mistake_trends (dict): Trends of each mistake.
        correct_reps (int): Number of correctly performed reps.
        exercise_type (str): The type of exercise.

    Returns:
        list: A list of comments.
    """
    comments = []

    # Overall Mistakes
    if total_mistakes == 0:
        comments.append("Excellent form throughout the set! Keep up the great work.")
    else:
        if most_frequent_mistake:
            readable_mistake = most_frequent_mistake.replace('_', ' ').capitalize()
            comments.append(
                f"The most frequent mistake was '{readable_mistake}' occurring {mistake_trends[most_frequent_mistake]['count']} times.")

    # Mistake Severity
    for mistake, details in mistake_trends.items():
        readable_mistake = mistake.replace('_', ' ').capitalize()
        if details["severity"] == "High":
            comments.append(f"Significant issues with '{readable_mistake}'.")
        elif details["severity"] == "Moderate":
            comments.append(f"Repeated mistakes in '{readable_mistake}'.")
        elif details["severity"] == "Low":
            comments.append(
                f"Some mistakes detected in '{readable_mistake}'. Consider paying extra attention to this area.")

    # Acknowledge overall performance
    if total_mistakes == 0 and correct_reps > 0:
        appraisal_messages = workout_configurations[exercise_type]["feedback_messages"]["appraisal"]
        appraisal = random.choice(appraisal_messages)
        comments.append(appraisal)

    return comments


def generate_recommendations(mistake_trends, exercise_type):
    """
    Generates recommendations based on the analysis of mistakes and feedback.

    Parameters:
        mistake_trends (dict): Trends of each mistake.
        exercise_type (str): The type of exercise.

    Returns:
        list: A list of recommendations.
    """
    recommendations = []
    exercise_recommendations = workout_configurations[exercise_type].get("recommendations", {})

    # Recommendations based on mistake types and severity
    for mistake, details in mistake_trends.items():
        severity = details["severity"]
        if mistake in exercise_recommendations:
            specific_recommendations = exercise_recommendations[mistake]
            rec = specific_recommendations.get(severity)
            if rec:
                recommendations.append(rec)


    # General Recommendations
    if not recommendations:
        recommendations.append("Maintain your current form and continue your consistent effort!")

    return recommendations
