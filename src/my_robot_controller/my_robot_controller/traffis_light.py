import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TrafficLight(Node):
    def __init__(self):
        super().__init__('traffic_lights')
        self.colors = ['RED', 'YELLOW', 'GREEN']
        self.current_index = 0
        self.publisher_ = self.create_publisher(
            String,
            'color'
        )