"""
eklenecekler
kullanıcı e devlet kısmında fotoğraf filtrelemesi yapacak ama sadece cinsiyet ve yaş aralığı olarak alsa yeterli
çünkü veri sızıntısı ihtimalini her zaman düşünmek gerekir

mobilden fotoğraf ve bilgiler yüklenecek zaten
faceDetect.py test edildi fakat göstermek için basit bir tkinter arayüzü yapılacak
"""




from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QFileDialog, QProgressBar, QTabWidget, QComboBox, 
                            QTreeWidget, QTreeWidgetItem, QFrame, QScrollArea,
                            QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from simulations.sehirler_ve_ilceler import sehirler
import os
import numpy as np
import shutil
import tempfile
import unicodedata
import re
import uuid
import cv2
import json
from datetime import datetime

# Global değişkenler
KAYBOLAN_SAYISI = 0
ESLESMESAYISI = 0

# Mevcut dosyanın bulunduğu dizini al
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Türkçe karakterleri İngilizce karakterlere dönüştüren fonksiyon
def turkce_karakter_cevir(text):
    # Türkçe karakterler ve İngilizce karşılıkları
    tr_karakterler = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    # Metindeki Türkçe karakterleri İngilizce karşılıklarıyla değiştir
    for tr_char, en_char in tr_karakterler.items():
        text = text.replace(tr_char, en_char)
    
    return text

# Genel temizleme fonksiyonu - hem unicodedata hem de özel karşılıklar
def temiz_metin_olustur(text):
    """Metindeki tüm özel karakterleri temizler ve ASCII olmayan tüm karakterleri kaldırır"""
    # Önce Türkçe karakterleri İngilizce karşılıklarına çevir
    text = turkce_karakter_cevir(text)
    
    # Unicode normalizasyonu uygula - aksanlı karakterleri çözümle
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    # Sadece alfanumerik, nokta, tire ve alt çizgi karakterlerini koru
    text = re.sub(r'[^\w\-\.]', '_', text)
    
    return text

# Dosya yolundaki Türkçe karakterleri dönüştürme ve geçici dosya oluşturma
def turkce_dosya_cozumle(dosya_yolu):
    """Türkçe karakterler içeren dosya yollarını işlemek için yardımcı fonksiyon."""
    
    try:
        # Önce dosyayı okuyabilir miyiz kontrol et
        with open(dosya_yolu, 'rb') as f:
            img_data = f.read()
        return dosya_yolu, False  # Dosya doğrudan okunabilir
    except Exception as e:
        print(f"Dosya okuma hatası: {str(e)}")
        
        # Dosya yolunu parçalara ayır
        dizin_yolu, dosya_adi = os.path.split(dosya_yolu)
        dosya_adi_temiz = temiz_metin_olustur(dosya_adi)
        
        # Benzersiz bir geçici dosya adı oluştur
        gecici_dosya_adi = f"{uuid.uuid4().hex}_{dosya_adi_temiz}"
        
        # Geçici dizine kopyala
        temp_dir = tempfile.gettempdir()
        gecici_dosya_yolu = os.path.join(temp_dir, gecici_dosya_adi)
        
        try:
            # Binary olarak dosyayı kopyala
            with open(dosya_yolu, 'rb') as f_in:
                with open(gecici_dosya_yolu, 'wb') as f_out:
                    f_out.write(f_in.read())
            print(f"Dosya geçici yola kopyalandı: {gecici_dosya_yolu}")
            return gecici_dosya_yolu, True
        except Exception as copy_error:
            print(f"Geçici dosya oluşturma hatası: {str(copy_error)}")
            
            # Son çare - doğrudan tempfile kullan
            try:
                temp_suffix = os.path.splitext(dosya_adi)[1]
                with tempfile.NamedTemporaryFile(suffix=temp_suffix, delete=False) as temp_file:
                    with open(dosya_yolu, 'rb') as f_in:
                        temp_file.write(f_in.read())
                    return temp_file.name, True
            except Exception as final_error:
                print(f"Son çare geçici dosya oluşturma hatası: {str(final_error)}")
                return None, False

class PhotoLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(150, 150)
        self.setMaximumSize(150, 150)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)

class MissingPersonDetectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.photo_grid = None
        self.scroll_area = None
        self.photos_widget = None
        self.current_photos = []
        # Widget'ları önce tanımla
        self.init_widgets()
        # Sonra UI'ı oluştur
        self.initUI()
        # Ana pencere boyutunu ayarla - tüm içeriğin görünmesi için
        self.setMinimumSize(1000, 800)
        # Genel stil uygulanıyor
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
            }
            QTableWidget {
                border: 1px solid #d0d0d0;
                background-color: #000000;
                alternate-background-color: #3d3d3d;
                color: white;
            }
            QHeaderView::section {
                background-color: #000000;
                color: white;
                padding: 5px;
                font-weight: bold;
                border: 1px solid #c0c0c0;
            }
            QLabel {
                color: #ffffff;
                font-weight: normal;
            }
            QTreeWidget {
                border: 1px solid #d0d0d0;
                background-color: #000000;
                color: white;
            }
            QTreeWidget::item {
                color: white;
            }
            QPushButton {
                background-color: #6a0dad;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a2be2;
            }
            QPushButton:pressed {
                background-color: #4b0082;
            }
            QScrollArea {
                border: 1px solid #d0d0d0;
                background-color: #000000;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                background-color: #000000;
            }
            QTabBar::tab {
                background-color: #4b0082;
                color: #ffffff;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #6a0dad;
                color: #ffffff;
                border-top: 3px solid #8a2be2;
            }
            QProgressBar::chunk {
                background-color: #6a0dad;
            }
            QComboBox {
                background-color: #000000;
                color: white;
                border: 1px solid #d0d0d0;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #000000;
                color: white;
                selection-background-color: #6a0dad;
            }
            QScrollBar {
                background-color: #000000;
                border: 1px solid #d0d0d0;
            }
            QScrollBar::handle {
                background-color: #6a0dad;
            }
        """)
        
    def init_widgets(self):
        """Widget'ları başlangıçta tanımla"""
        # Ana scroll area
        self.main_scroll_area = QScrollArea()
        self.main_scroll_area.setWidgetResizable(True)
        self.main_content_widget = QWidget()
        self.main_content_widget.setStyleSheet("background-color: #000000;")
        self.main_scroll_area.setWidget(self.main_content_widget)
        
        # Tablolar
        self.missing_table = QTableWidget()
        self.missing_table.setAlternatingRowColors(True)
        self.missing_table.setStyleSheet("""
            QTableWidget {
                color: white;
                gridline-color: #6a0dad;
            }
            QTableWidget::item {
                border-bottom: 1px solid #6a0dad;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: rgba(106, 13, 173, 0.5);
            }
        """)
        
        self.found_table = QTableWidget()
        self.found_table.setAlternatingRowColors(True)
        self.found_table.setStyleSheet("""
            QTableWidget {
                color: white;
                gridline-color: #6a0dad;
            }
            QTableWidget::item {
                border-bottom: 1px solid #6a0dad;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: rgba(106, 13, 173, 0.5);
            }
        """)
        
        # Ağaç widget'ı
        self.location_tree = QTreeWidget()
        # Başlık metnini kısalt
        self.location_tree.setHeaderLabel("Bölgeler")
        self.location_tree.setMinimumHeight(300)
        self.location_tree.setHeaderHidden(False)
        self.location_tree.headerItem().setTextAlignment(0, Qt.AlignCenter)
        # Daha geniş bir ağaç widget'ı sağla
        self.location_tree.setMinimumWidth(300)
        # Sütun genişliğini ayarla
        self.location_tree.setColumnWidth(0, 280)
        self.location_tree.setStyleSheet("""
            QTreeWidget {
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px 5px;
                border-bottom: 1px solid #555555;
                margin-top: 2px;
            }
            QTreeWidget::item:selected {
                background-color: rgba(106, 13, 173, 0.5);
                color: #ffffff;
            }
            QTreeWidget::branch {
                background-color: #000000;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAPZJREFUeNrM0s1OwlAUgNH2AtsKFKF/AkIIzYYF+xGjMb6D738D3ejOuPZFdIfRhRsS2jRS2lJK7494kzuYsGAmJnqST8A951wJ8X+P8I2XOI5VOecBBpijiQx38HAHnOIFb5VSlYjoI4cTeNhghNRdwDkGeK1UlHmeB2zbfnBdN88+22EY8r7vb8MwPIv8jw58/EDIsqyPOI77tm3HPM9jDMPgOOcTURT9OlIQBDsAcSoIglbXdYbjOJxSaokQYtq2nRBCCrZtM8dxBEVR2jiOv+IQDWyjhGM8wUcWXrFCHUUUYKGHKhcIkbmV/0Mdfbxgie09CCnAe7gX+BFgADq1Wd4sox+yAAAAAElFTkSuQmCC);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAPBJREFUeNrM0z1LAzEYwPE0TVPrS99sKVjq4CDoJl18WeXL5/O7uHfQxcVFcHTR0UHBSQcHsS1SqK21vZgoXJ4L/+AScnC7HByE+8GfwF1yCQlRPmIYbxijXq+v5nn+2Ov1otVq5Y4Q4swY85YkyRjfiHDhcr1erzJKqQPbtgt4nAihN0qprW63+9kLrJ0vCCHAdV0vy7JVKWVRFIVDCGkEQaA8zystK1gsFtR13SAIglVd15t5nneSJFnGQRCsMcZAKQXOOSilYIyB1voPRFGkmqbpoiiasixLhJCzKIrC6XT6o+HIOI4twzDOfd+/tW37GgTBKF4mz38EGADiE5vbNFhS8QAAAABJRU5ErkJggg==);
            }
            QHeaderView::section {
                background-color: #6a0dad;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-style: none;
                border-bottom: 2px solid #8a2be2;
                border-radius: 0px;
            }
        """)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #6a0dad;
                border-radius: 4px;
                background-color: #333333;
                text-align: center;
                height: 20px;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #6a0dad;
                width: 10px;
                margin: 0px;
            }
        """)
        
        # Seçim özeti etiketi
        self.selection_summary = QLabel("Seçili Bölgeler: Yok")
        self.selection_summary.setWordWrap(True)
        self.selection_summary.setStyleSheet("""
            QLabel {
                background-color: #000000;
                color: #ffffff;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #6a0dad;
                margin-top: 10px;
                font-size: 13px;
            }
        """)
        
        # İstatistik etiketi
        self.stats_label = QLabel("Toplam Kayıtlı Biyometrik Veri: 0")
        self.stats_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #ffffff;
                font-size: 14px;
                padding: 5px;
                background-color: #000000;
                border: 1px solid #6a0dad;
                border-radius: 4px;
            }
        """)

        # Fotoğraf görüntüleme alanı
        self.photos_widget = QWidget()
        self.photos_widget.setStyleSheet("background-color: #000000;")
        self.photo_grid = QGridLayout(self.photos_widget)
        self.photo_grid.setSpacing(10)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.photos_widget)
        self.scroll_area.setMinimumHeight(500)  # Minimum yükseklik 500 birim

    def initUI(self):
        # Ana layout
        global KAYBOLAN_SAYISI, ESLESMESAYISI
        main_layout = QVBoxLayout(self.main_content_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # Kenar boşlukları ayarla
        main_layout.setSpacing(20)  # Öğeler arası boşluk
        
        # Üst kısım - İstatistikler
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)  # İstatistik kartları arası boşluk
        
        # İstatistik kartları
        self.kayip_stat_card = self.create_stat_card("Toplam Kayıp İhbarı", str(KAYBOLAN_SAYISI), stats_layout)
        self.create_stat_card("Bugün Gelen İhbarlar", "0", stats_layout)
        self.eslesme_stat_card = self.create_stat_card("Eşleşme Sayısı", str(ESLESMESAYISI), stats_layout)
        
        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(15)  # Boşluk ekle
        
        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                padding: 15px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)
        
        # Kayıp İhbarları Tab'ı
        missing_reports_widget = QWidget()
        missing_reports_widget.setStyleSheet("background-color: #000000;")
        missing_reports_layout = QVBoxLayout()
        
        # Başlık ekleme
        kayip_title = QLabel("Kayıp İhbarları Listesi")
        kayip_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        missing_reports_layout.addWidget(kayip_title)
        
        # Tablo ayarları
        self.missing_table.setColumnCount(6)
        self.missing_table.setHorizontalHeaderLabels([
            "İhbar Tarihi", "Ad Soyad", "T.C. Kimlik No", 
            "Kaybolduğu Bölge", "Durum", "İşlemler"
        ])
        self.missing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        missing_reports_layout.addWidget(self.missing_table)
        
        missing_reports_widget.setLayout(missing_reports_layout)
        tab_widget.addTab(missing_reports_widget, "Kayıp İhbarları")
        
        # Bulunan Kişiler Tab'ı
        found_persons_widget = QWidget()
        found_persons_widget.setStyleSheet("background-color: #000000;")
        found_persons_layout = QVBoxLayout()
        
        # Başlık ekleme
        bulunan_title = QLabel("Bulunan Kişiler Listesi")
        bulunan_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        found_persons_layout.addWidget(bulunan_title)
        
        # Tablo ayarları
        self.found_table.setColumnCount(6)
        self.found_table.setHorizontalHeaderLabels([
            "Bulunma Tarihi", "Fotoğraf", "Bulunduğu Bölge", 
            "Bulan Personel", "Durum", "İşlemler"
        ])
        self.found_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        found_persons_layout.addWidget(self.found_table)
        
        found_persons_widget.setLayout(found_persons_layout)
        tab_widget.addTab(found_persons_widget, "Bulunan Kişiler")
        
        # E-Devlet Veri Yönetimi Tab'ı
        edevlet_widget = QWidget()
        edevlet_widget.setStyleSheet("background-color: #000000;")
        edevlet_layout = QVBoxLayout()
        edevlet_layout.setSpacing(15)  # Bileşenler arası boşluk
        edevlet_layout.setContentsMargins(10, 10, 10, 10)  # Kenar boşlukları
        
        # Ana başlık
        main_title = QLabel("E-Devlet Biyometrik Veri Yönetimi")
        main_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; margin-bottom: 15px; text-align: center;")
        main_title.setAlignment(Qt.AlignCenter)
        edevlet_layout.addWidget(main_title)
        
        # İki bölümlü layout (sol - bölge seçimi, sağ - fotoğraflar ve eşleşmeler)
        split_layout = QHBoxLayout()
        
        # Sol panel - Bölge seçimi
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #000000; border: 1px solid #6a0dad; border-radius: 8px;")
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Bölge Seçimi Başlığı
        location_title = QLabel("Bölge Seçimi")
        location_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; padding: 5px; background-color: #6a0dad; border-radius: 4px; text-align: center;")
        location_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(location_title)
        
        # Şehirler ve İlçeler için açıklama etiketi
        location_desc = QLabel("Veri güncellemesi yapmak istediğiniz bölgeleri seçiniz:")
        location_desc.setStyleSheet("font-size: 13px; color: #ffffff; margin: 10px 0;")
        location_desc.setWordWrap(True)
        left_layout.addWidget(location_desc)
        
        # Ağaç widget'ına event bağla
        self.location_tree.itemChanged.connect(self.on_item_changed)
        
        # Şehirleri ağaca ekle
        for sehir, ilceler in sorted(sehirler.items()):
            sehir_item = QTreeWidgetItem(self.location_tree)
            sehir_item.setText(0, f"{sehir}")
            sehir_item.setFlags(sehir_item.flags() | Qt.ItemIsUserCheckable)
            sehir_item.setCheckState(0, Qt.Unchecked)
            
            # İlçeleri ekle
            for ilce, nufus in sorted(ilceler.items()):
                ilce_item = QTreeWidgetItem(sehir_item)
                ilce_item.setText(0, f"{ilce} ({nufus:,} kişi)")
                ilce_item.setFlags(ilce_item.flags() | Qt.ItemIsUserCheckable)
                ilce_item.setCheckState(0, Qt.Unchecked)
                
                # İlçe elemanlarına biraz iç boşluk ekle
                for i in range(self.location_tree.columnCount()):
                    ilce_item.setTextAlignment(i, Qt.AlignLeft | Qt.AlignVCenter)
        
        # Ağaç widget'ını daha temiz bir container içine yerleştir
        tree_container = QWidget()
        tree_container.setStyleSheet("background-color: #000000; border: 1px solid #555555; border-radius: 4px;")
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(5, 5, 5, 5)
        tree_layout.addWidget(self.location_tree)
        
        left_layout.addWidget(tree_container)
        
        # Seçim özeti
        self.selection_summary.setStyleSheet("""
            QLabel {
                background-color: #000000;
                color: #ffffff;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #6a0dad;
                margin-top: 10px;
                font-size: 13px;
            }
        """)
        left_layout.addWidget(self.selection_summary)
        
        # Veri yükleme butonu
        upload_btn = QPushButton("Seçili Bölgelerin E-Devlet Verileri ile Eşleştir")
        upload_btn.setMinimumHeight(50)
        upload_btn.clicked.connect(self.update_edevlet_data)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a0dad;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 10px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #8a2be2;
            }
            QPushButton:pressed {
                background-color: #4b0082;
            }
        """)
        left_layout.addWidget(upload_btn)
        
        # İlerleme çubuğu
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #6a0dad;
                border-radius: 4px;
                background-color: #333333;
                text-align: center;
                height: 25px;
                color: white;
                font-weight: bold;
                margin-top: 10px;
            }
            QProgressBar::chunk {
                background-color: #6a0dad;
                width: 10px;
                margin: 0px;
            }
        """)
        left_layout.addWidget(self.progress_bar)
        
        # İstatistik etiketi
        self.stats_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #ffffff;
                font-size: 14px;
                padding: 8px;
                background-color: #000000;
                border: 1px solid #6a0dad;
                border-radius: 4px;
                margin-top: 10px;
            }
        """)
        left_layout.addWidget(self.stats_label)
        
        # Sağ panel - Fotoğraflar ve eşleşmeler
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #000000; border: 1px solid #6a0dad; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)
        
        # Eşleşmeler başlığı
        matches_title = QLabel("Biyometrik Eşleşmeler")
        matches_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; padding: 5px; background-color: #6a0dad; border-radius: 4px; text-align: center;")
        matches_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(matches_title)
        
        # Fotoğraf container'ı
        photos_container = QWidget()
        photos_container.setStyleSheet("background-color: #000000; border: 1px solid #555555; border-radius: 4px; padding: 10px;")
        photos_layout = QVBoxLayout(photos_container)
        photos_layout.addWidget(self.scroll_area)
        right_layout.addWidget(photos_container)
        
        # Panelleri layout'a ekle
        split_layout.addWidget(left_panel)
        split_layout.addWidget(right_panel)
        
        edevlet_layout.addLayout(split_layout)
        
        edevlet_widget.setLayout(edevlet_layout)
        tab_widget.addTab(edevlet_widget, "E-Devlet Veri Yönetimi")
        
        main_layout.addWidget(tab_widget)
        
        # Ana scroll area'yı widget'a ekle
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.main_scroll_area)

    def create_stat_card(self, title, value, parent_layout):
        card = QWidget()
        card.setObjectName("stat_card")
        card.setStyleSheet("""
            QWidget#stat_card {
                background-color: #000000;
                border: 1px solid #d0d0d0;
                border-left: 6px solid #6a0dad;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
            }
        """)
        
        card_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            background-color: rgba(106, 13, 173, 0.2);
            padding: 3px 8px;
            border-radius: 4px;
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            margin-top: 5px;
        """)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.setContentsMargins(10, 10, 10, 10)
        
        card.setLayout(card_layout)
        card.setMinimumSize(QSize(220, 120))
        
        parent_layout.addWidget(card)
        return value_label  # Değeri güncellemek için etiket referansını döndür

    def on_item_changed(self, item, column):
        # Eğer bir şehir seçildiyse/seçimi kaldırıldıysa
        parent = item.parent()
        if not parent:  # Bu bir şehir item'ı
            # Tüm ilçelerin durumunu şehir ile aynı yap
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, item.checkState(0))
        else:  # Bu bir ilçe item'ı
            # Eğer tüm ilçeler seçili/seçilmemiş ise şehri de seç/seçimi kaldır
            parent_state = parent.checkState(0)
            all_same = True
            for i in range(parent.childCount()):
                if parent.child(i).checkState(0) != item.checkState(0):
                    all_same = False
                    break
            if all_same:
                parent.setCheckState(0, item.checkState(0))
        
        self.update_selection_summary()

    def update_selection_summary(self):
        selected = []
        total_population = 0
        
        for i in range(self.location_tree.topLevelItemCount()):
            sehir_item = self.location_tree.topLevelItem(i)
            sehir = sehir_item.text(0)
            
            if sehir_item.checkState(0) == Qt.Checked:
                # Tüm şehir seçili
                selected.append(sehir)
                total_population += sum(sehirler[sehir].values())
            else:
                # Seçili ilçeleri kontrol et
                selected_ilceler = []
                for j in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(j)
                    if ilce_item.checkState(0) == Qt.Checked:
                        ilce = ilce_item.text(0).split(" (")[0]  # İlçe adını nüfus bilgisinden ayır
                        selected_ilceler.append(ilce)
                        total_population += sehirler[sehir][ilce]
                
                if selected_ilceler:
                    selected.append(f"{sehir} ({', '.join(selected_ilceler)})")
        
        if selected:
            summary = f"Seçili Bölgeler ({total_population:,} kişi):\n" + "\n".join(selected)
        else:
            summary = "Seçili Bölgeler: Yok"
        
        self.selection_summary.setText(summary)

    def load_photos_for_city(self, city):
        """Şehir için biyometrik fotoğrafları yükle"""
        # Mutlak yolu oluştur - Biyometrik_veriler klasörü face_recognition altında
        photo_dir = os.path.join(CURRENT_DIR, "Biyometrik_veriler", city)
        print(f"Aranacak klasör: {photo_dir}")  # Debug için
        
        if not os.path.exists(photo_dir):
            print(f"Klasör bulunamadı: {photo_dir}")  # Debug için
            QMessageBox.warning(self, "Hata", f"{city} için biyometrik veri klasörü bulunamadı:\n{photo_dir}")
            return []
        
        photos = []
        for file in os.listdir(photo_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                photo_path = os.path.join(photo_dir, file)
                print(f"Fotoğraf bulundu: {photo_path}")  # Debug için
                photos.append(photo_path)
        
        if not photos:
            print(f"Klasörde fotoğraf bulunamadı: {photo_dir}")  # Debug için
            QMessageBox.warning(self, "Uyarı", f"{city} klasöründe fotoğraf bulunamadı")
        
        return photos

    def display_photos(self, photo_paths):
        """Fotoğrafları grid layout'ta göster"""
        # Mevcut fotoğrafları temizle
        while self.photo_grid.count():
            item = self.photo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Yeni fotoğrafları ekle
        row = 0
        col = 0
        max_cols = 3  # Her satırda maksimum fotoğraf sayısını azalt
        
        for path in photo_paths:
            try:
                photo_label = PhotoLabel()
                photo_label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #ccc;
                        border-radius: 5px;
                        background-color: #000000;
                    }
                """)
                pixmap = QPixmap(path)
                
                if pixmap.isNull():
                    print(f"Fotoğraf yüklenemedi: {path}")  # Debug için
                    continue
                    
                photo_label.setPixmap(pixmap)
                
                # Dosya adını göster
                name_label = QLabel(os.path.basename(path))
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setStyleSheet("color: #ffffff; padding: 5px; background-color: #6a0dad; border-radius: 3px; margin-top: 5px;")
                
                # Fotoğraf ve ismi için container
                container = QWidget()
                container.setStyleSheet("background-color: #000000; border: 1px solid #d0d0d0; border-radius: 5px; padding: 8px;")
                container_layout = QVBoxLayout(container)
                container_layout.addWidget(photo_label)
                container_layout.addWidget(name_label)
                
                self.photo_grid.addWidget(container, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Hata oluştu: {str(e)}")  # Debug için

    
    def update_edevlet_data(self):
        # Seçili bölgelerin verilerini güncelleme işlemi
        global KAYBOLAN_SAYISI, ESLESMESAYISI
        
        selected_cities = {}
        
        # İlk olarak seçili şehirleri ve ilçeleri topla
        for i in range(self.location_tree.topLevelItemCount()):
            sehir_item = self.location_tree.topLevelItem(i)
            sehir = sehir_item.text(0)
            
            # Şehir seçiliyse tüm ilçelerini ekle
            if sehir_item.checkState(0) == Qt.Checked:
                print(f"Seçili şehir: {sehir}")
                selected_cities[sehir] = []
                
                # Şehrin tüm ilçelerini ekle
                for j in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(j)
                    ilce = ilce_item.text(0).split(" (")[0]  # İlçe adını nüfus bilgisinden ayır
                    selected_cities[sehir].append(ilce)
            else:
                # Seçili ilçeleri kontrol et
                selected_districts = []
                for j in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(j)
                    if ilce_item.checkState(0) == Qt.Checked:
                        ilce = ilce_item.text(0).split(" (")[0]  # İlçe adını nüfus bilgisinden ayır
                        selected_districts.append(ilce)
                
                if selected_districts:
                    selected_cities[sehir] = selected_districts
        
        if not selected_cities:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir şehir veya ilçe seçin.")
            return
        
        # Seçili her şehir ve ilçe için klasör yapısını oluştur
        for sehir, ilceler in selected_cities.items():
            # Şehir klasörünü oluştur (eğer yoksa)
            sehir_path = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir)
            if not os.path.exists(sehir_path):
                os.makedirs(sehir_path)
                print(f"Şehir klasörü oluşturuldu: {sehir_path}")
            
            # Her ilçe için klasör yapısını oluştur
            if ilceler:
                for ilce in ilceler:
                    ilce_path = os.path.join(sehir_path, ilce)
                    if not os.path.exists(ilce_path):
                        os.makedirs(ilce_path)
                        print(f"İlçe klasörü oluşturuldu: {ilce_path}")
                    
                    # Yetişkin ve çocuk veri tabanı klasörlerini oluştur
                    yetiskin_path = os.path.join(ilce_path, "yetiskinVeriTabani")
                    if not os.path.exists(yetiskin_path):
                        os.makedirs(yetiskin_path)
                        print(f"Yetişkin veri tabanı klasörü oluşturuldu: {yetiskin_path}")
                    
                    cocuk_path = os.path.join(ilce_path, "cocukVeriTabani")
                    if not os.path.exists(cocuk_path):
                        os.makedirs(cocuk_path)
                        print(f"Çocuk veri tabanı klasörü oluşturuldu: {cocuk_path}")
                    
                    # Alt klasörleri oluştur (kaybolanlar, bulunanlar, eşleşenler)
                    for database_path in [yetiskin_path, cocuk_path]:
                        for folder in ["kaybolanlar", "bulunanlar", "eslesenler"]:
                            subfolder_path = os.path.join(database_path, folder)
                            if not os.path.exists(subfolder_path):
                                os.makedirs(subfolder_path)
                                print(f"Alt klasör oluşturuldu: {subfolder_path}")
            else:
                # Şehir seçili ama ilçe belirtilmemiş, tüm ilçeleri ekle
                for ilce in sehirler[sehir].keys():
                    ilce_path = os.path.join(sehir_path, ilce)
                    if not os.path.exists(ilce_path):
                        os.makedirs(ilce_path)
                        print(f"İlçe klasörü oluşturuldu: {ilce_path}")
                    
                    # Yetişkin ve çocuk veri tabanı klasörlerini oluştur
                    yetiskin_path = os.path.join(ilce_path, "yetiskinVeriTabani")
                    if not os.path.exists(yetiskin_path):
                        os.makedirs(yetiskin_path)
                        print(f"Yetişkin veri tabanı klasörü oluşturuldu: {yetiskin_path}")
                    
                    cocuk_path = os.path.join(ilce_path, "cocukVeriTabani")
                    if not os.path.exists(cocuk_path):
                        os.makedirs(cocuk_path)
                        print(f"Çocuk veri tabanı klasörü oluşturuldu: {cocuk_path}")
                    
                    # Alt klasörleri oluştur (kaybolanlar, bulunanlar, eşleşenler)
                    for database_path in [yetiskin_path, cocuk_path]:
                        for folder in ["kaybolanlar", "bulunanlar", "eslesenler"]:
                            subfolder_path = os.path.join(database_path, folder)
                            if not os.path.exists(subfolder_path):
                                os.makedirs(subfolder_path)
                                print(f"Alt klasör oluşturuldu: {subfolder_path}")
        
        # İlerleme çubuğunu göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Seçili bölgelerden kayıp ve bulunan kişilerin fotoğraflarını topla
        kaybolanlar = []
        bulunanlar = []

        
        self.progress_bar.setValue(20)
        
        # Fotoğrafları topla
        for sehir, ilceler in selected_cities.items():
            sehir_path = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir)
            
            if not ilceler:
                # Tüm ilçeler için
                ilceler = sehirler[sehir].keys()
            
            for ilce in ilceler:
                ilce_path = os.path.join(sehir_path, ilce)
                # Dosya yolundaki Türkçe karakterler için önlem alıyoruz
                print(f"İşleniyor: Şehir={sehir}, İlçe={ilce}")
                
                # Yetişkin veritabanı için işlem
                try:
                    yetiskin_path = os.path.join(ilce_path, "yetiskinVeriTabani")
                    
                    # Kaybolanlar klasörü
                    kaybolan_klasor = os.path.join(yetiskin_path, "kaybolanlar")
                    self.process_folder(kaybolan_klasor, "yetiskin", "kaybolan", sehir, ilce, kaybolanlar)
                    
                    # Bulunanlar klasörü
                    bulunan_klasor = os.path.join(yetiskin_path, "bulunanlar")
                    self.process_folder(bulunan_klasor, "yetiskin", "bulunan", sehir, ilce, bulunanlar)
                    
                    # Çocuk veritabanı
                    cocuk_path = os.path.join(ilce_path, "cocukVeriTabani")
                    
                    # Kaybolanlar klasörü
                    kaybolan_klasor = os.path.join(cocuk_path, "kaybolanlar")
                    self.process_folder(kaybolan_klasor, "cocuk", "kaybolan", sehir, ilce, kaybolanlar)
                    
                    # Bulunanlar klasörü
                    bulunan_klasor = os.path.join(cocuk_path, "bulunanlar")
                    self.process_folder(bulunan_klasor, "cocuk", "bulunan", sehir, ilce, bulunanlar)
                
                except Exception as e:
                    print(f"İlçe işleme hatası: {ilce} - {str(e)}")
        
        self.progress_bar.setValue(40)
        
        try:
            # Faiss kütüphanesini içe aktar - yoksa normal işlem yap
            import faiss
            faiss_available = True
        except ImportError:
            faiss_available = False
            print("Faiss kütüphanesi bulunamadı. Normal benzerlik hesaplama kullanılacak.")
        
        # DeepFace'i içe aktar
        try:
            from deepface import DeepFace
            deepface_available = True
        except ImportError:
            deepface_available = False
            QMessageBox.warning(self, "Hata", "DeepFace kütüphanesi bulunamadı. Yüz tanıma yapılamayacak.")
            self.progress_bar.setVisible(False)
            return
        
        self.progress_bar.setValue(50)
        
        # Önce mevcut embeddinglari yükle
        print("Mevcut embeddingler kontrol ediliyor...")
        existing_embeddings = self.load_existing_embeddings(selected_cities)
        
        # Kaybolanlar ve bulunanlar için dosya yolları hazırla
        kaybolanlar_dict = {}  # dosya_yolu -> embedding_ve_bilgiler
        bulunanlar_dict = {}   # dosya_yolu -> embedding_ve_bilgiler
        
        # Mevcut embeddinglari sözlüğe ekle
        for item in existing_embeddings["kaybolanlar"]:
            if "yol" in item and "embedding" in item:
                kaybolanlar_dict[item["yol"]] = item
        
        for item in existing_embeddings["bulunanlar"]:
            if "yol" in item and "embedding" in item:
                bulunanlar_dict[item["yol"]] = item
        
        # Mevcut olmayan fotoğraflar için hazırla
        missing_kaybolanlar = []
        missing_bulunanlar = []
        
        # Mevcut embeddingi olmayan kaybolanları bul
        for item in kaybolanlar:
            if item["yol"] not in kaybolanlar_dict:
                missing_kaybolanlar.append(item)
        
        # Mevcut embeddingi olmayan bulunanları bul
        for item in bulunanlar:
            if item["yol"] not in bulunanlar_dict:
                missing_bulunanlar.append(item)
        
        print(f"Toplam kaybolan: {len(kaybolanlar)}, bunlardan {len(missing_kaybolanlar)} tanesi yeni")
        print(f"Toplam bulunan: {len(bulunanlar)}, bunlardan {len(missing_bulunanlar)} tanesi yeni")
        
        # Resimlerin embeddingllerini çıkar
        embeddings_kaybolanlar = []
        embeddings_bulunanlar = []
        
        def embedding_al(resim_yolu):
            """
            Verilen resim yolundan yüz embedding'i çıkarır.
            Türkçe karakter ve dosya yolu sorunlarını çözer.
            """
            print(f"Dosya işleniyor: {resim_yolu}")
            
            try:
                # Önce dosyayı belleğe okumayı dene
                with open(resim_yolu, 'rb') as file:
                    img_data = file.read()
                
                # Geçici bir dosya oluştur
                temp_file_name = f"temp_{uuid.uuid4().hex}.jpg"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
                
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(img_data)
                
                try:
                    # Geçici dosya üzerinden DeepFace işlemi yap
                    embedding = DeepFace.represent(
                        img_path=temp_file_path,
                        model_name="Facenet",
                        enforce_detection=True
                    )[0]["embedding"]
                    print(f"✅ Embedding alındı: {os.path.basename(resim_yolu)}")
                    os.remove(temp_file_path)  # Geçici dosyayı sil
                    return embedding, False
                except Exception as e1:
                    print(f"⚠️ Yüz algılanamadı: {os.path.basename(resim_yolu)} | {str(e1)}")
                    
                    # DeepFace başarısız olduysa, OpenCV ile yeniden boyutlandırma dene
                    try:
                        # Bellek üzerinden OpenCV ile oku
                        img_array = np.frombuffer(img_data, np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        
                        if img is None:
                            print(f"❌ Resim okunamadı: {resim_yolu}")
                            os.remove(temp_file_path)  # Geçici dosyayı sil
                            return None, False
                        
                        # Renk kanallarını düzenle
                        if len(img.shape) > 2:
                            if img.shape[2] == 4:
                                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                            elif len(img.shape) == 2:
                                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                        
                        # Boyutlandır
                        h, w = img.shape[:2]
                        target_size = 640
                        scale = target_size / max(h, w)
                        yeni_boyut = (int(w * scale), int(h * scale))
                        img = cv2.resize(img, yeni_boyut)
                        
                        # Yeni bir geçici dosya oluştur
                        resize_temp_file = f"resize_{uuid.uuid4().hex}.jpg"
                        resize_temp_path = os.path.join(tempfile.gettempdir(), resize_temp_file)
                        
                        # Dosyayı bellek üzerinden kaydet
                        is_success, buffer = cv2.imencode(".jpg", img)
                        if not is_success:
                            print(f"❌ Resim kaydedilemedi")
                            os.remove(temp_file_path)  # İlk geçici dosyayı sil
                            return None, False
                        
                        with open(resize_temp_path, 'wb') as f:
                            f.write(buffer)
                        
                        # Boyutlandırılmış resim üzerinden yeniden dene
                        try:
                            embedding = DeepFace.represent(
                                img_path=resize_temp_path,
                                model_name="Facenet",
                                detector_backend="mtcnn",
                                enforce_detection=True
                            )[0]["embedding"]
                            print(f"✅ Embedding (2. deneme): {os.path.basename(resim_yolu)}")
                            return embedding, True
                        except Exception as e2:
                            print(f"❌ Başarısız (2. deneme): {os.path.basename(resim_yolu)} | {str(e2)}")
                            return None, False
                        finally:
                            if os.path.exists(resize_temp_path):
                                os.remove(resize_temp_path)  # Boyutlandırılmış geçici dosyayı sil
                            os.remove(temp_file_path)  # İlk geçici dosyayı sil
                    except Exception as e3:
                        print(f"❌ İşlem hatası: {str(e3)}")
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)  # Geçici dosyayı sil
                        return None, False
            except Exception as e4:
                print(f"❌ Dosya okuma hatası: {str(e4)}")
                return None, False
        
        # Önce mevcut embeddinglari listeye ekle
        for item in kaybolanlar:
            if item["yol"] in kaybolanlar_dict:
                embeddings_kaybolanlar.append(kaybolanlar_dict[item["yol"]])
        
        for item in bulunanlar:
            if item["yol"] in bulunanlar_dict:
                embeddings_bulunanlar.append(bulunanlar_dict[item["yol"]])
        
        # Sadece eksik olan fotoğraflar için embeddingler oluştur
        self.progress_bar.setValue(60)
        print("Yeni kaybolan kişilerin fotoğraflarından yüz özellikleri çıkarılıyor...")
        for i, kaybolan in enumerate(missing_kaybolanlar):
            embedding, is_second_try = embedding_al(kaybolan["yol"])
            if embedding is not None:
                kaybolan["embedding"] = embedding
                kaybolan["is_second_try"] = is_second_try
                embeddings_kaybolanlar.append(kaybolan)
            
            # Her 10 fotoğrafta bir ilerleme çubuğunu güncelle
            if i % 10 == 0:
                progress = 60 + int((i / max(len(missing_kaybolanlar), 1)) * 15) if len(missing_kaybolanlar) > 0 else 75
                self.progress_bar.setValue(progress)
        
        self.progress_bar.setValue(75)
        print("Yeni bulunan kişilerin fotoğraflarından yüz özellikleri çıkarılıyor...")
        for i, bulunan in enumerate(missing_bulunanlar):
            embedding, is_second_try = embedding_al(bulunan["yol"])
            if embedding is not None:
                bulunan["embedding"] = embedding
                bulunan["is_second_try"] = is_second_try
                embeddings_bulunanlar.append(bulunan)
            
            # Her 10 fotoğrafta bir ilerleme çubuğunu güncelle
            if i % 10 == 0:
                progress = 75 + int((i / max(len(missing_bulunanlar), 1)) * 15) if len(missing_bulunanlar) > 0 else 90
                self.progress_bar.setValue(progress)
        
        self.progress_bar.setValue(90)
        
        print(f"Toplam {len(embeddings_kaybolanlar)} kaybolan ve {len(embeddings_bulunanlar)} bulunan kişi işlendi.")
        
        eslesmeler = []
        
        # Önce tüm embeddingler .npy dosyalarına kaydedilsin
        print("Embeddingler .npy dosyalarına kaydediliyor...")
        self.save_embeddings_to_npy(selected_cities, embeddings_kaybolanlar, embeddings_bulunanlar)
        
        # Şimdi kaydedilen .npy dosyalarını kullanarak Faiss ile arama yapalım
        print("Faiss ile arama başlatılıyor...")
        eslesmeler = self.search_with_faiss_from_npy(selected_cities)
        
        # Faiss yoksa veya kullanılamazsa, hata mesajı göster
        if not faiss_available:
            QMessageBox.warning(self, "Uyarı", "Faiss kütüphanesi bulunamadı. Embeddingler kaydedildi ama arama yapılamadı.")
        
        self.progress_bar.setValue(100)
        
        # Eşleşmeleri göster
        self.display_matches(eslesmeler)
        
        # Eşleşmeleri JSON dosyalarına kaydet ve fotoğrafları eslesenler klasörüne taşı
        self.save_matches_to_json(eslesmeler)
        
        # İstatistikleri güncelle
        self.stats_label.setText(f"Toplam Kayıtlı Biyometrik Veri: {len(kaybolanlar) + len(bulunanlar)} | Bulunan Eşleşme: {len(eslesmeler)}")
        KAYBOLAN_SAYISI = len(kaybolanlar)
        ESLESMESAYISI = len(eslesmeler)
        
        # Stat kartlarını güncelle
        self.kayip_stat_card.setText(self.kaybolan_sayisi(KAYBOLAN_SAYISI))
        self.eslesme_stat_card.setText(self.eslesme_sayisi(ESLESMESAYISI))
        
        QMessageBox.information(self, "Bilgi", f"Tarama tamamlandı. {len(eslesmeler)} eşleşme bulundu ve kaydedildi.")

    def process_folder(self, folder_path, tip, tur, sehir, ilce, result_list):
        """Belirtilen klasördeki fotoğrafları işler ve listeye ekler"""
        if not os.path.exists(folder_path):
            print(f"Klasör bulunamadı: {folder_path}")
            return
        
        try:
            # Klasördeki tüm dosyaları al
            files = os.listdir(folder_path)
            print(f"Klasörde {len(files)} dosya bulundu: {folder_path}")
            
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(folder_path, file)
                    result_list.append({
                        "yol": file_path,
                        "tip": tip,
                        "tur": tur,
                        "sehir": sehir,
                        "ilce": ilce
                    })
        except Exception as e:
            print(f"Klasör okuma hatası: {folder_path} - {str(e)}")

    def display_matches(self, eslesmeler):
        """Eşleşmeleri görüntüle"""
        # Mevcut fotoğrafları temizle
        while self.photo_grid.count():
            item = self.photo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Eşleşme yoksa bilgi ver
        if not eslesmeler:
            empty_label = QLabel("Eşleşme bulunamadı")
            empty_label.setStyleSheet("color: white; font-size: 18px; background-color: #000000; padding: 20px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.photo_grid.addWidget(empty_label, 0, 0)
            return
        
        # Eşleşmeleri göster
        row = 0
        col = 0
        max_cols = 1  # Her satırda bir eşleşme çifti
        
        for eslesme in eslesmeler:
            try:
                # Kaybolan ve bulunan dosya adlarını al
                kaybolan_dosya_adi = os.path.basename(eslesme["kaybolan"]["yol"])
                bulunan_dosya_adi = os.path.basename(eslesme["bulunan"]["yol"])
                
                # Container oluştur
                match_container = QWidget()
                match_container.setStyleSheet("background-color: #000000; border: 1px solid #6a0dad; border-radius: 8px; padding: 15px; margin: 10px;")
                match_layout = QVBoxLayout(match_container)
                
                # Başlık - eşleşme bilgisi
                title_widget = QWidget()
                title_layout = QHBoxLayout(title_widget)
                
                match_title = QLabel(f"Eşleşme Benzerliği: {eslesme['benzerlik']:.4f}")
                match_title.setStyleSheet("color: white; font-weight: bold; font-size: 16px; background-color: #6a0dad; padding: 8px; border-radius: 4px;")
                match_title.setAlignment(Qt.AlignCenter)
                title_layout.addWidget(match_title)
                
                match_layout.addWidget(title_widget)
                
                # Fotoğraf widget'ı
                photos_widget = QWidget()
                photos_layout = QHBoxLayout(photos_widget)
                
                # Kaybolan kişi
                kaybolan_container = QWidget()
                kaybolan_layout = QVBoxLayout(kaybolan_container)
                
                kaybolan_title = QLabel(f"Kaybolan {'Çocuk' if eslesme['kaybolan']['tip'] == 'cocuk' else 'Yetişkin'}: {kaybolan_dosya_adi}")
                kaybolan_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background-color: #4b0082; padding: 5px; border-radius: 4px;")
                kaybolan_title.setAlignment(Qt.AlignCenter)
                kaybolan_title.setWordWrap(True)
                kaybolan_layout.addWidget(kaybolan_title)
                
                kaybolan_photo = PhotoLabel()
                kaybolan_photo.setMinimumSize(200, 200)
                kaybolan_photo.setMaximumSize(200, 200)
                kaybolan_pixmap = QPixmap(eslesme["kaybolan"]["yol"])
                kaybolan_photo.setPixmap(kaybolan_pixmap)
                kaybolan_layout.addWidget(kaybolan_photo)
                
                kaybolan_info = QLabel(f"Kaybolduğu Yer: {eslesme['kaybolan']['sehir']} / {eslesme['kaybolan']['ilce']}")
                kaybolan_info.setStyleSheet("color: white; padding: 5px; background-color: #000000; border: 1px solid #6a0dad; border-radius: 4px;")
                kaybolan_info.setWordWrap(True)
                kaybolan_layout.addWidget(kaybolan_info)
                
                photos_layout.addWidget(kaybolan_container)
                
                # Ok işareti
                arrow_label = QLabel("→")
                arrow_label.setStyleSheet("color: #6a0dad; font-size: 30px; font-weight: bold;")
                arrow_label.setAlignment(Qt.AlignCenter)
                photos_layout.addWidget(arrow_label)
                
                # Bulunan kişi
                bulunan_container = QWidget()
                bulunan_layout = QVBoxLayout(bulunan_container)
                
                bulunan_title = QLabel(f"Bulunan {'Çocuk' if eslesme['bulunan']['tip'] == 'cocuk' else 'Yetişkin'}: {bulunan_dosya_adi}")
                bulunan_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background-color: #4b0082; padding: 5px; border-radius: 4px;")
                bulunan_title.setAlignment(Qt.AlignCenter)
                bulunan_title.setWordWrap(True)
                bulunan_layout.addWidget(bulunan_title)
                
                bulunan_photo = PhotoLabel()
                bulunan_photo.setMinimumSize(200, 200)
                bulunan_photo.setMaximumSize(200, 200)
                bulunan_pixmap = QPixmap(eslesme["bulunan"]["yol"])
                bulunan_photo.setPixmap(bulunan_pixmap)
                bulunan_layout.addWidget(bulunan_photo)
                
                bulunan_info = QLabel(f"Bulunduğu Yer: {eslesme['bulunan']['sehir']} / {eslesme['bulunan']['ilce']}")
                bulunan_info.setStyleSheet("color: white; padding: 5px; background-color: #000000; border: 1px solid #6a0dad; border-radius: 4px;")
                bulunan_info.setWordWrap(True)
                bulunan_layout.addWidget(bulunan_info)
                
                photos_layout.addWidget(bulunan_container)
                
                match_layout.addWidget(photos_widget)
                
                # Eşleşme container'ını ekle
                self.photo_grid.addWidget(match_container, row, col)
                
                row += 1
                
            except Exception as e:
                print(f"Eşleşme gösterme hatası: {str(e)}")
        
        # Scroll area'yı güncelle
        self.scroll_area.ensureVisible(0, 0)

    def save_matches_to_json(self, eslesmeler):
        """Eşleşmeleri ilgili klasörlerdeki JSON dosyalarına kaydeder ve fotoğrafları eslesenler klasörüne taşır"""
        if not eslesmeler:
            return
        
        # Eşleşmeleri şehir ve ilçelere göre grupla
        grouped_matches = {}
        
        for eslesme in eslesmeler:
            kaybolan = eslesme["kaybolan"]
            bulunan = eslesme["bulunan"]
            
            sehir = kaybolan["sehir"]
            ilce = kaybolan["ilce"]
            tip = kaybolan["tip"]  # yetiskin veya cocuk
            
            # Şehir anahtarını oluştur
            if sehir not in grouped_matches:
                grouped_matches[sehir] = {}
            
            # İlçe anahtarını oluştur
            if ilce not in grouped_matches[sehir]:
                grouped_matches[sehir][ilce] = {}
            
            # Tip anahtarını oluştur (yetiskin/cocuk)
            if tip not in grouped_matches[sehir][ilce]:
                grouped_matches[sehir][ilce][tip] = []
            
            # Eşleşme bilgilerini kaydet
            match_info = {
                "kaybolan_dosya": kaybolan["yol"],
                "bulunan_dosya": bulunan["yol"],
                "kaybolan_dosya_adi": os.path.basename(kaybolan["yol"]),
                "bulunan_dosya_adi": os.path.basename(bulunan["yol"]),
                "benzerlik": float(eslesme["benzerlik"]),
                "eslesme_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            grouped_matches[sehir][ilce][tip].append(match_info)
        
        # Her şehir ve ilçe için JSON dosyasını kaydet ve fotoğrafları taşı
        for sehir, ilceler in grouped_matches.items():
            for ilce, tipler in ilceler.items():
                for tip, matches in tipler.items():
                    # Veritabanı yolu
                    if tip == "yetiskin":
                        veritabani_klasoru = "yetiskinVeriTabani"
                    else:
                        veritabani_klasoru = "cocukVeriTabani"
                    
                    # JSON dosya yolu
                    json_path = os.path.join(
                        CURRENT_DIR, 
                        "Biyometrik_veriler", 
                        sehir, 
                        ilce, 
                        veritabani_klasoru, 
                        "eslesenler.json"
                    )
                    
                    # Eşleşenler klasörü
                    eslesenler_klasoru = os.path.join(
                        CURRENT_DIR, 
                        "Biyometrik_veriler", 
                        sehir, 
                        ilce, 
                        veritabani_klasoru,
                        "eslesenler"
                    )
                    
                    # Eşleşenler klasörünün varlığını kontrol et, yoksa oluştur
                    if not os.path.exists(eslesenler_klasoru):
                        os.makedirs(eslesenler_klasoru)
                    
                    # Mevcut eşleşmeleri oku (eğer dosya varsa)
                    existing_matches = []
                    try:
                        if os.path.exists(json_path):
                            with open(json_path, 'r', encoding='utf-8') as f:
                                existing_matches = json.load(f)
                    except Exception as e:
                        print(f"JSON dosyası okuma hatası: {json_path} - {str(e)}")
                    
                    # Yeni eşleşmeleri işle ve fotoğrafları taşı
                    updated_matches = []
                    for match in existing_matches:
                        # Eğer dosyalar hala varsa, listeye ekle
                        if os.path.exists(match["kaybolan_dosya"]) and os.path.exists(match["bulunan_dosya"]):
                            updated_matches.append(match)
                    
                    # Yeni eşleşmeleri işle
                    for match in matches:
                        kaybolan_dosya = match["kaybolan_dosya"]
                        bulunan_dosya = match["bulunan_dosya"]
                        
                        # Dosyalar halen mevcut mu kontrol et
                        if not os.path.exists(kaybolan_dosya) or not os.path.exists(bulunan_dosya):
                            print(f"Dosya bulunamadı, eşleşme atlanıyor: {match['kaybolan_dosya_adi']} -> {match['bulunan_dosya_adi']}")
                            continue
                        
                        # Eşleşenler klasörüne taşınacak dosya adları
                        kaybolan_hedef = os.path.join(eslesenler_klasoru, f"k_{match['kaybolan_dosya_adi']}")
                        bulunan_hedef = os.path.join(eslesenler_klasoru, f"b_{match['bulunan_dosya_adi']}")
                        
                        try:
                            # Fotoğrafları taşı
                            shutil.copy2(kaybolan_dosya, kaybolan_hedef)
                            shutil.copy2(bulunan_dosya, bulunan_hedef)
                            
                            # JSON'daki dosya yollarını güncelle
                            match["kaybolan_dosya"] = kaybolan_hedef
                            match["bulunan_dosya"] = bulunan_hedef
                            
                            # Güncellenmiş eşleşme bilgisini ekle
                            updated_matches.append(match)
                            
                            print(f"Fotoğraflar kopyalandı: {match['kaybolan_dosya_adi']} ve {match['bulunan_dosya_adi']}")
                        except Exception as e:
                            print(f"Fotoğraf kopyalama hatası: {str(e)}")
                    
                    # JSON dosyasına kaydet
                    try:
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(updated_matches, f, ensure_ascii=False, indent=2)
                        print(f"Eşleşmeler kaydedildi: {json_path} - Toplam {len(updated_matches)} eşleşme")
                    except Exception as e:
                        print(f"JSON dosyası yazma hatası: {json_path} - {str(e)}") 

    def kaybolan_sayisi(self, sayi):
        return str(sayi)

    def eslesme_sayisi(self, sayi):
        return str(sayi)

    def save_embeddings_to_npy(self, selected_cities, embeddings_kaybolanlar, embeddings_bulunanlar):
        """Embeddingler ve yolları her ilçe için .npy dosyalarına kaydeder"""
        print("Embeddingler .npy dosyalarına kaydediliyor...")
        
        # İlçelere göre embeddinglari grupla
        yetiskin_embeddings = {}
        cocuk_embeddings = {}
        
        # Kaybolanlar için
        for embed in embeddings_kaybolanlar:
            if embed.get("embedding") is None:
                continue
            
            sehir = embed["sehir"]
            ilce = embed["ilce"]
            tip = embed["tip"]
            
            key = f"{sehir}_{ilce}"
            
            if tip == "yetiskin":
                if key not in yetiskin_embeddings:
                    yetiskin_embeddings[key] = {
                        "kaybolan_embeddings": [],
                        "kaybolan_paths": [],
                        "bulunan_embeddings": [],
                        "bulunan_paths": []
                    }
                yetiskin_embeddings[key]["kaybolan_embeddings"].append(embed["embedding"])
                yetiskin_embeddings[key]["kaybolan_paths"].append(embed["yol"])
            else:  # cocuk
                if key not in cocuk_embeddings:
                    cocuk_embeddings[key] = {
                        "kaybolan_embeddings": [],
                        "kaybolan_paths": [],
                        "bulunan_embeddings": [],
                        "bulunan_paths": []
                    }
                cocuk_embeddings[key]["kaybolan_embeddings"].append(embed["embedding"])
                cocuk_embeddings[key]["kaybolan_paths"].append(embed["yol"])
        
        # Bulunanlar için
        for embed in embeddings_bulunanlar:
            if embed.get("embedding") is None:
                continue
            
            sehir = embed["sehir"]
            ilce = embed["ilce"]
            tip = embed["tip"]
            
            key = f"{sehir}_{ilce}"
            
            if tip == "yetiskin":
                if key not in yetiskin_embeddings:
                    yetiskin_embeddings[key] = {
                        "kaybolan_embeddings": [],
                        "kaybolan_paths": [],
                        "bulunan_embeddings": [],
                        "bulunan_paths": []
                    }
                yetiskin_embeddings[key]["bulunan_embeddings"].append(embed["embedding"])
                yetiskin_embeddings[key]["bulunan_paths"].append(embed["yol"])
            else:  # cocuk
                if key not in cocuk_embeddings:
                    cocuk_embeddings[key] = {
                        "kaybolan_embeddings": [],
                        "kaybolan_paths": [],
                        "bulunan_embeddings": [],
                        "bulunan_paths": []
                    }
                cocuk_embeddings[key]["bulunan_embeddings"].append(embed["embedding"])
                cocuk_embeddings[key]["bulunan_paths"].append(embed["yol"])
        
        # .npy dosyalarını her ilçe için kaydet
        for sehir, ilceler in selected_cities.items():
            if not ilceler:
                # Tüm ilçeler için
                ilceler = sehirler[sehir].keys()
            
            for ilce in ilceler:
                key = f"{sehir}_{ilce}"
                
                # Yetişkin veritabanı
                if key in yetiskin_embeddings:
                    yetiskin_path = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir, ilce, "yetiskinVeriTabani")
                    
                    # Kaybolanlar
                    if yetiskin_embeddings[key]["kaybolan_embeddings"]:
                        kaybolan_embeddings_path = os.path.join(yetiskin_path, "kaybolan_embeddings.npy")
                        kaybolan_paths_path = os.path.join(yetiskin_path, "kaybolan_paths.npy")
                        
                        try:
                            np.save(kaybolan_embeddings_path, np.array(yetiskin_embeddings[key]["kaybolan_embeddings"]))
                            np.save(kaybolan_paths_path, np.array(yetiskin_embeddings[key]["kaybolan_paths"]))
                            print(f"Yetişkin kaybolanlar .npy dosyaları kaydedildi: {sehir}/{ilce}")
                        except Exception as e:
                            print(f"Yetişkin kaybolanlar .npy kaydetme hatası: {sehir}/{ilce} - {str(e)}")
                    
                    # Bulunanlar
                    if yetiskin_embeddings[key]["bulunan_embeddings"]:
                        bulunan_embeddings_path = os.path.join(yetiskin_path, "bulunan_embeddings.npy")
                        bulunan_paths_path = os.path.join(yetiskin_path, "bulunan_paths.npy")
                        
                        try:
                            np.save(bulunan_embeddings_path, np.array(yetiskin_embeddings[key]["bulunan_embeddings"]))
                            np.save(bulunan_paths_path, np.array(yetiskin_embeddings[key]["bulunan_paths"]))
                            print(f"Yetişkin bulunanlar .npy dosyaları kaydedildi: {sehir}/{ilce}")
                        except Exception as e:
                            print(f"Yetişkin bulunanlar .npy kaydetme hatası: {sehir}/{ilce} - {str(e)}")
                
                # Çocuk veritabanı
                if key in cocuk_embeddings:
                    cocuk_path = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir, ilce, "cocukVeriTabani")
                    
                    # Kaybolanlar
                    if cocuk_embeddings[key]["kaybolan_embeddings"]:
                        kaybolan_embeddings_path = os.path.join(cocuk_path, "kaybolan_embeddings.npy")
                        kaybolan_paths_path = os.path.join(cocuk_path, "kaybolan_paths.npy")
                        
                        try:
                            np.save(kaybolan_embeddings_path, np.array(cocuk_embeddings[key]["kaybolan_embeddings"]))
                            np.save(kaybolan_paths_path, np.array(cocuk_embeddings[key]["kaybolan_paths"]))
                            print(f"Çocuk kaybolanlar .npy dosyaları kaydedildi: {sehir}/{ilce}")
                        except Exception as e:
                            print(f"Çocuk kaybolanlar .npy kaydetme hatası: {sehir}/{ilce} - {str(e)}")
                    
                    # Bulunanlar
                    if cocuk_embeddings[key]["bulunan_embeddings"]:
                        bulunan_embeddings_path = os.path.join(cocuk_path, "bulunan_embeddings.npy")
                        bulunan_paths_path = os.path.join(cocuk_path, "bulunan_paths.npy")
                        
                        try:
                            np.save(bulunan_embeddings_path, np.array(cocuk_embeddings[key]["bulunan_embeddings"]))
                            np.save(bulunan_paths_path, np.array(cocuk_embeddings[key]["bulunan_paths"]))
                            print(f"Çocuk bulunanlar .npy dosyaları kaydedildi: {sehir}/{ilce}")
                        except Exception as e:
                            print(f"Çocuk bulunanlar .npy kaydetme hatası: {sehir}/{ilce} - {str(e)}")
        
        print("Embeddingler .npy dosyalarına kaydedildi!") 

    def search_with_faiss_from_npy(self, selected_cities):
        """Kaydedilmiş .npy dosyalarını kullanarak Faiss ile arama yapar"""
        print("Kaydedilmiş .npy dosyaları ile eşleşme aranıyor...")
        eslesmeler = []
        
        # Faiss'in olup olmadığını kontrol et
        try:
            import faiss
        except ImportError:
            print("Faiss kütüphanesi bulunamadı. Hızlı arama yapılamayacak.")
            return eslesmeler
        
        # Seçili şehir ve ilçeleri dolaş
        for sehir, ilceler in selected_cities.items():
            if not ilceler:
                # Tüm ilçeler için
                ilceler = sehirler[sehir].keys()
            
            for ilce in ilceler:
                # Yetişkin veritabanı için arama
                yetiskin_path = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir, ilce, "yetiskinVeriTabani")
                yetiskin_eslesmeler = self.process_embeddings_with_faiss(yetiskin_path, "yetiskin", sehir, ilce)
                eslesmeler.extend(yetiskin_eslesmeler)
                
                # Çocuk veritabanı için arama
                cocuk_path = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir, ilce, "cocukVeriTabani")
                cocuk_eslesmeler = self.process_embeddings_with_faiss(cocuk_path, "cocuk", sehir, ilce)
                eslesmeler.extend(cocuk_eslesmeler)
        
        print(f"Toplam {len(eslesmeler)} eşleşme bulundu.")
        return eslesmeler
    
    def process_embeddings_with_faiss(self, veritabani_yolu, tip, sehir, ilce):
        """Belirtilen veritabanındaki embeddingler ile Faiss arama yapar"""
        eslesmeler = []
        
        try:
            import faiss
            
            # Embedding dosya yolları
            kaybolan_embeddings_path = os.path.join(veritabani_yolu, "kaybolan_embeddings.npy")
            kaybolan_paths_path = os.path.join(veritabani_yolu, "kaybolan_paths.npy")
            bulunan_embeddings_path = os.path.join(veritabani_yolu, "bulunan_embeddings.npy")
            bulunan_paths_path = os.path.join(veritabani_yolu, "bulunan_paths.npy")
            
            # Dosya varlığını kontrol et
            if not (os.path.exists(kaybolan_embeddings_path) and os.path.exists(kaybolan_paths_path) and 
                    os.path.exists(bulunan_embeddings_path) and os.path.exists(bulunan_paths_path)):
                print(f"{sehir}/{ilce} için gerekli .npy dosyaları eksik.")
                return eslesmeler
            
            try:
                # Dosyaları yükle
                kaybolan_embeddings = np.load(kaybolan_embeddings_path)
                kaybolan_paths = np.load(kaybolan_paths_path)
                bulunan_embeddings = np.load(bulunan_embeddings_path)
                bulunan_paths = np.load(bulunan_paths_path)
                
                # Her iki dizide de veri var mı kontrol et
                if len(kaybolan_embeddings) == 0 or len(bulunan_embeddings) == 0:
                    print(f"{sehir}/{ilce} için embedding verileri boş.")
                    return eslesmeler
                
                # Vektör boyutunu kontrol et
                if len(kaybolan_embeddings.shape) < 2:
                    kaybolan_embeddings = kaybolan_embeddings.reshape(1, -1)
                if len(bulunan_embeddings.shape) < 2:
                    bulunan_embeddings = bulunan_embeddings.reshape(1, -1)
                
                # Faiss indeksi oluştur
                d = bulunan_embeddings.shape[1]  # Boyut
                index = faiss.IndexFlatIP(d)  # Cosine benzerliği için iç çarpım indeksi
                
                # Float32 tipine dönüştür
                kaybolan_embeddings = kaybolan_embeddings.astype(np.float32)
                bulunan_embeddings = bulunan_embeddings.astype(np.float32)
                
                # Vektörleri normalize et (cosine benzerliği için)
                faiss.normalize_L2(kaybolan_embeddings)
                faiss.normalize_L2(bulunan_embeddings)
                
                # Bulunanları indekse ekle
                index.add(bulunan_embeddings)
                
                # Kaybolanlara en yakın bulunanları bul
                k = 1  # Her kaybolan için en iyi eşleşme
                D, I = index.search(kaybolan_embeddings, k)
                
                # Eşleşmeleri oluştur
                for i in range(len(kaybolan_paths)):
                    benzerlik = D[i][0]  # Benzerlik skoru
                    bulunan_idx = I[i][0]  # Bulunan indeksi
                    
                    # Tip kontrolü yap ve uygun eşik değerini belirle
                    if tip == "yetiskin":
                        esik = 0.45  # Yetişkin için eşik değeri
                    else:  # Çocuk
                        esik = 0.75  # Çocuk için eşik değeri
                    
                    if benzerlik > esik:
                        kaybolan_dict = {
                            "yol": str(kaybolan_paths[i]),
                            "tip": tip,
                            "tur": "kaybolan",
                            "sehir": sehir,
                            "ilce": ilce,
                        }
                        
                        bulunan_dict = {
                            "yol": str(bulunan_paths[bulunan_idx]),
                            "tip": tip,
                            "tur": "bulunan",
                            "sehir": sehir,
                            "ilce": ilce,
                        }
                        
                        eslesme = {
                            "kaybolan": kaybolan_dict,
                            "bulunan": bulunan_dict,
                            "benzerlik": float(benzerlik)
                        }
                        
                        eslesmeler.append(eslesme)
                        print(f"Eşleşme bulundu: {os.path.basename(kaybolan_dict['yol'])} -> {os.path.basename(bulunan_dict['yol'])}, Skor: {benzerlik:.4f}, Eşik: {esik}")
                
                return eslesmeler
                
            except Exception as e:
                print(f"{sehir}/{ilce} için .npy dosyalarını okuma hatası: {str(e)}")
                return eslesmeler
                
        except ImportError:
            print("Faiss kütüphanesi bulunamadı. Hızlı arama yapılamayacak.")
            return eslesmeler
        
        return eslesmeler

    def load_existing_embeddings(self, selected_cities):
        """Seçili şehir ve ilçeler için mevcut embeddinglari yükler"""
        result = {
            "kaybolanlar": [],
            "bulunanlar": []
        }
        
        # Seçili şehir ve ilçeleri dolaş
        for sehir, ilceler in selected_cities.items():
            if not ilceler:
                # Tüm ilçeler için
                ilceler = sehirler[sehir].keys()
            
            for ilce in ilceler:
                # Yetişkin veritabanı dosyaları
                yetiskin_db = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir, ilce, "yetiskinVeriTabani")
                
                # Kaybolanlar embeddinglari
                kaybolan_embeddings_path = os.path.join(yetiskin_db, "kaybolan_embeddings.npy")
                kaybolan_paths_path = os.path.join(yetiskin_db, "kaybolan_paths.npy")
                
                try:
                    if os.path.exists(kaybolan_embeddings_path) and os.path.exists(kaybolan_paths_path):
                        # Dosyaları yükle
                        kaybolan_embeddings = np.load(kaybolan_embeddings_path)
                        kaybolan_paths = np.load(kaybolan_paths_path)
                        
                        # Embeddingler ve dosya yollarını eşleştir
                        if len(kaybolan_embeddings) == len(kaybolan_paths):
                            for i in range(len(kaybolan_paths)):
                                result["kaybolanlar"].append({
                                    "yol": str(kaybolan_paths[i]),
                                    "embedding": kaybolan_embeddings[i],
                                    "tip": "yetiskin",
                                    "tur": "kaybolan",
                                    "sehir": sehir,
                                    "ilce": ilce,
                                    "is_second_try": False  # Varsayılan olarak False ayarla
                                })
                except Exception as e:
                    print(f"Yetişkin kaybolanlar verileri yüklenirken hata: {str(e)}")
                
                # Bulunanlar embeddinglari
                bulunan_embeddings_path = os.path.join(yetiskin_db, "bulunan_embeddings.npy")
                bulunan_paths_path = os.path.join(yetiskin_db, "bulunan_paths.npy")
                
                try:
                    if os.path.exists(bulunan_embeddings_path) and os.path.exists(bulunan_paths_path):
                        # Dosyaları yükle
                        bulunan_embeddings = np.load(bulunan_embeddings_path)
                        bulunan_paths = np.load(bulunan_paths_path)
                        
                        # Embeddingler ve dosya yollarını eşleştir
                        if len(bulunan_embeddings) == len(bulunan_paths):
                            for i in range(len(bulunan_paths)):
                                result["bulunanlar"].append({
                                    "yol": str(bulunan_paths[i]),
                                    "embedding": bulunan_embeddings[i],
                                    "tip": "yetiskin",
                                    "tur": "bulunan",
                                    "sehir": sehir,
                                    "ilce": ilce,
                                    "is_second_try": False  # Varsayılan olarak False ayarla
                                })
                except Exception as e:
                    print(f"Yetişkin bulunanlar verileri yüklenirken hata: {str(e)}")
                
                # Çocuk veritabanı dosyaları
                cocuk_db = os.path.join(CURRENT_DIR, "Biyometrik_veriler", sehir, ilce, "cocukVeriTabani")
                
                # Kaybolanlar embeddinglari
                kaybolan_embeddings_path = os.path.join(cocuk_db, "kaybolan_embeddings.npy")
                kaybolan_paths_path = os.path.join(cocuk_db, "kaybolan_paths.npy")
                
                try:
                    if os.path.exists(kaybolan_embeddings_path) and os.path.exists(kaybolan_paths_path):
                        # Dosyaları yükle
                        kaybolan_embeddings = np.load(kaybolan_embeddings_path)
                        kaybolan_paths = np.load(kaybolan_paths_path)
                        
                        # Embeddingler ve dosya yollarını eşleştir
                        if len(kaybolan_embeddings) == len(kaybolan_paths):
                            for i in range(len(kaybolan_paths)):
                                result["kaybolanlar"].append({
                                    "yol": str(kaybolan_paths[i]),
                                    "embedding": kaybolan_embeddings[i],
                                    "tip": "cocuk",
                                    "tur": "kaybolan",
                                    "sehir": sehir,
                                    "ilce": ilce,
                                    "is_second_try": False  # Varsayılan olarak False ayarla
                                })
                except Exception as e:
                    print(f"Çocuk kaybolanlar verileri yüklenirken hata: {str(e)}")
                
                # Bulunanlar embeddinglari
                bulunan_embeddings_path = os.path.join(cocuk_db, "bulunan_embeddings.npy")
                bulunan_paths_path = os.path.join(cocuk_db, "bulunan_paths.npy")
                
                try:
                    if os.path.exists(bulunan_embeddings_path) and os.path.exists(bulunan_paths_path):
                        # Dosyaları yükle
                        bulunan_embeddings = np.load(bulunan_embeddings_path)
                        bulunan_paths = np.load(bulunan_paths_path)
                        
                        # Embeddingler ve dosya yollarını eşleştir
                        if len(bulunan_embeddings) == len(bulunan_paths):
                            for i in range(len(bulunan_paths)):
                                result["bulunanlar"].append({
                                    "yol": str(bulunan_paths[i]),
                                    "embedding": bulunan_embeddings[i],
                                    "tip": "cocuk",
                                    "tur": "bulunan",
                                    "sehir": sehir,
                                    "ilce": ilce,
                                    "is_second_try": False  # Varsayılan olarak False ayarla
                                })
                except Exception as e:
                    print(f"Çocuk bulunanlar verileri yüklenirken hata: {str(e)}")
        
        print(f"Toplam {len(result['kaybolanlar'])} kaybolan ve {len(result['bulunanlar'])} bulunan embedding yüklendi.")
        return result