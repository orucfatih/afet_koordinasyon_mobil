from PyQt5.QtWidgets import (QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, 
                           QTextEdit, QComboBox,
                           QGroupBox, QLineEdit,
                           QFormLayout, QTableWidget,
                           QLabel, QSpacerItem,
                           QSizePolicy)
from PyQt5.QtCore import Qt
from styles_dark import *
from styles_light import *

class KaynakYonetimUI:
    def setup_ui(self, widget):
        # Ana layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Sol Panel
        self.setup_left_panel()
        
        # Sağ Panel
        self.setup_right_panel()
        
        # Panel genişliklerini ayarla
        self.left_panel.setMinimumWidth(600)  # Sol panel minimum genişlik
        self.right_panel.setMinimumWidth(400)  # Sağ panel minimum genişlik
        
        # Ana layout'a panelleri ekle
        self.main_layout.addWidget(self.left_panel, 60)
        self.main_layout.addWidget(self.right_panel, 40)
        
        widget.setLayout(self.main_layout)

    def setup_left_panel(self):
        """Sol panel bileşenlerini oluşturur"""
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setSpacing(15)
        
        # Arama ve Filtreleme Grubu
        self.setup_search_group()
        
        # İşlem Butonları
        self.setup_action_buttons()
        
        # Kaynak Listesi
        self.setup_resource_table()
        
        # Kaynak Ekleme Formu
        self.setup_add_resource_form()

    def setup_search_group(self):
        """Arama ve filtreleme bölümünü oluşturur"""
        search_widget = QWidget()
        search_widget.setStyleSheet(SEARCH_WIDGET_STYLE)
        
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kaynak ara...")
        self.search_input.setStyleSheet(RESOURCE_INPUT_STYLE)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tümü", "Su", "Gıda", "İlaç", "Çadır", "Battaniye", "Diğer"])
        self.filter_combo.setStyleSheet(COMBO_BOX_STYLE)
        
        search_layout.addWidget(self.search_input, 2)
        search_layout.addWidget(self.filter_combo, 1)
        
        search_widget.setLayout(search_layout)
        self.left_layout.addWidget(search_widget)

    def setup_action_buttons(self):
        """İşlem butonlarını oluşturur"""
        buttons_layout = QHBoxLayout()
        
        self.check_levels_btn = QPushButton("Kritik Seviyeleri Kontrol Et")
        self.export_excel_btn = QPushButton("Excel'e Aktar")
        
        for btn in [self.check_levels_btn, self.export_excel_btn]:
            btn.setStyleSheet(RESOURCE_BUTTON_STYLE)
            buttons_layout.addWidget(btn)
        
        self.left_layout.addLayout(buttons_layout)

    def setup_resource_table(self):
        """Kaynak tablosunu oluşturur"""
        self.resource_table = QTableWidget()
        self.resource_table.setStyleSheet(RESOURCE_TABLE_STYLE)
        
        # Tablo ayarları
        self.resource_table.setColumnCount(5)
        self.resource_table.setHorizontalHeaderLabels(["Kaynak Adı", "Tür", "Miktar", "Konum", "Durum"])
        self.resource_table.horizontalHeader().setStretchLastSection(True)
        self.resource_table.setAlternatingRowColors(True)
        
        # Sütun genişliklerini ayarla
        self.resource_table.setColumnWidth(0, 150)  # Kaynak Adı
        self.resource_table.setColumnWidth(1, 100)  # Tür
        self.resource_table.setColumnWidth(2, 100)  # Miktar
        self.resource_table.setColumnWidth(3, 150)  # Konum
        self.resource_table.setColumnWidth(4, 100)  # Durum
        
        # Minimum yükseklik ayarla
        self.resource_table.setMinimumHeight(300)
        
        self.left_layout.addWidget(self.resource_table)

    def setup_add_resource_form(self):
        """Kaynak ekleme formunu oluşturur"""
        add_group = QGroupBox("Yeni Kaynak Ekle")
        add_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(20, 20, 20, 20)  # Form kenar boşlukları
        
        # Form alanları için minimum genişlik
        min_width = 200
        
        # Form alanları
        self.resource_name = QLineEdit()
        self.resource_name.setMinimumWidth(min_width)
        
        self.resource_type = QComboBox()
        self.resource_type.setMinimumWidth(min_width)
        self.resource_type.addItems(["Su", "Gıda", "İlaç", "Çadır", "Battaniye", "Diğer"])
        
        self.resource_amount = QLineEdit()
        self.resource_amount.setMinimumWidth(min_width)
        
        self.resource_location = QLineEdit()
        self.resource_location.setMinimumWidth(min_width)
        
        # Form alanları stilleri
        for widget in [self.resource_name, self.resource_amount, self.resource_location]:
            widget.setStyleSheet(RESOURCE_INPUT_STYLE)
        
        self.resource_type.setStyleSheet(COMBO_BOX_STYLE)
        
        # Form alanlarını ekle
        form_layout.addRow("Kaynak Adı:", self.resource_name)
        form_layout.addRow("Kaynak Tipi:", self.resource_type)
        form_layout.addRow("Miktar:", self.resource_amount)
        form_layout.addRow("Konum:", self.resource_location)
        
        # Ekle butonu
        self.add_button = QPushButton("✚ Kaynak Ekle")
        self.add_button.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        form_layout.addRow(self.add_button)
        
        add_group.setLayout(form_layout)
        self.left_layout.addWidget(add_group)

    def setup_right_panel(self):
        """Sağ panel bileşenlerini oluşturur"""
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setSpacing(15)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Kaynak Detayları
        details_group = QGroupBox("Kaynak Detayları")
        details_group.setMinimumHeight(600)
        details_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet(RESOURCE_TEXT_EDIT_STYLE)
        
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        
        # Boşluk ekle
        self.right_layout.addWidget(details_group)
        self.right_layout.addStretch(1)  # Esnek boşluk ekle
        
        # Dağıtım Paneli
        distribution_group = QGroupBox("Kaynak Dağıtımı")
        distribution_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        
        dist_layout = QFormLayout()
        dist_layout.setSpacing(10)
        dist_layout.setContentsMargins(20, 20, 20, 20)
        
        # Form alanları için minimum genişlik
        min_width = 200
        
        self.dist_amount = QLineEdit()
        self.dist_amount.setMinimumWidth(min_width)
        
        self.dist_location = QLineEdit()
        self.dist_location.setMinimumWidth(min_width)
        
        self.dist_priority = QComboBox()
        self.dist_priority.setMinimumWidth(min_width)
        self.dist_priority.addItems(["Düşük", "Orta", "Yüksek", "Acil"])
        
        for widget in [self.dist_amount, self.dist_location]:
            widget.setStyleSheet(RESOURCE_INPUT_STYLE)
        
        self.dist_priority.setStyleSheet(COMBO_BOX_STYLE)
        
        dist_layout.addRow("Dağıtılacak Miktar:", self.dist_amount)
        dist_layout.addRow("Hedef Konum:", self.dist_location)
        dist_layout.addRow("Öncelik:", self.dist_priority)
        
        self.distribute_button = QPushButton("🚚 Dağıtımı Başlat")
        self.distribute_button.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        dist_layout.addRow(self.distribute_button)
        
        distribution_group.setLayout(dist_layout)
        self.right_layout.addWidget(distribution_group) 