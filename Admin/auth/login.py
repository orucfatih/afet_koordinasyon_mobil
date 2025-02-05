import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from styles_dark import LOGIN_DARK_STYLES
from styles_light import LOGIN_LIGHT_STYLES
from .login_ui import LoginUI

class StyledToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.setCursor(Qt.PointingHandCursor)
        self._slide_pos = 0
        self._animation = QPropertyAnimation(self, b"slide_pos")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)

    @pyqtProperty(float)
    def slide_pos(self):
        return self._slide_pos

    @slide_pos.setter
    def slide_pos(self, pos):
        self._slide_pos = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        bg_rect = self.rect()
        bg_color = QColor('#4a4a4a') if not self.isChecked() else QColor('#4CAF50')
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, 15, 15)

        # Slider
        slider_width = 26
        slider_height = 26
        margin = 2
        x = margin + self._slide_pos * (self.width() - slider_width - 2 * margin)
        slider_rect = QRect(int(x), margin, slider_width, slider_height)
        
        painter.setBrush(QBrush(QColor('white')))
        painter.drawEllipse(slider_rect)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.toggle()
        
        # Animate slider
        start_value = 0 if not self.isChecked() else 1
        end_value = 1 if not self.isChecked() else 0
        
        self._animation.setStartValue(start_value)
        self._animation.setEndValue(end_value)
        self._animation.start()

login_file = os.path.join(os.path.dirname(__file__), 'login.txt')
class LoginPage(LoginUI):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            with open(login_file, 'r') as file:
                credentials = json.load(file)
                stored_username = credentials.get("username")
                stored_password = credentials.get("password")
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Hata", "Login dosyası bulunamadı veya bozuk!")
            return
        
        if username == stored_username and password == stored_password:
            from ui import AfetYonetimAdmin
            
            # Ana pencereye seçilen temayı aktar
            self.main_window = AfetYonetimAdmin(initial_theme=self.theme)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")
