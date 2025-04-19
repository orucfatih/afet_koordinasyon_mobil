from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QMessageBox, 
                           QDialog, QFormLayout, QDialogButtonBox, QFileDialog, QInputDialog, 
                           QCalendarWidget, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QBrush, QColor, QIcon, QIntValidator
from styles.styles_dark import *
from styles.styles_light import *
from sample_data import EQUIPMENT_DATA
import os
from .equipment_management_ui import EquipmentManagementUI
import xlsxwriter
from .equipment_list_tab import EquipmentListTab
from .maintenance_tab import MaintenanceTab
from .inventory_tab import InventoryTab

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

class EquipmentManagementTab(EquipmentManagementUI):
    """Ekipman Yönetimi Sekmesi"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        # Alt modülleri başlat
        self.equipment_list_tab = EquipmentListTab(self)
        self.maintenance_tab = MaintenanceTab(self)
        self.inventory_tab = InventoryTab(self)
        
        # Verileri yükle
        self.load_equipment_data()
        self.load_inventory_data()
        
    def load_equipment_data(self):
        """Örnek ekipman verilerini yükler"""
        self.table.setRowCount(0)
        
        for equipment in EQUIPMENT_DATA:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Ekipman verilerini ekle
            for col, data in enumerate(equipment):
                if col < self.table.columnCount():  # Sütun sayısını aşmamak için kontrol
                    self.equipment_list_tab.add_item_to_table(row, col, data)
        
        self.table.resizeColumnsToContents()
        
        # İlk yükleme sonrası bakım takvimini güncelle
        current_date = self.calendar.selectedDate()
        self.maintenance_tab.show_maintenance_for_date(current_date)
        
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
                self.inventory_tab.add_item_to_inventory_table(row, col, value)

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
        self.equipment_tree.itemClicked.connect(self.filter_by_category)
        
        # Bakım işlemleri bağlantıları
        self.send_maintenance_btn.clicked.connect(self.send_to_maintenance)
        self.remove_maintenance_btn.clicked.connect(self.remove_from_maintenance)
        self.calendar_remove_maintenance_btn.clicked.connect(self.remove_from_maintenance)
        
        # Envanter düzenleme bağlantıları
        self.add_inventory_btn.clicked.connect(self.add_inventory)
        self.edit_inventory_btn.clicked.connect(self.edit_inventory)
        self.delete_inventory_btn.clicked.connect(self.delete_inventory)

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
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir ekipman seçin!")
            return
        
        # Mevcut verileri al
        values = []
        for col in range(self.table.columnCount()):
            item = self.table.item(current_row, col)
            if item:
                values.append(item.text())
            else:
                values.append("")
        
        dialog = EquipmentDialog(self)
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
        
        # Tablodaki tüm satırları sil
        self.upcoming_maintenance_table.setRowCount(0)
        
        # Tüm ekipmanları kontrol et ve seçili tarihte bakımda olanları göster
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 3)
            next_check_item = self.table.item(row, 5)
            
            if (status_item and status_item.text() == "Bakımda" and
                next_check_item and self.convert_date_format(next_check_item.text()) == selected_date):
                
                equipment_id = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
                equipment_name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                status_detail = self.table.item(row, 8).text() if self.table.item(row, 8) else ""
                
                # Bakım nedenini al
                reason = status_detail.replace("Bakım nedeni: ", "") if status_detail.startswith("Bakım nedeni: ") else ""
                
                # Bakım takvimine ekle (rekürsif çağrı yapmadan)
                # Yeni satır ekle
                new_row = self.upcoming_maintenance_table.rowCount()
                self.upcoming_maintenance_table.insertRow(new_row)
                
                # Verileri ekle
                data = [equipment_name, selected_date, "Bakım", "Yüksek"]
                
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
                            
                    # Ekipman ID'sini veri olarak sakla
                    if col == 0:  # Ekipman adı sütunu
                        item.setData(Qt.UserRole, equipment_id)
                        item.setToolTip(f"Bakım nedeni: {reason}")
                    
                    self.upcoming_maintenance_table.setItem(new_row, col, item)
        
        # Örnek bakım verilerini de ekle (gerçek uygulamada bu kısım veritabanından gelecek)
        maintenance_data = [
            ("Jeneratör A", "2024-04-15", "Periyodik Bakım", "Yüksek"),
            ("Kurtarma Vinci", "2024-04-18", "Yağ Değişimi", "Orta"),
            ("Su Pompası", "2024-04-20", "Kontrol", "Düşük"),
            ("İletişim Sistemi", "2024-04-22", "Yazılım Güncelleme", "Yüksek")
        ]
        
        filtered_data = [data for data in maintenance_data if data[1] == selected_date]
        
        for data in filtered_data:
            row = self.upcoming_maintenance_table.rowCount()
            self.upcoming_maintenance_table.insertRow(row)
            
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

    def convert_date_format(self, date_str):
        """dd.MM.yyyy formatını yyyy-MM-dd formatına çevirir"""
        try:
            # Tarih formatını kontrol et
            if "." in date_str:
                date = QDate.fromString(date_str, "dd.MM.yyyy")
                return date.toString("yyyy-MM-dd")
            return date_str
        except:
            return date_str

    def filter_inventory(self):
        """Envanter verilerini lokasyona göre filtrele"""
        selected_location = self.location_combo.currentText()
        
        for row in range(self.inventory_table.rowCount()):
            location_item = self.inventory_table.item(row, 0)
            if location_item:
                should_show = (selected_location == "Tüm Lokasyonlar" or 
                             location_item.text() == selected_location)
                self.inventory_table.setRowHidden(row, not should_show)
                
    def add_inventory(self):
        """Yeni envanter kaydı eklemek için dialog açar"""
        dialog = InventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            
            for col, value in enumerate(dialog.get_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Kritik seviye için renklendirme
                if col == 4 and int(value) > 0:  # Kritik seviye sütunu
                    item.setBackground(QBrush(QColor("#f44336")))
                    item.setForeground(QBrush(QColor("white")))
                
                self.inventory_table.setItem(row, col, item)

    def edit_inventory(self):
        """Seçili envanter kaydını düzenler"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir kayıt seçin!")
            return
        
        dialog = InventoryDialog(self)
        dialog.set_values([
            self.inventory_table.item(current_row, col).text()
            for col in range(self.inventory_table.columnCount())
        ])
        
        if dialog.exec_() == QDialog.Accepted:
            for col, value in enumerate(dialog.get_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Kritik seviye için renklendirme
                if col == 4 and int(value) > 0:  # Kritik seviye sütunu
                    item.setBackground(QBrush(QColor("#f44336")))
                    item.setForeground(QBrush(QColor("white")))
                
                self.inventory_table.setItem(current_row, col, item)

    def delete_inventory(self):
        """Seçili envanter kaydını siler"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir kayıt seçin!")
            return
        
        reply = QMessageBox.question(
            self,
            'Envanter Kaydı Silme Onayı',
            'Seçili envanter kaydını silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.inventory_table.removeRow(current_row)

    def send_to_maintenance(self):
        """Seçili ekipmanı bakıma gönder"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen bakıma göndermek için bir ekipman seçin!")
            return
        
        # Durum sütununu kontrol et
        status_item = self.table.item(current_row, 3)
        if status_item and status_item.text() == "Bakımda":
            QMessageBox.information(self, "Bilgi", "Bu ekipman zaten bakımda!")
            return
        
        # Bakım nedeni için dialog
        reason, ok = QInputDialog.getText(
            self, 
            "Bakım Nedeni",
            "Bakıma gönderme nedeni:",
            QLineEdit.Normal, 
            ""
        )
        
        if not ok:
            return
        
        # Tarih seçimi
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("Tahmini Tamamlanma Tarihi")
        layout = QVBoxLayout()
        
        calendar = QCalendarWidget()
        # Minimum tarih olarak bugünü ayarla
        calendar.setMinimumDate(QDate.currentDate())
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(date_dialog.accept)
        button_box.rejected.connect(date_dialog.reject)
        
        layout.addWidget(QLabel("Bakımın tahmini tamamlanma tarihini seçin:"))
        layout.addWidget(calendar)
        layout.addWidget(button_box)
        
        date_dialog.setLayout(layout)
        
        if date_dialog.exec_() != QDialog.Accepted:
            return
        
        selected_date = calendar.selectedDate()
        completion_date = selected_date.toString("dd.MM.yyyy")
        completion_date_iso = selected_date.toString("yyyy-MM-dd")
        
        # Ekipman bilgilerini al
        equipment_id = self.table.item(current_row, 0).text() if self.table.item(current_row, 0) else ""
        equipment_name = self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else ""
        
        # Durumu güncelle
        status_item.setText("Bakımda")
        status_item.setBackground(QBrush(QColor("#FFA500")))
        
        # Sonraki kontrol tarihini güncelle
        next_check_item = self.table.item(current_row, 5)
        if next_check_item:
            next_check_item.setText(completion_date)
        
        # Durum detayını güncelle
        status_detail_item = self.table.item(current_row, 8)
        if status_detail_item:
            status_detail_item.setText(f"Bakım nedeni: {reason}")
        
        QMessageBox.information(
            self, 
            "Başarılı", 
            f"Ekipman bakıma alındı.\nTahmini tamamlanma tarihi: {completion_date}"
        )
        
        # Rekürsif çağrı riski olmadan takvim tarihini güncelle
        self.calendar.setSelectedDate(selected_date)
        # Manuel olarak bakım listesini güncelle
        self.upcoming_maintenance_table.setRowCount(0)  # Önce tabloyu temizle
        self.show_maintenance_for_date(selected_date)  # Şimdi güvenli bir şekilde çağır

    def remove_from_maintenance(self):
        """Seçili ekipmanı bakımdan çıkar"""
        # Hangi sekmenin aktif olduğunu kontrol et
        current_tab = self.parent.findChild(QTabWidget).currentIndex() if self.parent else 0
        
        # Ekipman listesi sekmesinden mi yoksa bakım takviminden mi çağrıldı
        if current_tab == 0:  # Ekipman listesi sekmesi
            current_row = self.table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen bakımdan çıkarmak için bir ekipman seçin!")
                return
            
            # Durum sütununu kontrol et
            status_item = self.table.item(current_row, 3)
            if not status_item or status_item.text() != "Bakımda":
                QMessageBox.information(self, "Bilgi", "Bu ekipman bakımda değil!")
                return
            
            equipment_id = self.table.item(current_row, 0).text() if self.table.item(current_row, 0) else ""
            equipment_name = self.table.item(current_row, 1).text() if self.table.item(current_row, 1) else ""
        else:  # Bakım takvimi sekmesi
            current_row = self.upcoming_maintenance_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen bakımdan çıkarmak için bir ekipman seçin!")
                return
            
            equipment_name = self.upcoming_maintenance_table.item(current_row, 0).text() if self.upcoming_maintenance_table.item(current_row, 0) else ""
            
            # Ekipman ID'sini bul
            equipment_id = ""
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 1)
                if name_item and name_item.text() == equipment_name:
                    id_item = self.table.item(row, 0)
                    if id_item:
                        equipment_id = id_item.text()
                        current_row = row  # Ana tablodaki satır indeksini güncelle
                        break
            
            if not equipment_id:
                QMessageBox.warning(self, "Hata", "Ekipman bulunamadı!")
                return
        
        # İşlem notları için dialog
        notes, ok = QInputDialog.getText(
            self, 
            "Bakım Notları",
            "Yapılan işlemler ve notlar:",
            QLineEdit.Normal, 
            ""
        )
        
        if not ok:
            return
        
        # Şu anki tarihi al
        current_date = QDate.currentDate().toString("dd.MM.yyyy")
        
        # Bir sonraki bakım tarihini hesapla (3 ay sonra)
        next_date = QDate.currentDate().addMonths(3).toString("dd.MM.yyyy")
        
        # Durumu güncelle
        status_item = self.table.item(current_row, 3)
        if status_item:
            status_item.setText("Aktif")
            status_item.setBackground(QBrush(QColor("#4CAF50")))
        
        # Son kontrol tarihini güncelle
        last_check_item = self.table.item(current_row, 4)
        if last_check_item:
            last_check_item.setText(current_date)
        
        # Sonraki kontrol tarihini güncelle
        next_check_item = self.table.item(current_row, 5)
        if next_check_item:
            next_check_item.setText(next_date)
        
        # Durum detayını güncelle
        status_detail_item = self.table.item(current_row, 8)
        if status_detail_item:
            status_detail_item.setText(f"Bakım tamamlandı: {notes}")
        
        # Bakım takviminden kaldır - Eğer bakım takvimi sekmesinden çağrıldıysa
        if current_tab == 1:  # Bakım takvimi sekmesi
            self.upcoming_maintenance_table.removeRow(current_row)
        
        # Takvimde gösterilen günü güncelle
        self.show_maintenance_for_date(self.calendar.selectedDate())
        
        QMessageBox.information(
            self, 
            "Başarılı", 
            f"Ekipman bakımdan çıkarıldı ve aktif duruma alındı.\nBir sonraki bakım tarihi: {next_date}"
        )

    def add_to_maintenance_calendar(self, equipment_id, equipment_name, date, reason, priority="Orta"):
        """Bakım takvimine yeni bir görev ekle"""
        # Yeni satır ekle
        row = self.upcoming_maintenance_table.rowCount()
        self.upcoming_maintenance_table.insertRow(row)
        
        # Verileri ekle
        data = [equipment_name, date, "Bakım", priority]
        
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
                    
            # Ekipman ID'sini veri olarak sakla
            if col == 0:  # Ekipman adı sütunu
                item.setData(Qt.UserRole, equipment_id)
                item.setToolTip(f"Bakım nedeni: {reason}")
            
            self.upcoming_maintenance_table.setItem(row, col, item)

