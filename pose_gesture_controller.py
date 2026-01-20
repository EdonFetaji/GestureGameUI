"""
Pose-Based Gesture Recognition - MUCH MORE STABLE
Uses static hand poses instead of motion tracking

Gestures:
- FIST (all fingers closed) = DUCK
- ONE FINGER (index up) = JUMP
- OPEN PALM (all fingers up) = IDLE
- Hand on LEFT side of screen = LEFT
- Hand on RIGHT side of screen = RIGHT
"""

import time
import cv2
import mediapipe as mp
import numpy as np


class PoseGestureController:
    def __init__(
        self,
        cooldown_s: float = 0.4,
        mirror_view: bool = True,
        debug: bool = False,
    ):
        self.cooldown_s = cooldown_s
        self.mirror_view = mirror_view
        self.debug = debug

        print("=" * 60)
        print("Initializing POSE-BASED GestureController...")
        print("=" * 60)
        print("Gestures:")
        print("  FIST (closed hand)     → DUCK")
        print("  INDEX FINGER UP        → JUMP")
        print("  OPEN PALM              → IDLE")
        print("  Hand on LEFT side      → LEFT")
        print("  Hand on RIGHT side     → RIGHT")
        print("=" * 60)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.last_trigger_time = 0.0
        self.last_gesture = "IDLE"
        self.frames_without_hand = 0

        print("✓ POSE GestureController ready!\n")

    def _is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id):
        """Check if a finger is extended by comparing tip to PIP joint"""
        tip = landmarks.landmark[finger_tip_id]
        pip = landmarks.landmark[finger_pip_id]

        # Finger is extended if tip is above (lower y value) PIP
        # Add small threshold to avoid jitter
        return tip.y < (pip.y - 0.02)

    def _is_thumb_extended(self, landmarks):
        """Special check for thumb (uses different geometry)"""
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        thumb_mcp = landmarks.landmark[2]

        # Thumb extended if tip is farther from wrist than IP joint
        wrist = landmarks.landmark[0]

        tip_dist = abs(thumb_tip.x - wrist.x)
        ip_dist = abs(thumb_ip.x - wrist.x)

        return tip_dist > (ip_dist + 0.03)

    def _count_extended_fingers(self, landmarks):
        """Count how many fingers are extended"""
        fingers = {
            'thumb': self._is_thumb_extended(landmarks),
            'index': self._is_finger_extended(landmarks, 8, 6),
            'middle': self._is_finger_extended(landmarks, 12, 10),
            'ring': self._is_finger_extended(landmarks, 16, 14),
            'pinky': self._is_finger_extended(landmarks, 20, 18),
        }

        if self.debug:
            extended = [name for name, ext in fingers.items() if ext]
            print(f"    [DEBUG] Extended fingers: {extended}")

        return fingers, sum(fingers.values())

    def _get_hand_position(self, landmarks):
        """Get hand position (left/center/right) based on wrist location"""
        wrist = landmarks.landmark[0]
        x = wrist.x

        if self.debug:
            print(f"    [DEBUG] Hand X position: {x:.3f}")

        # Divide screen into 3 zones - WIDER zones for better detection
        if x < 0.40:  # LEFT zone is now 0-40%
            return "LEFT_ZONE"
        elif x > 0.60:  # RIGHT zone is now 60-100%
            return "RIGHT_ZONE"
        else:
            return "CENTER_ZONE"

    def _classify_pose(self, landmarks):
        """Classify the hand pose into a gesture"""
        fingers, count = self._count_extended_fingers(landmarks)
        position = self._get_hand_position(landmarks)

        if self.debug:
            print(f"    [DEBUG] Finger count: {count}, Position: {position}")

        # Priority 1: FIST (DUCK) - Most distinctive
        if count == 0:
            if self.debug:
                print(f"    [DEBUG] → FIST detected = DUCK")
            return "DUCK"

        # Priority 2: INDEX ONLY (JUMP)
        if count == 1 and fingers['index']:
            if self.debug:
                print(f"    [DEBUG] → INDEX FINGER UP = JUMP")
            return "JUMP"

        # Priority 3: Position-based (LEFT/RIGHT)
        # Only trigger if hand is in a neutral pose (2-5 fingers)
        if 2 <= count <= 5:
            if position == "LEFT_ZONE":
                if self.debug:
                    print(f"    [DEBUG] → Hand in LEFT zone = LEFT")
                return "LEFT"
            elif position == "RIGHT_ZONE":
                if self.debug:
                    print(f"    [DEBUG] → Hand in RIGHT zone = RIGHT")
                return "RIGHT"

        # Default: IDLE (open palm or unclear pose)
        if self.debug:
            print(f"    [DEBUG] → IDLE (open palm or unclear)")
        return "IDLE"

    def _cooldown_ok(self):
        return (time.time() - self.last_trigger_time) >= self.cooldown_s

    def process_frame(self, frame: np.ndarray):
        """
        Process frame and return detected gesture
        Returns: (gesture, landmarks)
        """
        if self.mirror_view:
            frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if not results.multi_hand_landmarks:
            self.frames_without_hand += 1

            if self.frames_without_hand == 30:
                print("  ⚠ No hand detected - show your hand to the camera")

            return "IDLE", None

        # Hand detected
        if self.frames_without_hand >= 30:
            print("  ✓ Hand detected")
        self.frames_without_hand = 0

        landmarks = results.multi_hand_landmarks[0]

        # Classify the current pose
        gesture = self._classify_pose(landmarks)

        # Only trigger if gesture changed and cooldown passed
        if gesture != "IDLE" and gesture != self.last_gesture:
            if self._cooldown_ok():
                self.last_gesture = gesture
                self.last_trigger_time = time.time()
                print(f"  ✓✓✓ {gesture} DETECTED ✓✓✓")
                return gesture, landmarks

        # Update last gesture even if not triggering
        if gesture == "IDLE":
            self.last_gesture = "IDLE"

        return "IDLE", landmarks

    def draw_hand_skeleton(self, frame, landmarks):
        """Draw hand landmarks for visual feedback"""
        if landmarks is None:
            return frame

        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )

        return frame