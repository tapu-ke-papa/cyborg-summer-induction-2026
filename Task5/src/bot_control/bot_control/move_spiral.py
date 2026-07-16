#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray
from bot_control.ik import inverse_kinematics

class TraceSpiral(Node):
    def __init__(self):
        super().__init__("trace_spiral")
        self.publisher = self.create_publisher(
            Float64MultiArray,
            "/wheel_velocity_controller/commands",
            10
        )
        self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )
        self.timer = self.create_timer(
            0.02,
            self.control_loop
        )
       
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.a_spiral = 0.1      
        self.b_spiral = 0.05     
        self.t = 0.0             
        self.speed = 0.15       
        self.max_t = 6.0 * math.pi 
        self.kp = 1.5            

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.theta = math.atan2(siny_cosp, cosy_cosp)
    def control_loop(self):
        if self.t > self.max_t:
            msg = Float64MultiArray()
            msg.data = [0.0, 0.0, 0.0]
            self.publisher.publish(msg)
            return
        self.t += self.speed * 0.02
        r = self.a_spiral + self.b_spiral * self.t
        x_d = r * math.cos(self.t)
        y_d = r * math.sin(self.t)
        
      
        error_x_global = x_d - self.x
        error_y_global = y_d - self.y
        
        
        vx_global = self.kp * error_x_global
        vy_global = self.kp * error_y_global
        
        vx = vx_global * math.cos(self.theta) + vy_global * math.sin(self.theta)
        vy = -vx_global * math.sin(self.theta) + vy_global * math.cos(self.theta)
        omega = 0.0  
        
        wl, wr, wb = inverse_kinematics(vx, vy, omega)
        
       
        msg = Float64MultiArray()
        msg.data = [wl, wr, wb]
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TraceSpiral()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
