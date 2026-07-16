#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from std_msgs.msg import Float64MultiArray
from bot_control.ik import inverse_kinematics


class GoToGoal(Node):

    def __init__(self):
        super().__init__("go_to_goal")

        self.create_subscription(
            Pose2D,
            "/bot_pose",
            self.pose_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Float64MultiArray,
            "/wheel_velocity_controller/commands",
            10
        )

        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.received_first_pose = False

        # Pulled safely inward to avoid physical wall collisions in Gazebo
        self.goal_points = [
            (85.0, 85.0),    # Goal 0
            (85.0, 415.0),   # Goal 1
            (415.0, 415.0),  # Goal 3
            (415.0, 85.0)    # Goal 2
        ]
        self.current_sequence_index = 0

        # Increased arrival threshold so it doesn't have to be pixel-perfect
        self.kp = 0.015 
        self.goal_threshold = 35.0
        self.max_velocity = 0.35

        self.timer = self.create_timer(0.02, self.control_loop)
        self.get_logger().info("Go To Goal Node Started.")

    def pose_callback(self, msg):
        self.robot_x = msg.x
        self.robot_y = msg.y
        self.robot_theta = msg.theta
        self.received_first_pose = True

    def control_loop(self):
        if not self.received_first_pose:
            return

        # Final Stop Condition
        if self.current_sequence_index >= len(self.goal_points):
            self.get_logger().info("All goals reached! Sequence Complete. Stopping.")
            stop_msg = Float64MultiArray()
            stop_msg.data = [0.0, 0.0, 0.0]
            self.cmd_pub.publish(stop_msg)
            return

        goal_x, goal_y = self.goal_points[self.current_sequence_index]

        ex = goal_x - self.robot_x
        ey = goal_y - self.robot_y

        distance = math.hypot(ex, ey)

        if distance < self.goal_threshold:
            self.get_logger().info(f"Target Sequence Index {self.current_sequence_index} Reached!")
            self.current_sequence_index += 1
            return

        v_world_x = ex
        v_world_y = -ey

        # Apply smooth proportional speed
        speed = min(self.kp * distance, self.max_velocity)
        v_world_x = (v_world_x / distance) * speed
        v_world_y = (v_world_y / distance) * speed

        # Transform world velocity into local body frame
        vx = v_world_x * math.cos(self.robot_theta) + v_world_y * math.sin(self.robot_theta)
        vy = -v_world_x * math.sin(self.robot_theta) + v_world_y * math.cos(self.robot_theta)

        omega = 0.0

        wl, wr, wb = inverse_kinematics(vx, vy, omega)

        cmd_msg = Float64MultiArray()
        cmd_msg.data = [float(wl), float(wr), float(wb)]
        self.cmd_pub.publish(cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    node = GoToGoal()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
