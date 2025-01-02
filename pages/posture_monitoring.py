# pages/1_Posture_Monitoring.py

import os
import threading
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
from menu import menu
from static.styles.page_styles.posture_monitoring_styles import css
from utils.posture_monitor import PostureMonitor
from utils.video_recording_utils import VideoRecorder
from utils import (
    utils,
    model_utils,
    interpolation_utils,
    keypoints_utils,
    feedback_utils,
    user_interaction_utils,
    visualization_utils,
    body_verification_utils,
    timer_utils,
    workout_record_utils
)
from components import components


# ----------------------------------------------------------------------------------
# Initialization Functions
# ----------------------------------------------------------------------------------
menu()
def initialize_session_state():
    """Initialize Streamlit session state with default values."""
    default_states = {
        "workout_time": "00:00",
        "set": 1,
        "set_results": [],
        "rep": 0,
        "button_hover_start_time": None,
        "button_ready_time": None,
        "current_button": None,
        "workout_state": "idle",  # States: idle, ready, start, pause
    }
    for key, value in default_states.items():
            st.session_state[key] = value

    if "posture_monitoring_IsRunning" not in st.session_state:
        st.session_state.posture_monitoring_IsRunning = False

def initialize_posture_monitor_and_video_recorders():
    if "exercise_video_recorder" not in st.session_state or "monitor" not in st.session_state or st.session_state.exercise_video_recorder != st.session_state.selected_exercise :
        st.session_state.exercise_video_recorder = st.session_state.selected_exercise
        st.session_state.video_recorders = initialize_video_recorders(system_config, workout_config)
        # Create PostureMonitor instance
        st.session_state.monitor = PostureMonitor(system_config=system_config,
                                 workout_config=workout_config,
                                 engine=engine,
                                 exercise=exercise,
                                 exercise_id=exercise_id,
                                 audio_temp_dir=audio_temp_dir,
                                 placeholders=placeholders,
                                 video_recorders=st.session_state.video_recorders,
                                 session_state=st.session_state,
                                 frame_window=frame_window)
    else:
        st.session_state.monitor.exercise_id = exercise_id

def initialize_video_recorders(system_config, workout_config):
    """Initialize video recorders for reps and sets."""
    rep_video_output_dir = workout_config["workout_data_directory"]["rep_video"]
    set_video_output_dir = workout_config["workout_data_directory"]["set_video"]
    os.makedirs(rep_video_output_dir, exist_ok=True)
    os.makedirs(set_video_output_dir, exist_ok=True)

    video_recorders = {}

    video_recorders["rep_video_recorder"] = VideoRecorder(
        resize_size=(system_config.get("resize_width", 640), system_config.get("resize_height", 480)),
        frame_rate=24,
        output_dir=rep_video_output_dir
    )

    video_recorders["set_video_recorder"] = VideoRecorder(
        resize_size=(system_config.get("resize_width", 640), system_config.get("resize_height", 480)),
        frame_rate=24,
        output_dir=set_video_output_dir
    )

    return video_recorders



# ----------------------------------------------------------------------------------
# UI Setup Functions
# ----------------------------------------------------------------------------------

