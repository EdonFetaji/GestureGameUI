"""
Pose-Based Gesture Tester
Test the new stable pose recognition system
"""

import cv2
import time
from pose_gesture_controller import PoseGestureController
from performance_tracker import PerformanceTracker


def draw_instructions(frame, current_test, test_passed):
    """Draw clear instructions for each pose"""
    h, w = frame.shape[:2]

    # Instructions for each gesture
    instructions = {
        0: ("DUCK", "Make a FIST (close all fingers)", "👊"),
        1: ("JUMP", "Point with INDEX finger only", "☝️"),
        2: ("LEFT", "Move hand to LEFT side of screen", "←"),
        3: ("RIGHT", "Move hand to RIGHT side of screen", "→"),
    }

    if current_test >= 4:
        # All done
        cv2.putText(frame, "ALL TESTS PASSED!", (w//2 - 200, h//2),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(frame, "Press Q to exit", (w//2 - 120, h//2 + 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return frame

    gesture, instruction, emoji = instructions[current_test]

    # Dark overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w-10, 220), (30, 30, 30), -1)
    frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)

    # Test number
    cv2.putText(frame, f"Test {current_test + 1}/4", (20, 45),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 200, 255), 2)

    # Gesture name
    color = (0, 255, 0) if test_passed[current_test] else (255, 255, 255)
    cv2.putText(frame, f"Gesture: {gesture}", (20, 90),
               cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2)

    # Instructions
    cv2.putText(frame, instruction, (20, 140),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    # Emoji/visual hint
    cv2.putText(frame, emoji, (20, 190),
               cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 200, 0), 3)

    # Status
    status = "✓ PASSED!" if test_passed[current_test] else "Waiting..."
    status_color = (0, 255, 0) if test_passed[current_test] else (100, 100, 100)
    cv2.putText(frame, status, (w - 200, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

    # Zone indicators for LEFT/RIGHT tests
    # FIXED: Swap zones to match mirrored camera view + WIDER zones
    if current_test in [2, 3]:
        # Draw LEFT zone (on RIGHT side of mirrored camera) - 60-100%
        cv2.rectangle(frame, (int(w * 0.60), 0), (w, h), (0, 100, 255), 3)
        cv2.putText(frame, "LEFT ZONE", (w - 180, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 100, 255), 2)
        cv2.putText(frame, "Move hand HERE", (w - 220, h - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 1)

        # Draw RIGHT zone (on LEFT side of mirrored camera) - 0-40%
        cv2.rectangle(frame, (0, 0), (int(w * 0.40), h), (255, 100, 0), 3)
        cv2.putText(frame, "RIGHT ZONE", (20, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 100, 0), 2)
        cv2.putText(frame, "Move hand HERE", (20, h - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 1)

    return frame


def main():
    print("=" * 60)
    print("POSE-BASED GESTURE TESTER")
    print("=" * 60)
    print("\nThis uses STATIC POSES - much more stable!")
    print("Press Q to quit anytime\n")

    recognizer = PoseGestureController(debug=True)
    perf = PerformanceTracker()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    test_sequence = ["DUCK", "JUMP", "LEFT", "RIGHT"]
    current_test = 0
    test_passed = [False, False, False, False]

    print(f"\nTest 1/4: Try {test_sequence[0]} (make a FIST)")

    while current_test < 4:
        ret, frame = cap.read()
        if not ret:
            break

        gesture, landmarks = recognizer.process_frame(frame)

        # Draw hand skeleton
        if landmarks:
            frame = recognizer.draw_hand_skeleton(frame, landmarks)

        # Check if correct gesture detected
        if gesture == test_sequence[current_test] and not test_passed[current_test]:
            test_passed[current_test] = True
            print(f"\n{'='*60}")
            print(f"✓✓✓ Test {current_test + 1}/4 PASSED! ✓✓✓")
            print(f"{'='*60}\n")

            # Brief pause before next test
            time.sleep(0.8)

            current_test += 1
            if current_test < 4:
                print(f"Test {current_test + 1}/4: Try {test_sequence[current_test]}")

        # Draw instructions
        display = draw_instructions(frame, current_test, test_passed)

        # FPS counter
        cv2.putText(display, f"FPS: {perf.get_fps():.1f}",
                   (display.shape[1] - 120, display.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Pose Gesture Tester", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        perf.record_frame()

    # Show final screen if all passed
    if all(test_passed):
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\nYour pose-based gestures work perfectly!")
        print("Now you can use pose_main.py to play games!")
        print("=" * 60 + "\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            display = draw_instructions(frame, 4, test_passed)
            cv2.imshow("Pose Gesture Tester", display)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()