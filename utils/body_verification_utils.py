
def determine_view(pose_landmarks, threshold=0.1):
    """
    Determines if the user is in front or side view based on MediaPipe Pose landmarks.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        threshold (float): Z-coordinate difference threshold to distinguish between front and side view.

    Returns:
        str: "front" if the user is in front view, "side" if the user is in side view.
    """
    # Landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24

    # Extract Z-coordinates for shoulders and hips
    left_shoulder_z = pose_landmarks.landmark[LEFT_SHOULDER].z
    right_shoulder_z = pose_landmarks.landmark[RIGHT_SHOULDER].z
    left_hip_z = pose_landmarks.landmark[LEFT_HIP].z
    right_hip_z = pose_landmarks.landmark[RIGHT_HIP].z

    # Calculate absolute Z-coordinate differences
    shoulder_diff = abs(left_shoulder_z - right_shoulder_z)
    hip_diff = abs(left_hip_z - right_hip_z)

    # Determine view based on threshold
    if shoulder_diff < threshold and hip_diff < threshold:
        return "front"
    else:
        return "side"

def determine_side_view(pose_landmarks, threshold=0.1):
    """
    Determines if the user is in a right-side or left-side view based on MediaPipe Pose landmarks.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        threshold (float): Z-coordinate difference threshold to distinguish between right and left side views.

    Returns:
        str: "right" if the user is in a right-side view, "left" if the user is in a left-side view,
             or "unknown" if the difference is inconclusive.
    """
    # Landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24

    # Extract Z-coordinates for shoulders and hips
    left_shoulder_z = pose_landmarks.landmark[LEFT_SHOULDER].z
    right_shoulder_z = pose_landmarks.landmark[RIGHT_SHOULDER].z
    left_hip_z = pose_landmarks.landmark[LEFT_HIP].z
    right_hip_z = pose_landmarks.landmark[RIGHT_HIP].z

    # Determine which side is closer
    shoulder_diff =right_shoulder_z - left_shoulder_z
    hip_diff = right_hip_z - left_hip_z

    # Determine side view
    if shoulder_diff > threshold and hip_diff > threshold:
        return "right"
    elif shoulder_diff < -threshold and hip_diff < -threshold:
        return "left"
    else:
        return "unknown"

def is_body_within_bounding_box(pose_landmarks,system_config):
    """
    Checks if the user's body landmarks are within the defined bounding box.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        frame_width (int): Width of the video frame.
        frame_height (int): Height of the video frame.
        bounding_box (dict): Dictionary containing 'x', 'y', 'width', 'height' of the bounding box.

    Returns:
        bool: True if key landmarks are within the bounding box, False otherwise.
    """
    key_landmarks = system_config["body_keypoints"]
    landmark_indices =  system_config["mediapipe_keypoints"]

    landmarks = pose_landmarks.landmark
    bbox_x, bbox_y, bbox_w, bbox_h = system_config["bounding_box"]["position"][0], system_config["bounding_box"]["position"][1], system_config["bounding_box"]["size"][0], system_config["bounding_box"]["size"][1]

    for landmark_name in key_landmarks:
        idx = landmark_indices[landmark_name]
        x = int(landmarks[idx].x * system_config["resize_width"])
        y = int(landmarks[idx].y * system_config["resize_height"])
        if not (bbox_x <= x <= bbox_x + bbox_w and bbox_y <= y <= bbox_y + bbox_h):
            return False

    return True

