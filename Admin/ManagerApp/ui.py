from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox,
                            QToolButton, QHBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from styles.styles_dark import *
from styles.styles_light import *
from utils import get_icon_path

class YonetimPaneli(QMainWindow):
    """Yönetim Paneli Ana Penceresi"""
    def __init__(self, initial_theme='dark'):
        super().__init__()
        self.current_theme = initial_theme
        self.current_tab_index = 0
        self.tabs_per_page = 7
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Yönetim Paneli")
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
        
        # Sağ ok butonu için corner widget
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
        right_layout.addWidget(self.right_arrow)
        
        # Corner widget'ları tab widget'a ekle
        self.tabs.setCornerWidget(left_corner, Qt.TopLeftCorner)
        self.tabs.setCornerWidget(right_corner, Qt.TopRightCorner)
        
        main_layout.addWidget(self.tabs)
        
        # Tüm sekmeleri liste olarak tut
        self.all_tabs = [
            ("Sistem Yönetimi", QWidget()),  # Placeholder, gerçek tab sınıfları eklenecek
            ("Kullanıcı Yönetimi", QWidget()),
            ("Yetkilendirme", QWidget()),
            ("Log Kayıtları", QWidget()),
            ("Sistem Ayarları", QWidget()),
            ("Veri Yönetimi", QWidget()),
            ("Raporlama", QWidget()),
            ("API Yönetimi", QWidget()),
            ("Güvenlik", QWidget()),
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
            "Yönetim panelini kapatmak istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            event.ignore()
        else:
            event.accept() 