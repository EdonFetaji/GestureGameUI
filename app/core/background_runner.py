import time
import cv2

from PySide6.QtCore import QThread

from app.core.controller import GameController
from app.core.recognizer_factory import get_recognizer


class GestureBackgroundWorker(QThread):
    """
    Runs gesture recognition in the background WITHOUT UI.
    When a gesture is detected, presses the correct key for the selected profile.
    """

    def __init__(self, profile="Subway Surfers", parent=None):
        super().__init__(parent)
        self.profile = profile
        self.running = True

        self.controller = GameController()

        # Don't grab recognizer here - get it fresh in run()
        # This ensures we always use the current singleton instance
        self.recognizer = None

        self.last_action = "IDLE"
        self.cooldown_s = 0.25
        self.last_press_time = 0.0

    def stop(self):
        self.running = False

    def run(self):
        # Get the current singleton recognizer at run time
        self.recognizer = get_recognizer()
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not cap.isOpened():
            print("❌ BackgroundWorker: Camera could not open")
            return

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue

                result = self.recognizer.process(frame)
                action = result.action

                now = time.time()

                # ✅ Trigger ONLY on IDLE -> ACTION (edge detection)
                if action != "IDLE" and self.last_action == "IDLE":
                    if (now - self.last_press_time) >= self.cooldown_s:
                        self.controller.execute_action(action, self.profile)
                        self.last_press_time = now

                self.last_action = action
                time.sleep(0.005)

        finally:
            cap.release()