def is_straight_side_view(pose_landmarks, system_config,side_view_direction,side_view_threshold = 15, tilt_threshold = 15, posture_threshold =20):
    """
    Checks if the user is in a straight side view based on MediaPipe Pose landmarks.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        frame_width (int): Width of the video frame.
        frame_height (int): Height of the video frame.
        alignment_threshold (float): Maximum allowed deviation in the X-axis for alignment.
        z_diff_threshold (float): Minimum Z-coordinate difference for shoulders or hips to confirm a side view.

    Returns:
        bool: True if the user is in a straight side view, False otherwise.
    """
    frame_width = system_config["resize_width"]
    frame_height = system_config["resize_height"]
    # Landmark indices
    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28

    # Extract landmarks and convert normalized coordinates to pixel coordinates
    landmarks = pose_landmarks.landmark

    left_shoulder_x, left_shoulder_y, left_shoulder_z = (
        landmarks[LEFT_SHOULDER].x * frame_width,
        landmarks[LEFT_SHOULDER].y * frame_height,
        landmarks[LEFT_SHOULDER].z,
    )
    right_shoulder_x, right_shoulder_y, right_shoulder_z = (
        landmarks[RIGHT_SHOULDER].x * frame_width,
        landmarks[RIGHT_SHOULDER].y * frame_height,
        landmarks[RIGHT_SHOULDER].z,
    )

    left_hip_x, left_hip_y, left_hip_z = (
        landmarks[LEFT_HIP].x * frame_width,
        landmarks[LEFT_HIP].y * frame_height,
        landmarks[LEFT_HIP].z,
    )
    right_hip_x, right_hip_y, right_hip_z = (
        landmarks[RIGHT_HIP].x * frame_width,
        landmarks[RIGHT_HIP].y * frame_height,
        landmarks[RIGHT_HIP].z,
    )

    # Check Z-difference for side view
    x_diff_shoulders = abs(right_shoulder_x -left_shoulder_x)
    x_diff_hips = abs(right_hip_x - left_hip_x)

    if x_diff_shoulders > side_view_threshold and x_diff_hips > side_view_threshold:
        print("Shoulders and hips are not in a side view")
        return False

    # Check vertical alignment (Y-axis) of shoulders and hips
    shoulder_alignment = abs(left_shoulder_y - right_shoulder_y)
    hip_alignment = abs(left_hip_y - right_hip_y)

    if shoulder_alignment > tilt_threshold or hip_alignment > tilt_threshold:
        print("Shoulders or hips are tilted")
        return False  # Shoulders or hips are tilted
    if side_view_direction == "right":
        # Check straight line alignment for head, shoulder, hip, knee, and ankle
        left_knee_x = landmarks[LEFT_KNEE].x * frame_width
        left_ankle_x = landmarks[LEFT_ANKLE].x * frame_width
        x_coords = [left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x]
    else:
        right_knee_x = landmarks[RIGHT_KNEE].x * frame_width
        right_ankle_x = landmarks[RIGHT_ANKLE].x * frame_width
        x_coords = [right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x]

    min_x = min(x_coords)
    max_x = max(x_coords)

    if max_x - min_x > posture_threshold:
        print("Points are not aligned in a vertical line")
        return False  # Points are not aligned in a vertical line

    return True

def is_standing_side_view(pose_landmarks, system_config,side_view_direction,side_view_threshold = 30, posture_threshold =40):
    """
    Checks if the user is in a straight side view based on MediaPipe Pose landmarks.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        frame_width (int): Width of the video frame.
        frame_height (int): Height of the video frame.
        alignment_threshold (float): Maximum allowed deviation in the X-axis for alignment.
        z_diff_threshold (float): Minimum Z-coordinate difference for shoulders or hips to confirm a side view.

    Returns:
        bool: True if the user is in a straight side view, False otherwise.
    """
    frame_width = system_config["resize_width"]
    frame_height = system_config["resize_height"]
    # Landmark indices

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_WRIST= 15
    RIGHT_WRIST= 16
    RIGHT_EYE=5

    # Extract landmarks and convert normalized coordinates to pixel coordinates
    landmarks = pose_landmarks.landmark

    left_shoulder_x, left_shoulder_y, left_shoulder_z = (
        landmarks[LEFT_SHOULDER].x * frame_width,
        landmarks[LEFT_SHOULDER].y * frame_height,
        landmarks[LEFT_SHOULDER].z,
    )
    right_shoulder_x, right_shoulder_y, right_shoulder_z = (
        landmarks[RIGHT_SHOULDER].x * frame_width,
        landmarks[RIGHT_SHOULDER].y * frame_height,
        landmarks[RIGHT_SHOULDER].z,
    )

    left_hip_x, left_hip_y, left_hip_z = (
        landmarks[LEFT_HIP].x * frame_width,
        landmarks[LEFT_HIP].y * frame_height,
        landmarks[LEFT_HIP].z,
    )
    right_hip_x, right_hip_y, right_hip_z = (
        landmarks[RIGHT_HIP].x * frame_width,
        landmarks[RIGHT_HIP].y * frame_height,
        landmarks[RIGHT_HIP].z,
    )

    # Check Z-difference for side view
    x_diff_shoulders = abs(right_shoulder_x -left_shoulder_x)
    x_diff_hips = abs(right_hip_x - left_hip_x)

    if x_diff_shoulders > side_view_threshold and x_diff_hips > side_view_threshold:
        print("Shoulders and hips are not in a side view")
        return False  # Shoulders and hips are not in a side view

    left_wrist_y = landmarks[LEFT_WRIST].y * frame_height
    right_wrist_y = landmarks[RIGHT_WRIST].y * frame_height
    right_eye_y = landmarks[RIGHT_EYE].y * frame_height



    if side_view_direction == "right":
        # Check straight line alignment for head, shoulder, hip, knee, and ankle
        left_knee_y = landmarks[LEFT_KNEE].y * frame_height
        if left_knee_y < left_wrist_y or left_wrist_y < right_eye_y:
            print("bow_left")
            return False

        left_knee_x = landmarks[LEFT_KNEE].x * frame_width
        left_ankle_x = landmarks[LEFT_ANKLE].x * frame_width
        x_coords = [left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x]
    else:
        right_knee_y = landmarks[RIGHT_KNEE].y * frame_height
        if right_knee_y < right_wrist_y or right_wrist_y < right_eye_y:
            print("bow_right")
            return False
        right_knee_x = landmarks[RIGHT_KNEE].x * frame_width
        right_ankle_x = landmarks[RIGHT_ANKLE].x * frame_width
        x_coords = [right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x]

    min_x = min(x_coords)
    max_x = max(x_coords)

    if max_x - min_x > posture_threshold:
        print("Points are not aligned in a vertical line")
        return False  # Points are not aligned in a vertical line

    return True

