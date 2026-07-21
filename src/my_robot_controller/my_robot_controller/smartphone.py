#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Smartphone(Node):
    """
    Узел-подписчик, который получает новости робота.
    """
    
    def __init__(self):
        super().__init__('smartphone')
        
        # Создаём Subscriber
        self.subscriber_ = self.create_subscription(
            String,                    # тип сообщения
            'robot_news',              # имя топика
            self.callback_news,        # функция обработки
            10                         # размер очереди
        )
        
        self.get_logger().info('Smartphone готов принимать новости!')
    
    def callback_news(self, msg):
        """
        Эта функция вызывается при получении каждого сообщения.
        """
        self.get_logger().info(f'📱 Получена новость: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Smartphone()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
