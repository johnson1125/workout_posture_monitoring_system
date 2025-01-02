import time
import streamlit as st


def get_hand_positions_pose(frame, pose_results):
    hand_positions = []
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        h, w, _ = frame.shape

        # Left Index Tip (Landmark 19)
        left_index = landmarks[19]
        left_x = int(left_index.x * w)
        left_y = int(left_index.y * h)
        hand_positions.append((left_x, left_y))

        # Right Index Tip (Landmark 20)
        right_index = landmarks[20]
        right_x = int(right_index.x * w)
        right_y = int(right_index.y * h)
        hand_positions.append((right_x, right_y))

    return hand_positions


# Function to handle interactions
def handle_interaction(hand_positions, buttons,session_state):
    activated_state = None

    for pos in hand_positions:
        x, y = pos
        for button in buttons:
            btn_x, btn_y = button["position"]
            btn_w, btn_h = button["size"]

            # Check if hand is within button boundaries
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                if session_state.current_button != button["label"]:
                    # Start hovering over a new button
                    session_state.current_button = button["label"]
                    session_state.button_hover_start_time = time.time()
                else:
                    # Continue hovering over the same button
                    elapsed_time = time.time() - session_state.button_hover_start_time
                    if elapsed_time >= 3:
                        # Activate the button
                        session_state.workout_state = button["next_state"]
                        activated_state = button["next_state"]

                        # Reset hover tracking
                        session_state.button_hover_start_time = None
                        session_state.current_button = None

                    return activated_state # Activate on first detection
                return activated_state

    # If no button is being hovered
    st.session_state.button_hover_start_time = None
    st.session_state.current_button = None
    return activated_state

def get_active_buttons(state, buttons):
    return [button for button in buttons if button["state"] == state]
