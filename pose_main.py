"""
Main program using POSE-BASED gesture control
Much more stable than motion-based control!
"""

from pose_gesture_controller import PoseGestureController
from ui_overlay import UIOverlay
from controller import GameController
from performance_tracker import PerformanceTracker
from ui_controller import UIController
import cv2
import time


def main():
    print("=" * 60)
    print("POSE-BASED GESTURE GAME CONTROLLER")
    print("=" * 60)
    print("Controls:")
    print("  SPACE - Toggle control ON/OFF")
    print("  P     - Switch game profile")
    print("  Q     - Quit")
    print("=" * 60)
    print("\nGestures:")
    print("  FIST (closed hand)  → DUCK")
    print("  INDEX finger up     → JUMP")
    print("  Hand on LEFT side   → LEFT")
    print("  Hand on RIGHT side  → RIGHT")
    print("=" * 60)

    # Initialize all components
    recognizer = PoseGestureController(debug=False)
    ui = UIOverlay()
    controller = GameController()
    perf = PerformanceTracker()
    ui_controller = UIController()  # New UI controller

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print(f"\n✓ Camera initialized")
    print(f"✓ Control status: {'ENABLED' if ui.enabled else 'DISABLED'}")
    print(f"✓ Game profile: {ui.game_profile}")
    print("\nStarting... Press SPACE to enable control!\n")

    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Failed to read from camera!")
            break

        # Flip frame horizontally for natural mirror view
        frame = cv2.flip(frame, 1)

        # Process gesture recognition
        gesture, landmarks = recognizer.process_frame(frame)
        latency = perf.get_latency_ms(start_time)

        # Execute gesture if control is enabled
        if ui.enabled and gesture != "IDLE":
            print(f"  → Executing {gesture} on {ui.game_profile}")
            controller.execute_gesture(gesture, ui.game_profile)

        # Render complete UI using the UI controller
        display = ui_controller.render_complete_ui(
            frame, gesture, landmarks, perf.get_fps(),
            latency, ui.enabled, ui.game_profile
        )

        cv2.imshow("Pose-Based Gesture Control", display)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n✓ Quit requested")
            break
        elif key == ord(' '):
            ui.enabled = not ui.enabled
            status = "ENABLED" if ui.enabled else "DISABLED"
            print(f"\n{'=' * 40}")
            print(f"Control {status}")
            print(f"{'=' * 40}\n")
        elif key == ord('p'):
            old_profile = ui.game_profile
            ui.game_profile = "Temple Run" if ui.game_profile == "Subway Surfers" else "Subway Surfers"
            print(f"\n{'=' * 40}")
            print(f"Profile: {old_profile} → {ui.game_profile}")
            print(f"{'=' * 40}\n")

        perf.record_frame()

    cap.release()
    cv2.destroyAllWindows()
    print("\n✓ Cleanup complete. Goodbye!")


if __name__ == "__main__":
    main()