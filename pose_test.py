"""
Pose-Based Gesture Tester
Test the stable pose recognition system with VICTORY and I LOVE YOU gestures
"""

import cv2
import time
from pose_gesture_controller import PoseGestureController
from performance_tracker import PerformanceTracker


def draw_instructions(frame, current_test, test_passed):
    """Draw clear instructions for each pose"""
    h, w = frame.shape[:2]

    # Instructions for each gesture - UPDATED for new static gestures
    instructions = {
        0: ("DUCK", "Make a FIST (close all fingers)", "👊"),
        1: ("JUMP", "Point with INDEX finger only", "☝️"),
        2: ("LEFT", "Show VICTORY sign (✌️)", "✌️"),
        3: ("RIGHT", "Show I LOVE YOU sign (🤟)", "🤟"),
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
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # Additional hint for gesture descriptions
    if current_test == 2:
        cv2.putText(frame, "(Index + Middle fingers up)", (20, 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    elif current_test == 3:
        cv2.putText(frame, "(Thumb + Index + Pinky up)", (20, 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    # Emoji/visual hint
    cv2.putText(frame, emoji, (20, 205),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 200, 0), 2)

    # Status
    status = "✓ PASSED!" if test_passed[current_test] else "Waiting..."
    status_color = (0, 255, 0) if test_passed[current_test] else (100, 100, 100)
    cv2.putText(frame, status, (w - 200, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

    # Visual guides for static gesture tests
    if current_test == 2:  # VICTORY (LEFT)
        # Draw visual representation
        center_x, center_y = w - 200, h // 2

        # Draw two fingers (simplified)
        cv2.line(frame, (center_x - 30, center_y + 50),
                (center_x - 30, center_y - 50), (0, 255, 255), 15)
        cv2.line(frame, (center_x + 30, center_y + 50),
                (center_x + 30, center_y - 50), (0, 255, 255), 15)

        cv2.putText(frame, "Like this!", (center_x - 60, center_y + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    elif current_test == 3:  # I LOVE YOU (RIGHT)
        # Draw visual representation
        center_x, center_y = 200, h // 2

        # Draw three fingers (thumb, index, pinky)
        cv2.line(frame, (center_x - 50, center_y + 20),
                (center_x - 60, center_y - 30), (255, 128, 0), 12)  # Thumb
        cv2.line(frame, (center_x, center_y + 50),
                (center_x, center_y - 50), (255, 128, 0), 15)  # Index
        cv2.line(frame, (center_x + 50, center_y + 50),
                (center_x + 50, center_y - 30), (255, 128, 0), 12)  # Pinky

        cv2.putText(frame, "Like this!", (center_x - 60, center_y + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 128, 0), 2)

    return frame


def main():
    print("=" * 60)
    print("POSE-BASED GESTURE TESTER")
    print("=" * 60)
    print("\nStatic gesture detection - no movement needed!")
    print("Gestures:")
    print("  1. FIST (all fingers closed)")
    print("  2. INDEX finger pointing up")
    print("  3. VICTORY sign (✌️ - index + middle)")
    print("  4. I LOVE YOU sign (🤟 - thumb + index + pinky)")
    print("\nPress Q to quit anytime\n")

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

        # Flip frame for mirror view
        frame = cv2.flip(frame, 1)

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
        print("\nYour static pose gestures work perfectly!")
        print("Now you can use pose_main.py to play games!")
        print("=" * 60 + "\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            display = draw_instructions(frame, 4, test_passed)
            cv2.imshow("Pose Gesture Tester", display)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()