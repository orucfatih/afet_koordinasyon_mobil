from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QDateTimeEdit,
                           QMessageBox, QRadioButton, QDialog, QButtonGroup)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
import json
import os
from styles.styles_dark import *
from styles.styles_light import *
from datetime import datetime   
import subprocess
from utils import get_icon_path




class FormatSecimDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dosya Formatı Seçimi")
        self.format = None
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Radio butonları oluştur
        self.json_radio = QRadioButton("JSON")
        self.txt_radio = QRadioButton("TXT")
        
        # Radio butonları için stil
        for radio in [self.json_radio, self.txt_radio]:
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    padding: 5px;
                }
                QRadioButton::indicator {
                    width: 15px;
                    height: 15px;
                }
            """)
        
        # Button group oluştur
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.json_radio)
        self.button_group.addButton(self.txt_radio)
        
        # Default seçim
        self.json_radio.setChecked(True)
        
        layout.addWidget(self.json_radio)
        layout.addWidget(self.txt_radio)
        
        # Tamam ve İptal butonları
        btn_layout = QHBoxLayout()
        tamam_btn = QPushButton("✓ Tamam")
        iptal_btn = QPushButton("✕ İptal")
        
        for btn in [tamam_btn, iptal_btn]:
            btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        
        tamam_btn.clicked.connect(self.accept)
        iptal_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(tamam_btn)
        btn_layout.addWidget(iptal_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def accept(self):
        # Seçilen formatı kaydet
        if self.json_radio.isChecked():
            self.format = "JSON"
        else:
            self.format = "TXT"
        super().accept()



class RaporYonetimTab(QWidget):
    """Rapor Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Sol Panel - Rapor Oluşturma
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Rapor Bilgileri Grubu
        report_info_group = QGroupBox("Rapor Bilgileri")
        report_info_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Tarih ve Saat Seçici
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setDateTime(QDateTime.currentDateTime())
        self.date_time_edit.setCalendarPopup(True)
        self.date_time_edit.setStyleSheet(RESOURCE_INPUT_STYLE)
        form_layout.addRow("Tarih ve Saat:", self.date_time_edit)
        
        # Afet Bölgesi Seçimi
        self.location_input = QLineEdit()
        self.location_input.setStyleSheet(RESOURCE_INPUT_STYLE)
        form_layout.addRow("Afet Bölgesi:", self.location_input)
        
        # Rapor Türü Seçimi
        self.report_type = QComboBox()
        self.report_type.setStyleSheet(COMBO_BOX_STYLE)
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
        content_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        
        # Durum Özeti
        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("Genel durum özeti...")
        self.summary_text.setStyleSheet(RESOURCE_TEXT_EDIT_STYLE)
        content_layout.addWidget(QLabel("Durum Özeti:"))
        content_layout.addWidget(self.summary_text)
        
        # Detaylı Bilgiler
        self.details_text = QTextEdit()
        self.details_text.setPlaceholderText("Detaylı bilgiler ve gözlemler...")
        self.details_text.setStyleSheet(RESOURCE_TEXT_EDIT_STYLE)
        content_layout.addWidget(QLabel("Detaylı Bilgiler:"))
        content_layout.addWidget(self.details_text)
        
        # İhtiyaçlar ve Öneriler
        self.needs_text = QTextEdit()
        self.needs_text.setPlaceholderText("Tespit edilen ihtiyaçlar ve öneriler...")
        self.needs_text.setStyleSheet(RESOURCE_TEXT_EDIT_STYLE)
        content_layout.addWidget(QLabel("İhtiyaçlar ve Öneriler:"))
        content_layout.addWidget(self.needs_text)
        
        content_group.setLayout(content_layout)
        left_layout.addWidget(content_group)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Raporu Kaydet")
        self.save_button.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        self.save_button.setIcon(QIcon(get_icon_path('save.png')))
        self.save_button.clicked.connect(self.save_report)
        
        self.clear_button = QPushButton("Formu Temizle")
        self.clear_button.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        self.clear_button.setIcon(QIcon(get_icon_path('broom.png')))
        self.clear_button.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.clear_button)
        left_layout.addLayout(buttons_layout)
        
        # Sağ Panel - Rapor Listesi ve Görüntüleme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Rapor Listesi
        list_group = QGroupBox("Kaydedilen Raporlar")
        list_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        
        # Arama ve Filtreleme
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rapor ara...")
        self.search_input.setStyleSheet(RESOURCE_INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_reports)
        
        self.filter_type = QComboBox()
        self.filter_type.setStyleSheet(COMBO_BOX_STYLE)
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
        self.reports_table.setStyleSheet(RESOURCE_TABLE_STYLE)
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels([
            "Tarih", "Bölge", "Tür", "Özet", "Format"  
        ])
        self.reports_table.itemDoubleClicked.connect(self.open_report_file)
        self.reports_table.itemClicked.connect(self.show_report_details)
        list_layout.addWidget(self.reports_table)
        
        list_group.setLayout(list_layout)
        right_layout.addWidget(list_group)
        
        # Silme Butonu
        self.delete_button = QPushButton("Seçili Raporu Sil")
        self.delete_button.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        self.delete_button.setIcon(QIcon(get_icon_path('bin.png')))
        self.delete_button.clicked.connect(self.delete_selected_report)
        right_layout.addWidget(self.delete_button)
        
        # Panel genişliklerini ayarla
        left_panel.setMinimumWidth(600)  # Sol panel minimum genişlik
        right_panel.setMinimumWidth(400)  # Sağ panel minimum genişlik
        
        # Ana layout'a panelleri ekleme
        main_layout.addWidget(left_panel, 60)
        main_layout.addWidget(right_panel, 40)
        
        self.setLayout(main_layout)
        
        # Raporları yükle
        self.load_reports()



    def create_report_file(self):
        """Rapor klasör oluştur"""
        if not os.path.exists('reports'):
            os.makedirs('reports')


    def save_report(self):
        # Format seçim dialogunu aç
        format_dialog = FormatSecimDialog(self)
        if format_dialog.exec_() == QDialog.Accepted:
            secilen_format = format_dialog.format
            
            # Rapor verilerini topla
            rapor_verileri = {
                "tarih": self.date_time_edit.dateTime().toString(Qt.ISODate),
                "bolge": self.location_input.text(),
                "tur": self.report_type.currentText(),
                "ozet": self.summary_text.toPlainText(),
                "detaylar": self.details_text.toPlainText(),
                "ihtiyaclar": self.needs_text.toPlainText()
            }
            
            # Zorunlu alanları kontrol et
            if not all([rapor_verileri["bolge"]]):
                QMessageBox.warning(self, "Uyarı", "Lütfen Bölge bilgilerini doldurun.")
                return
            
            # Raporlar klasörünü oluştur
            self.create_report_file()
            
            try:
                # Dosya adını oluştur
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if secilen_format == "JSON":
                    dosya_yolu = os.path.join('reports', f"rapor_{timestamp}.json")
                    with open(dosya_yolu, 'w', encoding='utf-8') as f:
                        json.dump(rapor_verileri, f, ensure_ascii=False, indent=4)
                else:
                    dosya_yolu = os.path.join('reports', f"rapor_{timestamp}.txt")
                    with open(dosya_yolu, 'w', encoding='utf-8') as f:
                        for anahtar, deger in rapor_verileri.items():
                            f.write(f"{anahtar.capitalize()}: {deger}\n")
                
                QMessageBox.information(self, "Başarılı", f"Rapor {secilen_format} formatında kaydedildi: {os.path.basename(dosya_yolu)}")
                self.clear_form()
                self.load_reports()
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Rapor kaydedilemedi: {str(e)}")
    
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
        
        for dosya_adi in os.listdir("reports"):
            dosya_yolu = os.path.join("reports", dosya_adi)
            format_adi = "JSON" if dosya_adi.endswith(".json") else "TXT"
            
            try:
                # Ortak yükleme mantığı
                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                    rapor_verileri = json.load(f) if format_adi == "JSON" else self.read_txt_file(f)
                
                # Tabloya ekle
                satir = self.reports_table.rowCount()
                self.reports_table.insertRow(satir)
                
                # Tarih formatını düzenle
                tarih = QDateTime.fromString(rapor_verileri["tarih"], Qt.ISODate)
                
                self.reports_table.setItem(satir, 0, QTableWidgetItem(tarih.toString("dd.MM.yyyy HH:mm")))
                self.reports_table.setItem(satir, 1, QTableWidgetItem(rapor_verileri["bolge"]))
                self.reports_table.setItem(satir, 2, QTableWidgetItem(rapor_verileri["tur"]))
                self.reports_table.setItem(satir, 3, QTableWidgetItem(
                    rapor_verileri["ozet"][:50] + "..." if len(rapor_verileri["ozet"]) > 50 
                    else rapor_verileri["ozet"]
                ))
                self.reports_table.setItem(satir, 4, QTableWidgetItem(format_adi))
                
            except Exception as e:
                print(f"Rapor yüklenemedi: {str(e)}")


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
            full_path = os.path.join("reports", filename)
            try:
                if filename.endswith(".json"):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    # Tarih formatını düzelt
                    report_date = QDateTime.fromString(
                        report_data["tarih"], 
                        Qt.ISODate
                    ).toString("dd.MM.yyyy HH:mm")
                    
                    if (report_date == date_item and 
                        report_data["bolge"] == location_item):
                        # Form alanlarını doldur
                        self.date_time_edit.setDateTime(
                            QDateTime.fromString(report_data["tarih"], Qt.ISODate)
                        )
                        self.location_input.setText(report_data["bolge"])
                        self.report_type.setCurrentText(report_data["tur"])
                        self.summary_text.setText(report_data["ozet"])
                        self.details_text.setText(report_data["detaylar"])
                        self.needs_text.setText(report_data["ihtiyaclar"])
                        break
            except Exception as e:
                print(f"Rapor yüklenirken hata: {e}")



    def read_txt_file(self, dosya):
        """TXT dosyasını okur ve sözlük formatına çevirir"""
        rapor_verileri = {}
        for satir in dosya:
            anahtar, deger = satir.split(": ", 1)
            rapor_verileri[anahtar.lower()] = deger.strip()
        return rapor_verileri



    def delete_selected_report(self):
        """Seçili raporu siler"""
        secili_satirlar = self.reports_table.selectedItems()
        
        if not secili_satirlar:
            QMessageBox.warning(self, "Uyarı", "Silinecek raporu seçin.")
            return
        
        # Silme işlemi için gerekli bilgileri al
        secili_satir = secili_satirlar[0].row()
        tarih = self.reports_table.item(secili_satir, 0).text()
        bolge = self.reports_table.item(secili_satir, 1).text()
        format_adi = self.reports_table.item(secili_satir, 4).text()
        
        # Dosya uzantısını belirle
        dosya_uzantisi = ".json" if format_adi == "JSON" else ".txt"
        
        # Tüm dosyaları tara ve sil
        for dosya_adi in os.listdir("reports"):
            if dosya_adi.endswith(dosya_uzantisi):
                dosya_yolu = os.path.join("reports", dosya_adi)
                
                # Dosyayı oku ve kontrol et
                try:
                    with open(dosya_yolu, 'r', encoding='utf-8') as f:
                        rapor_verileri = json.load(f) if format_adi == "JSON" else self.read_txt_file(f)
                    
                    # Tarih ve bölge kontrolü
                    if (QDateTime.fromString(rapor_verileri["tarih"], Qt.ISODate).toString("dd.MM.yyyy HH:mm") == tarih and 
                        rapor_verileri["bolge"] == bolge):
                        
                        # Silme onayı
                        onay = QMessageBox.question(
                            self, "Onay", f"{dosya_adi} dosyasını silmek istediğinizden emin misiniz?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if onay == QMessageBox.Yes:
                            os.remove(dosya_yolu)
                            QMessageBox.information(self, "Başarılı", "Rapor silindi.")
                            self.load_reports()
                        return
                
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Rapor silinemedi: {str(e)}")


    def open_report_file(self, item):
        """Seçilen raporu açar"""
        row = item.row()
        
        # Dosya formatını ve adını al
        format_item = self.reports_table.item(row, 4)
        tarih_item = self.reports_table.item(row, 0)
        bolge_item = self.reports_table.item(row, 1)
        
        if not (format_item and tarih_item and bolge_item):
            return
        
        # Dosya adını bul
        format_adi = format_item.text()
        dosya_uzantisi = ".json" if format_adi == "JSON" else ".txt"
        
        for dosya_adi in os.listdir("reports"):
            if dosya_adi.endswith(dosya_uzantisi):
                try:
                    with open(os.path.join("reports", dosya_adi), 'r', encoding='utf-8') as f:
                        rapor_verileri = json.load(f) if format_adi == "JSON" else self.read_txt_file(f)
                    
                    # Tarih ve bölge kontrolü
                    if (QDateTime.fromString(rapor_verileri["tarih"], Qt.ISODate).toString("dd.MM.yyyy HH:mm") == tarih_item.text() and 
                        rapor_verileri["bolge"] == bolge_item.text()):
                        
                        # Dosyayı sistem varsayılan uygulamasıyla aç
                        dosya_yolu = os.path.join("reports", dosya_adi)
                        if os.name == 'nt':  # Windows
                            os.startfile(dosya_yolu)
                        elif os.name == 'posix':  # macOS ve Linux
                            subprocess.run(['xdg-open' if os.uname().sysname == 'Linux' else 'open', dosya_yolu])
                        
                        return
                
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {str(e)}")