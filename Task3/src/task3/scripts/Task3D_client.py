#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from task3.srv import PrimeFactors

class PrimeFactorClient(Node):
    def __init__(self):
        super().__init__('prime_factor_client')
        self.client = self.create_client(PrimeFactors, 'prime_factors')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for server...")
    def send_request(self, number):
        request = PrimeFactors.Request()
        request.number = number
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            factors = list(future.result().factors)
            self.get_logger().info(
                f"Prime factors of {number}: {factors}"
            )
            print(f"\nPrime factors of {number} are: {factors}\n")
        else:
            self.get_logger().error("Service call failed!")

def main(args=None):
    rclpy.init(args=args)
    node = PrimeFactorClient()
    number = int(sys.argv[1]) if len(sys.argv) > 1 else 360
    node.send_request(number)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
