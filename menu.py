import streamlit as st
def menu():
    st.sidebar.image("static/logo.png",width=100)
    st.sidebar.title("Workout Monitoring System")
    st.sidebar.page_link("pages/1_main_page.py", label="Main Page")
    st.sidebar.page_link("pages/2_exercise_selection.py", label="Exercise Selection")
    st.sidebar.page_link("pages/3_exercise_summary.py", label="Exercise Summary")
    st.sidebar.page_link("pages/4_camera_calibration.py", label="Camera Calibration")