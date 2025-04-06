from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtGui import QColor
from datetime import datetime
import xlsxwriter
import os
from .kaynak_yonetimi_ui import KaynakYonetimUI
from .simulate import SimulationDialog
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
        self.ui.simulate_btn.clicked.connect(self.show_simulation_dialog)
        self.ui.export_excel_btn.clicked.connect(self.export_resources)
        self.ui.resource_table.itemClicked.connect(self.show_resource_details)
        self.ui.distribute_button.clicked.connect(self.distribute_resources)

    def show_simulation_dialog(self):
        """Simülasyon penceresini gösterir"""
        dialog = SimulationDialog(self)
        dialog.exec_()

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
                    if new_amount < 100:
                        self.ui.resource_table.item(selected_row, 4).setText("KRİTİK")
                        self.ui.resource_table.item(selected_row, 4).setBackground(QColor(255, 0, 0, 100))
                    
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

    def export_resources(self):
        """Kaynak listesini Excel dosyasına aktarır"""
        try:
            # Dosya kaydetme dialogunu göster
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Dosyasını Kaydet",
                os.path.expanduser("~/kaynak_listesi.xlsx"),
                "Excel Dosyaları (*.xlsx);;Tüm Dosyalar (*)"
            )
            
            if not file_path:  # Kullanıcı iptal ettiyse
                return
                
            # Dosya uzantısını kontrol et ve gerekirse ekle
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # Excel dosyasını oluştur
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()
            
            # Başlık formatı
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2c3e50',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            
            # Hücre formatı
            cell_format = workbook.add_format({
                'align': 'center',
                'border': 1
            })
            
            # Başlıkları yaz
            headers = ["Kaynak Adı", "Tür", "Miktar", "Konum", "Durum"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 15)  # Sütun genişliğini ayarla
            
            # Verileri yaz
            for row in range(self.ui.resource_table.rowCount()):
                for col in range(self.ui.resource_table.columnCount()):
                    item = self.ui.resource_table.item(row, col)
                    cell_value = item.text() if item is not None else ""
                    worksheet.write(row + 1, col, cell_value, cell_format)
            
            workbook.close()
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Kaynak listesi başarıyla kaydedildi!\nDosya Konumu: {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Excel dosyası oluşturulurken bir hata oluştu:\n{str(e)}"
            )