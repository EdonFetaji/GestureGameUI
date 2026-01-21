import sys
import time
import cv2

from .core.recognizer_factory import get_recognizer, RecognizerSingleton, RecognizerType
from .core.controller import GameController
from .core.performance import PerformanceTracker

from .ui.ui_draw import draw_ui, draw_hand_skeleton

def main():
    # Check for recognizer type argument from launcher
    if len(sys.argv) > 1:
        recognizer_arg = sys.argv[1]
        # Map argument to RecognizerType
        if recognizer_arg == "HYBRID_POSE" or recognizer_arg == RecognizerType.HYBRID_POSE.value:
            RecognizerSingleton.configure(RecognizerType.HYBRID_POSE)
        else:
            RecognizerSingleton.configure(RecognizerType.MEDIAPIPE_TASKS)
    
    # Use the singleton recognizer instance (configured from Settings UI)
    recognizer = get_recognizer()
    
    print("=" * 60)
    print(f"Gesture Controller - {recognizer.name}")
    print("=" * 60)
    print("Gesture → Action mappings:")
    for gesture, action in recognizer.keyMap.items():
        print(f"  {gesture:15} -> {action}")
    print("=" * 60)

    enabled = True
    profile = "Subway Surfers"  # you can change or load from launcher

    controller = GameController()
    perf = PerformanceTracker()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("❌ Camera could not open")
        return

    last_action = "IDLE"

    try:
        while True:
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            result = recognizer.process(frame)
            frame = result.frame
            action = result.action
            raw_label = result.raw_label
            score = result.confidence
            landmarks = result.landmarks
            latency = perf.latency_ms(start)

            # Draw skeleton
            if landmarks:
                frame = draw_hand_skeleton(frame, landmarks)

            # ✅ Press only once when gesture starts
            if enabled and action != "IDLE" and last_action == "IDLE":
                controller.execute_action(action, profile)

            last_action = action

            # ✅ Minimal UI only (no profiles, no control text, no space toggle help)
            frame = draw_ui(frame, action, raw_label, score, perf.get_fps(), latency, enabled)

            cv2.imshow("Gesture Controller", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            perf.record_frame()
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
