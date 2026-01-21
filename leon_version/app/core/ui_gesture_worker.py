import time
import cv2

from PySide6.QtCore import QThread, Signal
from .recognizer import GestureRecognizerMP
from .paths import asset_path


class UIGestureWorker(QThread):
    action_signal = Signal(str)

    def __init__(self, model_path=None, parent=None):
        super().__init__(parent)

        if model_path is None:
            model_path = asset_path("gesture_recognizer.task")

        self.model_path = model_path
        self.running = True

        self.recognizer = GestureRecognizerMP(
            model_path=self.model_path,
            min_score=0.65,
            max_hands=1,
            mirror_view=True,
        )

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

                _, action, raw_label, score, _ = self.recognizer.process(frame)

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