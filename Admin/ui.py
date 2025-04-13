from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox,
                            QToolButton, QHBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from stk_yonetim import STKYonetimTab
from resources_management.kaynak_yonetimi import KaynakYonetimTab
from report.rapor import RaporYonetimTab
from personnel import PersonelYonetimTab
from face_recognition.face_detect_ui import MissingPersonDetectionTab
from styles.styles_dark import *
from styles.styles_light import *
from operation_management.operation_management import OperationManagementTab
from message.message import MessageManager
from utils import get_icon_path
from equipment_management.equipment_management import EquipmentManagementTab
from citizen_death_report.citizen_report import CitizenReportTab
from simulations.simulation_tabs import SimulationTab
import os

class AfetYonetimAdmin(QMainWindow):
    """Ana Uygulama Penceresi"""
    def __init__(self, initial_theme='dark'):
        super().__init__()
        self.current_theme = initial_theme
        self.message_manager = MessageManager(self)
        self.current_tab_index = 0
        self.tabs_per_page = 7
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
        
        # Tab bar ayarları
        tab_bar = self.tabs.tabBar()
        tab_bar.setUsesScrollButtons(False)
        tab_bar.setDrawBase(True)
        
        self.tabs.setDocumentMode(True)
        tab_bar.setExpanding(True)
        
        # Buton stilleri
        arrow_style = "QToolButton { padding: 2px; border: none; }"
        
        # Sol ok butonu için corner widget
        left_corner = QWidget()
        left_layout = QHBoxLayout(left_corner)
        left_layout.setContentsMargins(5, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignVCenter)
        
        self.left_arrow = QToolButton()
        self.left_arrow.setIcon(QIcon(get_icon_path('left_arrow.png')))
        self.left_arrow.setIconSize(QSize(24, 24))
        self.left_arrow.setFixedSize(QSize(28, 28))
        self.left_arrow.setStyleSheet(arrow_style)
        self.left_arrow.clicked.connect(self.scroll_tabs_left)
        self.left_arrow.setEnabled(False)
        left_layout.addWidget(self.left_arrow)
        
        # Sağ ok butonu ve mesaj butonu için corner widget
        right_corner = QWidget()
        right_layout = QHBoxLayout(right_corner)
        right_layout.setContentsMargins(0, 0, 5, 0)
        right_layout.setAlignment(Qt.AlignVCenter)
        
        self.right_arrow = QToolButton()
        self.right_arrow.setIcon(QIcon(get_icon_path('right_arrow.png')))
        self.right_arrow.setIconSize(QSize(24, 24))
        self.right_arrow.setFixedSize(QSize(28, 28))
        self.right_arrow.setStyleSheet(arrow_style)
        self.right_arrow.clicked.connect(self.scroll_tabs_right)
        
        # Mesaj butonu
        message_btn = QToolButton()
        message_btn.setIcon(QIcon(get_icon_path('message.png')))
        message_btn.setIconSize(QSize(24, 24))
        message_btn.setFixedSize(QSize(40, 40))
        message_btn.setToolTip("Mesajlar")
        message_btn.setStyleSheet(MESSAGE_BUTTON_STYLE)
        message_btn.clicked.connect(self.message_manager.show_message_dialog)
        
        right_layout.addWidget(self.right_arrow)
        right_layout.addWidget(message_btn)
        
        # Corner widget'ları tab widget'a ekle
        self.tabs.setCornerWidget(left_corner, Qt.TopLeftCorner)
        self.tabs.setCornerWidget(right_corner, Qt.TopRightCorner)
        
        main_layout.addWidget(self.tabs)
        
        # Tüm sekmeleri liste olarak tut
        self.all_tabs = [
            ("Operasyon Yönetimi", OperationManagementTab()),
            ("STK Yönetimi", STKYonetimTab()),
            ("Rapor", RaporYonetimTab()),
            ("Personel Yönetim", PersonelYonetimTab()),
            ("Kayıp Vatandaş Tespiti", MissingPersonDetectionTab()),
            ("Ekipman Yönetimi", EquipmentManagementTab()),
            ("Vefat Kayıtları", CitizenReportTab()),
            ("Kaynak Yönetimi", KaynakYonetimTab()),
            ("İhtiyaç Talep Yönetimi", CitizenReportTab()),
            ("Gönüllü Yönetimi", CitizenReportTab()),
            ("Altyapı Durumu", CitizenReportTab()),
            ("Yardım Lojistiği", CitizenReportTab()),
            ("Geçici İskan Planlama", CitizenReportTab()),
            ("Kitlesel SMS/Bildirim Sistemi", CitizenReportTab()),
            ("Senaryo Simülasyonu", SimulationTab()),
            ("Finansal Yönetim", CitizenReportTab()),
            ("Vatandaş Feedback Sistemi", CitizenReportTab()),
            ("Bina Hasar Tespit Yönetimi", CitizenReportTab()),
        ]
        
        # İlk sayfadaki sekmeleri göster
        self.update_visible_tabs()
        
        # İlk başta seçilen temayı uygula
        self.setStyleSheet(DARK_THEME_STYLE if self.current_theme == 'dark' else LIGHT_THEME_STYLE)
        
        # Ok butonlarının durumunu güncelle
        self.update_arrow_states()

    def update_visible_tabs(self):
        # Mevcut sekmeleri temizle
        self.tabs.clear()
        
        # Görünür sekmeleri ekle
        start_idx = self.current_tab_index
        end_idx = min(start_idx + self.tabs_per_page, len(self.all_tabs))
        
        for i in range(start_idx, end_idx):
            tab_name, tab_widget = self.all_tabs[i]
            self.tabs.addTab(tab_widget, tab_name)

    def scroll_tabs_left(self):
        if self.current_tab_index > 0:
            self.current_tab_index -= self.tabs_per_page
            self.update_visible_tabs()
            self.update_arrow_states()

    def scroll_tabs_right(self):
        if self.current_tab_index + self.tabs_per_page < len(self.all_tabs):
            self.current_tab_index += self.tabs_per_page
            self.update_visible_tabs()
            self.update_arrow_states()

    def update_arrow_states(self):
        # Sol ok durumu
        self.left_arrow.setEnabled(self.current_tab_index > 0)
        
        # Sağ ok durumu
        self.right_arrow.setEnabled(
            self.current_tab_index + self.tabs_per_page < len(self.all_tabs)
        )

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