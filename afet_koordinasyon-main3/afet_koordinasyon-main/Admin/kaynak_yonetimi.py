from PyQt5.QtWidgets import (QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, 
                           QTextEdit, QComboBox,
                           QGroupBox, QLineEdit,
                           QFormLayout, QTableWidget, QTableWidgetItem, 
                           QMessageBox)
from styles import *
from PyQt5.QtGui import QIcon

class KaynakYonetimTab(QWidget):
    """Kaynak Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        
        # Sol Panel - Kaynak Listesi ve Ekleme
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Kaynak Ekleme Formu
        add_resource_group = QGroupBox("Kaynak Ekle")
        form_layout = QFormLayout()
        
        self.resource_name = QLineEdit()
        self.resource_type = QComboBox()
        self.resource_type.addItems(["Su", "Gıda", "İlaç", "Çadır", "Battaniye", "Diğer"])
        self.resource_amount = QLineEdit()
        self.resource_location = QLineEdit()
        
        form_layout.addRow("Kaynak Adı:", self.resource_name)
        form_layout.addRow("Kaynak Tipi:", self.resource_type)
        form_layout.addRow("Miktar:", self.resource_amount)
        form_layout.addRow("Konum:", self.resource_location)
        
        add_button = QPushButton(" Kaynak Ekle")
        add_button.setStyleSheet(GREEN_BUTTON_STYLE)
        add_button.setIcon(QIcon('icons/add1.png'))
        add_button.clicked.connect(self.add_resource)
        form_layout.addRow(add_button)
        
        add_resource_group.setLayout(form_layout)
        
        # Kaynak Listesi
        resource_list_group = QGroupBox("Kaynak Listesi")
        list_layout = QVBoxLayout()
        
        self.resource_table = QTableWidget()
        self.resource_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.resource_table.setColumnCount(5)
        self.resource_table.setHorizontalHeaderLabels(["Kaynak Adı", "Tür", "Miktar", "Konum", "Durum"])
        self.resource_table.itemClicked.connect(self.show_resource_details)
        
        list_layout.addWidget(self.resource_table)
        resource_list_group.setLayout(list_layout)
        
        left_layout.addWidget(add_resource_group)
        left_layout.addWidget(resource_list_group)
        
        # Sağ Panel - Kaynak Detayları ve Dağıtım
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Kaynak Detayları
        details_group = QGroupBox("Kaynak Detayları")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        
        # Dağıtım Paneli
        distribution_group = QGroupBox("Kaynak Dağıtımı")
        dist_layout = QFormLayout()
        
        self.dist_amount = QLineEdit()
        self.dist_location = QLineEdit()
        self.dist_priority = QComboBox()
        self.dist_priority.addItems(["Düşük", "Orta", "Yüksek", "Acil"])
        
        dist_layout.addRow("Dağıtılacak Miktar:", self.dist_amount)
        dist_layout.addRow("Hedef Konum:", self.dist_location)
        dist_layout.addRow("Öncelik:", self.dist_priority)
        
        distribute_button = QPushButton(" Dağıtımı Başlat")
        distribute_button.setStyleSheet(BUTTON_STYLE)
        distribute_button.setIcon(QIcon('icons/play.png'))
        distribute_button.clicked.connect(self.distribute_resources)
        dist_layout.addRow(distribute_button)
        
        distribution_group.setLayout(dist_layout)
        
        right_layout.addWidget(details_group)
        right_layout.addWidget(distribution_group)
        
        # Ana layout'a panelleri ekleme
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        self.setLayout(layout)
        
        # Örnek verileri yükle
        self.load_sample_resources()

    def add_resource(self):
        """Yeni kaynak ekler"""
        name = self.resource_name.text()
        resource_type = self.resource_type.currentText()
        amount = self.resource_amount.text()
        location = self.resource_location.text()
        
        if name and amount and location:
            row_position = self.resource_table.rowCount()
            self.resource_table.insertRow(row_position)
            self.resource_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.resource_table.setItem(row_position, 1, QTableWidgetItem(resource_type))
            self.resource_table.setItem(row_position, 2, QTableWidgetItem(amount))
            self.resource_table.setItem(row_position, 3, QTableWidgetItem(location))
            self.resource_table.setItem(row_position, 4, QTableWidgetItem("Hazır"))
            
            self.clear_form()
            QMessageBox.information(self, "Başarılı", "Kaynak başarıyla eklendi!")
        else:
            QMessageBox.warning(self, "Hata", "Lütfen gerekli alanları doldurun!")

    def clear_form(self):
        """Form alanlarını temizler"""
        self.resource_name.clear()
        self.resource_amount.clear()
        self.resource_location.clear()

    def show_resource_details(self, item):
        """Seçilen kaynağın detaylarını gösterir"""
        row = item.row()
        name = self.resource_table.item(row, 0).text()
        resource_type = self.resource_table.item(row, 1).text()
        amount = self.resource_table.item(row, 2).text()
        location = self.resource_table.item(row, 3).text()
        
        details = f"""Kaynak Detayları:
        
Ad: {name}
Tür: {resource_type}
Miktar: {amount}
Konum: {location}

Dağıtım Geçmişi:
- 15:30 - 100 birim gönderildi (Merkez)
- 14:45 - 50 birim gönderildi (Doğu bölgesi)
- 13:20 - 200 birim teslim alındı

Stok Durumu: Yeterli
Son Güncelleme: 15:30
"""
        self.details_text.setText(details)

    def distribute_resources(self):
        """Kaynakları dağıtır"""
        amount = self.dist_amount.text()
        location = self.dist_location.text()
        priority = self.dist_priority.currentText()
        
        if amount and location:
            QMessageBox.information(self, "Başarılı", 
                f"{amount} birim kaynak {location} konumuna {priority} öncelikle dağıtıma çıkarıldı!")
            self.dist_amount.clear()
            self.dist_location.clear()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen gerekli alanları doldurun!")

    def load_sample_resources(self):
        """Örnek kaynak verilerini yükler"""
        sample_data = [
            ["İçme Suyu", "Su", "1000 Lt", "Ana Depo", "Hazır"],
            ["Kuru Gıda", "Gıda", "500 Kg", "Batı Deposu", "Hazır"],
            ["Ateş Düşürücü", "İlaç", "1000 Kutu", "Sağlık Deposu", "Hazır"],
            ["Kışlık Çadır", "Çadır", "100 Adet", "Doğu Deposu", "Hazır"]
        ]
        
        for data in sample_data:
            row_position = self.resource_table.rowCount()
            self.resource_table.insertRow(row_position)
            for column, value in enumerate(data):
                self.resource_table.setItem(row_position, column, QTableWidgetItem(value))