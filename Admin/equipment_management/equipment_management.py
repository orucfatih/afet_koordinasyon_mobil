from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QMessageBox, 
                           QDialog, QFormLayout, QDialogButtonBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from styles.styles_dark import *
from styles.styles_light import *
from sample_data import EQUIPMENT_DATA
import os
from .equipment_management_ui import EquipmentManagementUI
import xlsxwriter

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

class EquipmentManagementTab(EquipmentManagementUI):
    """Ekipman Yönetimi Sekmesi"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setup_connections()
        self.load_equipment_data()
        self.load_maintenance_data()
        self.load_inventory_data()

    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        self.add_btn.clicked.connect(self.add_equipment)
        self.edit_btn.clicked.connect(self.edit_equipment)
        self.delete_btn.clicked.connect(self.remove_equipment)
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        self.search_box.textChanged.connect(self.filter_equipment)
        self.filter_combo.currentTextChanged.connect(self.filter_equipment)
        self.location_combo.currentTextChanged.connect(self.filter_inventory)
        self.calendar.clicked.connect(self.show_maintenance_for_date)

    def export_to_excel(self):
        """Ekipman listesini Excel dosyasına aktarır"""
        try:
            # Dosya kaydetme dialogunu göster
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Dosyasını Kaydet",
                os.path.expanduser("~/ekipman_listesi.xlsx"),
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
            
            # Durum hücre formatları
            status_formats = {
                'Aktif': workbook.add_format({
                    'align': 'center',
                    'border': 1,
                    'bg_color': '#4CAF50',
                    'font_color': 'white'
                }),
                'Bakımda': workbook.add_format({
                    'align': 'center',
                    'border': 1,
                    'bg_color': '#FFA500',
                    'font_color': 'white'
                }),
                'Onarımda': workbook.add_format({
                    'align': 'center',
                    'border': 1,
                    'bg_color': '#f44336',
                    'font_color': 'white'
                })
            }
            
            # Başlıkları yaz
            headers = ["Ekipman ID", "Ekipman Adı", "Tür", "Durum",
                      "Son Kontrol", "Sorumlu Personel", "Ekip ID"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 15)  # Sütun genişliğini ayarla
            
            # Verileri yaz
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    cell_value = item.text() if item is not None else ""
                    
                    # Durum sütunu için özel format
                    if col == 3 and item is not None:  # Durum sütunu
                        format_to_use = status_formats.get(cell_value, cell_format)
                    else:
                        format_to_use = cell_format
                    
                    worksheet.write(row + 1, col, cell_value, format_to_use)
            
            workbook.close()
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Ekipman listesi başarıyla kaydedildi!\nDosya Konumu: {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Excel dosyası oluşturulurken bir hata oluştu:\n{str(e)}"
            )

    def load_equipment_data(self):
        """Örnek ekipman verilerini yükler"""
        self.table.setRowCount(0)
        
        for equipment in EQUIPMENT_DATA:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Ekipman verilerini ekle
            for col, data in enumerate(equipment):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu için renklendirme
                if col == 3:  # Durum sütunu
                    if data == "Aktif":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    elif data == "Bakımda":
                        item.setBackground(QBrush(QColor("#FFA500")))
                    else:  # Onarımda
                        item.setBackground(QBrush(QColor("#f44336")))
                
                self.table.setItem(row, col, item)
            
            # Varsayılan ekip ID'si ekle
            if self.parent and self.parent.team_list.rowCount() > 0:
                default_team_id = self.parent.team_list.item(0, 0).text()
                team_id_item = QTableWidgetItem(default_team_id)
                team_id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 6, team_id_item)
        
        self.table.resizeColumnsToContents()

    def load_maintenance_data(self):
        """Bakım verilerini yükle"""
        # Örnek bakım verileri
        maintenance_data = [
            ("Jeneratör A", "2024-04-15", "Periyodik Bakım", "Yüksek"),
            ("Kurtarma Vinci", "2024-04-18", "Yağ Değişimi", "Orta"),
            ("Su Pompası", "2024-04-20", "Kontrol", "Düşük"),
            ("İletişim Sistemi", "2024-04-22", "Yazılım Güncelleme", "Yüksek")
        ]
        
        self.upcoming_maintenance_table.setRowCount(len(maintenance_data))
        for row, data in enumerate(maintenance_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Öncelik sütunu için renklendirme
                if col == 3:  # Öncelik sütunu
                    if value == "Yüksek":
                        item.setBackground(QBrush(QColor("#f44336")))
                    elif value == "Orta":
                        item.setBackground(QBrush(QColor("#FFA500")))
                    else:  # Düşük
                        item.setBackground(QBrush(QColor("#4CAF50")))
                
                self.upcoming_maintenance_table.setItem(row, col, item)

    def load_inventory_data(self):
        """Envanter dağılım verilerini yükle"""
        # Örnek envanter verileri
        inventory_data = [
            ("Ana Depo", "150", "120", "20", "5"),
            ("Mobil Depo 1", "75", "60", "10", "3"),
            ("Mobil Depo 2", "75", "65", "8", "2"),
            ("Saha", "50", "45", "5", "0")
        ]
        
        self.inventory_table.setRowCount(len(inventory_data))
        for row, data in enumerate(inventory_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Kritik seviye için renklendirme
                if col == 4 and int(value) > 0:  # Kritik seviye sütunu
                    item.setBackground(QBrush(QColor("#f44336")))
                    item.setForeground(QBrush(QColor("white")))
                
                self.inventory_table.setItem(row, col, item)

    def filter_equipment(self):
        """Ekipmanları arama kutusuna ve filtreye göre filtrele"""
        search_text = self.search_box.text().lower()
        filter_status = self.filter_combo.currentText()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Arama metnine göre filtrele
            if search_text:
                text_match = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                show_row = text_match
            
            # Durum filtresine göre filtrele
            if show_row and filter_status != "Tüm Ekipmanlar":
                status_item = self.table.item(row, 3)
                if status_item and status_item.text() != filter_status:
                    show_row = False
            
            self.table.setRowHidden(row, not show_row)

    def add_equipment(self):
        """Yeni ekipman eklemek için dialog açar"""
        dialog = EquipmentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            for col, value in enumerate(dialog.get_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                if col == 3:  # Durum sütunu
                    if value == "Aktif":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    elif value == "Bakımda":
                        item.setBackground(QBrush(QColor("#FFA500")))
                    else:  # Onarımda
                        item.setBackground(QBrush(QColor("#f44336")))
                
                self.table.setItem(row, col, item)

    def edit_equipment(self):
        """Seçili ekipmanı düzenler"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir ekipman seçin!")
            return
        
        dialog = EquipmentDialog(self)
        dialog.set_values([
            self.table.item(current_row, col).text()
            for col in range(self.table.columnCount())
        ])
        
        if dialog.exec_() == QDialog.Accepted:
            for col, value in enumerate(dialog.get_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                if col == 3:  # Durum sütunu
                    if value == "Aktif":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    elif value == "Bakımda":
                        item.setBackground(QBrush(QColor("#FFA500")))
                    else:  # Onarımda
                        item.setBackground(QBrush(QColor("#f44336")))
                
                self.table.setItem(current_row, col, item)

    def remove_equipment(self):
        """Seçili ekipmanı siler"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ekipman seçin!")
            return
        
        reply = QMessageBox.question(
            self,
            'Ekipman Silme Onayı',
            'Seçili ekipmanı silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.table.removeRow(current_row)

    def show_maintenance_for_date(self, date):
        """Seçili tarih için bakım planlarını göster"""
        selected_date = date.toString("yyyy-MM-dd")
        
        # Seçili tarihe ait bakımları filtrele
        maintenance_data = [
            ("Jeneratör A", "2024-04-15", "Periyodik Bakım", "Yüksek"),
            ("Kurtarma Vinci", "2024-04-18", "Yağ Değişimi", "Orta"),
            ("Su Pompası", "2024-04-20", "Kontrol", "Düşük"),
            ("İletişim Sistemi", "2024-04-22", "Yazılım Güncelleme", "Yüksek")
        ]
        
        filtered_data = [data for data in maintenance_data if data[1] == selected_date]
        
        self.upcoming_maintenance_table.setRowCount(len(filtered_data))
        for row, data in enumerate(filtered_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                if col == 3:  # Öncelik sütunu
                    if value == "Yüksek":
                        item.setBackground(QBrush(QColor("#f44336")))
                    elif value == "Orta":
                        item.setBackground(QBrush(QColor("#FFA500")))
                    else:  # Düşük
                        item.setBackground(QBrush(QColor("#4CAF50")))
                
                self.upcoming_maintenance_table.setItem(row, col, item)

    def filter_inventory(self):
        """Envanter verilerini lokasyona göre filtrele"""
        selected_location = self.location_combo.currentText()
        
        for row in range(self.inventory_table.rowCount()):
            location_item = self.inventory_table.item(row, 0)
            if location_item:
                should_show = (selected_location == "Tüm Lokasyonlar" or 
                             location_item.text() == selected_location)
                self.inventory_table.setRowHidden(row, not should_show)

class EquipmentDialog(QDialog):
    """Ekipman ekleme/düzenleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Ekipman Bilgileri")
        self.setFixedSize(400, 400)
        
        layout = QFormLayout()
        
        # Form alanları
        self.equipment_id = QLineEdit()
        self.equipment_name = QLineEdit()
        self.equipment_type = QComboBox()
        self.equipment_type.addItems([
            "Kurtarma Ekipmanı", "Arama Ekipmanı", "Güç Ekipmanı",
            "Sağlık Ekipmanı", "Yangın Ekipmanı", "İletişim Ekipmanı",
            "Su Tahliye", "Diğer"
        ])
        
        self.status = QComboBox()
        self.status.addItems(["Aktif", "Bakımda", "Onarımda"])
        
        self.last_check = QLineEdit()
        self.responsible = QLineEdit()
        self.team_id = QLineEdit()
        
        # Form alanlarını ekle
        layout.addRow("Ekipman ID:", self.equipment_id)
        layout.addRow("Ekipman Adı:", self.equipment_name)
        layout.addRow("Tür:", self.equipment_type)
        layout.addRow("Durum:", self.status)
        layout.addRow("Son Kontrol:", self.last_check)
        layout.addRow("Sorumlu Personel:", self.responsible)
        layout.addRow("Ekip ID:", self.team_id)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        """Form verilerini doğrula ve kaydet"""
        if not all([
            self.equipment_id.text(),
            self.equipment_name.text(),
            self.last_check.text(),
            self.responsible.text(),
            self.team_id.text()
        ]):
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        self.accept()

    def get_values(self):
        """Dialog form değerlerini liste olarak döndür"""
        return [
            self.equipment_id.text(),
            self.equipment_name.text(),
            self.equipment_type.currentText(),
            self.status.currentText(),
            self.last_check.text(),
            self.responsible.text(),
            self.team_id.text()
        ]

    def set_values(self, values):
        """Dialog form alanlarını verilen değerlerle doldur"""
        self.equipment_id.setText(values[0])
        self.equipment_name.setText(values[1])
        self.equipment_type.setCurrentText(values[2])
        self.status.setCurrentText(values[3])
        self.last_check.setText(values[4])
        self.responsible.setText(values[5])
        self.team_id.setText(values[6])
