import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose


def extract_keypoints(results, keypoints_to_extract):
    landmarks = results.pose_landmarks.landmark
    return np.array([
        [landmarks[getattr(mp_pose.PoseLandmark, kp)].x, landmarks[getattr(mp_pose.PoseLandmark, kp)].y]
        for kp in keypoints_to_extract
    ])


def scale_and_rel_position_normalize_keypoints(keypoints, flip_horizontally=False):
    """
    Normalize keypoints by scaling based on the distance between the hip and shoulder,
    and translate the hip to the origin. Optionally, flip the normalized keypoints horizontally.

    Args:
        keypoints (list): List of keypoints with (x, y) pairs.
        flip_horizontally (bool): If True, flip the normalized keypoints horizontally.

    Returns:
        np.ndarray: Flattened array of normalized keypoints.
    """
    hip_x, hip_y = keypoints[1]
    shoulder_x, shoulder_y = keypoints[0]

    # Step 1: Calculate the scaling factor
    hip = np.array([hip_x, hip_y])
    shoulder = np.array([shoulder_x, shoulder_y])
    scale = np.linalg.norm(hip - shoulder)
    scale_factor = 1 / scale if scale > 0 else 1.0  # Avoid division by zero

    # Step 2: Scale the keypoints
    scaled_keypoints = []
    for keypoint in keypoints:
        scaled_x = keypoint[0] * scale_factor
        scaled_y = keypoint[1] * scale_factor
        scaled_keypoints.append([scaled_x, scaled_y])

    # Step 3: Translate the scaled hip to the origin
    hip_scaled_x, hip_scaled_y = scaled_keypoints[1]
    normalized_frame_keypoints = []
    for keypoint in scaled_keypoints:
        normalized_x = keypoint[0] - hip_scaled_x
        normalized_y = keypoint[1] - hip_scaled_y
        normalized_frame_keypoints.append([normalized_x, normalized_y])

    # Step 4: Flip horizontally if required
    if flip_horizontally:
        for keypoint in normalized_frame_keypoints:
            keypoint[0] = -keypoint[0]  # Negate the x-coordinate

    return np.array(normalized_frame_keypoints).flatten()


# Define a function to preprocess keypoints
def preprocess_keypoints(keypoints, all_keypoints, selected_keypoints):
    """
    Extracts selected keypoints from a flattened array and formats them for angle calculations.

    Args:
        flattened_keypoints (np.ndarray): Flattened array of keypoints with shape (n * 2,).
        all_keypoints (list): List of all keypoint names in the order they appear in the flattened array.
        selected_keypoints (list): List of keypoints to extract for angle calculations.

    Returns:
        dict: Dictionary of selected keypoints with their [x, y] coordinates.
    """
    # Reshape flattened keypoints into pairs of (x, y)

    # Create a dictionary for all keypoints
    keypoint_dict = {name: keypoints[idx] for idx, name in enumerate(all_keypoints)}

    # Extract only the selected keypoints
    selected_keypoint_coords = {name: keypoint_dict[name] for name in selected_keypoints}

    return selected_keypoint_coords


def calculate_angle(point_a, point_b, point_c, width, height):
    """
    Calculate the angle (in degrees) between three points in 2D space.
    Multiplies normalized coordinates with width and height to convert to pixel space.

    Args:
        point_a (list or array): Normalized coordinates of the first point [x, y].
        point_b (list or array): Normalized coordinates of the middle point [x, y].
        point_c (list or array): Normalized coordinates of the third point [x, y].
        width (int): Width of the frame/image in pixels.
        height (int): Height of the frame/image in pixels.

    Returns:
        float: Angle in degrees between the three points.
    """
    # Convert normalized points to pixel coordinates
    point_a = np.array([point_a[0] * width, point_a[1] * height])
    point_b = np.array([point_b[0] * width, point_b[1] * height])
    point_c = np.array([point_c[0] * width, point_c[1] * height])

    # Vectors between the points
    vector_ab = point_a - point_b  # Vector from B to A
    vector_cb = point_c - point_b  # Vector from B to C

    # Dot product and magnitudes
    dot_product = np.dot(vector_ab, vector_cb)
    magnitude_ab = np.linalg.norm(vector_ab)
    magnitude_cb = np.linalg.norm(vector_cb)

    # Avoid division by zero
    if magnitude_ab == 0 or magnitude_cb == 0:
        return 0.0

    # Calculate the angle in radians
    cos_theta = dot_product / (magnitude_ab * magnitude_cb)

    # Clip cos_theta to avoid numerical issues (e.g., slightly > 1 or < -1)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # Convert to degrees
    angle = np.arccos(cos_theta) * (180.0 / np.pi)
    return angle


def count_reps_squat(current_stage, stage, keypoints, workout_config, system_config, view_direction):
    angle_keypoints = list(preprocess_keypoints(keypoints, workout_config["keypoints"][view_direction],
                                                workout_config["angle_keypoints"][view_direction]).values())
    angle = calculate_angle(angle_keypoints[0], angle_keypoints[1], angle_keypoints[2],
                            system_config["resize_width"], system_config["resize_height"])
    new_rep = False
    up_knee_angle = 173
    down_knee_angle = 140

    if angle > up_knee_angle:
        current_stage = "up"

    if angle < down_knee_angle:
        current_stage = "down"

    if stage == 'down' and current_stage == "up":
        new_rep = True

    return new_rep, current_stage, angle


def count_reps_bicep_curl(current_stage, stage, keypoints, workout_config, system_config, view_direction):
    angle_keypoints = list(preprocess_keypoints(keypoints, workout_config["keypoints"][view_direction],
                                                workout_config["angle_keypoints"][view_direction]).values())
    angle = calculate_angle(angle_keypoints[0], angle_keypoints[1], angle_keypoints[2],
                            system_config["resize_width"], system_config["resize_height"])
    new_rep = False
    contracted_angle = 100
    extended_angle = 150

    if angle > extended_angle:
        current_stage = "up"

    if angle < contracted_angle:
        current_stage = "down"

    if stage == 'down' and current_stage == "up":
        new_rep = True

    return new_rep, current_stage, angle


rep_counting_algorithms = {
    "squat": count_reps_squat,
    "bicep_curl": count_reps_bicep_curl,
}


def new_rep_squat(rep_frames_fps):
    avg_frames_fps = sum(rep_frames_fps) / len(rep_frames_fps)

    if avg_frames_fps < 10:
        feedback_delay = 3
    elif avg_frames_fps < 20:
        feedback_delay = 4
    else:
        feedback_delay = 5
    return feedback_delay


def new_rep_bicep_curl(rep_frames_fps):
    return 0


new_rep_delay_algorithm = {
    "squat": new_rep_squat,
    "bicep_curl": new_rep_bicep_curl,
}
