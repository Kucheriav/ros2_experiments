#!/usr/bin/env python3
"""Базовые операции с изображениями в OpenCV"""

import cv2
import os
import numpy as np

# 1. Создать чёрное изображение 480x640
image = np.zeros((480, 640, 3), dtype=np.uint8)

# 2. Нарисовать цветные примитивы
cv2.rectangle(image, (50, 50), (200, 200), (0, 255, 0), 3)      # Зелёный прямоугольник
cv2.circle(image, (400, 240), 80, (0, 0, 255), -1)              # Красный круг (заполненный)
cv2.line(image, (0, 480), (640, 0), (255, 255, 0), 2)           # Жёлтая диагональ
cv2.putText(image, 'OpenCV!', (220, 400),
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

# 3. Вывести информацию
print(f"Форма изображения: {image.shape}")   # (480, 640, 3)
print(f"Тип данных: {image.dtype}")          # uint8
print(f"Размер в байтах: {image.nbytes}")

# 4. Прочитать значение пикселя (зелёный квадрат)
pixel = image[100, 100]
print(f"Пиксель (100,100): BGR = {pixel}")   # [0, 255, 0]

# 5. Сохранить результат
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, 'image_basics.png')
print(save_path)
cv2.imwrite(save_path, image)
print("Сохранено.")