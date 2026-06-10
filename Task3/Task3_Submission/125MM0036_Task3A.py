#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
class InfinityTracer(Node):
    def __init__(self):
        super().__init__('infinity_tracer')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.pose = None
        self.state = 'wait'  
        self.linear_speed = 1.0
        self.radius = 1.5
        self.angular_speed = self.linear_speed / self.radius
        self.circle1_done = False
        self.circle2_done = False
        self.circle1_angle = 0.0
        self.circle2_angle = 0.0
        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info("Infinity Tracer started. Waiting for pose...")
    def pose_callback(self, msg):
        self.pose = msg
    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    def control_loop(self):
        if self.pose is None:
            return
        msg = Twist()
        if self.state == 'wait':
            self.circle1_angle = 0.0
            self.circle2_angle = 0.0
            self.state = 'circle1'
            self.get_logger().info("Starting circle 1 (left loop)...")
        elif self.state == 'circle1':
            msg.linear.x = self.linear_speed
            msg.angular.z = self.angular_speed  # left circle
            self.circle1_angle += self.angular_speed * 0.05
            if self.circle1_angle >= 2 * math.pi:
                self.state = 'circle2'
                self.circle2_angle = 0.0
                self.get_logger().info("Circle 1 done. Starting circle 2 (right loop)...")
        elif self.state == 'circle2':
            msg.linear.x = self.linear_speed
            msg.angular.z = -self.angular_speed  # right circle
            self.circle2_angle += self.angular_speed * 0.05
            if self.circle2_angle >= 2 * math.pi:
                self.state = 'done'
                self.get_logger().info("Infinity trace complete!")
        elif self.state == 'done':
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.pub.publish(msg)
            self.get_logger().info("Task 3A completed successfully!")
            self.destroy_node()
            rclpy.shutdown()
            return
        self.pub.publish(msg)
def main(args=None):
    rclpy.init(args=args)
    node = InfinityTracer()
    rclpy.spin(node)
if __name__ == '__main__':
    main()