def is_side_view(pose_landmarks, system_config,side_view_direction,side_view_threshold = 30):
    """
    Checks if the user is in a straight side view based on MediaPipe Pose landmarks.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        frame_width (int): Width of the video frame.
        frame_height (int): Height of the video frame.
        alignment_threshold (float): Maximum allowed deviation in the X-axis for alignment.
        z_diff_threshold (float): Minimum Z-coordinate difference for shoulders or hips to confirm a side view.

    Returns:
        bool: True if the user is in a straight side view, False otherwise.
    """
    frame_width = system_config["resize_width"]
    frame_height = system_config["resize_height"]
    # Landmark indices

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24

    # Extract landmarks and convert normalized coordinates to pixel coordinates
    landmarks = pose_landmarks.landmark

    left_shoulder_x, left_shoulder_y, left_shoulder_z = (
        landmarks[LEFT_SHOULDER].x * frame_width,
        landmarks[LEFT_SHOULDER].y * frame_height,
        landmarks[LEFT_SHOULDER].z,
    )
    right_shoulder_x, right_shoulder_y, right_shoulder_z = (
        landmarks[RIGHT_SHOULDER].x * frame_width,
        landmarks[RIGHT_SHOULDER].y * frame_height,
        landmarks[RIGHT_SHOULDER].z,
    )

    left_hip_x, left_hip_y, left_hip_z = (
        landmarks[LEFT_HIP].x * frame_width,
        landmarks[LEFT_HIP].y * frame_height,
        landmarks[LEFT_HIP].z,
    )
    right_hip_x, right_hip_y, right_hip_z = (
        landmarks[RIGHT_HIP].x * frame_width,
        landmarks[RIGHT_HIP].y * frame_height,
        landmarks[RIGHT_HIP].z,
    )

    # Check Z-difference for side view
    x_diff_shoulders = abs(right_shoulder_x -left_shoulder_x)
    x_diff_hips = abs(right_hip_x - left_hip_x)

    if x_diff_shoulders > side_view_threshold and x_diff_hips > side_view_threshold:
        return False  # Shoulders and hips are not in a side view

    return True

