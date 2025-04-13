"""
burası Firebase veritabanına bağlanacak 
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QDateTimeEdit,
                           QMessageBox)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
import json
import os
from styles.styles_dark import *
from styles.styles_light import *
from datetime import datetime   
import subprocess
from utils import get_icon_path
# Firebase bağlantıları için gerekli importlar
from database import get_database_ref, get_storage_bucket, initialize_firebase
import uuid

class RaporYonetimTab(QWidget):
    """Rapor Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        # Firebase referanslarını oluştur
        self.reports_ref = get_database_ref('/reports')  # Raporlar için Firebase referansı
        self.report_details_ref = get_database_ref('/report_details')  # Rapor detayları için referans
        
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
        self.reports_table.setColumnCount(4)
        self.reports_table.setHorizontalHeaderLabels([
            "Tarih", "Bölge", "Tür", "Özet"  # ID sütununu gizli tutalım
        ])
        self.reports_table.itemDoubleClicked.connect(self.view_report_details)
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
        """Rapor klasör oluştur - Firebase kullanıldığı için artık gerekli değil"""
        pass

    def save_report(self):
        """Raporu Firebase veritabanına kaydeder"""
        # Rapor verilerini topla
        rapor_verileri = {
            "tarih": self.date_time_edit.dateTime().toString(Qt.ISODate),
            "bolge": self.location_input.text(),
            "tur": self.report_type.currentText(),
            "ozet": self.summary_text.toPlainText(),
            "detaylar": self.details_text.toPlainText(),
            "ihtiyaclar": self.needs_text.toPlainText(),
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        }
        
        # Zorunlu alanları kontrol et
        if not rapor_verileri["bolge"]:
            QMessageBox.warning(self, "Uyarı", "Lütfen Bölge bilgilerini doldurun.")
            return
        
        try:
            # Benzersiz ID oluştur
            report_id = str(uuid.uuid4())
            
            # Firebase'e kaydet
            self.reports_ref.child(report_id).set(rapor_verileri)
            
            # Rapor detayları için ayrı bir referans kullan
            detail_data = {
                "id": report_id,
                "tarih": rapor_verileri["tarih"],
                "bolge": rapor_verileri["bolge"],
                "tur": rapor_verileri["tur"],
                "detaylar": rapor_verileri["detaylar"],
                "created_at": rapor_verileri["created_at"]
            }
            self.report_details_ref.child(report_id).set(detail_data)
            
            QMessageBox.information(self, "Başarılı", f"Rapor Firebase veritabanına kaydedildi!")
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
        """Firebase'den raporları yükler"""
        self.reports_table.setRowCount(0)
        
        try:
            # Firebase'den rapor verilerini al
            reports_data = self.reports_ref.get()
            
            if reports_data:
                for report_id, report_info in reports_data.items():
                    row_position = self.reports_table.rowCount()
                    self.reports_table.insertRow(row_position)
                    
                    # Tarih formatını düzenle
                    tarih_str = report_info.get('tarih', '')
                    tarih = QDateTime.fromString(tarih_str, Qt.ISODate)
                    
                    self.reports_table.setItem(row_position, 0, QTableWidgetItem(tarih.toString("dd.MM.yyyy HH:mm")))
                    self.reports_table.setItem(row_position, 1, QTableWidgetItem(report_info.get('bolge', '')))
                    self.reports_table.setItem(row_position, 2, QTableWidgetItem(report_info.get('tur', '')))
                    
                    # Özeti kısaltarak göster
                    ozet = report_info.get('ozet', '')
                    if len(ozet) > 50:
                        ozet = ozet[:50] + "..."
                    self.reports_table.setItem(row_position, 3, QTableWidgetItem(ozet))
                    
                    # ID'yi gizli veri olarak sakla
                    for i in range(4):
                        item = self.reports_table.item(row_position, i)
                        if item:
                            item.setData(Qt.UserRole, report_id)  # Her hücreye ID bilgisini ekle
            else:
                # Firebase'de veri yoksa bilgi mesajı göster
                QMessageBox.information(self, "Bilgi", "Kayıtlı rapor bulunamadı.")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Raporlar yüklenirken hata oluştu: {str(e)}")

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
        """Seçilen raporun detaylarını form alanlarında gösterir"""
        # ID bilgisini hücreden al
        report_id = item.data(Qt.UserRole)
        
        if not report_id:
            return
        
        try:
            # Firebase'den rapor verilerini al
            report_data = self.reports_ref.child(report_id).get()
            
            if report_data:
                # Form alanlarını doldur
                self.date_time_edit.setDateTime(
                    QDateTime.fromString(report_data.get('tarih', ''), Qt.ISODate)
                )
                self.location_input.setText(report_data.get('bolge', ''))
                self.report_type.setCurrentText(report_data.get('tur', ''))
                self.summary_text.setText(report_data.get('ozet', ''))
                self.details_text.setText(report_data.get('detaylar', ''))
                self.needs_text.setText(report_data.get('ihtiyaclar', ''))
            else:
                QMessageBox.warning(self, "Uyarı", "Rapor detayları bulunamadı.")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor detayları yüklenirken hata oluştu: {str(e)}")

    def delete_selected_report(self):
        """Seçili raporu Firebase veritabanından siler"""
        secili_satirlar = self.reports_table.selectedItems()
        
        if not secili_satirlar:
            QMessageBox.warning(self, "Uyarı", "Silinecek raporu seçin.")
            return
        
        # Seçili hücreden ID bilgisini al
        report_id = secili_satirlar[0].data(Qt.UserRole)
        
        if not report_id:
            return
        
        # Silme onayı
        onay = QMessageBox.question(
            self, "Onay", f"Bu raporu silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if onay == QMessageBox.Yes:
            try:
                # Firebase'den sil
                self.reports_ref.child(report_id).delete()
                self.report_details_ref.child(report_id).delete()
                
                # Tablodan kaldır
                for row in range(self.reports_table.rowCount()):
                    if self.reports_table.item(row, 0).data(Qt.UserRole) == report_id:
                        self.reports_table.removeRow(row)
                        break
                
                QMessageBox.information(self, "Başarılı", "Rapor silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Rapor silinemedi: {str(e)}")

    def view_report_details(self, item):
        """Seçilen raporun detaylarını bir diyalog penceresinde görüntüler"""
        # ID bilgisini hücreden al 
        report_id = item.data(Qt.UserRole)
        
        if not report_id:
            return
            
        try:
            # Firebase'den rapor verilerini al
            report_data = self.reports_ref.child(report_id).get()
            
            if report_data:
                # Tarih bilgisini formatla
                tarih_str = report_data.get('tarih', '')
                tarih = QDateTime.fromString(tarih_str, Qt.ISODate).toString("dd.MM.yyyy HH:mm")
                
                # Rapor içeriğini daha güzel formatlı bir şekilde göster
                rapor_icerik = f"""
                <h2>Rapor Detayları</h2>
                <p><b>Tarih:</b> {tarih}</p>
                <p><b>Bölge:</b> {report_data.get('bolge', '')}</p>
                <p><b>Tür:</b> {report_data.get('tur', '')}</p>
                <hr>
                <h3>Durum Özeti</h3>
                <p>{report_data.get('ozet', '')}</p>
                <hr>
                <h3>Detaylı Bilgiler</h3>
                <p>{report_data.get('detaylar', '')}</p>
                <hr>
                <h3>İhtiyaçlar ve Öneriler</h3>
                <p>{report_data.get('ihtiyaclar', '')}</p>
                """
                
                # Bilgiyi göster
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Rapor Detayları")
                msg_box.setText(rapor_icerik)
                msg_box.setTextFormat(Qt.RichText)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setDefaultButton(QMessageBox.Ok)
                msg_box.setStyleSheet("QLabel{min-width: 600px;}")
                msg_box.exec_()
            else:
                QMessageBox.warning(self, "Uyarı", "Rapor detayları bulunamadı.")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor detayları yüklenirken hata oluştu: {str(e)}")