from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QDateTimeEdit,
                           QMessageBox)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor
import json
import os
from styles import *
from datetime import datetime

class RaporYonetimTab(QWidget):
    """Rapor Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Sol Panel - Rapor Oluşturma
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Rapor Bilgileri Grubu
        report_info_group = QGroupBox("Rapor Bilgileri")
        form_layout = QFormLayout()
        
        # Tarih ve Saat Seçici
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setDateTime(QDateTime.currentDateTime())
        self.date_time_edit.setCalendarPopup(True)
        form_layout.addRow("Tarih ve Saat:", self.date_time_edit)
        
        # Afet Bölgesi Seçimi
        self.location_input = QLineEdit()
        form_layout.addRow("Afet Bölgesi:", self.location_input)
        
        # Rapor Türü Seçimi
        self.report_type = QComboBox()
        self.report_type.addItems([
            "Durum Değerlendirme Raporu",
            "Hasar Tespit Raporu",
            "İhtiyaç Analizi Raporu",
            "Müdahale Raporu",
            "Koordinasyon Raporu"
        ])
        form_layout.addRow("Rapor Türü:", self.report_type)
        
        report_info_group.setLayout(form_layout)
        left_layout.addWidget(report_info_group)
        
        # Rapor İçeriği Grubu
        content_group = QGroupBox("Rapor İçeriği")
        content_layout = QVBoxLayout()
        
        # Durum Özeti
        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("Genel durum özeti...")
        content_layout.addWidget(QLabel("Durum Özeti:"))
        content_layout.addWidget(self.summary_text)
        
        # Detaylı Bilgiler
        self.details_text = QTextEdit()
        self.details_text.setPlaceholderText("Detaylı bilgiler ve gözlemler...")
        content_layout.addWidget(QLabel("Detaylı Bilgiler:"))
        content_layout.addWidget(self.details_text)
        
        # İhtiyaçlar ve Öneriler
        self.needs_text = QTextEdit()
        self.needs_text.setPlaceholderText("Tespit edilen ihtiyaçlar ve öneriler...")
        content_layout.addWidget(QLabel("İhtiyaçlar ve Öneriler:"))
        content_layout.addWidget(self.needs_text)
        
        content_group.setLayout(content_layout)
        left_layout.addWidget(content_group)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton(" Raporu Kaydet")
        self.save_button.setStyleSheet(BUTTON_STYLE)
        self.save_button.setIcon(QIcon('icons/save.png'))
        self.save_button.clicked.connect(self.save_report)
        self.clear_button = QPushButton(" Formu Temizle")
        self.clear_button.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        self.clear_button.setIcon(QIcon('icons/broom.png'))
        self.clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.clear_button)
        left_layout.addLayout(buttons_layout)
        
        # Sağ Panel - Rapor Listesi ve Görüntüleme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Rapor Listesi
        list_group = QGroupBox("Kaydedilen Raporlar")
        list_layout = QVBoxLayout()
        
        # Arama ve Filtreleme
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rapor ara...")
        self.search_input.textChanged.connect(self.filter_reports)
        self.filter_type = QComboBox()
        self.filter_type.addItems(["Tüm Raporlar"] + [
            self.report_type.itemText(i) 
            for i in range(self.report_type.count())
        ])
        self.filter_type.currentTextChanged.connect(self.filter_reports)
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.filter_type)
        list_layout.addLayout(filter_layout)
        
        # Rapor Tablosu
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(4)
        self.reports_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.reports_table.setHorizontalHeaderLabels([
            "Tarih", "Bölge", "Tür", "Özet"
        ])
        self.reports_table.itemClicked.connect(self.show_report_details)
        list_layout.addWidget(self.reports_table)
        
        list_group.setLayout(list_layout)
        right_layout.addWidget(list_group)
        
        # Ana layout'a panelleri ekleme
        main_layout.addWidget(left_panel, stretch=2)
        main_layout.addWidget(right_panel, stretch=1)
        
        self.setLayout(main_layout)
        
        # Raporları yükle
        self.load_reports()


        # Sağ Panel - Silme Butonu Eklenmesi
        self.delete_button = QPushButton(" Seçili Raporu Sil")
        self.delete_button.setStyleSheet(RED_BUTTON_STYLE)
        self.delete_button.setIcon(QIcon('icons/bin.png'))
        self.delete_button.clicked.connect(self.delete_selected_report)
        right_layout.addWidget(self.delete_button)

        
    def save_report(self):
        """Raporu JSON formatında kaydeder"""
        report_data = {
            "datetime": self.date_time_edit.dateTime().toString(Qt.ISODate),
            "location": self.location_input.text(),
            "type": self.report_type.currentText(),
            "summary": self.summary_text.toPlainText(),
            "details": self.details_text.toPlainText(),
            "needs": self.needs_text.toPlainText()
        }
        
        # Basit doğrulama
        if not all([report_data["location"], report_data["summary"]]):
            QMessageBox.warning(self, "Uyarı", 
                              "Lütfen en azından bölge ve özet bilgilerini doldurun.")
            return
            
        try:
            # reports klasörünü kontrol et/oluştur
            if not os.path.exists("reports"):
                os.makedirs("reports")
            
            # Benzersiz dosya adı oluştur
            filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "Başarılı", "Rapor başarıyla kaydedildi.")
            self.clear_form()
            self.load_reports()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor kaydedilirken hata oluştu: {str(e)}")
    
    def clear_form(self):
        """Form alanlarını temizler"""
        self.date_time_edit.setDateTime(QDateTime.currentDateTime())
        self.location_input.clear()
        self.report_type.setCurrentIndex(0)
        self.summary_text.clear()
        self.details_text.clear()
        self.needs_text.clear()
    
    def load_reports(self):
        """Kaydedilmiş raporları yükler"""
        self.reports_table.setRowCount(0)
        
        if not os.path.exists("reports"):
            return
            
        for filename in os.listdir("reports"):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join("reports", filename), 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                        
                    row = self.reports_table.rowCount()
                    self.reports_table.insertRow(row)
                    
                    # Tarih formatını düzenle
                    date_obj = QDateTime.fromString(report_data["datetime"], Qt.ISODate)
                    formatted_date = date_obj.toString("dd.MM.yyyy HH:mm")
                    
                    self.reports_table.setItem(row, 0, QTableWidgetItem(formatted_date))
                    self.reports_table.setItem(row, 1, QTableWidgetItem(report_data["location"]))
                    self.reports_table.setItem(row, 2, QTableWidgetItem(report_data["type"]))
                    self.reports_table.setItem(row, 3, QTableWidgetItem(
                        report_data["summary"][:50] + "..." if len(report_data["summary"]) > 50 
                        else report_data["summary"]
                    ))
                    
                except Exception as e:
                    print(f"Rapor yüklenirken hata: {str(e)}")
    
    def filter_reports(self):
        """Raporları arama metni ve türe göre filtreler"""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_type.currentText()
        
        for row in range(self.reports_table.rowCount()):
            show_row = True
            
            # Metin araması
            if search_text:
                text_match = False
                for col in range(self.reports_table.columnCount()):
                    item = self.reports_table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                show_row = text_match
            
            # Tür filtresi
            if show_row and filter_type != "Tüm Raporlar":
                type_item = self.reports_table.item(row, 2)
                if type_item and type_item.text() != filter_type:
                    show_row = False
            
            self.reports_table.setRowHidden(row, not show_row)
    
    def show_report_details(self, item):
        """Seçilen raporun detaylarını gösterir"""
        row = item.row()
        date_item = self.reports_table.item(row, 0).text()
        location_item = self.reports_table.item(row, 1).text()
        
        # İlgili rapor dosyasını bul ve yükle
        for filename in os.listdir("reports"):
            if filename.endswith(".json"):
                with open(os.path.join("reports", filename), 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    
                report_date = QDateTime.fromString(
                    report_data["datetime"], 
                    Qt.ISODate
                ).toString("dd.MM.yyyy HH:mm")
                
                if (report_date == date_item and 
                    report_data["location"] == location_item):
                    # Form alanlarını doldur
                    self.date_time_edit.setDateTime(
                        QDateTime.fromString(report_data["datetime"], Qt.ISODate)
                    )
                    self.location_input.setText(report_data["location"])
                    self.report_type.setCurrentText(report_data["type"])
                    self.summary_text.setText(report_data["summary"])
                    self.details_text.setText(report_data["details"])
                    self.needs_text.setText(report_data["needs"])
                    break


    def delete_selected_report(self):
        """Seçili raporu siler"""
        selected_items = self.reports_table.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir rapor seçin.")
            return
        
        # Seçili satırdan tarih ve bölge bilgilerini al
        selected_row = selected_items[0].row()
        date_item = self.reports_table.item(selected_row, 0).text()
        location_item = self.reports_table.item(selected_row, 1).text()
        
        # İlgili dosyayı bul ve sil
        for filename in os.listdir("reports"):
            if filename.endswith(".json"):
                file_path = os.path.join("reports", filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                report_date = QDateTime.fromString(report_data["datetime"], Qt.ISODate).toString("dd.MM.yyyy HH:mm")
                
                if report_date == date_item and report_data["location"] == location_item:
                    # Onay mesajı
                    reply = QMessageBox.question(
                        self, "Onay", f"{filename} dosyasını silmek istediğinizden emin misiniz?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        try:
                            os.remove(file_path)
                            QMessageBox.information(self, "Başarılı", "Rapor başarıyla silindi.")
                            self.load_reports()  # Tabloyu güncelle
                        except Exception as e:
                            QMessageBox.critical(self, "Hata", f"Rapor silinirken hata oluştu: {str(e)}")
                    return
        
        QMessageBox.warning(self, "Uyarı", "Seçilen rapor bulunamadı veya silinemedi.")