def is_straight_front_view(pose_landmarks, system_config, alignment_threshold=20, z_diff_threshold=0.1):
    """
    Checks if the user is in a straight front view based on MediaPipe Pose landmarks.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        frame_width (int): Width of the video frame.
        frame_height (int): Height of the video frame.
        alignment_threshold (float): Maximum allowed deviation in the Y-axis for horizontal alignment.
        z_diff_threshold (float): Maximum allowed Z-coordinate difference for depth alignment.

    Returns:
        bool: True if the user is in a straight front view, False otherwise.

    """

    frame_width = system_config["resize_width"]
    frame_height = system_config["resize_height"]
    # Landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_HIP = 23
    RIGHT_HIP = 24
    NOSE = 0

    # Extract landmark coordinates
    landmarks = pose_landmarks.landmark

    # Shoulder coordinates
    left_shoulder_x, left_shoulder_y, left_shoulder_z = (
        landmarks[LEFT_SHOULDER].x * frame_width,
        landmarks[LEFT_SHOULDER].y * frame_height,
        landmarks[LEFT_SHOULDER].z,
    )
    right_shoulder_x, right_shoulder_y, right_shoulder_z = (
        landmarks[RIGHT_SHOULDER].x * frame_width,
        landmarks[RIGHT_SHOULDER].y * frame_height,
        landmarks[RIGHT_SHOULDER].z,
    )

    # Hip coordinates
    left_hip_x, left_hip_y, left_hip_z = (
        landmarks[LEFT_HIP].x * frame_width,
        landmarks[LEFT_HIP].y * frame_height,
        landmarks[LEFT_HIP].z,
    )
    right_hip_x, right_hip_y, right_hip_z = (
        landmarks[RIGHT_HIP].x * frame_width,
        landmarks[RIGHT_HIP].y * frame_height,
        landmarks[RIGHT_HIP].z,
    )

    # Nose coordinates
    nose_x = landmarks[NOSE].x * frame_width

    # Check vertical alignment (X-coordinates of nose, shoulders, hips)
    x_coords = [nose_x, left_shoulder_x, right_shoulder_x, left_hip_x, right_hip_x]
    min_x = min(x_coords)
    max_x = max(x_coords)

    if max_x - min_x > alignment_threshold:
        return False  # Points are not vertically aligned

    # Check horizontal alignment (Y-coordinates of shoulders and hips)
    shoulder_alignment = abs(left_shoulder_y - right_shoulder_y)
    hip_alignment = abs(left_hip_y - right_hip_y)

    if shoulder_alignment > alignment_threshold or hip_alignment > alignment_threshold:
        return False  # Shoulders or hips are tilted

    # Check depth alignment (Z-coordinates of shoulders and hips)
    shoulder_z_diff = abs(left_shoulder_z - right_shoulder_z)
    hip_z_diff = abs(left_hip_z - right_hip_z)

    if shoulder_z_diff > z_diff_threshold or hip_z_diff > z_diff_threshold:
        return False  # Shoulders or hips are not at the same depth

    return True

def verify_body_position(pose_landmarks, system_config,workout_config):
    """
    Verifies the body position by checking the body view, side view, straight side view, and bounding box alignment.

    Args:
        pose_landmarks (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Detected pose landmarks.
        system_config (dict): Configuration dictionary containing bounding box and other system parameters.

    Returns:
        dict: A dictionary containing:
            - body_view (str): "front", "side", or "unknown".
            - side_view_direction (str): "left", "right", or "unknown".
            - is_straight_side_view (bool): True if straight side view, False otherwise.
            - is_in_bounding_box (bool): True if body is within the bounding box, False otherwise.
            - feedback (str): Feedback message summarizing the results.
    """
    # Initialize result variables
    body_view = determine_view(pose_landmarks)
    view_direction = "unknown"
    correct_view = False

    if body_view == workout_config["view"]:
        correct_view = True
    # Check if the view is a side view
    if body_view == "side":
        view_direction = determine_side_view(pose_landmarks)
        is_straight_body_view = is_straight_side_view(pose_landmarks,system_config,side_view_direction = view_direction)
    else:
        view_direction = "front"
        is_straight_body_view = is_straight_front_view(pose_landmarks,system_config)

    # Check if the body is within the bounding box
    is_in_bounding_box = is_body_within_bounding_box(pose_landmarks, system_config)


    # Return the results as a dictionary
    return  correct_view,body_view, view_direction, is_straight_body_view, is_in_bounding_box


verify_rep_count_algorithms = {
    "squat": is_side_view,
    "bicep_curl": is_standing_side_view,
}


