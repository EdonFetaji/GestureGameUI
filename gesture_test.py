"""
Simple Gesture Testing Tool
Tests each gesture one at a time with visual feedback

Instructions:
1. Position your hand in the center of the frame
2. Make ONE clear gesture at a time
3. Wait for confirmation before next gesture
"""

import cv2
import time
from gesture_recognizer import GestureController
from performance_tracker import PerformanceTracker


def draw_instructions(frame, test_mode, gesture_count):
    """Draw testing instructions on frame"""
    h, w = frame.shape[:2]

    # Semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w-10, 200), (40, 40, 40), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

    # Title
    cv2.putText(frame, "GESTURE TESTING MODE", (20, 40),
                cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)

    # Current test
    tests = ["UP (JUMP)", "RIGHT", "LEFT", "DOWN (DUCK)", "COMPLETE!"]
    current_test = tests[min(test_mode, 4)]

    cv2.putText(frame, f"Test {test_mode + 1}/4: {current_test}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Progress
    progress = f"Detected: {gesture_count[test_mode]}/1"
    color = (0, 255, 0) if gesture_count[test_mode] >= 1 else (100, 100, 100)
    cv2.putText(frame, progress, (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    # Instructions
    instructions = [
        "Make a QUICK UPWARD swipe",
        "Make a QUICK RIGHT swipe",
        "Make a QUICK LEFT swipe",
        "Make a QUICK DOWNWARD swipe",
        "All tests passed! Press Q to quit"
    ]
    cv2.putText(frame, instructions[min(test_mode, 4)], (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    return frame


def main():
    print("=" * 60)
    print("GESTURE TESTER - Test Each Gesture")
    print("=" * 60)
    print("\nFollow the on-screen instructions")
    print("Press Q to quit anytime\n")

    recognizer = GestureController(debug=False)
    perf = PerformanceTracker()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    test_sequence = ["JUMP", "RIGHT", "LEFT", "DUCK"]
    test_mode = 0
    gesture_count = [0, 0, 0, 0]

    print(f"Test 1/4: Try {test_sequence[0]}")

    while test_mode < 4:
        ret, frame = cap.read()
        if not ret:
            break

        gesture, landmarks = recognizer.process_frame(frame)

        # Check if correct gesture detected
        if gesture == test_sequence[test_mode]:
            gesture_count[test_mode] += 1
            print(f"\n✓✓✓ {gesture} DETECTED! ✓✓✓")
            print(f"Test {test_mode + 1}/4 PASSED!")

            # Show success message
            success_frame = frame.copy()
            cv2.putText(success_frame, f"{gesture} SUCCESS!", (200, 300),
                       cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 4)
            cv2.imshow("Gesture Tester", success_frame)
            cv2.waitKey(1000)  # Show for 1 second

            # Move to next test
            test_mode += 1
            if test_mode < 4:
                print(f"\nTest {test_mode + 1}/4: Try {test_sequence[test_mode]}")
                time.sleep(0.5)  # Brief pause

        # Draw instructions
        display = draw_instructions(frame, test_mode, gesture_count)

        # Show FPS
        cv2.putText(display, f"FPS: {perf.get_fps():.1f}", (20, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Gesture Tester", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        perf.record_frame()

    # All tests complete
    if test_mode >= 4:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓✓✓")
        print("=" * 60)
        print("\nYour gesture recognition is working perfectly!")
        print("You can now use main.py to play games.")
        print("=" * 60)

        # Show success screen
        final_frame = frame.copy()
        cv2.putText(final_frame, "ALL TESTS PASSED!", (150, 300),
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(final_frame, "Press Q to exit", (250, 400),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imshow("Gesture Tester", final_frame)
        cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()