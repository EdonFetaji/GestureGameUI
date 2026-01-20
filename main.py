"""
Calibration Tool - Adjust gesture sensitivity in real-time
Press keys to adjust settings and find what works best for you!

Controls:
  H/h - Increase/Decrease horizontal sensitivity
  V/v - Increase/Decrease vertical sensitivity
  S/s - Increase/Decrease speed threshold
  C/c - Increase/Decrease cooldown
  R   - Reset to defaults
  D   - Toggle debug mode
  Q   - Quit
"""

import cv2
import time
from gesture_recognizer import GestureController
from ui_overlay import UIOverlay
from performance_tracker import PerformanceTracker


def main():
    print("=" * 60)
    print("CALIBRATION TOOL - Find Your Perfect Settings")
    print("=" * 60)
    print(__doc__)
    print("=" * 60)

    # Start with improved defaults
    recognizer = GestureController(
        buffer_size=15,
        ema_alpha=0.25,
        dx_thresh=0.10,
        dy_thresh=0.10,
        vmin=0.025,
        deadzone=0.012,
        cooldown_s=0.35,
        debug=True  # Debug ON by default
    )

    ui = UIOverlay()
    perf = PerformanceTracker()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("\n✓ Starting calibration mode...")
    print("Try making gestures and adjust settings until they feel right!\n")

    gesture_counts = {"LEFT": 0, "RIGHT": 0, "JUMP": 0, "DUCK": 0}

    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        gesture, landmarks = recognizer.process_frame(frame)
        latency = perf.get_latency_ms(start_time)

        # Count gestures
        if gesture != "IDLE":
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

        # Enhanced display with settings
        display = ui.render(frame, gesture, perf.get_fps(), latency)

        # Draw settings on screen
        y_pos = 220
        settings_info = [
            f"H-Thresh: {recognizer.dx_thresh:.3f}  (H/h to adjust)",
            f"V-Thresh: {recognizer.dy_thresh:.3f}  (V/v to adjust)",
            f"Speed Min: {recognizer.vmin:.3f}  (S/s to adjust)",
            f"Cooldown: {recognizer.cooldown_s:.2f}s  (C/c to adjust)",
            f"Debug: {'ON' if recognizer.debug else 'OFF'}  (D to toggle)",
            "",
            f"Counts: L:{gesture_counts['LEFT']} R:{gesture_counts['RIGHT']} "
            f"U:{gesture_counts['JUMP']} D:{gesture_counts['DUCK']}"
        ]

        for text in settings_info:
            cv2.putText(display, text, (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            y_pos += 25

        cv2.imshow("Calibration Tool", display)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('H'):  # Increase horizontal
            recognizer.dx_thresh = min(0.20, recognizer.dx_thresh + 0.01)
            print(f"\n→ H-Thresh increased to {recognizer.dx_thresh:.3f}")

        elif key == ord('h'):  # Decrease horizontal
            recognizer.dx_thresh = max(0.03, recognizer.dx_thresh - 0.01)
            print(f"\n→ H-Thresh decreased to {recognizer.dx_thresh:.3f}")

        elif key == ord('V'):  # Increase vertical
            recognizer.dy_thresh = min(0.20, recognizer.dy_thresh + 0.01)
            print(f"\n→ V-Thresh increased to {recognizer.dy_thresh:.3f}")

        elif key == ord('v'):  # Decrease vertical
            recognizer.dy_thresh = max(0.03, recognizer.dy_thresh - 0.01)
            print(f"\n→ V-Thresh decreased to {recognizer.dy_thresh:.3f}")

        elif key == ord('S'):  # Increase speed
            recognizer.vmin = min(0.10, recognizer.vmin + 0.005)
            print(f"\n→ Speed min increased to {recognizer.vmin:.3f}")

        elif key == ord('s'):  # Decrease speed
            recognizer.vmin = max(0.010, recognizer.vmin - 0.005)
            print(f"\n→ Speed min decreased to {recognizer.vmin:.3f}")

        elif key == ord('C'):  # Increase cooldown
            recognizer.cooldown_s = min(1.0, recognizer.cooldown_s + 0.05)
            print(f"\n→ Cooldown increased to {recognizer.cooldown_s:.2f}s")

        elif key == ord('c'):  # Decrease cooldown
            recognizer.cooldown_s = max(0.1, recognizer.cooldown_s - 0.05)
            print(f"\n→ Cooldown decreased to {recognizer.cooldown_s:.2f}s")

        elif key == ord('D'):  # Toggle debug
            recognizer.debug = not recognizer.debug
            print(f"\n→ Debug mode: {'ON' if recognizer.debug else 'OFF'}")

        elif key == ord('R'):  # Reset to defaults
            recognizer.dx_thresh = 0.10
            recognizer.dy_thresh = 0.10
            recognizer.vmin = 0.025
            recognizer.cooldown_s = 0.35
            print("\n→ Reset to default settings")

        perf.record_frame()

    # Print final settings
    print("\n" + "=" * 60)
    print("FINAL CALIBRATED SETTINGS:")
    print("=" * 60)
    print(f"dx_thresh={recognizer.dx_thresh:.3f}")
    print(f"dy_thresh={recognizer.dy_thresh:.3f}")
    print(f"vmin={recognizer.vmin:.3f}")
    print(f"cooldown_s={recognizer.cooldown_s:.2f}")
    print("\nCopy these values into your gesture_recognizer.py __init__ method!")
    print("=" * 60)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()