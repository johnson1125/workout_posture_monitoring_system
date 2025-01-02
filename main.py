import streamlit as st
from utils import utils
from utils import model_utils
import config


st.set_page_config(layout="wide",page_title="Workout Posture Monitoring System",initial_sidebar_state="collapsed" )

if "workout_config" not in st.session_state:
    st.session_state.workout_config = config.workout_configurations

if "system_config"  not in st.session_state:
    st.session_state.system_config = config.system_configuration

if "selected_exercise" not in st.session_state:
    st.session_state.selected_exercise = "squat"

if "camera_calibrated" not in st.session_state:
    st.session_state.camera_calibrated = False

if "selected_camera" not in st.session_state:
    st.session_state.selected_camera = 0

st.session_state.camera_dict = utils.get_camera_dict()


model_utils.load_mp_model()
model_utils.load_pyttsx3_engine()
model_utils.load_all_models(st.session_state.workout_config)


pages = [
    st.Page("pages/1_main_page.py", title="Main Page", default=True),
    st.Page("pages/2_exercise_selection.py", title="Exercise Selection"),
    st.Page("pages/3_exercise_summary.py", title="Exercise Summary"),
    st.Page("pages/4_camera_calibration.py", title="Camera Calibration"),
    st.Page("pages/posture_monitoring.py", title="Posture Monitoring"),
    st.Page("pages/exercise_summary_details.py", title="Exercise Summary Details"),
    st.Page("pages/exercise_set_video_playback.py", title="Set Video Player"),
    st.Page("pages/exercise_rep_video_list.py", title="Rep Video List"),
    st.Page("pages/exercise_rep_video_playback.py", title="Rep Video Player"),

]
nav = st.navigation(pages,position="hidden")
nav.run()

