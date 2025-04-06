"""
Operation Management modülü için yardımcı fonksiyonlar
"""
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QBrush, QColor

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

def create_status_item(status, status_colors):
    """Durum hücresi oluşturur ve renklendirir"""
    item = QTableWidgetItem(status)
    item.setTextAlignment(Qt.AlignCenter)
    if status in status_colors:
        item.setBackground(QBrush(QColor(status_colors[status])))
    return item 