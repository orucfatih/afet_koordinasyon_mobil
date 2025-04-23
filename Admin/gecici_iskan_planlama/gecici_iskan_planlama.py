import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QFormLayout, QLineEdit,
    QTextEdit, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QFont
from Admin.gecici_iskan_planlama.harita2 import GoogleMapsWindow
from Admin.config import initialize_firebase, get_firestore_client

class GeciciIskanPlanlamaTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geçici İskan Planlama Sistemi")
        self.setGeometry(100, 100, 1400, 800)
        
        # Firebase başlatma
        try:
            initialize_firebase()
            self.db = get_firestore_client()
            print("Firebase başarıyla başlatıldı!")
        except Exception as e:
            print(f"Firebase başlatılamadı: {e}")
            QMessageBox.critical(self, "Hata", f"Firebase bağlantısı kurulamadı: {e}")
            return

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sol Panel - Harita
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Harita widget'ını ekle
        self.map_widget = GoogleMapsWindow()
        left_layout.addWidget(self.map_widget)
        self.map_widget.setFixedHeight(850)  # Harita yüksekliğini sabitle
        
        # Sağ Panel - Kontrol ve Bilgi Paneli
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setMinimumWidth(400)
        right_panel.setMaximumWidth(400)

        # Tab Widget oluştur
        tab_widget = QTabWidget()
        
        # Kontrol Tab'ı
        control_tab = QWidget()
        control_layout = QVBoxLayout(control_tab)

        # Kontrol Grubu
        control_group = QGroupBox("Kontrol Paneli")
        control_form_layout = QFormLayout()

        # İl Seçimi
        self.il_combo = QComboBox()
        self.il_combo.addItems(["İzmir", "İstanbul", "Ankara", "Bursa"])  # Örnek iller
        control_form_layout.addRow("İl:", self.il_combo)

        # İlçe Seçimi
        self.ilce_combo = QComboBox()
        self.ilce_combo.addItems(["Merkez", "Bornova", "Karşıyaka"])  # Örnek ilçeler
        control_form_layout.addRow("İlçe:", self.ilce_combo)

        # Kapasite Girişi
        self.kapasite_spin = QSpinBox()
        self.kapasite_spin.setRange(0, 10000)
        self.kapasite_spin.setValue(100)
        control_form_layout.addRow("Kapasite:", self.kapasite_spin)

        # Alan Tipi Seçimi
        self.alan_tipi_combo = QComboBox()
        self.alan_tipi_combo.addItems([
            "Çadır Alanı",
            "Konteyner Kent",
            "Geçici Konut",
            "Spor Salonu",
            "Okul",
            "Otel"
        ])
        control_form_layout.addRow("Alan Tipi:", self.alan_tipi_combo)

        # Altyapı Durumu
        self.altyapi_combo = QComboBox()
        self.altyapi_combo.addItems([
            "Tam Donanımlı",
            "Temel Altyapı Mevcut",
            "Altyapı Gerekli"
        ])
        control_form_layout.addRow("Altyapı:", self.altyapi_combo)

        # Adres Girişi
        self.adres_text = QTextEdit()
        self.adres_text.setMaximumHeight(100)
        control_form_layout.addRow("Adres:", self.adres_text)

        # Notlar
        self.notlar_text = QTextEdit()
        self.notlar_text.setMaximumHeight(100)
        control_form_layout.addRow("Notlar:", self.notlar_text)

        # Kaydet Butonu
        self.kaydet_btn = QPushButton("Kaydet")
        self.kaydet_btn.clicked.connect(self.kaydet)
        control_form_layout.addRow(self.kaydet_btn)

        control_group.setLayout(control_form_layout)
        control_layout.addWidget(control_group)

        # İstatistik Grubu
        stats_group = QGroupBox("İstatistikler")
        stats_layout = QVBoxLayout()
        
        # İstatistik etiketleri
        self.toplam_alan_label = QLabel("Toplam Alan: 0")
        self.toplam_kapasite_label = QLabel("Toplam Kapasite: 0")
        self.doluluk_orani_label = QLabel("Doluluk Oranı: %0")
        
        stats_layout.addWidget(self.toplam_alan_label)
        stats_layout.addWidget(self.toplam_kapasite_label)
        stats_layout.addWidget(self.doluluk_orani_label)
        
        stats_group.setLayout(stats_layout)
        control_layout.addWidget(stats_group)

        # Alan Listesi
        list_group = QGroupBox("Kayıtlı Alanlar")
        list_layout = QVBoxLayout()
        
        self.alan_table = QTableWidget()
        self.alan_table.setColumnCount(4)
        self.alan_table.setHorizontalHeaderLabels(["Tip", "Kapasite", "Konum", "Durum"])
        self.alan_table.horizontalHeader().setStretchLastSection(True)
        
        list_layout.addWidget(self.alan_table)
        list_group.setLayout(list_layout)
        control_layout.addWidget(list_group)

        tab_widget.addTab(control_tab, "Kontrol")

        # Detaylar Tab'ı
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)
        
        # Detay bilgileri
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        tab_widget.addTab(details_tab, "Detaylar")

        # Raporlar Tab'ı
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        
        # Rapor oluşturma kontrolleri
        report_controls = QHBoxLayout()
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Günlük Durum Raporu",
            "Kapasite Analizi",
            "İhtiyaç Raporu",
            "Doluluk Raporu"
        ])
        report_controls.addWidget(self.report_type_combo)
        
        generate_report_btn = QPushButton("Rapor Oluştur")
        generate_report_btn.clicked.connect(self.generate_report)
        report_controls.addWidget(generate_report_btn)
        
        reports_layout.addLayout(report_controls)
        
        # Rapor görüntüleme alanı
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        reports_layout.addWidget(self.report_text)
        
        tab_widget.addTab(reports_tab, "Raporlar")

        right_layout.addWidget(tab_widget)

        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel, stretch=1)
        main_layout.addWidget(right_panel)

        # Verileri yükle
        self.load_data()

    def kaydet(self):
        """Yeni alan bilgilerini kaydet"""
        try:
            # Form verilerini al
            data = {
                'il': self.il_combo.currentText(),
                'ilce': self.ilce_combo.currentText(),
                'kapasite': self.kapasite_spin.value(),
                'alan_tipi': self.alan_tipi_combo.currentText(),
                'altyapi': self.altyapi_combo.currentText(),
                'adres': self.adres_text.toPlainText(),
                'notlar': self.notlar_text.toPlainText(),
                'durum': 'Aktif'
            }

            # Firebase'e kaydet
            doc_ref = self.db.collection('gecici_iskan_alanlari').add(data)
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", "Alan başarıyla kaydedildi!")
            
            # Tabloyu güncelle
            self.add_to_table(data)
            
            # Formu temizle
            self.clear_form()
            
            # İstatistikleri güncelle
            self.update_statistics()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt sırasında hata oluştu: {e}")

    def add_to_table(self, data):
        """Tabloya yeni alan ekle"""
        row = self.alan_table.rowCount()
        self.alan_table.insertRow(row)
        
        self.alan_table.setItem(row, 0, QTableWidgetItem(data['alan_tipi']))
        self.alan_table.setItem(row, 1, QTableWidgetItem(str(data['kapasite'])))
        self.alan_table.setItem(row, 2, QTableWidgetItem(f"{data['il']}/{data['ilce']}"))
        self.alan_table.setItem(row, 3, QTableWidgetItem(data['durum']))

    def clear_form(self):
        """Form alanlarını temizle"""
        self.kapasite_spin.setValue(100)
        self.adres_text.clear()
        self.notlar_text.clear()

    def load_data(self):
        """Firebase'den verileri yükle"""
        try:
            # Verileri çek
            docs = self.db.collection('gecici_iskan_alanlari').get()
            
            # Tabloyu temizle
            self.alan_table.setRowCount(0)
            
            # Verileri tabloya ekle
            for doc in docs:
                data = doc.to_dict()
                self.add_to_table(data)
            
            # İstatistikleri güncelle
            self.update_statistics()

        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Veriler yüklenirken hata oluştu: {e}")

    def update_statistics(self):
        """İstatistikleri güncelle"""
        try:
            # Toplam alan sayısı
            toplam_alan = self.alan_table.rowCount()
            
            # Toplam kapasite
            toplam_kapasite = 0
            for row in range(toplam_alan):
                kapasite = int(self.alan_table.item(row, 1).text())
                toplam_kapasite += kapasite
            
            # Doluluk oranı (örnek olarak sabit bir değer)
            doluluk_orani = 65  # Gerçek verilerle değiştirilmeli
            
            # Etiketleri güncelle
            self.toplam_alan_label.setText(f"Toplam Alan: {toplam_alan}")
            self.toplam_kapasite_label.setText(f"Toplam Kapasite: {toplam_kapasite}")
            self.doluluk_orani_label.setText(f"Doluluk Oranı: %{doluluk_orani}")

        except Exception as e:
            print(f"İstatistikler güncellenirken hata: {e}")

    def generate_report(self):
        """Seçilen rapor tipine göre rapor oluştur"""
        report_type = self.report_type_combo.currentText()
        
        report = f"=== {report_type} ===\n\n"
        current_time = QDateTime.currentDateTime()
        report += f"Oluşturma Tarihi: {current_time.toString('dd.MM.yyyy hh:mm')}\n\n"
        
        if report_type == "Günlük Durum Raporu":
            report += self.generate_daily_status_report()
        elif report_type == "Kapasite Analizi":
            report += self.generate_capacity_analysis()
        elif report_type == "İhtiyaç Raporu":
            report += self.generate_needs_report()
        elif report_type == "Doluluk Raporu":
            report += self.generate_occupancy_report()
        
        self.report_text.setText(report)

    def generate_daily_status_report(self):
        """Günlük durum raporu oluştur"""
        report = "GÜNLÜK DURUM RAPORU\n"
        report += "-" * 30 + "\n\n"
        
        # Toplam alan ve kapasite bilgileri
        report += f"Toplam Alan Sayısı: {self.alan_table.rowCount()}\n"
        
        # Alan tiplerine göre dağılım
        alan_tipleri = {}
        for row in range(self.alan_table.rowCount()):
            tip = self.alan_table.item(row, 0).text()
            alan_tipleri[tip] = alan_tipleri.get(tip, 0) + 1
        
        report += "\nAlan Tiplerine Göre Dağılım:\n"
        for tip, sayi in alan_tipleri.items():
            report += f"{tip}: {sayi} adet\n"
        
        return report

    def generate_capacity_analysis(self):
        """Kapasite analizi raporu oluştur"""
        report = "KAPASİTE ANALİZİ\n"
        report += "-" * 30 + "\n\n"
        
        toplam_kapasite = 0
        tip_kapasiteleri = {}
        
        for row in range(self.alan_table.rowCount()):
            tip = self.alan_table.item(row, 0).text()
            kapasite = int(self.alan_table.item(row, 1).text())
            
            toplam_kapasite += kapasite
            tip_kapasiteleri[tip] = tip_kapasiteleri.get(tip, 0) + kapasite
        
        report += f"Toplam Kapasite: {toplam_kapasite} kişi\n\n"
        report += "Alan Tiplerine Göre Kapasiteler:\n"
        for tip, kapasite in tip_kapasiteleri.items():
            report += f"{tip}: {kapasite} kişi\n"
        
        return report

    def generate_needs_report(self):
        """İhtiyaç raporu oluştur"""
        report = "İHTİYAÇ RAPORU\n"
        report += "-" * 30 + "\n\n"
        
        # Örnek ihtiyaç hesaplamaları
        toplam_kapasite = sum(int(self.alan_table.item(row, 1).text()) 
                            for row in range(self.alan_table.rowCount()))
        
        # Günlük temel ihtiyaç tahminleri
        report += "Günlük Temel İhtiyaç Tahminleri:\n"
        report += f"Su: {toplam_kapasite * 3} litre\n"  # Kişi başı 3 litre
        report += f"Ekmek: {toplam_kapasite * 2} adet\n"  # Kişi başı 2 adet
        report += f"Sıcak Yemek: {toplam_kapasite * 3} porsiyon\n"  # Günde 3 öğün
        report += f"Battaniye: {toplam_kapasite} adet\n"  # Kişi başı 1 adet
        
        return report

    def generate_occupancy_report(self):
        """Doluluk raporu oluştur"""
        report = "DOLULUK RAPORU\n"
        report += "-" * 30 + "\n\n"
        
        # Örnek doluluk verileri (gerçek verilerle değiştirilmeli)
        doluluk_oranlari = {
            "Çadır Alanı": 75,
            "Konteyner Kent": 85,
            "Geçici Konut": 60,
            "Spor Salonu": 90,
            "Okul": 70,
            "Otel": 55
        }
        
        report += "Alan Tiplerine Göre Doluluk Oranları:\n"
        for tip, oran in doluluk_oranlari.items():
            report += f"{tip}: %{oran}\n"
            
        # Genel doluluk ortalaması
        ortalama_doluluk = sum(doluluk_oranlari.values()) / len(doluluk_oranlari)
        report += f"\nGenel Doluluk Ortalaması: %{ortalama_doluluk:.1f}\n"
        
        return report

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeciciIskanPlanlamaTab()
    window.show()
    sys.exit(app.exec_()) 