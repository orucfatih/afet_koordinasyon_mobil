from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QLineEdit, QComboBox,
                           QFrame, QSpacerItem, QSizePolicy, QHeaderView,
                           QTabWidget, QCalendarWidget)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QIcon, QFont
from styles.styles_dark import *
import os

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

class EquipmentManagementUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Tab widget oluştur
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3f55;
                background: #1e222f;
            }
            QTabBar::tab {
                background: #2c3e50;
                color: white;
                padding: 8px 20px;
                border: 1px solid #3a3f55;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #34495e;
                border-bottom: none;
            }
        """)

        # Ekipman Listesi Tab'ı
        equipment_list_tab = QWidget()
        equipment_layout = QVBoxLayout()

        # Başlık ve arama bölümü
        header_layout = QHBoxLayout()
        
        # Başlık
        title_label = QLabel("Ekipman Listesi")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        # Arama kutusu
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Ekipman ara...")
        self.search_box.setStyleSheet(SEARCH_BOX_STYLE)
        self.search_box.setFixedWidth(300)
        
        # Filtre combobox
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tüm Ekipmanlar", "Aktif", "Bakımda", "Onarımda"])
        self.filter_combo.setStyleSheet(COMBO_BOX_STYLE)
        self.filter_combo.setFixedWidth(150)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_box)
        header_layout.addWidget(self.filter_combo)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3a3f55;")
        
        # Butonlar bölümü
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Ekipman ekle butonu
        self.add_btn = QPushButton(" Yeni Ekipman")
        self.add_btn.setIcon(QIcon(get_icon_path('add-tool.png')))
        self.add_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        self.add_btn.setIconSize(QSize(20, 20))
        
        # Ekipman düzenle butonu
        self.edit_btn = QPushButton(" Düzenle")
        self.edit_btn.setIcon(QIcon(get_icon_path('edit-tool.png')))
        self.edit_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        self.edit_btn.setIconSize(QSize(20, 20))
        
        # Ekipman sil butonu
        self.delete_btn = QPushButton(" Sil")
        self.delete_btn.setIcon(QIcon(get_icon_path('delete-tool.png')))
        self.delete_btn.setStyleSheet(RED_BUTTON_STYLE)
        self.delete_btn.setIconSize(QSize(20, 20))
        
        # Excel'e Aktar butonu
        self.export_excel_btn = QPushButton(" Excel'e Aktar")
        self.export_excel_btn.setIcon(QIcon(get_icon_path('excel.png')))
        self.export_excel_btn.setStyleSheet(RESOURCE_BUTTON_STYLE)
        self.export_excel_btn.setIconSize(QSize(20, 20))
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.export_excel_btn)
        
        # Tablo widget'ı
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Konum ve Durum Detayı sütunları eklendi
        self.table.setHorizontalHeaderLabels([
            "Ekipman ID", "Ekipman Adı", "Tür", "Durum",
            "Son Kontrol", "Sonraki Kontrol", "Sorumlu Personel", 
            "Konum/Depo", "Durum Detayı"
        ])
        
        # Tablo özelliklerini ayarla
        self.table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Ekipman Listesi tab'ına bileşenleri ekle
        equipment_layout.addLayout(header_layout)
        equipment_layout.addWidget(line)
        equipment_layout.addLayout(button_layout)
        equipment_layout.addWidget(self.table)
        equipment_list_tab.setLayout(equipment_layout)
        
        # Bakım Takvimi Tab'ı
        maintenance_tab = QWidget()
        maintenance_layout = QVBoxLayout()
        
        # Takvim widget'ı
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #1e222f;
                color: white;
            }
            QCalendarWidget QTableView {
                background-color: #2c3e50;
                selection-background-color: #34495e;
                selection-color: white;
            }
            QCalendarWidget QMenu {
                background-color: #2c3e50;
                color: white;
            }
        """)
        
        # Yaklaşan bakımlar listesi
        upcoming_maintenance_label = QLabel("Yaklaşan Bakımlar")
        upcoming_maintenance_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        upcoming_maintenance_label.setStyleSheet("color: white;")
        
        self.upcoming_maintenance_table = QTableWidget()
        self.upcoming_maintenance_table.setColumnCount(4)
        self.upcoming_maintenance_table.setHorizontalHeaderLabels([
            "Ekipman", "Planlanan Tarih", "Tür", "Öncelik"
        ])
        self.upcoming_maintenance_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.upcoming_maintenance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        maintenance_layout.addWidget(self.calendar)
        maintenance_layout.addWidget(upcoming_maintenance_label)
        maintenance_layout.addWidget(self.upcoming_maintenance_table)
        maintenance_tab.setLayout(maintenance_layout)
        
        # Envanter Dağılımı Tab'ı
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout()
        
        # Depo/Lokasyon filtresi
        location_filter_layout = QHBoxLayout()
        location_label = QLabel("Depo/Lokasyon:")
        location_label.setStyleSheet("color: white;")
        self.location_combo = QComboBox()
        self.location_combo.addItems(["Tüm Lokasyonlar", "Ana Depo", "Mobil Depo 1", "Mobil Depo 2", "Saha"])
        self.location_combo.setStyleSheet(COMBO_BOX_STYLE)
        
        location_filter_layout.addWidget(location_label)
        location_filter_layout.addWidget(self.location_combo)
        location_filter_layout.addStretch()
        
        # Envanter tablosu
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "Lokasyon", "Toplam Ekipman", "Aktif", "Bakımda", "Kritik Seviye"
        ])
        self.inventory_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        inventory_layout.addLayout(location_filter_layout)
        inventory_layout.addWidget(self.inventory_table)
        inventory_tab.setLayout(inventory_layout)
        
        # Tab'ları ekle
        tab_widget.addTab(equipment_list_tab, "Ekipman Listesi")
        tab_widget.addTab(maintenance_tab, "Bakım Takvimi")
        tab_widget.addTab(inventory_tab, "Envanter Dağılımı")
        
        # Ana layout'a tab widget'ı ekle
        main_layout.addWidget(tab_widget)
        
        self.setLayout(main_layout)
