import cv2
import time
import mediapipe as mp
from . import (timer_utils,
               user_interaction_utils,
               body_verification_utils,
               visualization_utils,
               feedback_utils,
               keypoints_utils,
               interpolation_utils,
               model_utils,
               utils,
               workout_record_utils)
from components import components
from .keypoints_utils import mp_pose


class PostureMonitor:
    def __init__(self, system_config, workout_config, exercise, exercise_id, engine, audio_temp_dir, placeholders,
                 video_recorders,
                 session_state, frame_window):

        self.audio_duration = 3
        self.audio_last_played_time = 0
        self.system_config = system_config
        self.workout_config = workout_config
        self.exercise = exercise
        self.exercise_id = exercise_id
        self.engine = engine
        self.audio_temp_dir = audio_temp_dir
        self.placeholders = placeholders
        self.session_state = session_state
        self.video_recorders = video_recorders
        self.frame_window = frame_window
        self.timer = timer_utils.Timer()

        # fps calculation
        self.frame_count = 0
        self.current_fps = 0

        # frame interpolation
        self.sequence = []
        self.interpolate_sequence = []

        # feedback generation
        self.feedback_delay = None
        self.rep_detections = []
        self.rep_frames_fps = []
        self.reps_results = []
        self.mistake_counts = {key: 0 for key in workout_config["labels"]}

        # ready stage handling
        self.body_position_feedback_played = None
        self.feedback_played = False
        self.correct_position = False
        self.view_direction = None
        self.feedback = ""

        # rep counting
        self.current_stage = "none"
        self.stage = "none"

        # inference model
        self.interpreter, self.input_details, self.output_details = model_utils.load_tflite_model(
            self.workout_config["model_path"])

        # media pose
        self.pose = mp.solutions.pose.Pose(min_tracking_confidence=0.8)
        self.mp_drawing = mp.solutions.drawing_utils

        # in bounding box detection
        self.keypoints = None

    def handle_ready_state(self, frame, results):
        """Handle the 'ready' state by verifying body position and providing feedback."""
        # Body verification
        current_time = time.time()
        verification = body_verification_utils.verify_body_position(
            results.pose_landmarks, self.system_config, self.workout_config
        )
        correct_view, body_view, self.view_direction, is_straight_body_view, is_in_bounding_box = verification

        # Draw bounding box
        visualization_utils.draw_bounding_box(frame, self.system_config["bounding_box"], is_in_bounding_box)

        # Generate feedback
        body_position_feedback, correct_body_position = feedback_utils.generate_body_position_feedback(
            correct_view, body_view, self.view_direction, is_straight_body_view, is_in_bounding_box
        )

        # Update ready time and correct position flag
        if correct_body_position:
            if not self.correct_position:
                self.session_state.ready_time = time.time()
            self.correct_position = True
        else:
            self.correct_position = False
            self.session_state.ready_time = None

        # Play feedback audio if not already played
        if current_time > self.audio_last_played_time + self.audio_duration and body_position_feedback != self.body_position_feedback_played:
            duration = feedback_utils.text_to_audio_feedback(self.audio_temp_dir, body_position_feedback, self.engine)
            self.audio_last_played_time = current_time
            self.audio_duration = duration + 0.5
            self.body_position_feedback_played = body_position_feedback

        # Update system info UI
        self.placeholders['system_info'].success(body_position_feedback)

        # Draw progress and check if ready to start
        if self.session_state.ready_time is not None:
            elapsed_time = time.time() - self.session_state.ready_time
            visualization_utils.draw_progress(frame, self.system_config, elapsed_time)
            if elapsed_time >= 3 and correct_body_position:
                # Transition to 'start' state
                self.session_state.ready_time = None
                self.session_state.workout_state = "start"
                self.placeholders['system_info'].success(f"Start monitoring {self.exercise}")
                self.audio_last_played_time = 0
                self.audio_duration = 0
                self.body_position_feedback_played = "none"
                feedback_utils.text_to_audio_feedback(
                    self.audio_temp_dir,
                    f"{self.exercise} monitoring started, Rep {self.session_state.rep}",
                    self.engine
                )
                self.timer.start()

    def handle_start_state(self, frame, results):
        """Handle the 'start' state by monitoring reps and providing feedback."""
        # Update workout time
        seconds = int(self.timer.get_time())
        formatted_time = self.timer.format_time(seconds)
        self.session_state.workout_time = formatted_time
        components.text_container_with_label(self.placeholders["workout_time"], "Workout Time",
                                             self.session_state.workout_time)

        # Check if body is within bounding box
        is_in_bounding_box = body_verification_utils.is_body_within_bounding_box(results.pose_landmarks,
                                                                                 self.system_config)
        if is_in_bounding_box:
            # Posture classification and feedback
            rep_count = body_verification_utils.verify_rep_count_algorithms[self.session_state.selected_exercise](
                pose_landmarks = results.pose_landmarks,
                system_config = self.system_config,
                side_view_direction = self.view_direction)
            print(rep_count)
            if rep_count:
                self.handle_posture_classification()

            else:
                self.stage="none"
            self.rep_frames_fps.append(self.current_fps)

            # Update rep and set information on frame
            cv2.putText(frame, f'Set: {self.session_state.set}', (10, frame.shape[0] - 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, f'Rep: {self.session_state.rep}', (10, frame.shape[0] - 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            # Enqueue frames for recording
            self.video_recorders["set_video_recorder"].enqueue_frame(frame.copy(), self.exercise_id,
                                                                     set_num=self.session_state.set)
            self.video_recorders["rep_video_recorder"].enqueue_frame(frame.copy(), self.exercise_id,
                                                                     rep=self.session_state.rep,
                                                                     set_num=self.session_state.set)
            print(self.view_direction)
            if rep_count:
            # Count reps

                new_rep, self.current_stage, angle = keypoints_utils.rep_counting_algorithms[
                    self.session_state.selected_exercise
                ](
                    current_stage=self.current_stage,
                    stage=self.stage,
                    keypoints=self.keypoints,
                    workout_config=self.workout_config,
                    system_config=self.system_config,
                    view_direction=self.view_direction
                )
                print(angle)

                if new_rep:
                    self.feedback_delay = keypoints_utils.new_rep_delay_algorithm[self.session_state.selected_exercise](self.rep_frames_fps)

            if self.feedback_delay is not None:
                if self.feedback_delay > 0:
                    self.feedback_delay -= 1
                elif self.feedback_delay == 0:
                    self.session_state.rep+=1
                    # Update rep count in UI
                    components.text_container_with_label(self.placeholders["rep"], "Rep", self.session_state.rep)

                    rep_result, self.reps_results, feedback, self.mistake_counts = feedback_utils.analyze_rep(
                        self.session_state.rep, self.reps_results, self.rep_detections, self.rep_frames_fps,
                        self.workout_config,
                        self.mistake_counts
                    )

                    feedback_utils.text_to_audio_feedback(self.audio_temp_dir, f"Rep {self.session_state.rep}, {feedback}",
                                                          self.engine)
                    self.rep_detections.clear()
                    self.rep_frames_fps.clear()

                    # Update mistake counts in UI
                    for label in self.workout_config["labels"]:
                        components.text_container_with_label(
                            self.placeholders["label"][label],
                            utils.remove_underscores_and_capitalize(label),
                            self.mistake_counts[label]
                        )

                    # Update feedback UI
                    components.feedback_container(self.placeholders["feedback"], feedback)

                    # Stop recording for the current rep
                    self.video_recorders["rep_video_recorder"].stop_recording(self.exercise_id,
                                                                              rep=self.session_state.rep - 1,
                                                                              set_num=self.session_state.set)

                    # Start recording for the new rep
                    self.video_recorders["rep_video_recorder"].start_recording(self.exercise_id, rep=self.session_state.rep,
                                                                               set_num=self.session_state.set)

                    self.feedback_delay = None
            self.stage = self.current_stage
        else:
            # Pause workout if body is outside bounding box
            self.timer.pause()
            self.rep_detections.clear()
            self.rep_frames_fps.clear()
            # Clear sequences
            self.interpolate_sequence.clear()
            self.sequence.clear()
            self.session_state.workout_state = "pause"
            self.stage = "none"
            self.current_stage = "none"

    def handle_posture_classification(self):
        """Process keypoint sequences for posture classification and provide feedback."""
        posture_class, confidence = model_utils.predict_posture(
            self.interpolate_sequence,
            self.interpreter,
            self.input_details,
            self.output_details,
            self.workout_config["sequence_length"]
        )

        if posture_class is not None:
            self.rep_detections.append(posture_class)

    def keypoint_extraction_and_normalization(self, results):

        if self.view_direction in self.workout_config["keypoints"]:
            self.keypoints = keypoints_utils.extract_keypoints(results, self.workout_config["keypoints"][
                self.view_direction])
            if self.view_direction == "right":
                keypoints_normalized = keypoints_utils.scale_and_rel_position_normalize_keypoints(
                    self.keypoints, flip_horizontally=True)
            else:
                keypoints_normalized = keypoints_utils.scale_and_rel_position_normalize_keypoints(
                    self.keypoints, flip_horizontally=False)
            self.sequence.append(keypoints_normalized)

            # Limit sequence length
        if len(self.sequence) > self.workout_config["sequence_length"]:
            self.sequence.pop(0)

    def sequence_interpolation(self):
        sequence_needed = interpolation_utils.calculate_sequence_needed(self.current_fps,
                                                                        self.system_config["target_fps"],
                                                                        self.workout_config["sequence_length"])

        if len(self.sequence) >= sequence_needed and self.current_fps != 0:
            self.interpolate_sequence = interpolation_utils.process_keypoints_sequence(
                self.sequence[-sequence_needed:], self.current_fps, self.system_config["target_fps"],
                self.workout_config["sequence_length"]
            )

    # Handle user interactions
    def handle_user_interactions(self, frame, results):
        active_buttons = user_interaction_utils.get_active_buttons(self.session_state.workout_state,
                                                                   self.system_config["buttons"].values())

        # Draw active buttons on frame
        frame = visualization_utils.draw_buttons(frame, active_buttons, self.session_state.current_button)

        # Detect hand positions using Pose
        hand_positions = user_interaction_utils.get_hand_positions_pose(frame, results)

        # Handle button interactions
        activated_state = user_interaction_utils.handle_interaction(hand_positions, active_buttons, self.session_state)

        # Handle state transitions based on interaction
        if activated_state == "idle":
            # Save workout set records
            workout_record_utils.save_workout_set_record(
                self.exercise_id, self.session_state.set, self.reps_results,
                self.session_state.workout_time, self.mistake_counts, self.workout_config
            )
            self.reset_workout_state()
            self.video_recorders["set_video_recorder"].stop_recording(self.exercise_id,
                                                                      set_num=self.session_state.set - 1)
            self.video_recorders["rep_video_recorder"].stop_all_recordings()

        elif activated_state == "ready":
            # Start a new set
            if self.session_state.rep == 0:
                self.session_state.rep += 1
                components.text_container_with_label(self.placeholders["rep"], "Rep", self.session_state.rep)

            self.session_state.workout_state = "ready"
            self.video_recorders["set_video_recorder"].start_recording(self.exercise_id,
                                                                       set_num=self.session_state.set)
            self.video_recorders["rep_video_recorder"].start_recording(self.exercise_id,
                                                                       set_num=self.session_state.set,
                                                                       rep=self.session_state.rep)

        elif activated_state == 'pause':
            self.timer.pause()
            self.rep_detections.clear()
            self.rep_frames_fps.clear()
            # Clear sequences
            self.interpolate_sequence.clear()
            self.sequence.clear()
            self.session_state.workout_state = "pause"
            self.stage = "none"
            self.current_stage = "none"

        if self.session_state.current_button:
            for button in active_buttons:
                if button["label"] == self.session_state.current_button:
                    elapsed = time.time() - self.session_state.button_hover_start_time
                    frame = visualization_utils.draw_hover_progress(frame, button, elapsed)
                    break

    # Reset workout state after completing a set
    def reset_workout_state(self):
        self.session_state.rep = 0
        self.session_state.set += 1
        self.session_state.set_results.append(self.reps_results)
        self.reps_results.clear()
        self.timer.reset()
        self.session_state.workout_time = "00:00"

        components.text_container_with_label(self.placeholders["workout_time"], "Workout Time",
                                             self.session_state.workout_time)
        components.text_container_with_label(self.placeholders["rep"], "Rep", self.session_state.rep)
        components.text_container_with_label(self.placeholders["set"], "Set", self.session_state.set)

        self.mistake_counts = {key: 0 for key in self.workout_config["labels"]}
        for label in self.workout_config["labels"]:
            components.text_container_with_label(
                self.placeholders["label"][label],
                utils.remove_underscores_and_capitalize(label),
                self.mistake_counts[label]
            )

    def run_posture_monitoring(self):
        resize_size = (self.system_config["resize_width"], self.system_config["resize_height"])
        frame_size = (self.system_config["frame_width"], self.system_config["resize_height"])
        cap = cv2.VideoCapture(self.session_state['selected_camera'], cv2.CAP_MSMF)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
        start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.resize(frame, resize_size)
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False


            results = self.pose.process(image)

            if results.pose_landmarks:
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)



                # Handle workout states
                state = self.session_state.workout_state
                if state != "idle":
                    self.keypoint_extraction_and_normalization(results)
                    self.sequence_interpolation()
                    if state == "ready":
                        self.handle_ready_state(frame, results)
                    elif state == "start":
                        self.handle_start_state(frame, results)

            self.handle_user_interactions(frame, results)

            # FPS calculation
            self.frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time > 1:
                self.current_fps = self.frame_count / elapsed_time
                self.frame_count = 0
                start_time = time.time()

            time_per_frame_ms = (1 / self.current_fps) * 1000 if self.current_fps > 0 else 0

            # Draw FPS info on frame
            cv2.putText(frame, f'FPS: {self.current_fps:.2f}', (10, resize_size[1] - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, f'Time per frame: {time_per_frame_ms:.2f} ms', (10, resize_size[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            # Display frame in Streamlit
            self.frame_window.image(frame, channels="BGR", use_container_width=True)

        cap.release()
        cv2.destroyAllWindows()
        self.session_state.posture_monitoring_IsRunning = False  # Ensure monitoring stops
