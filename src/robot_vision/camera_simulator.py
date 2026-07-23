#!/usr/bin/env python3
"""
camera_simulator.py
Публикует тестовые изображения в топик /camera_node/image_raw
Используется для разработки без доступа к реальной камере
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
import numpy as np
import math

class CameraSimulator(Node):
    def __init__(self):
        super().__init__('camera_simulator')
        self.width, self.height, self.fps = 640, 480, 30
        self.image_pub = self.create_publisher(Image, '/camera_node/image_raw', 10)
        self.info_pub  = self.create_publisher(CameraInfo, '/camera/camera_info', 10)
        self.timer = self.create_timer(1.0 / self.fps, self.publish_frame)
        self.frame_count = 0
        self.get_logger().info(f'Camera Simulator: {self.width}x{self.height} @ {self.fps} FPS')

    def publish_frame(self):
        t = self.frame_count / self.fps
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Движущийся цветной фон (шаг 4 пикселя для скорости)
        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                r = int(127 + 127 * math.sin(x / 50 + t))
                g = int(127 + 127 * math.sin(y / 50 + t))
                b = int(127 + 127 * math.sin((x + y) / 50 + t))
                image[y:y+4, x:x+4] = [b, g, r]  # BGR

        # Движущийся красный круг
        cx = int(self.width / 2 + 200 * math.sin(t * 0.7))
        cy = int(self.height / 2 + 150 * math.cos(t * 0.5))
        for dy in range(-35, 36):
            for dx in range(-35, 36):
                if dx*dx + dy*dy < 35**2:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        image[ny, nx] = [0, 0, 255]  # Красный (BGR)

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_link'
        msg.height, msg.width = self.height, self.width
        msg.encoding = 'bgr8'
        msg.is_bigendian = False
        msg.step = self.width * 3
        msg.data = image.tobytes()
        self.image_pub.publish(msg)

        info = CameraInfo()
        info.header = msg.header
        info.width, info.height = self.width, self.height
        self.info_pub.publish(info)

        self.frame_count += 1
        if self.frame_count % (self.fps * 5) == 0:
            self.get_logger().info(f'Опубликовано кадров: {self.frame_count}')

def main():
    rclpy.init()
    node = CameraSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()