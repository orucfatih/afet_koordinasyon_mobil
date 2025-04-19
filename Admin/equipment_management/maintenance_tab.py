from PyQt5.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, 
                          QLabel, QInputDialog, QLineEdit, QDialogButtonBox, QCalendarWidget, 
                          QTabWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QBrush, QColor

class MaintenanceTab:
    """Bakım Takvimi sekmesi için işlemler"""
    def __init__(self, parent):
        self.parent = parent
        self.calendar = parent.calendar
        self.upcoming_maintenance_table = parent.upcoming_maintenance_table
        self.calendar_remove_maintenance_btn = parent.calendar_remove_maintenance_btn
        
        # Bağlantıları kur
        self.setup_connections()
        
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        self.calendar.clicked.connect(self.show_maintenance_for_date)
        self.calendar_remove_maintenance_btn.clicked.connect(self.remove_from_maintenance)
    
    def send_to_maintenance(self):
        """Seçili ekipmanı bakıma gönder"""
        current_row = self.parent.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.parent, "Uyarı", "Lütfen bakıma göndermek için bir ekipman seçin!")
            return
        
        # Durum sütununu kontrol et
        status_item = self.parent.table.item(current_row, 3)
        if status_item and status_item.text() == "Bakımda":
            QMessageBox.information(self.parent, "Bilgi", "Bu ekipman zaten bakımda!")
            return
        
        # Bakım nedeni için dialog
        reason, ok = QInputDialog.getText(
            self.parent, 
            "Bakım Nedeni",
            "Bakıma gönderme nedeni:",
            QLineEdit.Normal, 
            ""
        )
        
        if not ok:
            return
        
        # Tarih seçimi
        date_dialog = QDialog(self.parent)
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
        equipment_id = self.parent.table.item(current_row, 0).text() if self.parent.table.item(current_row, 0) else ""
        equipment_name = self.parent.table.item(current_row, 1).text() if self.parent.table.item(current_row, 1) else ""
        
        # Durumu güncelle
        status_item.setText("Bakımda")
        status_item.setBackground(QBrush(QColor("#FFA500")))
        
        # Sonraki kontrol tarihini güncelle
        next_check_item = self.parent.table.item(current_row, 5)
        if next_check_item:
            next_check_item.setText(completion_date)
        
        # Durum detayını güncelle
        status_detail_item = self.parent.table.item(current_row, 8)
        if status_detail_item:
            status_detail_item.setText(f"Bakım nedeni: {reason}")
        
        QMessageBox.information(
            self.parent, 
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
        current_tab = self.parent.parent.findChild(QTabWidget).currentIndex() if self.parent.parent else 0
        
        # Ekipman listesi sekmesinden mi yoksa bakım takviminden mi çağrıldı
        if current_tab == 0:  # Ekipman listesi sekmesi
            current_row = self.parent.table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self.parent, "Uyarı", "Lütfen bakımdan çıkarmak için bir ekipman seçin!")
                return
            
            # Durum sütununu kontrol et
            status_item = self.parent.table.item(current_row, 3)
            if not status_item or status_item.text() != "Bakımda":
                QMessageBox.information(self.parent, "Bilgi", "Bu ekipman bakımda değil!")
                return
            
            equipment_id = self.parent.table.item(current_row, 0).text() if self.parent.table.item(current_row, 0) else ""
            equipment_name = self.parent.table.item(current_row, 1).text() if self.parent.table.item(current_row, 1) else ""
        else:  # Bakım takvimi sekmesi
            current_row = self.upcoming_maintenance_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self.parent, "Uyarı", "Lütfen bakımdan çıkarmak için bir ekipman seçin!")
                return
            
            equipment_name = self.upcoming_maintenance_table.item(current_row, 0).text() if self.upcoming_maintenance_table.item(current_row, 0) else ""
            
            # Ekipman ID'sini bul
            equipment_id = ""
            for row in range(self.parent.table.rowCount()):
                name_item = self.parent.table.item(row, 1)
                if name_item and name_item.text() == equipment_name:
                    id_item = self.parent.table.item(row, 0)
                    if id_item:
                        equipment_id = id_item.text()
                        current_row = row  # Ana tablodaki satır indeksini güncelle
                        break
            
            if not equipment_id:
                QMessageBox.warning(self.parent, "Hata", "Ekipman bulunamadı!")
                return
        
        # İşlem notları için dialog
        notes, ok = QInputDialog.getText(
            self.parent, 
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
        status_item = self.parent.table.item(current_row, 3)
        if status_item:
            status_item.setText("Aktif")
            status_item.setBackground(QBrush(QColor("#4CAF50")))
        
        # Son kontrol tarihini güncelle
        last_check_item = self.parent.table.item(current_row, 4)
        if last_check_item:
            last_check_item.setText(current_date)
        
        # Sonraki kontrol tarihini güncelle
        next_check_item = self.parent.table.item(current_row, 5)
        if next_check_item:
            next_check_item.setText(next_date)
        
        # Durum detayını güncelle
        status_detail_item = self.parent.table.item(current_row, 8)
        if status_detail_item:
            status_detail_item.setText(f"Bakım tamamlandı: {notes}")
        
        # Bakım takviminden kaldır - Eğer bakım takvimi sekmesinden çağrıldıysa
        if current_tab == 1:  # Bakım takvimi sekmesi
            self.upcoming_maintenance_table.removeRow(current_row)
        
        # Takvimde gösterilen günü güncelle
        self.show_maintenance_for_date(self.calendar.selectedDate())
        
        QMessageBox.information(
            self.parent, 
            "Başarılı", 
            f"Ekipman bakımdan çıkarıldı ve aktif duruma alındı.\nBir sonraki bakım tarihi: {next_date}"
        )

    def show_maintenance_for_date(self, date):
        """Seçili tarih için bakım planlarını göster"""
        selected_date = date.toString("yyyy-MM-dd")
        
        # Tablodaki tüm satırları sil
        self.upcoming_maintenance_table.setRowCount(0)
        
        # Tüm ekipmanları kontrol et ve seçili tarihte bakımda olanları göster
        for row in range(self.parent.table.rowCount()):
            status_item = self.parent.table.item(row, 3)
            next_check_item = self.parent.table.item(row, 5)
            
            if (status_item and status_item.text() == "Bakımda" and
                next_check_item and self.convert_date_format(next_check_item.text()) == selected_date):
                
                equipment_id = self.parent.table.item(row, 0).text() if self.parent.table.item(row, 0) else ""
                equipment_name = self.parent.table.item(row, 1).text() if self.parent.table.item(row, 1) else ""
                status_detail = self.parent.table.item(row, 8).text() if self.parent.table.item(row, 8) else ""
                
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