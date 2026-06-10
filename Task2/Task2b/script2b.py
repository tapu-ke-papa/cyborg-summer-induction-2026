import cv2
import numpy as np
import os

def map_arena():
    
    script_dir = os.path.dirname(os.path.abspath(__file__))

    image_path = os.path.join(
        script_dir,
        "test_images",
        "angled_arena.png"
    )

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not load angled_arena.png from {image_path}")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    color_ranges = {
        "red": [
            (np.array([0,   120,  70]),  np.array([10,  255, 255])),
            (np.array([170, 120,  70]),  np.array([180, 255, 255])),
        ],
        "green": [
            (np.array([36,  50,  50]),   np.array([89,  255, 255])),
        ],
        "blue": [
            (np.array([90,  50,  50]),   np.array([130, 255, 255])),
        ],
        "yellow": [
            (np.array([20,  100, 100]),  np.array([35,  255, 255])),
        ],
    }

    def get_centroid(color_name):
        ranges = color_ranges[color_name]
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (lo, hi) in ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
        mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise RuntimeError(f"Could not detect '{color_name}' corner in the image.")

        largest = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M["m00"] == 0:
            raise RuntimeError(f"Zero-area contour for colour '{color_name}'.")

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return [cx, cy]

    tl = get_centroid("red")
    tr = get_centroid("green")
    br = get_centroid("blue")
    bl = get_centroid("yellow")

    corner_points_detected = [tl, tr, br, bl]

    OUTPUT_SIZE = 500

    pts_src = np.float32([tl, tr, br, bl])
    pts_dst = np.float32([
        [0,           0          ],
        [OUTPUT_SIZE, 0          ],
        [OUTPUT_SIZE, OUTPUT_SIZE],
        [0,           OUTPUT_SIZE],
    ])

    matrix     = cv2.getPerspectiveTransform(pts_src, pts_dst)
    flat_image = cv2.warpPerspective(image, matrix, (OUTPUT_SIZE, OUTPUT_SIZE))

    birds_view_path = os.path.join(script_dir, "birdsview.png")
    cv2.imwrite(birds_view_path, flat_image)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector   = cv2.aruco.ArucoDetector(dictionary, parameters)

    corners, ids, _ = detector.detectMarkers(flat_image)

    robot_pixel_coord      = None
    robot_real_world_coord = None

    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            if int(marker_id) == 1:
                mc = corners[i][0]
                cx = int(np.mean(mc[:, 0]))
                cy = int(np.mean(mc[:, 1]))
                robot_pixel_coord = [cx, cy]

                SCALE = 200.0 / OUTPUT_SIZE
                x_cm = round(cx * SCALE, 1)
                y_cm = round(cy * SCALE, 1)
                robot_real_world_coord = [x_cm, y_cm]
                break

    if robot_pixel_coord is None:
        raise RuntimeError(
            "ArUco marker ID 1 not found in the warped bird's-eye image."
        )

    result = {
        "corner_points_detected": corner_points_detected,
        "robot_pixel_coord":      robot_pixel_coord,
        "robot_real_world_coord": robot_real_world_coord,
    }

    return result

if __name__ == "__main__":
    output = map_arena()
    print(output)