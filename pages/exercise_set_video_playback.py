import os.path
import streamlit as st
from static.styles.page_styles.exercise_set_video_playback_styles import css
from menu import menu
from utils import utils
from components import components

if "selected_set" not in st.session_state  or "selected_summary_exercise" not in st.session_state:
    st.switch_page("pages/3_exercise_summary.py")


menu()
st.markdown(css, unsafe_allow_html=True)
components.top_navbar()
components.title(f"{utils.remove_underscores_and_capitalize(st.session_state.selected_summary_exercise)} Exercise Set Video Playback")
components.subtitle(st.session_state.selected_set)

video_folder_path = st.session_state.workout_config[st.session_state.selected_summary_exercise]["workout_data_directory"]["set_video"]

video_file_path = f"{video_folder_path}/{st.session_state.selected_set}.mp4"
print(video_file_path)
video_file = open(video_file_path, "rb")
video_bytes = video_file.read()

components.set_video_playback(video_bytes,st.session_state.set_analysis)



