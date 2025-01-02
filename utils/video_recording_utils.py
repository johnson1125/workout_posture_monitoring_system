import threading
import cv2
import time
import os
from datetime import datetime
from queue import Queue, Empty
import atexit


class VideoRecorder:
    def __init__(self, resize_size, frame_rate, output_dir):
        self.resize_size = resize_size
        self.frame_rate = frame_rate
        self.output_dir = output_dir
        self.recordings = {}  # Store threads and queues for concurrent recordings
        self.lock = threading.Lock()

        # Register cleanup on script exit
        atexit.register(self.stop_all_recordings)

    def start_recording(self, exercise_id, set_num, rep=None):
        """
        Start a new recording in a separate thread.
        :param recording_id: Unique identifier for the recording session.
        :param exercise_id: Exercise ID for the video.
        :param set_num: Set number.
        :param rep: Optional rep number.
        """
        # Create file name and path
        if rep is not None:

            filename = f"{exercise_id}_set_{set_num}_rep_{rep}.mp4"
            recording_id = f"{exercise_id}_set_{set_num}_rep_{rep}"
        else:
            filename = f"{exercise_id}_set_{set_num}.mp4"
            recording_id = f"{exercise_id}_set_{set_num}"

        with self.lock:
            if recording_id in self.recordings:
                print(f"Recording {recording_id} already exists.")
                return


            filepath = os.path.join(self.output_dir, filename)

            # Initialize VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            out = cv2.VideoWriter(filepath, fourcc, self.frame_rate, self.resize_size)

            # Create a frame queue for this recording
            frame_queue = Queue(maxsize=100)

            # Start a new thread for recording
            thread = threading.Thread(target=self._record, args=(out, frame_queue))
            thread.start()

            # Store the thread and queue
            self.recordings[recording_id] = {"thread": thread, "queue": frame_queue}

    def stop_all_recordings(self):
        """
        Stop and discard all active recordings.
        """
        with self.lock:
            for recording_id in list(self.recordings.keys()):
                print(f"Stopping recording: {recording_id}")
                self.recordings[recording_id]["queue"].put(None)  # Sentinel to stop the thread
                thread = self.recordings[recording_id]["thread"]
                thread.join()  # Wait for each thread to finish

            self.recordings.clear()
            print("All recordings have been stopped.")
    def stop_recording(self, exercise_id, set_num, rep=None):
        """
        Stop the recording for a specific recording ID.
        :param recording_id: The ID of the recording session to stop.
        """

        if rep is not None:
            recording_id = f"{exercise_id}_set_{set_num}_rep_{rep}"
        else:
            recording_id = f"{exercise_id}_set_{set_num}"
        with self.lock:
            if recording_id not in self.recordings:
                print(f"No active recording found for {recording_id}.")
                return

            # Signal the thread to stop
            self.recordings[recording_id]["queue"].put(None)  # Sentinel to stop the thread
            thread = self.recordings[recording_id]["thread"]
            thread.join()  # Wait for the thread to finish

            # Clean up
            del self.recordings[recording_id]
            print(f"Recording {recording_id} stopped.")

    def enqueue_frame(self, frame,exercise_id, set_num, rep=None ):
        """
        Add a frame to the recording's queue.
        :param recording_id: The ID of the recording session.
        :param frame: The frame to record.
        """
        if rep is not None:
            recording_id = f"{exercise_id}_set_{set_num}_rep_{rep}"
        else:
            recording_id = f"{exercise_id}_set_{set_num}"

        with self.lock:
            if recording_id not in self.recordings:
                print(f"No active recording found for {recording_id}.")
                return
            try:
                self.recordings[recording_id]["queue"].put_nowait(frame)
            except:
                print(f"Frame queue for {recording_id} is full. Dropping frame.")

    def _record(self, out, frame_queue):
        """
        Background recording thread.
        :param out: The VideoWriter object.
        :param frame_queue: The Queue for frames.
        """
        while True:
            try:
                frame = frame_queue.get(timeout=1)
                if frame is None:  # Sentinel value to stop the thread
                    break
                out.write(frame)
            except Empty:
                continue
        out.release()  # Release the VideoWriter when done