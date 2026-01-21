import time
import cv2

from PySide6.QtCore import QThread, Signal
from .recognizer_factory import RecognizerFactory, RecognizerType


class UIGestureWorker(QThread):
    """
    Gesture worker dedicated to UI navigation.
    Uses its own separate MediaPipe recognizer instance (not the singleton)
    so UI gestures always work regardless of game recognizer settings.
    """
    action_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

        # Create a DEDICATED recognizer for UI navigation only
        # This is separate from the singleton used for games
        self.recognizer = RecognizerFactory.create(RecognizerType.MEDIAPIPE_TASKS)

        self.last_action = "IDLE"
        self.cooldown_s = 0.55
        self.last_emit_time = 0.0

    def stop(self):
        self.running = False

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not cap.isOpened():
            return

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue

                result = self.recognizer.process(frame)
                action = result.action

                # Emit only on IDLE -> ACTION (edge trigger)
                now = time.time()
                if action != "IDLE" and self.last_action == "IDLE":
                    if (now - self.last_emit_time) >= self.cooldown_s:
                        self.action_signal.emit(action)
                        self.last_emit_time = now

                self.last_action = action
                time.sleep(0.005)

        finally:
            cap.release()
            # Clean up the dedicated recognizer
            if self.recognizer:
                self.recognizer.cleanup()