import numpy as np

def calculate_sequence_needed(current_fps, target_fps, sequence_length):
    # Duration of the sequence in seconds
    sequence_duration = sequence_length / target_fps

    # Number of frames needed from the real-time video
    sequence_needed = int(sequence_duration * current_fps + 0.5)  # +0.5 for rounding to nearest integer

    return sequence_needed
def interpolate_keypoints(frame1, frame2, num_interpolated_points):
    """
    Linearly interpolates between two keyframes to generate intermediate frames.

    frame1: Keypoints of the first frame (shape: (6, 3)).
    frame2: Keypoints of the second frame (shape: (6, 3)).
    num_interpolated_points: Number of intermediate frames to generate.

    Returns: A list of interpolated keyframes, each with shape (6, 3).
    """
    interpolated_frames = []

    # Convert frames to np.array for operations
    frame1 = np.array(frame1)
    frame2 = np.array(frame2)

    for i in range(num_interpolated_points):
        ratio = (i + 1) / (num_interpolated_points + 1)
        interpolated_frame = frame1 * (1 - ratio) + frame2 * ratio
        interpolated_frames.append(interpolated_frame)

    return interpolated_frames

def process_keypoints_sequence(keypoints_sequence, current_fps, target_fps, target_frame_count):
    """
    Adjusts a sequence of keypoints to match the required frame count by interpolating frames.

    keypoints_sequence: List of keypoints arrays from the real-time video.
    current_fps: Frame rate at which keypoints are captured.
    target_fps: Desired frame rate for the LSTM model.
    target_frame_count: Number of frames needed for LSTM input.

    Returns: A list of keypoints arrays interpolated to match the target_frame_count,
    with the start and end frames being the same as the original sequence.
    """

    # Calculate the interpolation factor
    interpolation_factor = target_fps / current_fps

    # Create a list to store the interpolated keypoints
    interpolated_sequence = []

    # Track the indices of original frames
    original_frame_indices = []

    # Determine how many frames to include for each interval
    num_frames_between = int(interpolation_factor)

    # Interpolate between frames
    for i in reversed(range(1,len(keypoints_sequence))):
        # Append the original frame and store its index
        interpolated_sequence.insert(0,keypoints_sequence[i])
        original_frame_indices.append(len(interpolated_sequence) - 1)

        if i > 0 :
            num_interpolated_points = max(1,num_frames_between - 1)
            interpolated_frames = interpolate_keypoints(
                keypoints_sequence[i - 1], keypoints_sequence[i], num_interpolated_points)
            interpolated_sequence[:0] = interpolated_frames

    # Append the last frame and store its index
    interpolated_sequence.insert(0,keypoints_sequence[0])
    original_frame_indices.append(len(interpolated_sequence) - 1)

    # If the sequence is too long, remove non-original frames with gaps
    if len(interpolated_sequence) > target_frame_count:
        excess_frames = len(interpolated_sequence) - target_frame_count
        interpolated_sequence.reverse()
        # Create a list of non-original frame indices
        non_original_indices = [i for i in range(len(interpolated_sequence)) if i not in original_frame_indices]

        # # Remove non-original frames gradually with gaps
        frames_to_remove=[]
        # Repeat until the required number of frames to remove is reached
        while len(frames_to_remove) != excess_frames:
            # Select frames to remove using the current step
            step = max(2, len(non_original_indices) // (excess_frames - len(frames_to_remove)))
            additional_frames = sorted(non_original_indices[::step], reverse=True)[
                                :(excess_frames - len(frames_to_remove))]

            # Add selected frames to the list of frames to remove
            frames_to_remove.extend(additional_frames)

            # Remove selected frames from the list of non-original indices
            non_original_indices = [i for i in non_original_indices if i not in frames_to_remove]

        frames_to_remove = sorted(frames_to_remove,reverse=True)
        for i in frames_to_remove:
            del interpolated_sequence[i]

        interpolated_sequence.reverse()

    # If the sequence is too short, pad with interpolated frames
    elif len(interpolated_sequence) < target_frame_count:
        additional_frames_needed = target_frame_count - len(interpolated_sequence)

        step = max(2, len(interpolated_sequence) // additional_frames_needed)

        # Start from the last frame and move backward
        i = 0  # Start from the last frame
        while additional_frames_needed > 0:
            # Interpolate between the current frame and the previous frame
            if i < len(interpolated_sequence)-1 :  # Ensure there's a previous frame
                interpolated_frames = interpolate_keypoints(
                    interpolated_sequence[i], interpolated_sequence[i+1], 1)

                # Insert the interpolated frame before the current frame
                interpolated_sequence.insert(i, interpolated_frames[0])
                additional_frames_needed -= 1

            # Move the index backward by the step size
            i += step

            # Wrap around if we run out of indices to insert frames
            if i>=len(interpolated_sequence):
                i=0

    return interpolated_sequence
