from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                          QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QMessageBox, 
                          QDialog, QFormLayout, QDialogButtonBox, QFileDialog, QInputDialog, 
                          QCalendarWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QBrush, QColor, QIcon, QIntValidator
import os
import xlsxwriter

class EquipmentListTab:
    """Ekipman Listesi sekmesi için işlemler"""
    def __init__(self, parent):
        self.parent = parent
        self.table = parent.table
        self.search_box = parent.search_box
        self.filter_combo = parent.filter_combo
        self.equipment_tree = parent.equipment_tree
        self.add_btn = parent.add_btn
        self.edit_btn = parent.edit_btn
        self.delete_btn = parent.delete_btn
        self.export_excel_btn = parent.export_excel_btn
        self.send_maintenance_btn = parent.send_maintenance_btn
        self.remove_maintenance_btn = parent.remove_maintenance_btn
        
        # Bağlantıları kur
        self.setup_connections()
        
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        self.add_btn.clicked.connect(self.add_equipment)
        self.edit_btn.clicked.connect(self.edit_equipment)
        self.delete_btn.clicked.connect(self.remove_equipment)
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        self.search_box.textChanged.connect(self.filter_equipment)
        self.filter_combo.currentTextChanged.connect(self.filter_equipment)
        self.equipment_tree.itemClicked.connect(self.filter_by_category)
        self.send_maintenance_btn.clicked.connect(lambda: self.parent.maintenance_tab.send_to_maintenance())
        self.remove_maintenance_btn.clicked.connect(lambda: self.parent.maintenance_tab.remove_from_maintenance())
        
    def filter_by_category(self, item):
        """Ekipman ağacındaki seçime göre ekipmanları filtrele"""
        category = item.text(0)
        parent = item.parent()
        
        # Arama kutusunu ve filtre combobox'ını temizle
        self.search_box.clear()
        self.filter_combo.setCurrentText("Tüm Ekipmanlar")
        
        # Üst kategori ve alt kategorisini birleştir
        if parent:
            full_category = f"{parent.text(0)} - {category}"
        else:
            full_category = category
        
        # Tüm satırları gez ve eşleşen türleri göster
        for row in range(self.table.rowCount()):
            show_row = False
            type_item = self.table.item(row, 2)  # Tür sütunu
            if type_item:
                equipment_type = type_item.text()
                
                # Ana kategori seçildiyse
                if not parent and equipment_type == category:
                    show_row = True
                # Alt kategori seçildiyse (daha detaylı filtreleme gerekiyor)
                elif parent:
                    # Bu kısımda gerçek uygulamada alt kategori bilgisi
                    # veritabanında tutulacaktır. Burada basit bir kontrol yapılıyor.
                    if category in equipment_type or parent.text(0) == equipment_type:
                        show_row = True
            
            self.table.setRowHidden(row, not show_row)
    
    def export_to_excel(self):
        """Ekipman listesini Excel dosyasına aktarır"""
        try:
            # Dosya kaydetme dialogunu göster
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent,
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
                      "Son Kontrol", "Sonraki Kontrol", "Sorumlu Personel", 
                      "Konum/Depo", "Durum Detayı"]
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
                self.parent,
                "Başarılı",
                f"Ekipman listesi başarıyla kaydedildi!\nDosya Konumu: {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Hata",
                f"Excel dosyası oluşturulurken bir hata oluştu:\n{str(e)}"
            )
    
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
        from .equipment_dialogs import EquipmentDialog
        dialog = EquipmentDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            values = dialog.get_values()
            
            # Ekipman verilerini tabloya ekle
            for col, value in enumerate(values):
                if col < self.table.columnCount():  # Tablodaki sütun sayısını kontrol et
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
        from .equipment_dialogs import EquipmentDialog
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.parent, "Uyarı", "Lütfen düzenlemek için bir ekipman seçin!")
            return
        
        # Mevcut verileri al
        values = []
        for col in range(self.table.columnCount()):
            item = self.table.item(current_row, col)
            if item:
                values.append(item.text())
            else:
                values.append("")
        
        dialog = EquipmentDialog(self.parent)
        dialog.set_values(values)
        
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.get_values()
            
            # Değişiklikleri tabloya yansıt
            for col, value in enumerate(values):
                if col < self.table.columnCount():  # Tablodaki sütun sayısını kontrol et
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
            QMessageBox.warning(self.parent, "Uyarı", "Lütfen silmek için bir ekipman seçin!")
            return
        
        reply = QMessageBox.question(
            self.parent,
            'Ekipman Silme Onayı',
            'Seçili ekipmanı silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.table.removeRow(current_row)
            
    def add_item_to_table(self, row, col, data):
        """Tabloya bir hücre ekler ve formatlar"""
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
        
        # Varsayılan ekip ID'si ekle (eğer son sütuna geldiysek)
        if col == self.table.columnCount() - 1 and self.parent.parent and hasattr(self.parent.parent, 'team_list') and self.parent.parent.team_list.rowCount() > 0:
            team_id_item = QTableWidgetItem(self.parent.parent.team_list.item(0, 0).text())
            team_id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, team_id_item)  # Ekip ID sütunu 