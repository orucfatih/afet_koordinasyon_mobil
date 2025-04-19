import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QCheckBox, QDesktopWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush
from .login_ui import LoginUI, adjust_window_to_screen
from ui import AfetYonetimAdmin
import firebase_admin
from firebase_admin import credentials, auth


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

class LoginPage(LoginUI):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.login_button.clicked.connect(self.handle_login)
        self.current_login_type = None
        
        # Firebase uygulamasını başlat
        self.initialize_firebase()
        
        # Test modunda kullanılacak tuş kombinasyonu için timer ve flag
        self.key_sequence = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_key_sequence)
        self.timer.setSingleShot(True)

    def initialize_firebase(self):
        """Firebase yapılandırması"""
        try:
            # Firebase uygulaması zaten başlatılmış mı kontrol et
            firebase_admin.get_app()
        except ValueError:
            # Eğer yoksa, credentials dosyasını kullanarak Firebase'i yapılandır
            cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'firebase-adminsdk.json')
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase başarıyla başlatıldı!")
            else:
                print(f"Firebase credentials dosyası bulunamadı: {cred_path}")
        
    def handle_login(self):
        """Giriş işlemini yönet"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            # Gerçek uygulamada firebase ile doğrulama yapılabilir
            # user = auth.get_user_by_email(username)
            # veya başka bir doğrulama yöntemi...
            
            if username and password:  # Basit kontrol (gerçek uygulamada daha güvenli olmalı)
                self.open_admin_panel()
            else:
                self.show_error_message("Lütfen kullanıcı adı ve şifre girin!")
        except Exception as e:
            self.show_error_message(f"Giriş hatası: {str(e)}")
    
    def open_admin_panel(self):
        """Yönetim panelini aç"""
        self.hide()  # Giriş ekranını gizle
        
        # Ana uygulamayı başlat
        self.admin_panel = AfetYonetimAdmin()
        
        # Pencereyi ekrana sığdır
        adjust_window_to_screen(self.admin_panel)
        
        self.admin_panel.show()
    
    def show_error_message(self, message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Giriş Hatası", message)
    
    def keyPressEvent(self, event):
        """Özel tuş kombinasyonlarını yönet"""
        # Ctrl+Alt+T kombinasyonu için kontrol
        if event.key() == Qt.Key_T and (event.modifiers() & Qt.ControlModifier) and (event.modifiers() & Qt.AltModifier):
            self.open_admin_panel()  # Test modu için direkt giriş
            return
            
        # Diğer özel kombinasyonlar için dizi yaklaşımı
        self.key_sequence.append(event.key())
        
        # Kombo süresi için timer'ı yeniden başlat
        self.timer.start(500)  # 500ms sonra sekans sıfırlanır
        
        # Konami kodu örneği :)
        if len(self.key_sequence) >= 8:
            last_eight = self.key_sequence[-8:]
            konami_code = [Qt.Key_Up, Qt.Key_Up, Qt.Key_Down, Qt.Key_Down, 
                          Qt.Key_Left, Qt.Key_Right, Qt.Key_Left, Qt.Key_Right]
            
            if last_eight == konami_code:
                self.open_admin_panel()  # Gizli komboyla giriş
                self.reset_key_sequence()
                return
        
        super().keyPressEvent(event)
    
    def reset_key_sequence(self):
        """Tuş kombinasyonu sekansını sıfırla"""
        self.key_sequence = []
