from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox)
from stk_yonetim import STKYonetimTab
from kaynak_yonetimi import KaynakYonetimTab
from rapor import RaporYonetimTab
from afad_personel import PersonelYonetimTab
from styles_dark import *
from styles_light import *
from operation_management import OperationManagementTab


class AfetYonetimAdmin(QMainWindow):
    """Ana Uygulama Penceresi"""
    def __init__(self, initial_theme='dark'):
        super().__init__()
        self.current_theme = initial_theme
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Admin Paneli")
        self.setGeometry(100, 100, 1400, 800)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Tab widget oluşturma
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_WIDGET_STYLE)
        self.tabs.addTab(OperationManagementTab(), "Operasyon Yönetimi")
        self.tabs.addTab(STKYonetimTab(), "STK Yönetimi")
        self.tabs.addTab(KaynakYonetimTab(), "Kaynak Yönetimi")
        self.tabs.addTab(RaporYonetimTab(), "Rapor")
        self.tabs.addTab(PersonelYonetimTab(), "Personel Yönetim")

        layout.addWidget(self.tabs)

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