import time

class Timer:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False

    def start(self):
        if not self.is_running:  # Start only if not already running
            self.start_time = time.time()
            self.is_running = True

    def pause(self):
        if self.is_running:  # Pause only if currently running
            self.elapsed_time += time.time() - self.start_time
            self.is_running = False

    def reset(self):
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False

    def get_time(self):
        if self.is_running:
            return self.elapsed_time + (time.time() - self.start_time)
        return self.elapsed_time

    def format_time(self,seconds):
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02}:{seconds:02}"

