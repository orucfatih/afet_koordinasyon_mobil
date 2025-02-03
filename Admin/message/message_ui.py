from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QListWidget,
                            QPushButton, QTextEdit, QLabel, QComboBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles_dark import *

class MessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Mesajlaşma")
        self.setMinimumSize(800, 600)
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        
        # Sol Panel - Konuşma Listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Yeni mesaj butonu
        new_message_btn = QPushButton(" Yeni Mesaj")
        new_message_btn.setIcon(QIcon('icons/new-message.png'))
        new_message_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        new_message_btn.clicked.connect(self.new_message)
        
        # Konuşma listesi
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.chat_list.itemClicked.connect(self.load_chat)
        
        left_layout.addWidget(new_message_btn)
        left_layout.addWidget(self.chat_list)
        left_panel.setLayout(left_layout)
        
        # Sağ Panel - Mesajlaşma Alanı
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Mesaj geçmişi
        self.message_history = QListWidget()
        self.message_history.setStyleSheet(LIST_WIDGET_STYLE)
        
        # Mesaj yazma alanı
        message_input_container = QWidget()
        message_input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Mesajınızı yazın...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet(TEXT_EDIT_STYLE)
        
        send_btn = QPushButton(" Gönder")
        send_btn.setIcon(QIcon('icons/send.png'))
        send_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        send_btn.clicked.connect(self.send_message)
        
        message_input_layout.addWidget(self.message_input)
        message_input_layout.addWidget(send_btn)
        message_input_container.setLayout(message_input_layout)
        
        right_layout.addWidget(self.message_history)
        right_layout.addWidget(message_input_container)
        right_panel.setLayout(right_layout)
        
        # Splitter ile panelleri ayır
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])  # Sol panel 200px, sağ panel 600px
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Örnek verileri yükle
        self.load_sample_data()
    
    def load_sample_data(self):
        """Örnek konuşmaları yükler"""
        sample_chats = [
            "AFAD Merkez",
            "İl Kriz Masası",
            "Sağlık Ekibi",
            "Arama Kurtarma Ekibi",
            "Lojistik Destek Ekibi"
        ]
        self.chat_list.addItems(sample_chats)
    
    def new_message(self):
        """Yeni mesaj başlatır"""
        pass
    
    def load_chat(self, item):
        """Seçili konuşmayı yükler"""
        self.message_history.clear()
        chat_name = item.text()
        
        # Örnek mesajlar
        sample_messages = [
            f"{chat_name}: Merhaba, durum raporu alabilir miyim?",
            "Siz: Tabii, hazırlıyorum...",
            f"{chat_name}: Teşekkürler, beklemedeyim.",
            "Siz: Rica ederim, 5 dakika içinde ileteceğim."
        ]
        self.message_history.addItems(sample_messages)
    
    def send_message(self):
        """Mesajı gönderir"""
        message = self.message_input.toPlainText().strip()
        if message:
            self.message_history.addItem(f"Siz: {message}")
            self.message_input.clear() 