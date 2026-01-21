import cv2


def draw_ui(frame, action, raw_label, score, fps, latency_ms, enabled):
    """
    Minimal UI:
    - Action
    - Model label + score
    - FPS + latency
    (No profiles box, no control status, no space toggle text)
    """
    overlay = frame.copy()

    # Small panel top-left
    x1, y1 = 15, 15
    x2, y2 = 420, 140
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (40, 40, 40), -1)
    frame = cv2.addWeighted(overlay, 0.65, frame, 0.35, 0)

    # Action (big)
    action_color = (0, 255, 0) if action != "IDLE" else (170, 170, 170)
    cv2.putText(frame, f"Action: {action}", (x1 + 12, y1 + 40),
                cv2.FONT_HERSHEY_DUPLEX, 1.0, action_color, 2)

    # Model label
    model_text = "None" if not raw_label else f"{raw_label} ({score:.2f})"
    cv2.putText(frame, f"Model: {model_text}", (x1 + 12, y1 + 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 2)

    # Performance line
    cv2.putText(frame, f"FPS: {fps:.1f} | Latency: {latency_ms:.0f}ms", (x1 + 12, y1 + 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, (200, 200, 200), 2)

    # ✅ Bottom-left hint
    h, w = frame.shape[:2]
    cv2.putText(
        frame,
        "[Q] = Quit",
        (15, h - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (1, 1, 1),
        2,
    )

    return frame


def draw_hand_skeleton(frame, landmarks):
    """
    Draw MediaPipe hand skeleton lines + points.
    landmarks: list of mediapipe normalized landmarks (x,y)
    """
    h, w = frame.shape[:2]

    # Standard MediaPipe hand connections
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),       # thumb
        (0, 5), (5, 6), (6, 7), (7, 8),       # index
        (0, 9), (9, 10), (10, 11), (11, 12),  # middle
        (0, 13), (13, 14), (14, 15), (15, 16),# ring
        (0, 17), (17, 18), (18, 19), (19, 20),# pinky
        (5, 9), (9, 13), (13, 17)             # palm
    ]

    # Convert to pixel coords
    pts = []
    for lm in landmarks:
        x = int(lm.x * w)
        y = int(lm.y * h)
        pts.append((x, y))

    # Draw lines
    for a, b in connections:
        cv2.line(frame, pts[a], pts[b], (0, 0, 255), 2)

    # Draw points
    for (x, y) in pts:
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    return frame
