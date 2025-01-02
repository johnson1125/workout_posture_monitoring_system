import cv2


def draw_hover_progress(frame, button, elapsed_time, required_time=3):
    x, y = button["position"]
    w, h = button["size"]
    progress_width = int((elapsed_time / required_time) * w)
    cv2.rectangle(frame, (x, y + h + 10), (x + progress_width, y + h + 15), (0, 255, 0), -1)
    return frame

def draw_progress(frame,system_config, elapsed_time, required_time=3):
    x, y = (0,0)
    w, h = (system_config["resize_width"],system_config["resize_height"])
    progress_width = int((elapsed_time / required_time) * w)
    cv2.rectangle(frame, (x,  20), ( progress_width,  25), (0, 255, 0), -1)
    return frame

def draw_buttons(frame, buttons, hover_state=None):
    for button in buttons:
        x, y = button["position"]
        w, h = button["size"]

        # Change color if hovered
        if hover_state == button["state"]:
            color = (0, 255, 0)  # Green
        else:
            color = (255, 0, 0)  # Blue

        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        text_size = cv2.getTextSize(button["label"], cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_width, text_height = text_size[0]

        text_x = x + (w - text_width) // 2
        text_y = y + (h + text_height) // 2

        # Put label
        cv2.putText(frame, button["label"], (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return frame



def draw_bounding_box(frame, bounding_box, status):
    """
    Draws a bounding box on a frame and changes the box color based on the status.

    Args:
        frame (numpy.ndarray): The video frame or image to draw on.
        bounding_box (dict): A dictionary containing the bounding box parameters:
            - x: X-coordinate of the top-left corner.
            - y: Y-coordinate of the top-left corner.
            - width: Width of the bounding box.
            - height: Height of the bounding box.
        status (bool): Status indicating whether the box should be green (True) or red (False).

    Returns:
        numpy.ndarray: The frame with the bounding box drawn.
    """
    # Extract bounding box parameters
    x,y = bounding_box['position']
    width,height = bounding_box['size']

    # Set box color based on status
    color = (0, 255, 0) if status else (0, 0, 255)  # Green if True, Red if False

    # Draw the rectangle
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)

    return frame
