workout_configurations = {
    "squat": {
        "model_path": "models/squat_posture_model.tflite",
        "view": "side",
        "keypoints": {
            "right": ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE", "LEFT_HEEL", "LEFT_FOOT_INDEX"],
            "left": ["RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE", "RIGHT_HEEL", "RIGHT_FOOT_INDEX"],
        },
        "keypoints_num": 6,
        "angle_keypoints": {
            "right": ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"],
            "left": ["RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"],
        },
        "body_verification": {
            "right": ["RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE", "RIGHT_HEEL", "RIGHT_FOOT_INDEX"],
            "left": ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE", "LEFT_HEEL", "LEFT_FOOT_INDEX"],
        },
        "sequence_length": 60,
        "normalization": "combined",
        "labels": {"proper_squat": 0,
                   "lifting_heels": 1,
                   "shallow_depth": 2},
        "feedback_messages": {
            "normal": {
                "shallow_depth": ["Go deeper in your squat.", "Lower your hips further."],
                "lifting_heels": ["Keep your heels flat on the ground.", "Distribute your weight evenly."],
            },
            "elevated": {
                "shallow_depth": ["Your depth is consistently shallow.",
                                  "Focus on lowering your hips below your knees."],
                "lifting_heels": ["Your heels keep lifting. Keep them grounded.",
                                  "Anchor your heels for better stability."],
            },
            "supportive": {
                "shallow_depth": ["Good improvement on depth!", "You're getting better at going deeper."],
                "lifting_heels": ["Nice job keeping your heels down!", "Your stance looks much more stable."],
            },
            "appraisal": [
                "Excellent squat!", "Great job! Keep it up.", "Perfect form!", "You're doing amazing!",
                "Fantastic work! Keep going."
            ]
        },
        "workout_data_directory": {
            "workout_data": "exercise/squat/workout_record.json",
            "set_video": "exercise/squat/video/set",
            "rep_video": "exercise/squat/video/rep",

        },
        "mistake_types": ["lifting_heels", "shallow_depth"],
        "recommendations": {
            "shallow_depth": {
                "Low": "Focus on maintaining proper squat depth for better effectiveness.",
                "Moderate": "Work on achieving a slightly deeper squat to improve form.",
                "High": "Ensure you're lowering your hips sufficiently to achieve a deeper squat. Consider using a mirror or video feedback to monitor depth."
            },
            "lifting_heels": {
                "Low": "Pay attention to your heel position to maintain proper form.",
                "Moderate": "Try to keep your heels flat to enhance stability during squats.",
                "High": "Focus on keeping your heels firmly on the ground. Strengthen your calves and practice maintaining balance."
            },
        },

    },
    "bicep_curl": {
        "model_path": "models/bicep_curl_posture_model.tflite",
        "view": "side",
        "keypoints": {
            "right": [
                "LEFT_SHOULDER", "LEFT_HIP", "LEFT_ELBOW", "LEFT_WRIST",
                "LEFT_PINKY", "LEFT_INDEX", "LEFT_THUMB"
            ],
            "left": [
                "RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_ELBOW", "RIGHT_WRIST",
                "RIGHT_PINKY", "RIGHT_INDEX", "RIGHT_THUMB"
            ],

        },
        "keypoints_num": 7,
        "angle_keypoints": {
            "right": ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"],
            "left": ["RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"],

        },
        "body_verification": {
            "right": ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE", "LEFT_HEEL", "LEFT_FOOT_INDEX"],
            "left": ["RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE", "RIGHT_HEEL", "RIGHT_FOOT_INDEX"],

        },
        "sequence_length": 60,
        "normalization": "combined",
        "labels": {
            "proper_bicep_curl": 0,
            "elbow_drift": 1,
            "incomplete_contraction": 2,
            "momentum_cheat": 3
        },
        "feedback_messages": {
            "normal": {
                "elbow_drift": ["Keep your elbows close to your sides.", "Avoid letting your elbows move forward."],
                "incomplete_contraction": ["Fully contract your biceps at the top.",
                                           "Squeeze your biceps for maximum contraction."],
                "momentum_cheat": ["Perform the movement slowly and with control.",
                                   "Avoid using momentum to lift the weight."]
            },
            "elevated": {
                "elbow_drift": ["Your elbows are consistently drifting forward.",
                                "Focus on keeping elbows stationary to isolate biceps."],
                "incomplete_contraction": ["You're not fully contracting your biceps.",
                                           "Ensure each rep reaches full contraction at the top."],
                "momentum_cheat": ["You're relying too much on momentum.",
                                   "Control the weight during both lifting and lowering phases."]
            },
            "supportive": {
                "elbow_drift": ["Great job keeping your elbows steady!", "You're improving your elbow position."],
                "incomplete_contraction": ["Good work achieving full contractions!",
                                           "Your bicep engagement is improving."],
                "momentum_cheat": ["Nice control over your movements!", "You're lifting with excellent form."]
            },
            "appraisal": [
                "Fantastic curls!", "Your form is excellent!", "Great job! Keep it up!", "Perfect bicep curls!",
                "You're crushing it!"
            ]
        },
        "workout_data_directory": {
            "workout_data": "exercise/bicep_curl/workout_record.json",
            "set_video": "exercise/bicep_curl/video/set",
            "rep_video": "exercise/bicep_curl/video/rep",
        },
        "mistake_types": ["elbow_drift", "incomplete_contraction", "momentum_cheat"],
        "recommendations": {
            "elbow_drift": {
                "Low": "Focus on keeping your elbows stationary to improve bicep engagement.",
                "Moderate": "Ensure your elbows stay close to your sides throughout the movement.",
                "High": "Use a mirror or video feedback to monitor and correct elbow drift."
            },
            "incomplete_contraction": {
                "Low": "Work on fully contracting your biceps at the top of the curl.",
                "Moderate": "Focus on completing the full range of motion for better results.",
                "High": "Slow down your movements and emphasize squeezing at the top to achieve full contractions."
            },
            "momentum_cheat": {
                "Low": "Avoid using momentum by performing slower, controlled movements.",
                "Moderate": "Reduce the weight slightly and focus on controlled lifting and lowering phases.",
                "High": "Prioritize control over speed. Practice with lighter weights to perfect your form."
            }
        }
    }
}

