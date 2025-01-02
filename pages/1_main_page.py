import streamlit as st
from components import components
from static.styles.page_styles.main_page_styles import css
from menu import menu
menu()
st.markdown(css, unsafe_allow_html=True)

components.top_navbar()
components.title("Main Menu")

_, col1, _ = st.columns([1,1,1])
with col1:
    if st.button("Start Exercise", key="start_exercise_btn", use_container_width=True):
        st.switch_page("pages/2_exercise_selection.py")

    components.empty(20)
    if st.button("Exercise Summary", key="exercise_summary_btn", use_container_width=True):
        st.switch_page("pages/3_exercise_summary.py")

