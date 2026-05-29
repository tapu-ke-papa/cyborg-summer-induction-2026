import cv2
import numpy as np


def analyze_video(video_path):

    # ==========================================
    # OUTPUT DICTIONARY
    # ==========================================

    result = {
        "top_wall_hits": 0,
        "bottom_wall_hits": 0,
        "left_wall_hits": 0,
        "right_wall_hits": 0
    }

    # ==========================================
    # OPEN VIDEO
    # ==========================================

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video")
        return result

    # ==========================================
    # GREEN COLOR RANGE (HSV)
    # ==========================================

    lower_green = np.array([40, 80, 80])
    upper_green = np.array([85, 255, 255])

    # ==========================================
    # FRAME DIMENSIONS
    # ==========================================

    WIDTH  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # ==========================================
    # WALL THRESHOLD
    # ==========================================

    wall_threshold = 45         

    # ==========================================
    # COLLISION COOLDOWN
    # ==========================================
    COOLDOWN = 10
    cooldowns = {
        "top":    0,
        "bottom": 0,
        "left":   0,
        "right":  0,
    }

    # ==========================================
    # TRACKING STATE
    # ==========================================

    MIN_CONTOUR_AREA = 500
    HISTORY_LEN = 5
    positions = []  

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # ==========================================
    # PROCESS VIDEO
    # ==========================================

    while True:

        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_green, upper_green)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        for wall in cooldowns:
            if cooldowns[wall] > 0:
                cooldowns[wall] -= 1
        valid_contours = [c for c in contours if cv2.contourArea(c) >= MIN_CONTOUR_AREA]

        if not valid_contours:
            positions.append(None)
            if len(positions) > HISTORY_LEN:
                positions.pop(0)
            continue
        largest = max(valid_contours, key=cv2.contourArea)

        M = cv2.moments(largest)
        if M["m00"] == 0:
            positions.append(None)
            if len(positions) > HISTORY_LEN:
                positions.pop(0)
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        positions.append((cx, cy))
        if len(positions) > HISTORY_LEN:
            positions.pop(0)

        # ==========================================
        # VELOCITY ESTIMATION over recent history
        # ==========================================
        valid_history = [p for p in positions[:-1] if p is not None]
        def net_velocity():
            """Returns (vx, vy) as net displacement from oldest valid to current."""
            if not valid_history:
                return (0, 0)
            oldest = valid_history[0]
            return (cx - oldest[0], cy - oldest[1])

        vx, vy = net_velocity()

        # ==========================================
        # BOUNCE DETECTION LOGIC
        # ==========================================
        def is_approaching(wall):
            """True if the ball is moving toward the given wall."""
            if wall == "top":
                # cy decreasing = moving up = toward top
                return vy < 2
            if wall == "bottom":
                return vy > -2
            if wall == "left":
                return vx < 2
            if wall == "right":
                return vx > -2
            return False
        wall_checks = [
            ("top",    cy <= wall_threshold),
            ("bottom", cy >= HEIGHT - wall_threshold),
            ("left",   cx <= wall_threshold),
            ("right",  cx >= WIDTH - wall_threshold),
        ]
        for wall, is_near in wall_checks:
            if is_near and cooldowns[wall] == 0:
                if not valid_history or is_approaching(wall):
                    if wall == "top":
                        result["top_wall_hits"] += 1
                    elif wall == "bottom":
                        result["bottom_wall_hits"] += 1
                    elif wall == "left":
                        result["left_wall_hits"] += 1
                    elif wall == "right":
                        result["right_wall_hits"] += 1
                    cooldowns[wall] = COOLDOWN
    cap.release()
    return result