class EquipmentDialog(QDialog):
    """Ekipman ekleme/düzenleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Ekipman Bilgileri")
        self.setFixedSize(400, 500)
        
        layout = QFormLayout()
        
        # Form alanları
        self.equipment_id = QLineEdit()
        self.equipment_name = QLineEdit()
        self.equipment_type = QComboBox()
        self.equipment_type.addItems([
            "Kurtarma Ekipmanı", "Arama Ekipmanı", "Güç Ekipmanı",
            "Güç Ekipmanı - Jeneratörler", "Sağlık Ekipmanı", "Yangın Ekipmanı", 
            "İletişim Ekipmanı", "Su Tahliye", "Diğer"
        ])
        
        self.status = QComboBox()
        self.status.addItems(["Aktif", "Bakımda", "Onarımda"])
        
        self.last_check = QLineEdit()
        self.next_check = QLineEdit()
        self.responsible = QLineEdit()
        self.location = QComboBox()
        self.location.addItems(["Ana Depo", "Mobil Depo 1", "Mobil Depo 2", "Saha"])
        self.location.setEditable(True)
        self.status_detail = QLineEdit()
        self.team_id = QLineEdit()
        
        # Form alanlarını ekle
        layout.addRow("Ekipman ID:", self.equipment_id)
        layout.addRow("Ekipman Adı:", self.equipment_name)
        layout.addRow("Tür:", self.equipment_type)
        layout.addRow("Durum:", self.status)
        layout.addRow("Son Kontrol:", self.last_check)
        layout.addRow("Sonraki Kontrol:", self.next_check)
        layout.addRow("Sorumlu Personel:", self.responsible)
        layout.addRow("Konum/Depo:", self.location)
        layout.addRow("Durum Detayı:", self.status_detail)
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
            self.next_check.text(),
            self.responsible.text(),
            self.team_id.text()
        ]):
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
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
            self.next_check.text(),
            self.responsible.text(),
            self.location.currentText(),
            self.status_detail.text(),
            self.team_id.text()
        ]

    def set_values(self, values):
        """Dialog form alanlarını verilen değerlerle doldur"""
        self.equipment_id.setText(values[0])
        self.equipment_name.setText(values[1])
        self.equipment_type.setCurrentText(values[2])
        self.status.setCurrentText(values[3])
        self.last_check.setText(values[4])
        
        # Eğer sonraki kontrol tarihini içeren bir array ise
        if len(values) > 5:
            self.next_check.setText(values[5])
            if len(values) > 6:
                self.responsible.setText(values[6])
                if len(values) > 7:
                    self.location.setCurrentText(values[7])
                    if len(values) > 8:
                        self.status_detail.setText(values[8])
                        if len(values) > 9:
                            self.team_id.setText(values[9])
                        else:
                            self.team_id.setText("")
                    else:
                        self.status_detail.setText("")
                else:
                    self.location.setCurrentText("Ana Depo")
            else:
                self.responsible.setText("")
        else:
            self.next_check.setText("")

class InventoryDialog(QDialog):
    """Envanter ekleme/düzenleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Envanter Bilgileri")
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        # Form alanları
        self.location = QComboBox()
        self.location.addItems(["Ana Depo", "Mobil Depo 1", "Mobil Depo 2", "Saha", "Yeni Depo"])
        self.location.setEditable(True)  # Kullanıcı yeni lokasyon girebilir
        
        self.total_equipment = QLineEdit()
        self.active = QLineEdit()
        self.in_maintenance = QLineEdit()
        self.critical_level = QLineEdit()
        
        # Sayısal alanlar için validasyon
        self.total_equipment.setValidator(QIntValidator(0, 9999))
        self.active.setValidator(QIntValidator(0, 9999))
        self.in_maintenance.setValidator(QIntValidator(0, 9999))
        self.critical_level.setValidator(QIntValidator(0, 9999))
        
        # Form alanlarını ekle
        layout.addRow("Lokasyon/Depo:", self.location)
        layout.addRow("Toplam Ekipman:", self.total_equipment)
        layout.addRow("Aktif Ekipman:", self.active)
        layout.addRow("Bakımda Olan:", self.in_maintenance)
        layout.addRow("Kritik Seviye:", self.critical_level)
        
        # Yardım metni
        help_label = QLabel("* Kritik seviye, stok miktarının altına düştüğünde uyarı verilecek eşik değeridir.")
        help_label.setStyleSheet("color: #FFA500; font-size: 11px;")
        layout.addRow("", help_label)
        
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
            self.location.currentText(),
            self.total_equipment.text(),
            self.active.text(),
            self.in_maintenance.text(),
            self.critical_level.text()
        ]):
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        # Aktif + Bakımda sayısının toplam sayıdan fazla olmadığını kontrol et
        total = int(self.total_equipment.text())
        active = int(self.active.text())
        in_maintenance = int(self.in_maintenance.text())
        
        if active + in_maintenance > total:
            QMessageBox.warning(self, "Uyarı", "Aktif ve bakımdaki ekipman sayısı toplamı, toplam ekipman sayısından fazla olamaz!")
            return
        
        self.accept()

    def get_values(self):
        """Dialog form değerlerini liste olarak döndür"""
        return [
            self.location.currentText(),
            self.total_equipment.text(),
            self.active.text(),
            self.in_maintenance.text(),
            self.critical_level.text()
        ]

    def set_values(self, values):
        """Dialog form alanlarını verilen değerlerle doldur"""
        self.location.setCurrentText(values[0])
        self.total_equipment.setText(values[1])
        self.active.setText(values[2])
        self.in_maintenance.setText(values[3])
        self.critical_level.setText(values[4])
