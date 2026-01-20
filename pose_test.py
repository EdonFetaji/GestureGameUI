"""
Pose-Based Gesture Tester
Test the new stable pose recognition system with INDEX FINGER MOVEMENT controls
"""

import cv2
import time
from pose_gesture_controller import PoseGestureController
from performance_tracker import PerformanceTracker


def draw_instructions(frame, current_test, test_passed):
    """Draw clear instructions for each pose"""
    h, w = frame.shape[:2]

    # Instructions for each gesture - UPDATED for index finger movement
    instructions = {
        0: ("DUCK", "Make a FIST (close all fingers)", "👊"),
        1: ("JUMP", "Point with INDEX finger only", "☝️"),
        2: ("LEFT", "Move INDEX FINGER to the LEFT", "👈"),
        3: ("RIGHT", "Move INDEX FINGER to the RIGHT", "👉"),
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

    # Additional hint for movement gestures
    if current_test in [2, 3]:
        cv2.putText(frame, "(Keep 2+ fingers open)", (20, 170),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    # Emoji/visual hint
    cv2.putText(frame, emoji, (20, 205),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 200, 0), 2)

    # Status
    status = "✓ PASSED!" if test_passed[current_test] else "Waiting..."
    status_color = (0, 255, 0) if test_passed[current_test] else (100, 100, 100)
    cv2.putText(frame, status, (w - 200, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

    # Visual guides for movement (LEFT/RIGHT tests)
    if current_test == 2:  # LEFT test
        # Draw arrow showing LEFT movement
        center_y = h // 2
        arrow_start_x = w - 150
        arrow_end_x = w - 350

        cv2.arrowedLine(frame, (arrow_start_x, center_y), (arrow_end_x, center_y),
                       (0, 255, 255), 8, tipLength=0.3)

        cv2.putText(frame, "Move index finger", (arrow_end_x - 50, center_y - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "THIS WAY", (arrow_end_x, center_y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    elif current_test == 3:  # RIGHT test
        # Draw arrow showing RIGHT movement
        center_y = h // 2
        arrow_start_x = 150
        arrow_end_x = 350

        cv2.arrowedLine(frame, (arrow_start_x, center_y), (arrow_end_x, center_y),
                       (255, 128, 0), 8, tipLength=0.3)

        cv2.putText(frame, "Move index finger", (arrow_start_x - 50, center_y - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 128, 0), 2)
        cv2.putText(frame, "THIS WAY", (arrow_start_x + 50, center_y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 128, 0), 2)

    return frame


def draw_index_movement_indicator(frame, landmarks, recognizer):
    """Draw a visual indicator showing index finger movement"""
    if landmarks is None:
        return frame

    h, w, _ = frame.shape

    # Get index finger tip
    index_tip = landmarks.landmark[8]

    # Convert to screen coordinates (with flip correction)
    index_x = int(w - (index_tip.x * w))
    index_y = int(index_tip.y * h)

    # Draw large circle at index finger tip
    cv2.circle(frame, (index_x, index_y), 15, (0, 255, 255), -1)
    cv2.circle(frame, (index_x, index_y), 18, (255, 255, 255), 2)

    # Draw previous position if available
    if recognizer.prev_index_x is not None and recognizer.prev_index_y is not None:
        prev_x = int(w - (recognizer.prev_index_x * w))
        prev_y = int(recognizer.prev_index_y * h)

        # Draw line showing movement
        cv2.line(frame, (prev_x, prev_y), (index_x, index_y),
                (255, 255, 0), 3)

        # Calculate and display delta
        delta_x = index_tip.x - recognizer.prev_index_x
        delta_y = index_tip.y - recognizer.prev_index_y

        # Determine direction
        if abs(delta_x) > recognizer.movement_threshold:
            if delta_x < -recognizer.movement_threshold:
                direction = "LEFT"
                color = (0, 255, 255)
            elif delta_x > recognizer.movement_threshold:
                direction = "RIGHT"
                color = (255, 128, 0)
            else:
                direction = "NEUTRAL"
                color = (150, 150, 150)
        else:
            direction = "NEUTRAL"
            color = (150, 150, 150)

        # Draw direction label
        label_y = index_y - 40

        # Background for text
        text_size = cv2.getTextSize(direction, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cv2.rectangle(frame,
                     (index_x - text_size[0]//2 - 5, label_y - text_size[1] - 5),
                     (index_x + text_size[0]//2 + 5, label_y + 5),
                     (0, 0, 0), -1)

        cv2.putText(frame, direction, (index_x - text_size[0]//2, label_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Show delta values for debugging
        cv2.putText(frame, f"dX: {delta_x:.3f}", (index_x - 60, label_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    return frame


def main():
    print("=" * 60)
    print("POSE-BASED GESTURE TESTER")
    print("=" * 60)
    print("\nThis uses INDEX FINGER MOVEMENT detection!")
    print("Gestures:")
    print("  1. FIST (all fingers closed)")
    print("  2. INDEX finger pointing up")
    print("  3. Move INDEX FINGER to the LEFT")
    print("  4. Move INDEX FINGER to the RIGHT")
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

            # Draw index movement indicator for LEFT/RIGHT tests
            if current_test in [2, 3]:
                frame = draw_index_movement_indicator(frame, landmarks, recognizer)

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
        print("\nYour INDEX FINGER MOVEMENT gestures work perfectly!")
        print("Now you can use main.py to play games!")
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