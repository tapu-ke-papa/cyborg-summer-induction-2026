#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math
class InfinityTracer(Node):
    def __init__(self):
        super().__init__('infinity_tracer')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.t = 0.0
        self.dt = 0.05
        self.timer = self.create_timer(self.dt, self.move_turtle)
        self.a = 2.0
    def move_turtle(self):
        t = self.t
        a = self.a
        dt = self.dt
        def pos(s):
            denom = 1 + math.sin(s)**2
            x = a * math.cos(s) / denom
            y = a * math.sin(s) * math.cos(s) / denom
            return x, y
        x0, y0 = pos(t)
        x1, y1 = pos(t + dt)
        dx = x1 - x0
        dy = y1 - y0
        target_angle = math.atan2(dy, dx)
        xp, yp = pos(t - dt)
        prev_angle = math.atan2(y0 - yp, x0 - xp)
        dtheta = target_angle - prev_angle
        while dtheta > math.pi:
            dtheta -= 2 * math.pi
        while dtheta < -math.pi:
            dtheta += 2 * math.pi
        speed = math.sqrt(dx**2 + dy**2) / dt
        msg = Twist()
        msg.linear.x = float(speed)
        msg.angular.z = float(dtheta / dt)
        self.pub.publish(msg)
        self.t += dt
        if self.t >= 2 * math.pi:
            self.pub.publish(Twist())
            self.get_logger().info("Task 3A completed — infinity traced!")
            self.destroy_node()
            rclpy.shutdown()
def main(args=None):
    rclpy.init(args=args)
    node = InfinityTracer()
    rclpy.spin(node)
if __name__ == '__main__':
    main()
