from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor
from datetime import datetime
import xlsxwriter
from .kaynak_yonetimi_ui import KaynakYonetimUI
from sample_data import RESOURCE_DATA

class KaynakYonetimTab(QWidget):
    """Kaynak Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.ui = KaynakYonetimUI()
        self.ui.setup_ui(self)
        self.setup_connections()
        self.distribution_history = []
        self.load_sample_resources()

    def setup_connections(self):
        """Signal-slot bağlantılarını kur"""
        self.ui.add_button.clicked.connect(self.add_resource)
        self.ui.search_input.textChanged.connect(self.filter_resources)
        self.ui.filter_combo.currentTextChanged.connect(self.filter_resources)
        self.ui.check_levels_btn.clicked.connect(self.check_resource_levels)
        self.ui.export_excel_btn.clicked.connect(lambda: self.export_resources("excel"))
        self.ui.resource_table.itemClicked.connect(self.show_resource_details)
        self.ui.distribute_button.clicked.connect(self.distribute_resources)

    def add_resource(self):
        """Yeni kaynak ekler"""
        name = self.ui.resource_name.text()
        resource_type = self.ui.resource_type.currentText()
        amount = self.ui.resource_amount.text()
        location = self.ui.resource_location.text()
        
        if name and amount and location:
            row_position = self.ui.resource_table.rowCount()
            self.ui.resource_table.insertRow(row_position)
            self.ui.resource_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.ui.resource_table.setItem(row_position, 1, QTableWidgetItem(resource_type))
            self.ui.resource_table.setItem(row_position, 2, QTableWidgetItem(amount))
            self.ui.resource_table.setItem(row_position, 3, QTableWidgetItem(location))
            self.ui.resource_table.setItem(row_position, 4, QTableWidgetItem("Hazır"))
            
            self.clear_form()
            QMessageBox.information(self, "Başarılı", "Kaynak başarıyla eklendi!")
        else:
            QMessageBox.warning(self, "Hata", "Lütfen gerekli alanları doldurun!")

    def clear_form(self):
        """Form alanlarını temizler"""
        self.ui.resource_name.clear()
        self.ui.resource_amount.clear()
        self.ui.resource_location.clear()

    def show_resource_details(self, item):
        """Seçilen kaynağın detaylarını gösterir"""
        row = item.row()
        name = self.ui.resource_table.item(row, 0).text()
        resource_type = self.ui.resource_table.item(row, 1).text()
        amount = self.ui.resource_table.item(row, 2).text()
        location = self.ui.resource_table.item(row, 3).text()
        
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
        self.ui.details_text.setText(details)

    def distribute_resources(self):
        """Kaynakları dağıtır ve geçmişi kaydeder"""
        amount = self.ui.dist_amount.text()
        location = self.ui.dist_location.text()
        priority = self.ui.dist_priority.currentText()
        
        if amount and location:
            # Seçili kaynağın miktarını güncelle
            selected_row = self.ui.resource_table.currentRow()
            if selected_row >= 0:
                current_amount = self.ui.resource_table.item(selected_row, 2).text()
                resource_name = self.ui.resource_table.item(selected_row, 0).text()
                
                # Dağıtım kaydını tut
                distribution = {
                    "resource": resource_name,
                    "amount": amount,
                    "location": location,
                    "priority": priority,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "Tamamlandı"
                }
                self.distribution_history.append(distribution)
                
                # Detay metnini güncelle
                self.show_resource_details(self.ui.resource_table.item(selected_row, 0))
                
                # Miktarı güncelle
                try:
                    # Mevcut miktarı sayıya çevir
                    current_numeric = float(''.join(filter(str.isdigit, current_amount)))
                    dist_numeric = float(''.join(filter(str.isdigit, amount)))
                    
                    # Yeni miktarı hesapla
                    new_amount = current_numeric - dist_numeric
                    
                    # Birimi al (Lt, Kg, Adet vs.)
                    unit = ''.join(filter(str.isalpha, current_amount))
                    
                    # Yeni miktarı tabloda güncelle
                    self.ui.resource_table.setItem(selected_row, 2, QTableWidgetItem(f"{new_amount} {unit}"))
                    
                    # Kritik seviye kontrolü
                    self.check_resource_levels()
                except ValueError:
                    pass  # Sayısal dönüşüm hatası durumunda işlem yapma
                
            QMessageBox.information(self, "Başarılı", 
                f"{amount} birim kaynak {location} konumuna {priority} öncelikle dağıtıma çıkarıldı!")
            self.ui.dist_amount.clear()
            self.ui.dist_location.clear()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen gerekli alanları doldurun!")

    def load_sample_resources(self):
        """Örnek kaynak verilerini yükler"""
        for data in RESOURCE_DATA:
            row_position = self.ui.resource_table.rowCount()
            self.ui.resource_table.insertRow(row_position)
            for column, value in enumerate(data):
                self.ui.resource_table.setItem(row_position, column, QTableWidgetItem(value))

    def filter_resources(self):
        """Kaynakları filtreler"""
        search_text = self.ui.search_input.text().lower()
        filter_type = self.ui.filter_combo.currentText()
        
        for row in range(self.ui.resource_table.rowCount()):
            show_row = True
            name = self.ui.resource_table.item(row, 0).text().lower()
            resource_type = self.ui.resource_table.item(row, 1).text()
            
            # Arama metni kontrolü
            if search_text and search_text not in name:
                show_row = False
            
            # Tür filtresi kontrolü
            if filter_type != "Tümü" and filter_type != resource_type:
                show_row = False
            
            self.ui.resource_table.setRowHidden(row, not show_row)

    def check_resource_levels(self):
        """Kaynak seviyelerini kontrol eder ve kritik seviyeleri işaretler"""
        for row in range(self.ui.resource_table.rowCount()):
            amount = self.ui.resource_table.item(row, 2).text()
            resource_type = self.ui.resource_table.item(row, 1).text()
            
            # Miktar değerini sayısal formata çevir
            numeric_amount = float(''.join(filter(str.isdigit, amount)))
            
            # Kaynak tipine göre kritik seviyeleri kontrol et
            if resource_type == "Su" and numeric_amount < 100:
                self.ui.resource_table.item(row, 4).setText("KRİTİK")
                self.ui.resource_table.item(row, 4).setBackground(QColor(255, 0, 0, 100))
            elif resource_type == "Gıda" and numeric_amount < 50:
                self.ui.resource_table.item(row, 4).setText("KRİTİK")
                self.ui.resource_table.item(row, 4).setBackground(QColor(255, 0, 0, 100))

    def export_resources(self, format="excel"):
        """Kaynak listesini Excel veya PDF olarak dışa aktarır"""
        if format == "excel":
            workbook = xlsxwriter.Workbook('resources/kaynak_raporu.xlsx')
            worksheet = workbook.add_worksheet()
            
            # Başlıkları yaz
            headers = ["Kaynak Adı", "Tür", "Miktar", "Konum", "Durum"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Verileri yaz
            for row in range(self.ui.resource_table.rowCount()):
                for col in range(self.ui.resource_table.columnCount()):
                    worksheet.write(row+1, col, self.ui.resource_table.item(row, col).text())
            
            workbook.close()