from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtGui import QIcon
from styles.styles_dark import *
from styles.styles_light import *

class NotificationDetailDialog(QDialog):
    """Bildirim Detayları Dialog Penceresi"""
    def __init__(self, title, details, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Detay metni
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setText(details)
        self.detail_text.setStyleSheet(DIALOG_TEXT_STYLE)        

        # Kapat butonu
        close_button = QPushButton(" Kapat")
        close_button.setIcon(QIcon('icons/close.png'))
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(BUTTON_STYLE)
        
        layout.addWidget(self.detail_text)
        layout.addWidget(close_button)
        
        self.setLayout(layout) 