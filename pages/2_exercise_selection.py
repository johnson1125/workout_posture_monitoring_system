import streamlit as st
from components import components
from static.styles.page_styles.exercise_selection_styles import css
from menu import menu
menu()

st.markdown(css, unsafe_allow_html=True)
components.top_navbar()
components.title("Select an exercise")

_, col1, _ = st.columns([1,1,1])
with col1:
    if st.button("Squat", key="squat_btn", use_container_width=True):
        st.session_state.selected_exercise = 'squat'
        st.switch_page("pages/posture_monitoring.py")
    components.empty(20)
    if st.button("Bicep Curl", key="bicep_curl_btn", use_container_width=True):
        st.session_state.selected_exercise = 'bicep_curl'
        st.switch_page("pages/posture_monitoring.py")
    components.empty(20)
