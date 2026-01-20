import time


class PerformanceTracker:
    def __init__(self, window_size=30):
        self.frame_times = []
        self.window_size = window_size

    def record_frame(self):
        self.frame_times.append(time.time())
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)

    def get_fps(self):
        if len(self.frame_times) < 2:
            return 0
        time_diff = self.frame_times[-1] - self.frame_times[0]
        return (len(self.frame_times) - 1) / time_diff if time_diff > 0 else 0

    def get_latency_ms(self, start_time):
        return (time.time() - start_time) * 1000