import tensorflow as tf
import numpy as np
import streamlit as st
import mediapipe as mp
import pyttsx3
@st.cache_resource
def load_mp_model():
    return mp.solutions.pose

def load_pyttsx3_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    return engine

def load_all_models(workout_configurations):
    models = {}
    for workout, config in workout_configurations.items():
        models[workout] = load_tflite_model(config["model_path"])
    return models
@st.cache_resource
def load_tflite_model(model_path):
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    return interpreter, input_details, output_details

def predict_posture(sequence, interpreter, input_details, output_details, sequence_length):
    if len(sequence) == sequence_length:
        sequence_array = np.array(sequence).reshape(1, sequence_length, -1).astype(np.float32)
        interpreter.set_tensor(input_details[0]['index'], sequence_array)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        posture_class = np.argmax(output_data)
        confidence = np.max(output_data)
        return posture_class, confidence
    return None, None
