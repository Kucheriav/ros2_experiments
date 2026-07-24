#!/usr/bin/env python3
"""
yolo_detector.py
Детекция объектов с помощью YOLO в видеопотоке ROS 2
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import json

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("ВНИМАНИЕ: ultralytics не установлен, используется заглушка")


class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')

        self.declare_parameter('model', 'yolov8n.pt')
        self.declare_parameter('confidence', 0.5)
        self.declare_parameter('target_classes', ['person', 'chair', 'bottle'])

        model_name   = self.get_parameter('model').value
        self.conf    = self.get_parameter('confidence').value
        self.targets = self.get_parameter('target_classes').value

        self.bridge = CvBridge()

        if YOLO_AVAILABLE:
            self.get_logger().info(f'Загрузка модели: {model_name}')
            self.model = YOLO(model_name)
            self.get_logger().info('YOLO готов к детекции')
        else:
            self.model = None
            self.get_logger().warn('YOLO недоступен, результаты будут пустыми')

        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.detect, 10)
        self.img_pub  = self.create_publisher(Image, '/camera/yolo_annotated', 10)
        self.det_pub  = self.create_publisher(String, '/detections', 10)

        self.frame_count = 0

    def detect(self, msg):
        self.frame_count += 1
        if self.frame_count % 3 != 0:   # Обрабатываем каждый 3-й кадр
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'cv_bridge ошибка: {e}')
            return

        detections = []
        annotated  = frame.copy()

        if self.model is not None:
            results = self.model(frame, conf=self.conf, verbose=False)

            for result in results:
                for box in result.boxes:
                    cls_id    = int(box.cls[0])
                    cls_name  = result.names[cls_id]
                    confidence = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Фильтр по классам (если задан список)
                    if self.targets and cls_name not in self.targets:
                        continue

                    detections.append({
                        'class':      cls_name,
                        'confidence': round(confidence, 3),
                        'bbox':       [x1, y1, x2, y2]
                    })

                    # Рисуем bounding box
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f'{cls_name} {confidence:.2f}'
                    cv2.putText(annotated, label, (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Счётчик и количество детекций
        cv2.putText(annotated,
                    f'Frame: {self.frame_count}  Objects: {len(detections)}',
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Публикуем аннотированное изображение
        out_msg = self.bridge.cv2_to_imgmsg(annotated, 'bgr8')
        out_msg.header = msg.header
        self.img_pub.publish(out_msg)

        # Публикуем детекции в JSON
        if detections:
            self.det_pub.publish(String(data=json.dumps(detections)))
            for d in detections:
                self.get_logger().info(
                    f"{d['class']} ({d['confidence']:.2f}) "
                    f"bbox={d['bbox']}")


def main():
    rclpy.init()
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()