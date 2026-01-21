import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from .paths import asset_path


# MediaPipe label -> your action
LABEL_TO_ACTION = {
    "Victory": "LEFT",
    "ILoveYou": "RIGHT",
    "Pointing_Up": "JUMP",
    "Closed_Fist": "DUCK",
    "Thumb_Up": "SPACE",   # ✅ NEW
}


class GestureRecognizerMP:
    def __init__(
        self,
        model_path=asset_path("gesture_recognizer.task"),
        min_score=0.60,
        max_hands=1,
        mirror_view=True,
    ):
        self.min_score = min_score
        self.mirror_view = mirror_view
        self.last_result = None
        self.last_timestamp_ms = 0

        base_options = python.BaseOptions(model_asset_path=model_path)

        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=max_hands,
            result_callback=self._on_result,
        )

        self.recognizer = vision.GestureRecognizer.create_from_options(options)

    def _on_result(self, result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        self.last_result = result
        self.last_timestamp_ms = timestamp_ms

    def process(self, frame_bgr):
        """
        Input: BGR frame
        Output:
          - display_frame (mirrored if mirror_view=True)
          - action ("LEFT", "RIGHT", "JUMP", "DUCK", "SPACE", "IDLE")
          - raw_label (e.g. "Victory")
          - score (float)
          - hand_landmarks (for drawing) or None
        """
        if self.mirror_view:
            frame_bgr = cv2.flip(frame_bgr, 1)

        # Send to MediaPipe
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1

        self.recognizer.recognize_async(mp_image, timestamp_ms)

        label, score = self._top_label()
        action = self._label_to_action(label, score)
        landmarks = self._get_hand_landmarks()

        return frame_bgr, action, label, score, landmarks

    def _top_label(self):
        if self.last_result is None or not self.last_result.gestures:
            return None, 0.0

        best_label = None
        best_score = 0.0

        for hand_gestures in self.last_result.gestures:
            if not hand_gestures:
                continue
            top = hand_gestures[0]
            lbl = top.category_name
            scr = float(top.score)
            if scr > best_score:
                best_score = scr
                best_label = lbl

        return best_label, best_score

    def _label_to_action(self, label, score):
        if not label or score < self.min_score:
            return "IDLE"
        return LABEL_TO_ACTION.get(label, "IDLE")

    def _get_hand_landmarks(self):
        if self.last_result is None:
            return None
        if not hasattr(self.last_result, "hand_landmarks"):
            return None
        if not self.last_result.hand_landmarks:
            return None
        return self.last_result.hand_landmarks[0]
