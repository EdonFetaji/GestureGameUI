# gesture_recognizer.py - HIGHLY IMPROVED VERSION
# Fixed: hand stability, multiple triggers, better detection

import time
from collections import deque
from typing import Deque, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


class GestureController:
    def __init__(
            self,
            buffer_size: int = 12,
            ema_alpha: float = 0.3,
            dx_thresh: float = 0.12,
            dy_thresh: float = 0.12,
            vmin: float = 0.08,
            deadzone: float = 0.015,
            cooldown_s: float = 0.5,
            mirror_view: bool = True,
            debug: bool = False,
    ):
        self.buffer_size = buffer_size
        self.ema_alpha = float(ema_alpha)
        self.dx_thresh = float(dx_thresh)
        self.dy_thresh = float(dy_thresh)
        self.vmin = float(vmin)
        self.deadzone = float(deadzone)
        self.cooldown_s = float(cooldown_s)
        self.mirror_view = mirror_view
        self.debug = debug

        print("Initializing STABLE GestureController...")
        print(f"  Settings optimized for accuracy and stability")
        print(f"  Cooldown: {cooldown_s}s (prevents multiple triggers)")

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.6,  # LOWER to maintain tracking
            min_tracking_confidence=0.5,  # LOWER to prevent loss
        )

        self._ema_xy: Optional[Tuple[float, float]] = None
        self.hist: Deque[Tuple[float, float, float]] = deque(maxlen=self.buffer_size)

        self.last_trigger_time = 0.0
        self.last_gesture = "IDLE"
        self.gesture_in_progress = False

        # Track hand loss
        self.frames_without_hand = 0
        self.max_frames_without_warning = 30

        print("✓ STABLE GestureController initialized\n")

    def _cooldown_ok(self) -> bool:
        return (time.time() - self.last_trigger_time) >= self.cooldown_s

    def _reset(self) -> None:
        """IMPROVED: Only clear history, keep EMA for stability"""
        self.hist.clear()
        # Don't reset EMA - keeps position stable

    def _ema_update(self, x: float, y: float) -> Tuple[float, float]:
        if self._ema_xy is None:
            self._ema_xy = (x, y)
            return x, y
        ex, ey = self._ema_xy
        a = self.ema_alpha
        ex = a * x + (1.0 - a) * ex
        ey = a * y + (1.0 - a) * ey
        self._ema_xy = (ex, ey)
        return ex, ey

    def _classify(self) -> str:
        """IMPROVED: Single clear gesture detection"""
        if len(self.hist) < 8:
            return "IDLE"

        xs = np.array([p[0] for p in self.hist], dtype=np.float32)
        ys = np.array([p[1] for p in self.hist], dtype=np.float32)

        # Calculate displacement from start to end
        x_start, y_start = xs[0], ys[0]
        x_end, y_end = xs[-1], ys[-1]

        dx = x_end - x_start
        dy = y_end - y_start

        # Total distance moved
        distance = np.sqrt(dx ** 2 + dy ** 2)

        if self.debug:
            print(f"    [DEBUG] Movement: dx={dx:.4f}, dy={dy:.4f}, dist={distance:.4f}")

        # Must move minimum distance
        if distance < self.vmin:
            if self.debug:
                print(f"    [DEBUG] Distance too small")
            return "IDLE"

        # Calculate angle of movement
        angle = np.arctan2(dy, dx) * 180 / np.pi

        if self.debug:
            print(f"    [DEBUG] Angle: {angle:.1f}°")

        # Determine direction based on angle
        # RIGHT: -45 to 45 degrees
        if -45 <= angle <= 45 and abs(dx) >= self.dx_thresh:
            if self.debug:
                print(f"    [DEBUG] → RIGHT detected!")
            return "RIGHT"

        # LEFT: 135 to 180 or -180 to -135 degrees
        if (angle >= 135 or angle <= -135) and abs(dx) >= self.dx_thresh:
            if self.debug:
                print(f"    [DEBUG] ← LEFT detected!")
            return "LEFT"

        # JUMP (UP): -135 to -45 degrees
        if -135 <= angle <= -45 and abs(dy) >= self.dy_thresh:
            if self.debug:
                print(f"    [DEBUG] ↑ JUMP detected!")
            return "JUMP"

        # DUCK (DOWN): 45 to 135 degrees
        if 45 <= angle <= 135 and abs(dy) >= self.dy_thresh:
            if self.debug:
                print(f"    [DEBUG] ↓ DUCK detected!")
            return "DUCK"

        return "IDLE"

    def process_frame(self, frame: np.ndarray):
        """
        IMPROVED: Better hand tracking and single gesture per motion
        """
        if self.mirror_view:
            frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if not results.multi_hand_landmarks:
            self.frames_without_hand += 1

            # Only warn occasionally
            if self.frames_without_hand == self.max_frames_without_warning:
                print("  ⚠ Hand tracking lost - hold hand steady in frame")

            self._reset()
            self.gesture_in_progress = False
            return "IDLE", None

        # Hand detected - reset counter
        if self.frames_without_hand >= self.max_frames_without_warning:
            print("  ✓ Hand tracking recovered")
        self.frames_without_hand = 0

        landmarks = results.multi_hand_landmarks[0]
        wrist = landmarks.landmark[0]

        # EMA smooth
        x_s, y_s = self._ema_update(float(wrist.x), float(wrist.y))
        now = time.time()
        self.hist.append((x_s, y_s, now))

        gesture = self._classify()

        # CRITICAL FIX: Only trigger once per gesture
        if gesture != "IDLE":
            if self._cooldown_ok() and not self.gesture_in_progress:
                # New gesture detected!
                self.gesture_in_progress = True
                self.last_trigger_time = now
                self.last_gesture = gesture
                print(f"  ✓✓✓ {gesture} GESTURE CONFIRMED ✓✓✓")
                self._reset()
                return gesture, landmarks
        else:
            # Reset when hand stops moving
            if self.gesture_in_progress:
                self.gesture_in_progress = False
                if self.debug:
                    print("    [DEBUG] Gesture completed, ready for next")

        return "IDLE", landmarks