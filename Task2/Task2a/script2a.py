import cv2
import numpy as np
import glob
import os

def localize_bot():
    CHECKERBOARD = (9, 6)
    SQUARE_SIZE  = 2.5
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE
    objpoints = []
    imgpoints = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    calib_path = os.path.join(script_dir, "calibration_images", "*.jpg")
    images = glob.glob(calib_path)
    if not images:
        calib_path = os.path.join(script_dir, "calibration_images", "*.png")
        images = glob.glob(calib_path)
    if not images:
        calib_path = os.path.join(script_dir, "calibration_images", "*")
        images = glob.glob(calib_path)
    img_shape = None
    for fname in images:
        img  = cv2.imread(fname)
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_shape = gray.shape[::-1]
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
        if ret:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints.append(corners_refined)
    if not objpoints:
        raise RuntimeError(
            "No checkerboard corners found. Check that calibration_images/ "
            "exists and contains valid checkerboard photos."
        )
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, img_shape, None, None
    )

    camera_matrix_trace = round(float(np.trace(mtx)), 2)

    arena_path = os.path.join(script_dir, "test_images/test_arena.jpg")
    raw_image  = cv2.imread(arena_path)

    if raw_image is None:
        raise FileNotFoundError(f"Could not load test_arena.jpg from {arena_path}")

    fixed_image = cv2.undistort(raw_image, mtx, dist, None, mtx)

    dictionary  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters  = cv2.aruco.DetectorParameters()
    detector    = cv2.aruco.ArucoDetector(dictionary, parameters)

    corners, ids, rejected = detector.detectMarkers(fixed_image)

    markers_result = {}

    if ids is not None and len(ids) > 0:
        MARKER_SIZE = 5.0

        half = MARKER_SIZE / 2.0
        marker_3d_edges = np.array([
            [-half,  half, 0],
            [ half,  half, 0],
            [ half, -half, 0],
            [-half, -half, 0]
        ], dtype=np.float32)

        for i, marker_id in enumerate(ids.flatten()):
            corner_pts = corners[i][0].astype(np.float32)

            success, rvec, tvec = cv2.solvePnP(
                marker_3d_edges, corner_pts, mtx, dist
            )

            if success:
                distance_z = round(float(tvec[2][0]), 1)
                x_offset   = round(float(tvec[0][0]), 1)

                key = f"id_{marker_id}"
                markers_result[key] = {
                    "distance_z": distance_z,
                    "x_offset":   x_offset
                }

    result = {
        "camera_matrix_trace": camera_matrix_trace,
        "markers": markers_result
    }

    return result

if __name__ == "__main__":
    output = localize_bot()
    print(output)