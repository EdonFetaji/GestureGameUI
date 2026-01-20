"""
Pose-Based Gesture Recognition - MUCH MORE STABLE
Uses static hand poses instead of motion tracking

Gestures:
- FIST (all fingers closed) = DUCK
- ONE FINGER (index up) = JUMP
- Index finger moving LEFT = LEFT
- Index finger moving RIGHT = RIGHT
- OPEN PALM (all fingers up) = IDLE
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
        print("  Index finger LEFT      → LEFT")
        print("  Index finger RIGHT     → RIGHT")
        print("  OPEN PALM              → IDLE")
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

        # ADDED: Track previous index finger position for movement detection
        self.prev_index_x = None
        self.prev_index_y = None
        self.movement_threshold = 0.05

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

    def _detect_index_movement(self, landmarks):
        """
        COPIED FROM JUPYTER NOTEBOOK:
        Detect LEFT/RIGHT movement based on index finger tip movement
        Returns: "LEFT", "RIGHT", or "NEUTRAL"
        """
        index_tip = landmarks.landmark[8]  # Index finger tip

        # Initialize on first frame
        if self.prev_index_x is None or self.prev_index_y is None:
            self.prev_index_x = index_tip.x
            self.prev_index_y = index_tip.y
            return "NEUTRAL"

        # Calculate movement delta
        delta_x = index_tip.x - self.prev_index_x
        delta_y = index_tip.y - self.prev_index_y

        # Update previous position
        self.prev_index_x = index_tip.x
        self.prev_index_y = index_tip.y

        if self.debug:
            print(f"    [DEBUG] Index movement delta_x: {delta_x:.3f}, delta_y: {delta_y:.3f}")

        # Check if movement is significant
        if abs(delta_x) > self.movement_threshold or abs(delta_y) > self.movement_threshold:
            # Prioritize horizontal movement
            if abs(delta_x) > abs(delta_y):
                # FIXED: Swapped LEFT and RIGHT to account for mirroring
                if delta_x < -self.movement_threshold:
                    if self.debug:
                        print(f"    [DEBUG] → Index moving RIGHT")
                    return "RIGHT"  # Swapped from LEFT
                elif delta_x > self.movement_threshold:
                    if self.debug:
                        print(f"    [DEBUG] → Index moving LEFT")
                    return "LEFT"  # Swapped from RIGHT

        return "NEUTRAL"

    def _classify_pose(self, landmarks):
        """Classify the hand pose into a gesture"""
        fingers, count = self._count_extended_fingers(landmarks)
        index_movement = self._detect_index_movement(landmarks)

        if self.debug:
            print(f"    [DEBUG] Finger count: {count}, Index movement: {index_movement}")

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

        # Priority 3: INDEX MOVEMENT (LEFT/RIGHT)
        # Detect movement when 2+ fingers are extended
        if count >= 2:
            if index_movement == "LEFT":
                if self.debug:
                    print(f"    [DEBUG] → Index moving LEFT = LEFT")
                return "LEFT"
            elif index_movement == "RIGHT":
                if self.debug:
                    print(f"    [DEBUG] → Index moving RIGHT = RIGHT")
                return "RIGHT"

        # Default: IDLE
        if self.debug:
            print(f"    [DEBUG] → IDLE")
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

            # Reset index tracking when hand is lost
            self.prev_index_x = None
            self.prev_index_y = None

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
        """Draw hand skeleton with coordinates flipped to correct mirroring"""
        h, w, _ = frame.shape

        # Hand landmark connections
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm
            (5, 9), (9, 13), (13, 17)
        ]

        # Extract points with FLIPPED x-coordinates
        points = []
        for lm in landmarks.landmark:
            # FIX: Flip x-coordinate by subtracting from width
            x = int(w - (lm.x * w))  # This mirrors the x-coordinate
            y = int(lm.y * h)
            points.append((x, y))

        # Draw connections
        for connection in connections:
            start_idx, end_idx = connection
            cv2.line(frame, points[start_idx], points[end_idx],
                     (0, 255, 0), 2)

        # Draw landmarks
        for point in points:
            cv2.circle(frame, point, 4, (255, 0, 255), -1)

        # Highlight index finger tip
        cv2.circle(frame, points[8], 8, (0, 255, 255), -1)

        return frame