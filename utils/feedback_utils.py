import base64
import os
import random
import wave

import streamlit as st


def analyze_rep(rep,reps_results, rep_detections, rep_frames_fps,workout_config, mistake_counts):
    """
     Analyze squat rep data and generate feedback.

     Args:
         rep_detection (list): List of frame classifications for the current rep.
         rep_results (list): List of results for past reps.
         workout_configurations (dict): Configuration for the workout (e.g., squat).

     Returns:
         dict: The result of the current rep and the generated feedback.
     """

    labels = workout_config["labels"]
    labels_key = list(labels.keys())
    feedback_messages = workout_config["feedback_messages"]

    avg_frames_fps = sum(rep_frames_fps) / len(rep_frames_fps)

    if avg_frames_fps < 10:
        threshold_mistake_frames = 3
    elif avg_frames_fps < 20:
        threshold_mistake_frames = 4
    else:
        threshold_mistake_frames = 5



        # Mistake Detection
    mistake = None
    count = 0
    last_frame = None
    print(rep_detections)
    rep_detections = list(rep_detections[threshold_mistake_frames:])
    for frame in rep_detections:
        if frame == 0:  # Proper squat
            count = 0  # Reset the counter
        elif frame == last_frame:  # Consecutive mistake frames
            count += 1
            if count == threshold_mistake_frames:
                mistake = frame
                break
        else:
            count = 1  # Start counting for a new mistake
        last_frame = frame

    # Result of the rep
    rep_result = mistake if mistake is not None else 0

    # Feedback Type Decision
    consecutive_rep_mistake_count = 0
    feedback_type = "normal"
    if len(reps_results) > 4:
        # Analyze recent results
        last_rep_result_name = reps_results[-1]["result"]
        if last_rep_result_name != labels_key[0]:
            for past_rep in reversed(reps_results[-3:]):  # Check the last 3 reps
                if past_rep["result"] == last_rep_result_name:
                    consecutive_rep_mistake_count += 1
                else:
                    break

        # Decide feedback type
        if consecutive_rep_mistake_count >= 3 and rep_result == labels[last_rep_result_name]:  # Escalate to elevated feedback
            feedback_type = "elevated"
        elif consecutive_rep_mistake_count >= 1 and rep_result == 0:  # Supportive feedback if corrected
            feedback_type = "supportive"

    # Feedback Generation
    posture_name = [name for name, value in labels.items() if value == rep_result][0]
    rep_result_name = posture_name
    mistake_counts[posture_name] += 1
    if rep_result == 0:  # Proper squat
        feedback = random.choice(feedback_messages["appraisal"])
        if feedback_type == "supportive":
            feedback = random.choice(
                feedback_messages[feedback_type][last_rep_result_name]
            )

    else:
        feedback = random.choice(
            feedback_messages[feedback_type][posture_name]
        )

    reps_results.append({
        "rep_index": rep-1,
        "result": rep_result_name,
        "feedback": feedback,
        "feedback_type": feedback_type
    })
    print(reps_results[-1])
    print(rep_detections)

    return rep_result,reps_results, feedback, mistake_counts


def text_to_audio_feedback(audio_temp_dir, text, engine):
    os.makedirs(audio_temp_dir, exist_ok=True)
    temp_audio_path = os.path.join(audio_temp_dir, "feedback.wav")

    engine.save_to_file(text, temp_audio_path)
    engine.runAndWait()
    # with wave.open(temp_audio_path, 'rb') as wf:
    #     frames = wf.getnframes()
    #     rate = wf.getframerate()
    #     duration = frames / float(rate)  # Duration in seconds

    with open(temp_audio_path, "rb") as audio_file:
        audio_data = audio_file.read()
        base64_audio = base64.b64encode(audio_data).decode()

    # Create a hidden autoplay audio element
    audio_html = f"""
                                <audio class="audio_player" autoplay style="display:none; height:0px;">
                                    <source src="data:audio/wav;base64,{base64_audio}" type="audio/mpeg">
                                </audio>
                            """
    duration = 3
    st.markdown(audio_html, unsafe_allow_html=True)
    return duration


def generate_body_position_feedback(is_view_correct, body_view, view_direction, is_straight_body_view,
                                    is_in_bounding_box):
    """
    Generates concise feedback based on body position verification results.

    Args:
        body_view (str): The detected body view ("front", "side", or "unknown").
        side_view_direction (str): The side view direction ("left", "right", or "unknown").
        is_straight_body_view (bool): True if the body is straight (side or front view), False otherwise.
        is_in_bounding_box (bool): True if the body is within the bounding box, False otherwise.

    Returns:
        str: Concise feedback message summarizing the body position status.
    """

    feedback = ""
    is_position_correct = False

    if not is_view_correct:
        correct_body_position = False
        if body_view == "front":
            feedback = "Adjust to a side view."
        elif body_view == "side":
            feedback = "Adjust to a front view."
        return feedback, is_position_correct

    if not is_in_bounding_box:
        feedback = "Adjust your position to fit within the bounding box."
        return feedback, is_position_correct

    if body_view == "unknown":
        feedback = "Unable to detect your position. Adjust your pose."
        return feedback, is_position_correct

    if body_view == "front" and not is_straight_body_view:
        feedback = "Align shoulders and hips for a straight front view."
        return feedback, is_position_correct

    if body_view == "side":
        if view_direction == "unknown":
            feedback = "Adjust your pose to face left or right side."
            return feedback, is_position_correct
        if not is_straight_body_view:
            feedback = f"Align your body for a straight {view_direction} side view."
            return feedback, is_position_correct

    feedback = "Your position is correct."
    is_position_correct = True

    return feedback, is_position_correct
