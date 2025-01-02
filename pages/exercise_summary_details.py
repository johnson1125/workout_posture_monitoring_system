import streamlit as st
from static.styles.page_styles.exercise_summary_details_styles import css
from menu import menu
from utils import workout_record_utils
from utils import utils
from components import components
from utils import exercise_analyze_utils

if "selected_summary" not in st.session_state  or "selected_summary_exercise" not in st.session_state:
    st.switch_page("pages/3_exercise_summary.py")


records = workout_record_utils.load_workout_summary_details(st.session_state.workout_config,st.session_state.selected_summary)
menu()
st.markdown(css, unsafe_allow_html=True)
components.top_navbar()
components.title(utils.remove_underscores_and_capitalize(st.session_state.selected_summary_exercise) + " Exercise Summary")
components.subtitle(st.session_state.selected_summary)

set_analysis_entries = exercise_analyze_utils.analyze_exercise_sets(records,st.session_state.selected_summary_exercise)

for entry in set_analysis_entries:
    components.summary_details_item_container(entry)


