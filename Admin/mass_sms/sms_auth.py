from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QLineEdit, QDialogButtonBox, QLabel)
from PyQt5.QtCore import Qt

class SMSAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SMS Yetkilendirme")
        self.setModal(True)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Form düzeni
        form_layout = QFormLayout()
        
        # Kullanıcı adı alanı
        self.username = QLineEdit()
        form_layout.addRow("Kullanıcı Adı:", self.username)
        
        # Şifre alanı
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Şifre:", self.password)
        
        layout.addLayout(form_layout)
        
        # Bilgi etiketi
        info_label = QLabel(
            "Not: Bu sistem sadece yetkili personel tarafından kullanılabilir."
        )
        info_label.setStyleSheet("color: #666;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def validate(self):
        """Kullanıcı adı ve şifre doğrulama"""
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        # TODO: Gerçek kimlik doğrulama sistemi entegre edilecek
        # Şimdilik basit bir kontrol
        if username == "admin" and password == "1234":
            self.accept()
        else:
            self.username.clear()
            self.password.clear()
            self.username.setFocus() 