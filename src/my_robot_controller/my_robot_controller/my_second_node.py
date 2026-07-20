#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class MySecondNode(Node):
    def __init__(self):
        super().__init__('my_second_node')
        self.get_logger().info('Hello World 2')
        self.c = 0
        self.create_timer(2.0, self.timer_callback)
    
    def timer_callback(self):
        self.c += 1
        self.get_logger().info(str(self.c))


def main(args=None):
    rclpy.init(args=args)
    node = MySecondNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()