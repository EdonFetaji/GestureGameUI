"""
Pose-Based Gesture Recognizer Implementation.

Uses MediaPipe Hands solution with custom pose classification.
Detects gestures based on finger positions and movement tracking.

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
from typing import Any, Optional

from .gesture_interface import GestureRecognizerInterface, GestureResult


class HybridGestureRecognizer(GestureRecognizerInterface):
    """
    Gesture recognizer using pose-based detection.
    
    Uses MediaPipe Hands to track finger positions and classify
    gestures based on which fingers are extended and their movement.
    More stable for motion-based gestures like swiping left/right.
    """
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        movement_threshold: float = 0.05,
        mirror_view: bool = True,
        debug: bool = False,
    ):
        """
        Initialize the pose-based recognizer.
        
        Args:
            min_detection_confidence: MediaPipe hand detection confidence
            min_tracking_confidence: MediaPipe hand tracking confidence
            movement_threshold: Minimum movement delta to trigger LEFT/RIGHT
            mirror_view: Whether to flip the frame horizontally
            debug: Print debug information
        """
        self.mirror_view = mirror_view
        self.debug = debug
        self.movement_threshold = movement_threshold
        
        # Initialize MediaPipe Hands
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        
        # Movement tracking state
        self._prev_index_x: Optional[float] = None
        self._prev_index_y: Optional[float] = None
        self._frames_without_hand = 0
        
        print("[PoseBasedRecognizer] Initialized")
        print("[PoseBasedRecognizer] Gestures:")
        print("  FIST (closed hand)     → DUCK")
        print("  INDEX FINGER UP        → JUMP")
        print("  THUMB UP ONLY          → SPACE")
        print("  Index finger LEFT      → LEFT")
        print("  Index finger RIGHT     → RIGHT")
        print("  OPEN PALM              → IDLE")

    @property
    def name(self) -> str:
        return "Pose-Based (MediaPipe Hands)"
    
    @property
    def keyMap(self) -> dict[str,str]:
        return {
            "FIST": "DUCK",
            "ONE FINGER": "JUMP",
            "THUMB UP": "SPACE",
            "INDEX LEFT": "LEFT",
            "INDEX RIGHT": "RIGHT",
            "OPEN PALM": "IDLE",
        }

    def process(self, frame_bgr: np.ndarray) -> GestureResult:
        """
        Process a BGR frame and return gesture result.
        """
        if self.mirror_view:
            frame_bgr = cv2.flip(frame_bgr, 1)

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        # No hand detected
        if not results.multi_hand_landmarks:
            self._frames_without_hand += 1
            
            if self._frames_without_hand == 30 and self.debug:
                print("  ⚠ No hand detected - show your hand to the camera")
            
            # Reset tracking
            self._prev_index_x = None
            self._prev_index_y = None
            
            return GestureResult(
                frame=frame_bgr,
                action="IDLE",
                raw_label=None,
                confidence=0.0,
                landmarks=None,
            )

        # Hand detected
        if self._frames_without_hand >= 30 and self.debug:
            print("  ✓ Hand detected")
        self._frames_without_hand = 0

        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Classify pose
        gesture, confidence = self._classify_pose(hand_landmarks)
        
        return GestureResult(
            frame=frame_bgr,
            action=gesture,
            raw_label=gesture,  # Same as action for pose-based
            confidence=confidence,
            landmarks=hand_landmarks.landmark,  # Return list of landmarks, not NormalizedLandmarkList
        )

    def _is_finger_extended(self, landmarks, tip_id: int, pip_id: int) -> bool:
        """Check if a finger is extended by comparing tip to PIP joint."""
        tip = landmarks.landmark[tip_id]
        pip = landmarks.landmark[pip_id]
        # Finger extended if tip is above (lower y) PIP with threshold
        return tip.y < (pip.y - 0.02)

    def _is_thumb_extended(self, landmarks) -> bool:
        """Special check for thumb using different geometry."""
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        wrist = landmarks.landmark[0]
        
        tip_dist = abs(thumb_tip.x - wrist.x)
        ip_dist = abs(thumb_ip.x - wrist.x)
        
        return tip_dist > (ip_dist + 0.03)

    def _count_extended_fingers(self, landmarks) -> tuple[dict, int]:
        """Count how many fingers are extended."""
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

    def _detect_index_movement(self, landmarks) -> str:
        """Detect LEFT/RIGHT movement based on index finger tip movement."""
        index_tip = landmarks.landmark[8]
        
        # Initialize on first frame
        if self._prev_index_x is None or self._prev_index_y is None:
            self._prev_index_x = index_tip.x
            self._prev_index_y = index_tip.y
            return "NEUTRAL"
        
        # Calculate movement delta
        delta_x = index_tip.x - self._prev_index_x
        delta_y = index_tip.y - self._prev_index_y
        
        # Update previous position
        self._prev_index_x = index_tip.x
        self._prev_index_y = index_tip.y
        
        if self.debug:
            print(f"    [DEBUG] Index delta_x: {delta_x:.3f}, delta_y: {delta_y:.3f}")
        
        # Check if movement is significant
        if abs(delta_x) > self.movement_threshold or abs(delta_y) > self.movement_threshold:
            if abs(delta_x) > abs(delta_y):
                # Account for mirroring - swapped for correct user perspective
                if delta_x < -self.movement_threshold:
                    return "LEFT"
                elif delta_x > self.movement_threshold:
                    return "RIGHT"
        
        return "NEUTRAL"

    def _classify_pose(self, landmarks) -> tuple[str, float]:
        """Classify the hand pose into a gesture with confidence."""
        fingers, count = self._count_extended_fingers(landmarks)
        index_movement = self._detect_index_movement(landmarks)
        
        if self.debug:
            print(f"    [DEBUG] Finger count: {count}, Movement: {index_movement}")
        
        # Priority 1: FIST = DUCK
        if count == 0:
            if self.debug:
                print("    [DEBUG] → FIST detected = DUCK")
            return "DUCK", 0.9
        
        # Priority 2: THUMB ONLY = SPACE
        if count == 1 and fingers['thumb']:
            if self.debug:
                print("    [DEBUG] → THUMB UP = SPACE")
            return "SPACE", 0.85
        
        # Priority 3: INDEX ONLY = JUMP
        if count == 1 and fingers['index']:
            if self.debug:
                print("    [DEBUG] → INDEX FINGER UP = JUMP")
            return "JUMP", 0.85
        
        # Priority 4: INDEX MOVEMENT (2+ fingers)
        if count >= 2:
            if index_movement == "LEFT":
                if self.debug:
                    print("    [DEBUG] → Moving LEFT")
                return "LEFT", 0.8
            elif index_movement == "RIGHT":
                if self.debug:
                    print("    [DEBUG] → Moving RIGHT")
                return "RIGHT", 0.8
        
        # Default: IDLE
        return "IDLE", 0.5

    def draw_landmarks(self, frame: np.ndarray, landmarks: Any) -> np.ndarray:
        """Draw hand skeleton on frame."""
        if landmarks is None:
            return frame
            
        h, w, _ = frame.shape
        
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
        
        # Extract points (flip x for mirror view)
        points = []
        for lm in landmarks.landmark:
            x = int(w - (lm.x * w))  # Mirror x-coordinate
            y = int(lm.y * h)
            points.append((x, y))
        
        # Draw connections
        for start_idx, end_idx in connections:
            cv2.line(frame, points[start_idx], points[end_idx], (0, 255, 0), 2)
        
        # Draw landmarks
        for i, point in enumerate(points):
            color = (0, 255, 255) if i == 8 else (255, 0, 255)
            radius = 8 if i == 8 else 4
            cv2.circle(frame, point, radius, color, -1)
        
        return frame

    def cleanup(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, '_hands'):
            self._hands.close()
