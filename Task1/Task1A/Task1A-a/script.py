
import cv2
import numpy as np


def analyze_arena(input_image):

    # ==========================================
    # LOAD IMAGE
    # ==========================================

    image = cv2.imread(input_image)

    if image is None:

        print("Error loading image.")
        return {}

    # ==========================================
    # INITIALIZE OUTPUT
    # ==========================================

    result = {

        "arena_size": None,
        "start": None,
        "goal": None,
        "special_cells": {}

    }

    # ==========================================
    # WRITE YOUR LOGIC BELOW
    # ==========================================

    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv  = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mid_y = h // 2
    mid_x = w // 2
    row_mid = gray[mid_y, :]
    col_mid = gray[:, mid_x]

    left_border   = next((x for x in range(w)         if abs(int(row_mid[x]) - 200) < 15), 0)
    right_border  = next((x for x in range(w-1, -1, -1) if abs(int(row_mid[x]) - 200) < 15), w-1)
    top_border    = next((y for y in range(h)         if abs(int(col_mid[y]) - 200) < 15), 0)
    bottom_border = next((y for y in range(h-1, -1, -1) if abs(int(col_mid[y]) - 200) < 15), h-1)

    ax1 = left_border  + 1
    ax2 = right_border
    ay1 = top_border   + 1
    ay2 = bottom_border
    band_counts = {}
    for y in range(ay1 + 5, ay2 - 5, 3):
        line = gray[y, ax1:ax2]
        bands = 0
        in_line = False
        for v in line:
            if abs(int(v) - 120) < 15 and not in_line:
                in_line = True
                bands += 1
            elif abs(int(v) - 120) >= 15:
                in_line = False
        if bands > 0:
            band_counts[bands] = band_counts.get(bands, 0) + 1

    if not band_counts:
        arena_size = 8  
    else:
        n_internal_lines = max(band_counts, key=lambda k: band_counts[k])
        arena_size = n_internal_lines + 1

    result["arena_size"] = arena_size
    cell_w = (ax2 - ax1) / arena_size
    cell_h = (ay2 - ay1) / arena_size
    color_ranges = {
        "RED":    [(np.array([0,   120,  70]),  np.array([10,  255, 255])),
                   (np.array([170, 120,  70]),  np.array([180, 255, 255]))],
        "GREEN":  [(np.array([40,  60,   60]),  np.array([85,  255, 255]))],
        "BLUE":   [(np.array([100, 80,   80]),  np.array([130, 255, 255]))],
        "ORANGE": [(np.array([10,  120,  100]), np.array([25,  255, 255]))],
        "YELLOW": [(np.array([22,  100,  100]), np.array([38,  255, 255]))],
        "CYAN":   [(np.array([85,  80,   80]),  np.array([100, 255, 255]))],
    }

    masks = {}
    for color, ranges in color_ranges.items():
        mask = np.zeros((h, w), dtype=np.uint8)
        for lo, hi in ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
        masks[color] = mask

    color_meaning = {
        "RED":    "DANGER",
        "GREEN":  "SAFE",
        "BLUE":   "REFUEL",
        "ORANGE": "SLOW",
    }
    for row_idx in range(arena_size):
        for col_idx in range(arena_size):
            cx = int(ax1 + (col_idx + 0.5) * cell_w)
            cy = int(ay1 + (row_idx + 0.5) * cell_h)
            dx = int(cell_w * 0.25)
            dy = int(cell_h * 0.25)
            sx1 = max(0, cx - dx); sx2 = min(w, cx + dx)
            sy1 = max(0, cy - dy); sy2 = min(h, cy + dy)
            col_letter = chr(ord('A') + col_idx)
            row_number = arena_size - row_idx       
            coord = f"{col_letter}{row_number}"
            detected   = None
            max_ratio  = 0.20 
            for color in ["YELLOW", "CYAN", "RED", "GREEN", "BLUE", "ORANGE"]:
                region = masks[color][sy1:sy2, sx1:sx2]
                total  = (sx2 - sx1) * (sy2 - sy1)
                if total == 0:
                    continue
                ratio = cv2.countNonZero(region) / total
                if ratio > max_ratio:
                    detected  = color
                    max_ratio = ratio
                    break
            if detected == "YELLOW":
                result["start"] = coord
            elif detected == "CYAN":
                result["goal"] = coord
            elif detected in color_meaning:
                result["special_cells"][coord] = color_meaning[detected]

    # ==========================================
    # SORT SPECIAL CELLS
    # ==========================================

    sorted_cells = dict(

        sorted(

            result["special_cells"].items(),

            key=lambda item: (

                item[0][0],
                int(item[0][1:])

            )
        )
    )

    result["special_cells"] = sorted_cells

    # ==========================================
    # RETURN FINAL OUTPUT
    # ==========================================

    return result