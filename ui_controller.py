"""
UI Controller - Handles all visual rendering for the gesture control interface
Separates drawing logic from main program flow
"""

import cv2
import numpy as np


class UIController:
    def __init__(self):
        """Initialize UI controller with default settings"""
        self.show_skeleton = True
        self.show_status_panel = True
        self.show_gesture_guide = True

    def draw_hand_skeleton(self, frame, landmarks):
        """Draw hand skeleton with corrected (non-mirrored) coordinates"""
        if not self.show_skeleton or landmarks is None:
            return frame

        h, w, _ = frame.shape

        # Hand landmark connections (MediaPipe standard)
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

        # Extract points with FLIPPED x-coordinates to correct mirroring
        points = []
        for lm in landmarks.landmark:
            # Flip x-coordinate: subtract from width to mirror
            x = int(w - (lm.x * w))
            y = int(lm.y * h)
            points.append((x, y))

        # Draw connections (green lines)
        for connection in connections:
            start_idx, end_idx = connection
            cv2.line(frame, points[start_idx], points[end_idx],
                     (0, 255, 0), 2)

        # Draw landmark points (magenta circles)
        for point in points:
            cv2.circle(frame, point, 4, (255, 0, 255), -1)

        return frame

    def draw_status_panel(self, frame, gesture, fps, latency, enabled, profile):
        """Draw the main status panel (top-left)"""
        if not self.show_status_panel:
            return frame

        h, w = frame.shape[:2]

        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 200), (40, 40, 40), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Current gesture - Large and prominent
        gesture_color = (0, 255, 0) if gesture != "IDLE" else (100, 100, 100)
        cv2.putText(frame, f"Gesture: {gesture}", (20, 50),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, gesture_color, 2)

        # Game profile
        cv2.putText(frame, f"Profile: {profile}", (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Control enabled/disabled status
        status_color = (0, 255, 0) if enabled else (100, 100, 100)
        status_text = 'ENABLED' if enabled else 'DISABLED'
        cv2.putText(frame, f"Control: {status_text}",
                    (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)

        # Performance metrics
        cv2.putText(frame, f"FPS: {fps:.1f} | Latency: {latency:.0f}ms",
                    (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Keyboard controls help
        cv2.putText(frame, "SPACE=Toggle  P=Profile  Q=Quit",
                    (20, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

        return frame

    def draw_gesture_guide(self, frame):
        """Draw gesture guide panel (bottom-left)"""
        if not self.show_gesture_guide:
            return frame

        h, w = frame.shape[:2]

        # Position at bottom-left
        guide_y = h - 160

        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, guide_y - 10), (320, h - 10), (30, 30, 30), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Guide title
        cv2.putText(frame, "GESTURE GUIDE:", (20, guide_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

        # Individual gesture instructions - UPDATED FOR NEW GESTURES
        cv2.putText(frame, "Fist = DUCK", (20, guide_y + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(frame, "Index up = JUMP", (20, guide_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(frame, "Victory sign = LEFT", (20, guide_y + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(frame, "I love you = RIGHT", (20, guide_y + 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        # Add small emoji-like indicators
        cv2.putText(frame, "V", (280, guide_y + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(frame, "Y", (280, guide_y + 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)

        return frame

    def render_complete_ui(self, frame, gesture, landmarks, fps, latency, enabled, profile):
        """
        Render the complete UI with all components
        This is the main method to call from the main loop
        """
        # Draw hand skeleton first (so it appears behind UI panels)
        frame = self.draw_hand_skeleton(frame, landmarks)

        # Draw UI panels on top
        frame = self.draw_status_panel(frame, gesture, fps, latency, enabled, profile)
        frame = self.draw_gesture_guide(frame)

        return frame

    def toggle_skeleton(self):
        """Toggle skeleton visibility"""
        self.show_skeleton = not self.show_skeleton
        return self.show_skeleton

    def toggle_status_panel(self):
        """Toggle status panel visibility"""
        self.show_status_panel = not self.show_status_panel
        return self.show_status_panel

    def toggle_gesture_guide(self):
        """Toggle gesture guide visibility"""
        self.show_gesture_guide = not self.show_gesture_guide
        return self.show_gesture_guide