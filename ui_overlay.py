import cv2


class UIOverlay:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.enabled = False
        self.game_profile = "Subway Surfers"
        self.sensitivity_h = 0.15
        self.sensitivity_v = 0.30

    def _draw_slider(self, img, label, value, x, y):
        """
        Draws a simple slider bar in [0..1] range.
        value: float in [0, 1]
        """
        value = max(0.0, min(1.0, float(value)))

        bar_w = 220
        bar_h = 16

        # Label
        cv2.putText(
            img,
            f"{label}: {value:.2f}",
            (x, y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

        # Background bar
        cv2.rectangle(img, (x, y), (x + bar_w, y + bar_h), (70, 70, 70), -1)

        # Filled bar
        fill_w = int(bar_w * value)
        cv2.rectangle(img, (x, y), (x + fill_w, y + bar_h), (0, 200, 0), -1)

        # Border
        cv2.rectangle(img, (x, y), (x + bar_w, y + bar_h), (180, 180, 180), 1)

        # Knob
        knob_x = x + fill_w
        cv2.circle(img, (knob_x, y + bar_h // 2), 8, (230, 230, 230), -1)
        cv2.circle(img, (knob_x, y + bar_h // 2), 8, (60, 60, 60), 1)

    def render(self, frame, gesture, fps, latency_ms):
        overlay = frame.copy()

        # Status panel (top-left)
        cv2.rectangle(overlay, (10, 10), (300, 180), (40, 40, 40), -1)
        cv2.putText(overlay, f"Gesture: {gesture}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(overlay, f"Profile: {self.game_profile}", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(overlay, f"Control: {'ON' if self.enabled else 'OFF'}",
                    (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0) if self.enabled else (100, 100, 100), 1)
        cv2.putText(overlay, f"FPS: {fps:.1f} | Latency: {latency_ms:.0f}ms",
                    (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Sensitivity indicators
        self._draw_slider(overlay, "H-Sens", self.sensitivity_h, 320, 30)
        self._draw_slider(overlay, "V-Sens", self.sensitivity_v, 320, 80)

        return overlay
