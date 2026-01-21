import time
import cv2

from app.core.recognizer import GestureRecognizerMP
from app.core.controller import GameController
from app.core.performance import PerformanceTracker
from app.core.paths import asset_path

from app.ui.ui_draw import draw_ui, draw_hand_skeleton

def main():
    print("=" * 60)
    print("Gesture Controller (Clean UI)")
    print("=" * 60)
    print("Gesture → Action mappings:")
    print("  Victory      -> LEFT")
    print("  ILoveYou     -> RIGHT")
    print("  Pointing_Up  -> JUMP")
    print("  Closed_Fist  -> DUCK")
    print("  Thumb_Up     -> SPACE")
    print("  else         -> IDLE")
    print("=" * 60)

    enabled = True
    profile = "Subway Surfers"  # you can change or load from launcher

    recognizer = GestureRecognizerMP(
        model_path=asset_path("gesture_recognizer.task"),
        min_score=0.60,
        max_hands=1,
        mirror_view=True,
    )

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

            frame, action, raw_label, score, landmarks = recognizer.process(frame)
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
