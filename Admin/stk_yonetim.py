from PyQt5.QtWidgets import (QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, 
                           QTextEdit, QComboBox,
                           QGroupBox, QLineEdit,
                           QFormLayout, QTableWidget, QTableWidgetItem, 
                           QMessageBox, )
from styles import *
from PyQt5.QtGui import QIcon, QColor


class STKYonetimTab(QWidget):
    """STK Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        
        # Sol Panel - STK Listesi ve Ekleme
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # STK Ekleme Formu
        add_ngo_group = QGroupBox("STK Ekle")
        form_layout = QFormLayout()
        
        self.ngo_name = QLineEdit()
        self.ngo_type = QComboBox()
        self.ngo_type.addItems(["Arama Kurtarma", "Sağlık", "Gıda", "Barınma", "Lojistik"])
        self.ngo_contact = QLineEdit()
        self.ngo_capacity = QLineEdit()
        self.ngo_region = QLineEdit()
        
        form_layout.addRow("STK Adı:", self.ngo_name)
        form_layout.addRow("STK Türü:", self.ngo_type)
        form_layout.addRow("İletişim:", self.ngo_contact)
        form_layout.addRow("Kapasite:", self.ngo_capacity)
        form_layout.addRow("Faaliyet Bölgesi:", self.ngo_region)
        
        add_button = QPushButton("STK Ekle")
        add_button.setStyleSheet(GREEN_BUTTON_STYLE)
        add_button.setIcon(QIcon('icons/add1.png'))
        add_button.clicked.connect(self.add_ngo)
        form_layout.addRow(add_button)
        
        add_ngo_group.setLayout(form_layout)
        
        # STK Listesi
        ngo_list_group = QGroupBox("STK Listesi")
        list_layout = QVBoxLayout()
        
        self.ngo_table = QTableWidget()
        self.ngo_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.ngo_table.setColumnCount(6)
        self.ngo_table.setHorizontalHeaderLabels(["STK Adı", "Tür", "İletişim", "Kapasite", "Bölge", "Durum"])
        self.ngo_table.itemClicked.connect(self.show_ngo_details)
        
        list_layout.addWidget(self.ngo_table)
        ngo_list_group.setLayout(list_layout)
        
        left_layout.addWidget(add_ngo_group)
        left_layout.addWidget(ngo_list_group)
        
        # Sağ Panel - STK Detayları ve İletişim
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # STK Detayları
        details_group = QGroupBox("STK Detayları")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        
        # İletişim Paneli
        communication_group = QGroupBox("İletişim Paneli")
        comm_layout = QVBoxLayout()
        
        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText("Mesajınızı yazın...")
        
        send_button = QPushButton("Mesaj Gönder")
        send_button.setStyleSheet(GREEN_BUTTON_STYLE)
        send_button.setIcon(QIcon('icons/paper/plane.png'))
        send_button.clicked.connect(self.send_message)
        
        comm_layout.addWidget(self.message_text)
        comm_layout.addWidget(send_button)
        
        communication_group.setLayout(comm_layout)
        
        right_layout.addWidget(details_group)
        right_layout.addWidget(communication_group)
        
        # Ana layout'a panelleri ekleme
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        self.setLayout(layout)
        
        # Örnek verileri yükle
        self.load_sample_ngos()

    def add_ngo(self):
        """Yeni STK ekler"""
        name = self.ngo_name.text()
        ngo_type = self.ngo_type.currentText()
        contact = self.ngo_contact.text()
        capacity = self.ngo_capacity.text()
        region = self.ngo_region.text()
        
        if name and contact:
            row_position = self.ngo_table.rowCount()
            self.ngo_table.insertRow(row_position)
            self.ngo_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.ngo_table.setItem(row_position, 1, QTableWidgetItem(ngo_type))
            self.ngo_table.setItem(row_position, 2, QTableWidgetItem(contact))
            self.ngo_table.setItem(row_position, 3, QTableWidgetItem(capacity))
            self.ngo_table.setItem(row_position, 4, QTableWidgetItem(region))
            self.ngo_table.setItem(row_position, 5, QTableWidgetItem("Aktif"))
            
            self.clear_form()
            QMessageBox.information(self, "Başarılı", "STK başarıyla eklendi!")
        else:
            QMessageBox.warning(self, "Hata", "Lütfen gerekli alanları doldurun!")

    def clear_form(self):
        """Form alanlarını temizler"""
        self.ngo_name.clear()
        self.ngo_contact.clear()
        self.ngo_capacity.clear()
        self.ngo_region.clear()

    def show_ngo_details(self, item):
        """Seçilen STK'nın detaylarını gösterir"""
        row = item.row()
        name = self.ngo_table.item(row, 0).text()
        ngo_type = self.ngo_table.item(row, 1).text()
        contact = self.ngo_table.item(row, 2).text()
        capacity = self.ngo_table.item(row, 3).text()
        region = self.ngo_table.item(row, 4).text()
        
        details = f"""STK Detayları:
        
İsim: {name}
Tür: {ngo_type}
İletişim: {contact}
Kapasite: {capacity}
Faaliyet Bölgesi: {region}

Aktif Görevler:
- Arama kurtarma operasyonu (Merkez)
- Gıda dağıtımı (Doğu bölgesi)

Son Aktiviteler:
- 15:30 - Saha raporu gönderildi
- 14:45 - Yeni ekip göreve başladı
- 13:20 - Malzeme temini tamamlandı
"""
        self.details_text.setText(details)

    def send_message(self):
        """STK'ya mesaj gönderir"""
        message = self.message_text.toPlainText()
        if message:
            QMessageBox.information(self, "Başarılı", "Mesaj gönderildi!")
            self.message_text.clear()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen bir mesaj yazın!")

    def load_sample_ngos(self):
        """Örnek STK verilerini yükler"""
        sample_data = [
            ["AKUT", "Arama Kurtarma", "0532xxx xxxx", "50 personel", "Tüm Türkiye", "Aktif"],
            ["Kızılay", "Gıda", "0533xxx xxxx", "200 personel", "Tüm Türkiye", "Aktif"],
            ["Sağlık Gönüllüleri", "Sağlık", "0535xxx xxxx", "30 personel", "Marmara", "Aktif"]
        ]
        
        for data in sample_data:
            row_position = self.ngo_table.rowCount()
            self.ngo_table.insertRow(row_position)
            for column, value in enumerate(data):
                self.ngo_table.setItem(row_position, column, QTableWidgetItem(value))