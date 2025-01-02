import time
import numpy as np
import streamlit as st
from utils import feedback_utils,model_utils
from components import components
from static.styles.page_styles.posture_monitoring_menu_styles import css
import cv2
import gc
import mediapipe as mp
from menu import menu

system_config = st.session_state.system_config
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
engine = model_utils.load_pyttsx3_engine()
audio_temp_dir = system_config.get("audio_temp_files_path", "/tmp")
IDEAL_CAMERA_HEIGHT = 1.5  # meters, example: 1.5 meters from the ground
CENTER_TOLERANCE = 0.1  # tolerance for body center alignment (normalized)
TILT_THRESHOLD = 1  # degrees, allowable tilt angle between shoulders
# Calibration state variables
calibration_started = False
calibration_start_time = None

if "hand_inside_start_time" not in st.session_state:
    st.session_state.hand_inside_start_time = None

if "camera_calibration_IsRunning" not in st.session_state:
    st.session_state.camera_calibration_IsRunning = False

def update_session_data_value(session_data,value):
    st.session_state[session_data] = value

def calibrate_camera(frame):
    feedback = []

    # Convert frame to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Extract keypoints
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        # Calculate mid-point of shoulders (as body center)
        body_center_x = (left_shoulder.x + right_shoulder.x) / 2

        # Provide feedback on body alignment
        if abs(body_center_x - 0.5) > CENTER_TOLERANCE:
            feedback.append("Adjust your camera to center your body in the frame.")

        # Estimate camera height based on nose position (simplified for demo purposes)
        camera_height_estimation = 1 / nose.y  # Assume a proportional relationship for demonstration
        if abs(camera_height_estimation - IDEAL_CAMERA_HEIGHT) > 0.2:
            feedback.append(f"Adjust your camera height. Suggested height: {IDEAL_CAMERA_HEIGHT} meters.")

        # Check camera tilt based on shoulder alignment
        shoulder_angle = calculate_angle(left_shoulder, right_shoulder)
        if abs(shoulder_angle) > TILT_THRESHOLD:
            feedback.append(
                f"Your camera appears tilted by {abs(shoulder_angle):.1f}° relative to the horizontal plane. Adjust your camera to reduce tilt.")

        # Draw pose landmarks on frame
        frame = frame.copy()
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    else:
        feedback.append("No pose detected. Please ensure you are visible to the camera.")

    return frame, feedback


def start_calibration():
    st.session_state.camera_calibration_IsRunning = True

def end_calibration():
    st.session_state.camera_calibration_IsRunning = False
    gc.collect()
    cap.release()

