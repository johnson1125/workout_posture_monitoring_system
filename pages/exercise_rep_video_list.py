import streamlit as st
from static.styles.page_styles.exercise_rep_video_list_styles import css
from menu import menu
from utils import workout_record_utils
from utils import utils
from components import components
from utils import exercise_analyze_utils

if "selected_set" not in st.session_state  or "selected_summary_exercise" not in st.session_state:
    st.switch_page("pages/3_exercise_summary.py")
menu()
st.markdown(css, unsafe_allow_html=True)

components.top_navbar()
components.title(utils.remove_underscores_and_capitalize(st.session_state.selected_summary_exercise) + " Exercise Rep Video List")
components.subtitle(st.session_state.selected_set)

records = workout_record_utils.load_rep_records(st.session_state.workout_config,st.session_state.selected_summary,st.session_state.selected_set)

for entry in records:
    components.rep_video_list_item_container(entry,st.session_state.selected_set)


