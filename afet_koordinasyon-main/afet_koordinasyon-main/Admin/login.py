import sys
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPixmap
from styles_dark import LOGIN_DARK_STYLES
from styles_light import LOGIN_LIGHT_STYLES

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

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.theme = 'dark'
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Giriş")
        self.setFixedSize(500, 700)  # Sabit boyut
        
        # Arka plan resmi
        self.background_image = QPixmap("afet_koordinasyon-main/Admin/icons/AFAD-Logo-Renkli.png")
        
        # İlk tema stilleri
        self.setStyleSheet(LOGIN_DARK_STYLES)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo veya Başlık
        title_label = QLabel("Afet Yönetim Sistemi")
        title_label.setFont(QFont('Arial', 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        # Kullanıcı Adı Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı")
        
        # Şifre Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)  # Başlangıçta şifre gizli
        
        # Şifreyi Göster/Gizle Butonu
        self.show_hide_button = QPushButton("Şifreyi Göster")
        self.show_hide_button.clicked.connect(self.toggle_password_visibility)
        
        # Tema Değiştirme
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        
        self.theme_toggle = StyledToggle()
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_toggle)
        theme_layout.addStretch()
        
        # Giriş Butonu
        login_button = QPushButton("Giriş Yap")
        login_button.clicked.connect(self.login)
        
        # Layout'a ekleme
        layout.addWidget(title_label)
        layout.addWidget(self.username_input)
        
        # Şifre ve butonları aynı satıra eklemek için bir HBoxLayout kullanalım
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_hide_button)
        
        layout.addLayout(password_layout)
        layout.addLayout(theme_layout)
        layout.addWidget(login_button)
        layout.addStretch()
        
        self.setLayout(layout)

    def paintEvent(self, event):
        """Arka plan resmini çizme ve saydamlık ekleme"""
        painter = QPainter(self)
        
        # Arka plan resmini pencereye çizme
        painter.drawPixmap(115, 400, 300, 250, self.background_image)
        
        # Saydamlık eklemek için opaklık ayarlama
        painter.setOpacity(0.2)  # Saydamlık değeri (0.0-1.0 arasında)
        
        super().paintEvent(event)

    def toggle_theme(self):
        """Tema değişikliği"""
        self.theme = 'light' if self.theme_toggle.isChecked() else 'dark'
        
        if self.theme == 'dark':
            self.setStyleSheet(LOGIN_DARK_STYLES)
        else:
            self.setStyleSheet(LOGIN_LIGHT_STYLES)

    def toggle_password_visibility(self):
        """Şifreyi göster/gizle"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_hide_button.setText("Şifreyi Gizle")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_hide_button.setText("Şifreyi Göster")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "a" and password == "a":
            from ui import AfetYonetimAdmin
            
            # Ana pencereye seçilen temayı aktar
            self.main_window = AfetYonetimAdmin(initial_theme=self.theme)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "a" and password == "a":
            from ui import AfetYonetimAdmin
            
            # Ana pencereye seçilen temayı aktar
            self.main_window = AfetYonetimAdmin(initial_theme=self.theme)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")
