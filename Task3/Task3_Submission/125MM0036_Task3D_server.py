#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from task3.srv import PrimeFactors

class PrimeFactorServer(Node):
    def __init__(self):
        super().__init__('prime_factor_server')
        self.srv = self.create_service(
            PrimeFactors,
            'prime_factors',
            self.handle_request
        )
        self.get_logger().info("Prime Factor Server is ready.")

    def handle_request(self, request, response):
        n = request.number
        self.get_logger().info(f"Received request: {n}")

        factors = []
        if n <= 1:
            response.factors = factors
            return response
        while n % 2 == 0:
            factors.append(2)
            n //= 2
        i = 3
        while i * i <= n:
            while n % i == 0:
                factors.append(i)
                n //= i
            i += 2
        if n > 1:
            factors.append(n)

        response.factors = factors
        self.get_logger().info(f"Prime factors: {factors}")
        return response

def main(args=None):
    rclpy.init(args=args)
    node = PrimeFactorServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