# Function to calculate angle between two points
# Function to draw a start button and check for user action
def detect_start_action(frame, results):
    start_detected = False
    button_region = (0, 0, 405, 50)  # Define a region for the button (x1, y1, x2, y2)
    progress_bar_height = 10  # Height of the progress bar
    progress_bar_region = (button_region[0], button_region[3] + 5, button_region[2], button_region[3] + 5 + progress_bar_height)

    # Check if landmarks are detected
    if results.pose_landmarks:
        # Get hand landmarks
        landmarks = results.pose_landmarks.landmark
        left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        # Convert hand positions to pixel coordinates
        x_lh, y_lh = int(left_hand.x * frame.shape[1]), int(left_hand.y * frame.shape[0])
        x_rh, y_rh = int(right_hand.x * frame.shape[1]), int(right_hand.y * frame.shape[0])

        # Check if either hand is within the button region
        hand_in_box = (
            (button_region[0] < x_lh < button_region[2] and button_region[1] < y_lh < button_region[3])
            or (button_region[0] < x_rh < button_region[2] and button_region[1] < y_rh < button_region[3])
        )

        # If the hand is in the box, start the timer or update progress
        if hand_in_box:
            if st.session_state.hand_inside_start_time is None:
                # Start the timer
                st.session_state.hand_inside_start_time = time.time()
            else:
                # Calculate elapsed time and update the progress bar
                elapsed_time = time.time() - st.session_state.hand_inside_start_time
                progress_percentage = min(elapsed_time / 3, 1)  # Cap at 100%

                # Draw progress bar
                cv2.rectangle(frame,
                              (progress_bar_region[0], progress_bar_region[1]),
                              (int(progress_bar_region[0] + progress_percentage * (progress_bar_region[2] - progress_bar_region[0])), progress_bar_region[3]),
                              (255, 0, 0), -1)  # Blue fill for progress

                # If the hand stays for 3 seconds, trigger start
                if elapsed_time >= 3:
                    start_detected = True
        else:
            # Reset timer and progress bar if the hand exits the box
            st.session_state.hand_inside_start_time = None

        # Change button color when hovered
        button_color = (0, 255, 0) if hand_in_box else (0, 200, 0)  # Bright green if hovered, darker otherwise
    else:
        # Reset the timer if no landmarks are detected
        st.session_state.hand_inside_start_time = None
        button_color = (0, 200, 0)  # Default button color

    # Draw button on the frame
    cv2.rectangle(frame, (button_region[0], button_region[1]), (button_region[2], button_region[3]), button_color, -1)  # Button fill
    text_size = cv2.getTextSize("Start", cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    text_width, text_height = text_size[0]
    text_x = button_region[0] + (button_region[2] - text_width) // 2
    text_y = button_region[1] + (button_region[3] + text_height) // 2
    cv2.putText(frame, "Start", (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return frame, start_detected


# Function to calculate angle between two points
def calculate_angle(p1, p2):
    delta_y = p2.y - p1.y
    delta_x = p2.x - p1.x
    angle = np.degrees(np.arctan2(delta_y, delta_x))
    return angle

# Function to provide calibration feedback
def calibrate_pose(results):
    feedback = []
    config_IsCorrect = True

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Extract keypoints
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        # Check camera tilt based on shoulder alignment
        shoulder_angle = calculate_angle(left_shoulder, right_shoulder)
        hip_angle = calculate_angle(left_hip, right_hip)
        if abs(shoulder_angle) > TILT_THRESHOLD and abs(hip_angle) > TILT_THRESHOLD :
            config_IsCorrect = False
            if shoulder_angle > 0:
                feedback.append(
                    f"Your camera is tilted to the left by {abs(shoulder_angle):.1f}°. Adjust it to the right.")
            else:
                feedback.append(
                    f"Your camera is tilted to the right by {abs(shoulder_angle):.1f}°. Adjust it to the left.")



        # Check body alignment in frame (horizontal centering)
        body_center_x = (left_shoulder.x + right_shoulder.x) / 2
        if abs(body_center_x - 0.5) > CENTER_TOLERANCE:
            feedback.append("Adjust your camera to center your body in the frame.")
            config_IsCorrect = False

    return feedback,config_IsCorrect
def update_selected_camera():
    selected_index = st.session_state.camera_dict[st.session_state.camera_selector]
    st.session_state.selected_camera = selected_index % 10

menu()
st.markdown(css, unsafe_allow_html=True)
components.top_navbar()
components.title("Camera Calibration")


_, row1_col1,row1_col2, _ = st.columns([1,5,1,1],vertical_alignment="bottom")

with row1_col1:
    if st.session_state.camera_dict:
        # Camera selection
        st.selectbox("Select a Camera:", key="camera_selector",options=list(st.session_state.camera_dict.keys()),index=st.session_state.selected_camera,on_change=update_selected_camera)

    else:
        st.write("No cameras found.")

with row1_col2:
    if st.session_state.camera_calibration_IsRunning:
        st.button("End", key="end_btn", use_container_width=True,on_click=end_calibration)

    else:
        st.button("Start", key="start_btn",use_container_width=True,on_click=start_calibration)

_,row2_col1,_ = st.columns([1,1,1])
row3_col1 = st.columns(1)[0]

with row3_col1:
    progress_placeholder = st.empty()
    feedback_placeholders = st.empty()

with row2_col1:
    _,row2_col1_c1,_ = st.columns([2,15,2])
    with row2_col1_c1:
        if st.session_state.camera_calibration_IsRunning:
            FRAME_WINDOW = st.image([])
            FIXED_WIDTH = 405
            FIXED_HEIGHT = 720
            cap = cv2.VideoCapture(st.session_state.selected_camera, cv2.CAP_MSMF)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.resize(frame, (FIXED_WIDTH, FIXED_HEIGHT))
                frame = cv2.flip(frame,1)
                # Process with MediaPipe Hands
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pose_results = pose.process(frame_rgb)

                # Detect start action
                frame_with_button, start_detected = detect_start_action(frame, pose_results)

                # If start is detected, begin calibration
                if start_detected and not calibration_started:
                    calibration_started = True
                    calibration_start_time = time.time()
                    components.feedback_container(feedback_placeholders,
                                                  "Stand still for 3 seconds...")
                    feedback_utils.text_to_audio_feedback(audio_temp_dir, "Stand still for 3 seconds.", engine)

                # If calibration is in progress
                if calibration_started:
                    elapsed_time = time.time() - calibration_start_time
                    if elapsed_time <= 3:
                        # Show progress bar below the button
                        FRAME_WINDOW.image(cv2.cvtColor(frame_with_button, cv2.COLOR_BGR2RGB), channels="RGB")
                        progress_placeholder.progress(int(elapsed_time / 3 * 100))
                    else:
                        # Calibration complete
                        feedback,config_IsCorrect = calibrate_pose(pose_results)

                        if(config_IsCorrect):
                            feedback_utils.text_to_audio_feedback(audio_temp_dir, "Calibration completed",
                                                                  engine)
                            components.feedback_container(feedback_placeholders,
                                                         "Calibration completed")
                            st.session_state.camera_calibrated = True
                        else:
                            feedback_utils.text_to_audio_feedback(audio_temp_dir, "Camera configuration incorrect, please adjust it.",
                                                                  engine)
                            components.feedback_container(feedback_placeholders,
                                                          "Feedback:\n" + "\n".join(f"- {msg}" for msg in feedback))
                            st.session_state.camera_calibrated = False
                        calibration_started=False
                        # Show feedback and reset state

                        progress_placeholder.empty()

                # Display the video feed with the button
                FRAME_WINDOW.image(cv2.cvtColor(frame_with_button, cv2.COLOR_BGR2RGB), channels="RGB")



                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
