import time


class PerformanceTracker:
    def __init__(self):
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0.0

    def record_frame(self):
        self.frame_count += 1
        now = time.time()
        if now - self.last_time >= 1.0:
            self.fps = self.frame_count / (now - self.last_time)
            self.last_time = now
            self.frame_count = 0

    def get_fps(self):
        return self.fps

    def latency_ms(self, start_time):
        return (time.time() - start_time) * 1000
