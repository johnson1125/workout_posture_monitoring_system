from cv2_enumerate_cameras import enumerate_cameras
def remove_underscores_and_capitalize(text):
    # Replace underscores with spaces
    text_with_spaces = text.replace('_', ' ')
    # Capitalize the first letter of each word
    result = text_with_spaces.title()
    return result

def extract_exercise_key(text):
    exercise, _, _ = text.split("-")

    exercise = exercise.lower()
    return exercise



def get_camera_dict():
    # Enumerate connected cameras
    camera_list = enumerate_cameras()

    # Filter cameras with index 1400 and above
    filtered_cameras = [cam for cam in camera_list if cam.index >= 1400]

    # Create a dictionary for selection
    camera_dict = {f"{cam.name}": cam.index for cam in filtered_cameras}

    return camera_dict