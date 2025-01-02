import streamlit as st
from static.styles.page_styles.exercise_summary_styles import css
from menu import menu
from utils import workout_record_utils
from components import components

if "selected_summary" not in st.session_state:
    st.session_state.selected_summary = None
menu()
st.markdown(css, unsafe_allow_html=True)
components.top_navbar()
components.title("Exercise Summary")

tab1, tab2 = st.tabs(["Squat", "Bicep Curl",])

with tab1:
    entries = workout_record_utils.load_workout_summary(st.session_state.workout_config,"squat")
    for entry in entries:
        components.summary_item_container(entry)

with tab2:
    entries = workout_record_utils.load_workout_summary(st.session_state.workout_config, "bicep_curl")
    for entry in entries:
        components.summary_item_container(entry)

