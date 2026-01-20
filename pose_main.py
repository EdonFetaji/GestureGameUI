"""
Main program using POSE-BASED gesture control
Much more stable than motion-based control!
"""

from pose_gesture_controller import PoseGestureController
from ui_overlay import UIOverlay
from controller import GameController
from performance_tracker import PerformanceTracker
import cv2
import time


def draw_pose_ui(frame, gesture, fps, latency, enabled, profile):
    """Enhanced UI with pose visualization"""
    h, w = frame.shape[:2]

    # Status panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 200), (40, 40, 40), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

    # Current gesture - BIG and clear
    gesture_color = (0, 255, 0) if gesture != "IDLE" else (100, 100, 100)
    cv2.putText(frame, f"Gesture: {gesture}", (20, 50),
                cv2.FONT_HERSHEY_DUPLEX, 1.0, gesture_color, 2)

    # Profile
    cv2.putText(frame, f"Profile: {profile}", (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Control status
    status_color = (0, 255, 0) if enabled else (100, 100, 100)
    cv2.putText(frame, f"Control: {'ENABLED' if enabled else 'DISABLED'}",
                (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)

    # Performance
    cv2.putText(frame, f"FPS: {fps:.1f} | Latency: {latency:.0f}ms",
                (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # Controls help
    cv2.putText(frame, "SPACE=Toggle  P=Profile  Q=Quit",
                (20, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

    # Gesture guide
    guide_y = h - 160
    cv2.rectangle(overlay, (10, guide_y - 10), (300, h - 10), (30, 30, 30), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

    cv2.putText(frame, "POSE GUIDE:", (20, guide_y + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)
    cv2.putText(frame, "Fist = DUCK", (20, guide_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    cv2.putText(frame, "Index up = JUMP", (20, guide_y + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    cv2.putText(frame, "Hand left = LEFT", (20, guide_y + 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    cv2.putText(frame, "Hand right = RIGHT", (20, guide_y + 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    return frame


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

    recognizer = PoseGestureController(debug=False)
    ui = UIOverlay()
    controller = GameController()
    perf = PerformanceTracker()

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

        # Process gesture
        gesture, landmarks = recognizer.process_frame(frame)
        latency = perf.get_latency_ms(start_time)

        # Draw hand skeleton
        if landmarks:
            frame = recognizer.draw_hand_skeleton(frame, landmarks)

        # Execute gesture if enabled
        if ui.enabled and gesture != "IDLE":
            print(f"  → Executing {gesture} on {ui.game_profile}")
            controller.execute_gesture(gesture, ui.game_profile)

        # Render UI
        display = draw_pose_ui(frame, gesture, perf.get_fps(), latency,
                               ui.enabled, ui.game_profile)
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