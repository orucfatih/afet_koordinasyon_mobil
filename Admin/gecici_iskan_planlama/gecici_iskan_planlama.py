from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QPushButton,
                            QHBoxLayout, QComboBox, QLineEdit, QFormLayout,
                            QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt

class GeciciIskanPlanlamaTab(QWidget):
    """Geçici İskan Planlama Sekmesi"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Kullanıcı arayüzünü oluşturur"""
        main_layout = QVBoxLayout()
        
        # Başlık
        baslik = QLabel("Geçici İskan Planlama ve Yönetimi")
        baslik.setStyleSheet("font-size: 18px; font-weight: bold;")
        baslik.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(baslik)
        
        # Filtreleme alanı
        filtre_grup = QGroupBox("Filtreler")
        filtre_layout = QHBoxLayout()
        
        # Konum filtresi
        self.konum_combo = QComboBox()
        self.konum_combo.addItems(["Tüm Konumlar", "İstanbul", "Ankara", "İzmir", "Bursa", "Adana"])
        filtre_layout.addWidget(QLabel("Konum:"))
        filtre_layout.addWidget(self.konum_combo)
        
        # Durum filtresi
        self.durum_combo = QComboBox()
        self.durum_combo.addItems(["Tümü", "Aktif", "Planlanan", "Kapatıldı"])
        filtre_layout.addWidget(QLabel("Durum:"))
        filtre_layout.addWidget(self.durum_combo)
        
        # Arama kutusu
        self.arama_kutusu = QLineEdit()
        self.arama_kutusu.setPlaceholderText("İskan alanı ara...")
        filtre_layout.addWidget(QLabel("Ara:"))
        filtre_layout.addWidget(self.arama_kutusu)
        
        # Ara butonu
        self.ara_butonu = QPushButton("Ara")
        filtre_layout.addWidget(self.ara_butonu)
        
        filtre_grup.setLayout(filtre_layout)
        main_layout.addWidget(filtre_grup)
        
        # İskan alanları tablosu
        self.iskan_tablo = QTableWidget()
        self.iskan_tablo.setColumnCount(7)
        self.iskan_tablo.setHorizontalHeaderLabels([
            "İskan ID", "İsim", "Konum", "Kapasite", 
            "Mevcut Kişi", "Durum", "Son Güncelleme"
        ])
        
        # Örnek veriler
        self.ornek_veriler_ekle()
        
        # Tablo görünüm ayarları
        self.iskan_tablo.setAlternatingRowColors(True)
        self.iskan_tablo.horizontalHeader().setStretchLastSection(True)
        self.iskan_tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.iskan_tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        main_layout.addWidget(self.iskan_tablo)
        
        # Butonlar
        buton_layout = QHBoxLayout()
        self.yeni_btn = QPushButton("Yeni İskan Alanı Ekle")
        self.duzenle_btn = QPushButton("Düzenle")
        self.durum_guncelle_btn = QPushButton("Durum Güncelle")
        self.rapor_btn = QPushButton("Rapor Oluştur")
        
        buton_layout.addWidget(self.yeni_btn)
        buton_layout.addWidget(self.duzenle_btn)
        buton_layout.addWidget(self.durum_guncelle_btn)
        buton_layout.addWidget(self.rapor_btn)
        
        main_layout.addLayout(buton_layout)
        
        # Buton bağlantıları
        self.yeni_btn.clicked.connect(self.yeni_iskan_alani)
        self.duzenle_btn.clicked.connect(self.iskan_duzenle)
        self.durum_guncelle_btn.clicked.connect(self.durum_guncelle)
        self.rapor_btn.clicked.connect(self.rapor_olustur)
        
        self.setLayout(main_layout)
    
    def ornek_veriler_ekle(self):
        """Tabloya örnek veriler ekler"""
        veriler = [
            ("ISK001", "Çadır Kent 1", "İstanbul", "500", "320", "Aktif", "15.04.2023"),
            ("ISK002", "Konteyner Kent 1", "Ankara", "300", "270", "Aktif", "12.04.2023"),
            ("ISK003", "Çadır Kent 2", "İzmir", "400", "0", "Planlanan", "20.04.2023"),
            ("ISK004", "Okul Konaklaması", "Bursa", "150", "120", "Aktif", "10.04.2023"),
            ("ISK005", "Spor Salonu", "Adana", "200", "180", "Aktif", "08.04.2023"),
            ("ISK006", "Çadır Kent 3", "İstanbul", "350", "0", "Kapatıldı", "01.04.2023"),
        ]
        
        self.iskan_tablo.setRowCount(len(veriler))
        
        for satir, (iskan_id, isim, konum, kapasite, mevcut, durum, guncelleme) in enumerate(veriler):
            self.iskan_tablo.setItem(satir, 0, QTableWidgetItem(iskan_id))
            self.iskan_tablo.setItem(satir, 1, QTableWidgetItem(isim))
            self.iskan_tablo.setItem(satir, 2, QTableWidgetItem(konum))
            self.iskan_tablo.setItem(satir, 3, QTableWidgetItem(kapasite))
            self.iskan_tablo.setItem(satir, 4, QTableWidgetItem(mevcut))
            self.iskan_tablo.setItem(satir, 5, QTableWidgetItem(durum))
            self.iskan_tablo.setItem(satir, 6, QTableWidgetItem(guncelleme))
    
    def yeni_iskan_alani(self):
        """Yeni iskan alanı ekleme işlevi"""
        QMessageBox.information(self, "Bilgi", "Yeni iskan alanı ekleme fonksiyonu")
    
    def iskan_duzenle(self):
        """Seçili iskan alanını düzenleme işlevi"""
        secili_satir = self.iskan_tablo.currentRow()
        if secili_satir >= 0:
            iskan_id = self.iskan_tablo.item(secili_satir, 0).text()
            QMessageBox.information(self, "Bilgi", f"{iskan_id} ID'li iskan alanı düzenleme fonksiyonu")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir iskan alanı seçiniz!")
    
    def durum_guncelle(self):
        """Seçili iskan alanının durumunu güncelleme işlevi"""
        secili_satir = self.iskan_tablo.currentRow()
        if secili_satir >= 0:
            iskan_id = self.iskan_tablo.item(secili_satir, 0).text()
            QMessageBox.information(self, "Bilgi", f"{iskan_id} ID'li iskan alanı durum güncelleme fonksiyonu")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir iskan alanı seçiniz!")
    
    def rapor_olustur(self):
        """İskan alanları için rapor oluşturma işlevi"""
        QMessageBox.information(self, "Bilgi", "İskan alanları rapor oluşturma fonksiyonu") 