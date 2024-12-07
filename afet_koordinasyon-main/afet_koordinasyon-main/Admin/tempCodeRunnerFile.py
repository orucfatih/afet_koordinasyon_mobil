import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, 
                             QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from styles import DARK_THEME_STYLE, LIGHT_THEME_STYLE

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.theme = self.load_theme()  # Kayıtlı temayı yükle
        self.initUI()

    def load_theme(self):
        """Kayıtlı temayı dosyadan yükle"""
        try:
            with open('theme.txt', 'r') as f:
                return f.read().strip() or 'dark'
        except FileNotFoundError:
            return 'dark'

    def save_theme(self, theme):
        """Seçilen temayı dosyaya kaydet"""
        with open('theme.txt', 'w') as f:
            f.write(theme)

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Giriş")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Afet Yönetim Sistemi")
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ad Soyad")
        self.username_input.setFont(QFont('Arial', 12))
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont('Arial', 12))
        
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_switch = QCheckBox("Dark Mode")
        
        # Kayıtlı temaya göre checkbox durumunu ayarla
        self.theme_switch.setChecked(self.theme == 'dark')
        self.theme_switch.stateChanged.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_switch)
        
        login_button = QPushButton("Giriş Yap")
        login_button.setFont(QFont('Arial', 12))
        login_button.clicked.connect(self.login)
        
        layout.addStretch(1)
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(self.username_input)
        layout.addSpacing(10)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addLayout(theme_layout)
        layout.addSpacing(10)
        layout.addWidget(login_button)
        layout.addStretch(1)
        
        self.setLayout(layout)
        
        # İlk tema ayarı
        self.apply_theme()

    def apply_theme(self):
        """Seçili temayı uygula"""
        if self.theme == 'dark':
            self.setStyleSheet(DARK_THEME_STYLE + """
                QLineEdit {
                    background-color: #2e2e2e;
                    color: white;
                    border: 1px solid #444;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QLabel {
                    color: white;
                }
                QCheckBox {
                    color: white;
                }
            """)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLE + """
                QLineEdit {
                    background-color: #e6f3e8;
                    color: #db9ca2;
                    border: 1px solid #c0c0c0;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #c0c0c0;
                    color: #db9ca2;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #a0a0a0;
                }
                QLabel {
                    color: #db9ca2;
                }
                QCheckBox {
                    color: #db9ca2;
                }
            """)

    def toggle_theme(self):
        """Tema değişikliği"""
        self.theme = 'dark' if self.theme_switch.isChecked() else 'light'
        self.save_theme(self.theme)  # Temayı kaydet
        self.apply_theme()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            with open('login.txt', 'r') as file:
                stored_username = file.readline().strip()
                stored_password = file.readline().strip()
        except FileNotFoundError:
            QMessageBox.warning(self, "Hata", "Login dosyası bulunamadı!")
            return
        
        if username == stored_username and password == stored_password:
            from ui import AfetYonetimAdmin
            
            # Ana pencereye seçilen temayı aktar
            self.main_window = AfetYonetimAdmin(initial_theme=self.theme)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginPage()
    login.show()
    sys.exit(app.exec_())