from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox,
                            QToolButton, QHBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from stk_yonetim import STKYonetimTab
from resources_management.kaynak_yonetimi import KaynakYonetimTab
from rapor import RaporYonetimTab
from personnel import PersonelYonetimTab
from styles_dark import *
from styles_light import *
from operation_management.operation_management import OperationManagementTab
from message.message import MessageManager


class AfetYonetimAdmin(QMainWindow):
    """Ana Uygulama Penceresi"""
    def __init__(self, initial_theme='dark'):
        super().__init__()
        self.current_theme = initial_theme
        self.message_manager = MessageManager(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Admin Paneli")
        self.setGeometry(100, 100, 1400, 800)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget oluşturma
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_WIDGET_STYLE)
        
        # Sekmeleri ekle
        self.tabs.addTab(OperationManagementTab(), "Operasyon Yönetimi")
        self.tabs.addTab(STKYonetimTab(), "STK Yönetimi")
        self.tabs.addTab(KaynakYonetimTab(), "Kaynak Yönetimi")
        self.tabs.addTab(RaporYonetimTab(), "Rapor")
        self.tabs.addTab(PersonelYonetimTab(), "Personel Yönetim")
        
        # Mesaj butonu için özel bir widget oluştur
        tab_corner_widget = QWidget()
        corner_layout = QHBoxLayout(tab_corner_widget)
        corner_layout.setContentsMargins(0, 0, 5, 0)  # Sağ tarafta biraz boşluk bırak
        
        # Mesaj butonu
        message_btn = QToolButton()
        message_btn.setIcon(QIcon('icons/message.png'))
        message_btn.setIconSize(QSize(24, 24))
        message_btn.setToolTip("Mesajlar")
        message_btn.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 5px;
                margin-top: 2px;
                border-radius: 3px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
        """)
        message_btn.clicked.connect(self.message_manager.show_message_dialog)
        
        corner_layout.addWidget(message_btn)
        corner_layout.addStretch()  # Butonu sağa yasla
        
        # Mesaj butonunu sekmelerin sağ üst köşesine yerleştir
        self.tabs.setCornerWidget(tab_corner_widget, Qt.TopRightCorner)
        
        main_layout.addWidget(self.tabs)
        
        # İlk başta seçilen temayı uygula
        self.setStyleSheet(DARK_THEME_STYLE if self.current_theme == 'dark' else LIGHT_THEME_STYLE)

    def closeEvent(self, event):
        """Kapatma butonu (çarpı) tıklanınca uyarı verir."""
        reply = QMessageBox.question(
            self,
            "Çıkış Onayı",
            "Uygulamayı kapatmak istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            event.ignore()  # Kapatma işlemini iptal et
        else:
            event.accept()  # Kapatma işlemini onayla