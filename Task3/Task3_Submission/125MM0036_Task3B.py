#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

import math


class WaypointNavigator(Node):

    def __init__(self):
        super().__init__('waypoint_navigator')

        self.pose = None

        self.waypoints = [
            (5.5, 9.5),
            (7.0, 5.5),
            (10.0, 5.5),
            (7.8, 3.0),
            (9.0, 0.5),
            (5.5, 2.5),
            (2.0, 0.5),
            (3.2, 3.0),
            (1.0, 5.5),
            (4.0, 5.5),
            (5.5, 9.5)
        ]

        self.current_goal = 0

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.navigate
        )

    def pose_callback(self, msg):
        self.pose = msg

    def navigate(self):

        if self.pose is None:
            return

        if self.current_goal >= len(self.waypoints):

            stop = Twist()
            self.cmd_pub.publish(stop)

            self.get_logger().info("All waypoints completed")

            self.destroy_node()
            rclpy.shutdown()
            return

        goal_x, goal_y = self.waypoints[self.current_goal]

        dx = goal_x - self.pose.x
        dy = goal_y - self.pose.y

        distance = math.sqrt(dx * dx + dy * dy)

        target_theta = math.atan2(dy, dx)

        heading_error = target_theta - self.pose.theta

        while heading_error > math.pi:
            heading_error -= 2 * math.pi

        while heading_error < -math.pi:
            heading_error += 2 * math.pi

        cmd = Twist()

        cmd.linear.x = 1.5 * distance
        cmd.angular.z = 6.0 * heading_error

        self.cmd_pub.publish(cmd)

        if distance < 0.2:
            self.get_logger().info(
                f"Reached waypoint {self.current_goal + 1}"
            )
            self.current_goal += 1


def main(args=None):

    rclpy.init(args=args)

    node = WaypointNavigator()

    rclpy.spin(node)


if __name__ == '__main__':
    main()