def st_ui(system_config, workout_config, exercise):
    """Setup the main UI components."""
    st.markdown(css, unsafe_allow_html=True)
    components.top_navbar()
    components.title(f"{exercise} Posture Monitoring")
    placeholders = {}

    # Columns for camera selection and calibration/start buttons
    _, row1_col1, row1_col2, _ = st.columns([1, 5, 1, 1], vertical_alignment="bottom")

    with row1_col1:
        st.selectbox(
            "Selected Camera:",
            key="camera_selector",
            options=list(st.session_state.get("camera_dict", {}).keys()),
            index=st.session_state.selected_camera,
            disabled=True
        )

    with row1_col2:
        if st.session_state.camera_calibrated:
            if not st.session_state.posture_monitoring_IsRunning:
                st.button("Start", key="start_btn", use_container_width=True, on_click=start_monitoring)
            else:
                st.button("End", key="stop_btn", use_container_width=True, on_click=stop_monitoring)
        else:
            if st.button("Calibrate Camera", key="calibrate_btn", use_container_width=True):
                st.switch_page("pages/4_camera_calibration.py")

    if st.session_state.posture_monitoring_IsRunning:
        # Setup UI elements visible when monitoring is running
        row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 1], vertical_alignment="top")
        row3_col1 = st.columns(1)[0]

        with row3_col1:
            placeholders["system_info"] = st.empty()
            placeholders["feedback"] = st.empty()
            components.feedback_container(placeholders["feedback"], "")

        with row2_col1:
            _, _, row2_col1_c1 = st.columns([1, 1, 2])
            with row2_col1_c1:
                # Exercise Information
                placeholders["exercise"] = st.empty()
                components.text_container_with_label(placeholders["exercise"], "Exercise", exercise)
                components.empty(20)

                # Workout Time
                placeholders["workout_time"] = st.empty()
                components.text_container_with_label(placeholders["workout_time"], "Workout Time",
                                                     st.session_state.workout_time)
                components.empty(20)

                # Set Information
                placeholders["set"] = st.empty()
                components.text_container_with_label(placeholders["set"], "Set", str(st.session_state.set))
                components.empty(20)

                # Rep Information
                placeholders["rep"] = st.empty()
                components.text_container_with_label(placeholders["rep"], "Rep", str(st.session_state.rep))

        with row2_col3:
            row2_col3_c1, _, _ = st.columns([2, 1, 1])
            with row2_col3_c1:
                placeholders["label"] = {}

                for label in workout_config.get("labels", []):
                    placeholders["label"][label] = st.empty()
                    components.empty(20)
                    components.text_container_with_label(
                        placeholders["label"][label],
                        utils.remove_underscores_and_capitalize(label),
                        "0"
                    )





        with row2_col2:
            _, row2_col2_c1, _ = st.columns([2, 4, 2])
            with row2_col2_c1:
                # Placeholder for video frames
                frame_window = st.image([])
                return frame_window, placeholders


# ----------------------------------------------------------------------------------
# Callback Functions
# ----------------------------------------------------------------------------------

def start_monitoring():
    """Callback to start posture monitoring."""
    st.session_state.posture_monitoring_IsRunning = True

def stop_monitoring():
    st.session_state.posture_monitoring_IsRunning = False
    st.session_state.monitor.video_recorders["rep_video_recorder"].stop_all_recordings()
    st.session_state.monitor.video_recorders["set_video_recorder"].stop_all_recordings()





# Load configurations
workout_config = st.session_state.workout_config.get(st.session_state.selected_exercise, {})
system_config = st.session_state.system_config

# Initialize session state
initialize_session_state()
exercise = utils.remove_underscores_and_capitalize(st.session_state.selected_exercise)
exercise_id = workout_record_utils.generate_exercise_id(st.session_state.selected_exercise)



# Setup UI and get UI components
setup_ui_output = st_ui(system_config, workout_config, exercise)
if setup_ui_output:
    frame_window, placeholders = setup_ui_output

    # Load audio engine and set audio temp directory
    engine = model_utils.load_pyttsx3_engine()
    audio_temp_dir = system_config.get("audio_temp_files_path", "/tmp")

    initialize_posture_monitor_and_video_recorders()
    print(st.session_state.video_recorders["set_video_recorder"].recordings)
    print(st.session_state.video_recorders["rep_video_recorder"].recordings)

    if st.session_state.posture_monitoring_IsRunning:
        st.session_state.monitor.run_posture_monitoring()

    # Optional: Handle stopping the monitoring via a button
    if st.session_state.posture_monitoring_IsRunning:
        if st.button("Stop Monitoring"):
            st.session_state.posture_monitoring_IsRunning = False
            st.rerun()  # Trigger Streamlit to rerun the script


