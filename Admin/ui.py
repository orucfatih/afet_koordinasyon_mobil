from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox)
from stk_yonetim import STKYonetimTab
from kaynak_yonetimi import KaynakYonetimTab
from rapor import RaporYonetimTab
from afad_personel import PersonelYonetimTab
from styles import *
from operation_management import OperationManagementTab


class AfetYonetimAdmin(QMainWindow):
    """Ana Uygulama Penceresi"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Admin Paneli")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(DARK_THEME_STYLE)

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Tab widget oluşturma
        tabs = QTabWidget()
        tabs.setStyleSheet(TAB_WIDGET_STYLE)
        tabs.addTab(OperationManagementTab(), "Operasyon Yönetimi")
        tabs.addTab(STKYonetimTab(), "STK Yönetimi")
        tabs.addTab(KaynakYonetimTab(), "Kaynak Yönetimi")
        tabs.addTab(RaporYonetimTab(), "Rapor")
        tabs.addTab(PersonelYonetimTab(), "Personel Yönetim")


        layout.addWidget(tabs)

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
