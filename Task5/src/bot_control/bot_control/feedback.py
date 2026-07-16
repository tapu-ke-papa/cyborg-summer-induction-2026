#!/usr/bin/env python3

import math
import cv2
import cv2.aruco as aruco

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose2D

from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data


class Feedback(Node):

    def __init__(self):
        super().__init__("feedback")
        self.bridge = CvBridge()
        
        self.create_subscription(
            Image,
            "/camera",
            self.image_callback,
            qos_profile_sensor_data
        )

        self.pose_pub = self.create_publisher(
            Pose2D,
            "/bot_pose",
            10
        )

        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
        self.parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.dictionary, self.parameters)

        self.robot_id = 1
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.corner_markers = {}

        self.get_logger().info("Feedback Node Started")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {str(e)}")
            return

        corners, ids, rejected = self.detector.detectMarkers(cv_image)

        if ids is not None:
            aruco.drawDetectedMarkers(cv_image, corners, ids)
            ids = ids.flatten()

            for idx, marker_id in enumerate(ids):
                marker_corners = corners[idx][0]
                
                c0 = marker_corners[0]
                c1 = marker_corners[1]
                c2 = marker_corners[2]
                c3 = marker_corners[3]

                cx = int((c0[0] + c1[0] + c2[0] + c3[0]) / 4.0)
                cy = int((c0[1] + c1[1] + c2[1] + c3[1]) / 4.0)

                front_x = (c0[0] + c1[0]) / 2.0
                front_y = (c0[1] + c1[1]) / 2.0
                theta = math.atan2(cy - front_y, front_x - cx)

                if marker_id in [0, 1, 2, 3]:
                    self.corner_markers[int(marker_id)] = (cx, cy)

                if marker_id == self.robot_id:
                    self.robot_x = float(cx)
                    self.robot_y = float(cy)
                    self.robot_theta = float(theta)

                    pose_msg = Pose2D()
                    pose_msg.x = self.robot_x
                    pose_msg.y = self.robot_y
                    pose_msg.theta = self.robot_theta
                    self.pose_pub.publish(pose_msg)

                    cv2.circle(cv_image, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.line(cv_image, (cx, cy), (int(front_x), int(front_y)), (0, 255, 0), 2)
                    cv2.putText(
                        cv_image, 
                        f"Pose: ({cx},{cy},{theta:.2f})", 
                        (cx + 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (255, 255, 255), 
                        1
                    )

        cv2.imshow("Overhead Camera Feed", cv_image)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = Feedback()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
