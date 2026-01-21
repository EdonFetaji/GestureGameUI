"""
MediaPipe Tasks API Gesture Recognizer Implementation.

Uses the pre-trained gesture_recognizer.task model for gesture detection.
Recognizes: Victory, ILoveYou, Pointing_Up, Closed_Fist, Thumb_Up, etc.
"""

import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from typing import Any, Optional

from .gesture_interface import GestureRecognizerInterface, GestureResult
from .paths import asset_path


# MediaPipe label -> game action
LABEL_TO_ACTION = {
    "Victory": "LEFT",
    "ILoveYou": "RIGHT",
    "Pointing_Up": "JUMP",
    "Closed_Fist": "DUCK",
    "Thumb_Up": "SPACE",
}


class GestureRecognizerMP(GestureRecognizerInterface):
    """
    Gesture recognizer using MediaPipe Tasks API.
    
    Uses a pre-trained .task model file for accurate gesture recognition.
    Good for recognizing specific hand poses with high confidence.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        min_score: float = 0.60,
        max_hands: int = 1,
        mirror_view: bool = True,
    ):
        """
        Initialize the MediaPipe Tasks recognizer.
        
        Args:
            model_path: Path to gesture_recognizer.task file (uses default if None)
            min_score: Minimum confidence threshold (0.0 - 1.0)
            max_hands: Maximum number of hands to detect
            mirror_view: Whether to flip the frame horizontally
        """
        if model_path is None:
            model_path = asset_path("gesture_recognizer.task")
            
        self.min_score = min_score
        self.mirror_view = mirror_view
        self._last_result = None
        self._last_timestamp_ms = 0

        base_options = python.BaseOptions(model_asset_path=model_path)

        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=max_hands,
            result_callback=self._on_result,
        )

        self._recognizer = vision.GestureRecognizer.create_from_options(options)
        
        print(f"[MediaPipeTasksRecognizer] Initialized with model: {model_path}")
        print(f"[MediaPipeTasksRecognizer] Gesture mappings: {LABEL_TO_ACTION}")

    @property
    def name(self) -> str:
        return "MediaPipe Tasks API"
    
    @property
    def keyMap(self) -> dict[str,str]:
        return LABEL_TO_ACTION
    def _on_result(
        self,
        result: vision.GestureRecognizerResult,
        output_image: mp.Image,
        timestamp_ms: int
    ):
        """Callback for async gesture recognition."""
        self._last_result = result
        self._last_timestamp_ms = timestamp_ms

    def process(self, frame_bgr: np.ndarray) -> GestureResult:
        """
        Process a BGR frame and return gesture result.
        """
        if self.mirror_view:
            frame_bgr = cv2.flip(frame_bgr, 1)

        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Generate unique timestamp
        timestamp_ms = int(time.time() * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms

        # Run async recognition
        self._recognizer.recognize_async(mp_image, timestamp_ms)

        # Get results
        label, score = self._get_top_label()
        action = self._label_to_action(label, score)
        landmarks = self._get_hand_landmarks()

        return GestureResult(
            frame=frame_bgr,
            action=action,
            raw_label=label,
            confidence=score,
            landmarks=landmarks,
        )

    def _get_top_label(self) -> tuple[Optional[str], float]:
        """Get the highest confidence gesture label."""
        if self._last_result is None or not self._last_result.gestures:
            return None, 0.0

        best_label = None
        best_score = 0.0

        for hand_gestures in self._last_result.gestures:
            if not hand_gestures:
                continue
            top = hand_gestures[0]
            if float(top.score) > best_score:
                best_score = float(top.score)
                best_label = top.category_name

        return best_label, best_score

    def _label_to_action(self, label: Optional[str], score: float) -> str:
        """Convert MediaPipe label to game action."""
        if not label or score < self.min_score:
            return "IDLE"
        return LABEL_TO_ACTION.get(label, "IDLE")

    def _get_hand_landmarks(self) -> Optional[Any]:
        """Get hand landmarks from last result."""
        if self._last_result is None:
            return None
        if not hasattr(self._last_result, "hand_landmarks"):
            return None
        if not self._last_result.hand_landmarks:
            return None
        return self._last_result.hand_landmarks[0]

    def draw_landmarks(self, frame: np.ndarray, landmarks: Any) -> np.ndarray:
        """
        Draw MediaPipe hand landmarks on frame.
        """
        if landmarks is None:
            return frame
            
        h, w, _ = frame.shape
        
        # MediaPipe hand connections
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm
            (5, 9), (9, 13), (13, 17),
        ]
        
        # Convert landmarks to pixel coordinates
        points = []
        for lm in landmarks:
            x = int(lm.x * w)
            y = int(lm.y * h)
            points.append((x, y))
        
        # Draw connections
        for start_idx, end_idx in connections:
            if start_idx < len(points) and end_idx < len(points):
                cv2.line(frame, points[start_idx], points[end_idx], (0, 255, 0), 2)
        
        # Draw landmarks
        for i, point in enumerate(points):
            color = (0, 255, 255) if i == 8 else (255, 0, 255)  # Highlight index tip
            radius = 8 if i == 8 else 4
            cv2.circle(frame, point, radius, color, -1)
        
        return frame

    def cleanup(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, '_recognizer'):
            self._recognizer.close()
