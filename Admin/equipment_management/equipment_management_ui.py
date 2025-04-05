from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QLineEdit, QComboBox,
                           QFrame, QSpacerItem, QSizePolicy, QHeaderView)
from PyQt5.QtCore import Qt, QSize
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

        # Başlık ve arama bölümü
        header_layout = QHBoxLayout()
        
        # Başlık
        title_label = QLabel("Ekipman Yönetimi")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Ekipman ID", "Ekipman Adı", "Tür", "Durum",
            "Son Kontrol", "Sorumlu Personel", "Ekip ID"
        ])
        
        # Tablo özelliklerini ayarla
        self.table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Ana layout'a bileşenleri ekle
        main_layout.addLayout(header_layout)
        main_layout.addWidget(line)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