system_configuration = {
    "target_fps": 30,
    "frame_width": 1280,
    "frame_height": 720,
    "resize_width": 405,
    "resize_height": 720,
    "audio_temp_files_path": "utils/audio_temp_files",
    "mediapipe_keypoints": {'nose': 0,
                            'left_eye_inner': 1,
                            'left_eye': 2,
                            'left_eye_outer': 3,
                            'right_eye_inner': 4,
                            'right_eye': 5,
                            'right_eye_outer': 6,
                            'left_ear': 7,
                            'right_ear': 8,
                            'mouth_left': 9,
                            'mouth_right': 10,
                            'left_shoulder': 11,
                            'right_shoulder': 12,
                            'left_elbow': 13,
                            'right_elbow': 14,
                            'left_wrist': 15,
                            'right_wrist': 16,
                            'left_pinky': 17,
                            'right_pinky': 18,
                            'left_index': 19,
                            'right_index': 20,
                            'left_thumb': 21,
                            'right_thumb': 22,
                            'left_hip': 23,
                            'right_hip': 24,
                            'left_knee': 25,
                            'right_knee': 26,
                            'left_ankle': 27,
                            'right_ankle': 28,
                            'left_heel': 29,
                            'right_heel': 30,
                            'left_foot_index': 31,
                            'right_foot_index': 32},
    "bounding_box": {
        "position": (0, 80),  # (x, y)
        "size": (405, 640),
    },
    "body_keypoints":
        [
            'nose',
            'left_eye_inner',
            'left_eye',
            'left_eye_outer',
            'right_eye_inner',
            'right_eye',
            'right_eye_outer',
            'left_ear',
            'right_ear',
            'mouth_left',
            'mouth_right',
            'left_shoulder',
            'right_shoulder',
            'left_hip',
            'right_hip',
            'left_knee',
            'right_knee',
            'left_ankle',
            'right_ankle',
            'left_heel',
            'right_heel',
            'left_foot_index',
            'right_foot_index'
        ]
    ,
    "buttons": {"start_button": {
        "label": "Start",
        "position": (0, 0),  # (x, y)
        "size": (405, 50),  # (width, height)
        "state": "idle",
        "next_state": "ready"
    },
        "pause_button": {
            "label": "Pause",
            "position": (0, 0),  # (x, y)
            "size": (405, 50),  # (width, height)
            "state": "start",
            "next_state": "pause"
        },
        "resume_button": {
            "label": "Resume",
            "position": (0, 0),  # (x, y)
            "size": (202, 50),  # (width, height)
            "state": "pause",
            "next_state": "ready"
        },
        "end_button": {
            "label": "End",
            "position": (203, 0),  # (x, y)
            "size": (202, 50),  # (width, height)
            "state": "pause",
            "next_state": "idle"
        }
    }

}
