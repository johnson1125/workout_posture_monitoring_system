# Workout Posture Monitoring System

The Workout Posture Monitoring System is a real-time application designed to evaluate and improve exercise posture using advanced computer vision and machine learning techniques. It leverages MediaPipe for keypoint detection, TensorFlow Lite for posture classification, and employs Streamlit as the frontend framework for an intuitive and interactive user interface. The system provides functionalities such as real-time posture analysis, rep counting, feedback on common mistakes, and video playback for detailed performance review, ensuring a comprehensive and user-friendly experience for fitness enthusiasts.

## Prerequisites

Before setting up the environment, ensure the following tools are installed on your system:

1. Anaconda
2. Python 3.8 or above
3. GPU with CUDA support

## Setting Up the Environment

1. Create a new Conda environment using the provided `environment.yml` file:
   ```bash
   conda env create -f environment.yml
   ```

2. Activate the environment:
   ```bash
   conda activate workout_posture_monitoring
   ```

## Usage

1. Launch the Streamlit application:
   ```bash
   streamlit run main.py
   ```

2. Follow the steps to:
   - Calibrate your camera.
   - Select an exercise (e.g., Squats or Bicep Curls).
   - Start monitoring your workout posture in real time.

3. Review your workout summary and recorded videos for detailed feedback.

[Learn more about Anaconda](https://www.anaconda.com/)

## Functionalities

### Directories and Scripts

- **`models/`:**
  Stores pre-trained TensorFlow Lite (TFLite) models for posture classification.

- **`utils/`:**
  Contains utility scripts for keypoint processing, feedback generation, data normalization, and more.
  - `body_verification_utils.py`: Verifies user posture alignment and view direction during exercises.
  - `exercise_analyze_utils.py`: Analyzes workout sets, identifies trends, and provides recommendations.
  - `feedback_utils.py`: Generates real-time textual and audio feedback for detected mistakes.
  - `interpolation_utils.py`: Handles interpolation of keypoint sequences to match model input requirements.
  - `keypoints_utils.py`: Processes keypoints, normalizes positions, and computes angles for posture evaluation.
  - `model_utils.py`: Loads MediaPipe models, TensorFlow Lite models, and manages inference.
  - `posture_monitor_utils.py`: Manages real-time posture monitoring with feedback and repetition counting.
  - `timer_utils.py`: Tracks workout durations and formats elapsed time for display.
  - `user_interaction_utils.py`: Handles touchless interactions through hand gesture recognition.
  - `utils.py`: Provides general utility functions like camera selection and string formatting.
  - `video_recording_utils.py`: Manages concurrent video recordings for workout sets and repetitions.
  - `visualization_utils.py`: Overlays visual feedback elements like progress bars and bounding boxes on frames.
  - `workout_record_utils.py`: Handles storage, retrieval, and summarization of workout data.

- **`pages/`:**
  Implements the web interface using Streamlit.
  - `main_page.py`: Entry page with options to start an exercise or view workout summaries.
  - `exercise_selection.py`: Allows users to select the type of exercise (e.g., squats or bicep curls).
  - `exercise_summary.py`: Displays a summary of workout history for each exercise.
  - `camera_calibration.py`: Guides users through camera calibration for accurate pose detection.
  - `exercise_summary_details.py`: Provides detailed insights into a specific workout session.
  - `exercise_set_video_playback.py`: Allows users to review video recordings of entire workout sets.
  - `exercise_rep_video_list.py`: Lists individual repetition videos for a selected workout set.
  - `exercise_rep_video_playback.py`: Enables playback of videos for individual repetitions, with detailed feedback.
  - `posture_monitor.py`: Handles real-time posture monitoring, feedback, and repetition counting.

- **`static/`:**
  Contains styling resources and application branding assets.

- **`main.py`:**
  The central application script that integrates all modules and functionalities.

- **`config.py`:**
  Defines configurations for exercises, feedback messages, model paths, and more.
