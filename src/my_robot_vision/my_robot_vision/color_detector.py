#!/usr/bin/env python3
"""
color_detector.py
Находит красные объекты в видеопотоке, публикует обработанное изображение
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')
        self.bridge = CvBridge()

        # Диапазон красного в HSV (красный "оборачивается" через 0/180)
        self.lower_red1 = np.array([0,   100, 100])
        self.upper_red1 = np.array([10,  255, 255])
        self.lower_red2 = np.array([160, 100, 100])
        self.upper_red2 = np.array([180, 255, 255])

        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.detect_color, 10)
        self.pub = self.create_publisher(
            Image, '/camera/color_detected', 10)

        self.get_logger().info('Color Detector запущен. Ищу красные объекты.')

    def detect_color(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

            # Маска для красного цвета
            mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
            mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
            mask = mask1 | mask2

            # Морфологическая очистка маски
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            result = cv_image.copy()
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 500:
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w // 2, y + h // 2

                cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(result, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(result, f'RED ({cx},{cy})',
                            (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)

                self.get_logger().info(
                    f'Красный объект: центр=({cx},{cy}), площадь={area:.0f}')

            out = self.bridge.cv2_to_imgmsg(result, 'bgr8')
            out.header = msg.header
            self.pub.publish(out)

        except Exception as e:
            self.get_logger().error(f'Ошибка: {e}')

def main():
    rclpy.init()
    node = ColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()