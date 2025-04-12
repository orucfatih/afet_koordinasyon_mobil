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

# Mevcut dosyanın bulunduğu dizini al
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

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
        
    def init_widgets(self):
        """Widget'ları başlangıçta tanımla"""
        # Ana scroll area
        self.main_scroll_area = QScrollArea()
        self.main_scroll_area.setWidgetResizable(True)
        self.main_content_widget = QWidget()
        self.main_scroll_area.setWidget(self.main_content_widget)
        
        # Tablolar
        self.missing_table = QTableWidget()
        self.found_table = QTableWidget()
        
        # Ağaç widget'ı
        self.location_tree = QTreeWidget()
        self.location_tree.setHeaderLabel("Şehirler ve İlçeler")
        self.location_tree.setMinimumHeight(300)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Seçim özeti etiketi
        self.selection_summary = QLabel("Seçili Bölgeler: Yok")
        self.selection_summary.setWordWrap(True)
        
        # İstatistik etiketi
        self.stats_label = QLabel("Toplam Kayıtlı Biyometrik Veri: 0")

        # Fotoğraf görüntüleme alanı
        self.photos_widget = QWidget()
        self.photo_grid = QGridLayout(self.photos_widget)
        self.photo_grid.setSpacing(10)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.photos_widget)
        self.scroll_area.setMinimumHeight(500)  # Minimum yükseklik 500 birim

    def initUI(self):
        # Ana layout
        main_layout = QVBoxLayout(self.main_content_widget)
        
        # Üst kısım - İstatistikler
        stats_layout = QHBoxLayout()
        
        # İstatistik kartları
        self.create_stat_card("Toplam Kayıp İhbarı", "0", stats_layout)
        self.create_stat_card("Bugün Gelen İhbarlar", "0", stats_layout)
        self.create_stat_card("Eşleşme Sayısı", "0", stats_layout)
        
        main_layout.addLayout(stats_layout)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Kayıp İhbarları Tab'ı
        missing_reports_widget = QWidget()
        missing_reports_layout = QVBoxLayout()
        
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
        found_persons_layout = QVBoxLayout()
        
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
        edevlet_layout = QVBoxLayout()
        
        # Üst kısım - Bölge seçimi
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        
        # Bölge Seçimi Başlığı
        location_title = QLabel("Bölge Seçimi")
        location_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        top_layout.addWidget(location_title)
        
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
        
        top_layout.addWidget(self.location_tree)
        top_layout.addWidget(self.selection_summary)
        
        # Ayırıcı çizgi
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        top_layout.addWidget(line)
        
        # Veri yükleme butonu
        upload_btn = QPushButton("Seçili Bölgelerin E-Devlet Verilerini Güncelle")
        upload_btn.setMinimumHeight(40)
        upload_btn.clicked.connect(self.update_edevlet_data)
        top_layout.addWidget(upload_btn)
        
        top_layout.addWidget(self.progress_bar)
        top_layout.addWidget(self.stats_label)
        
        edevlet_layout.addWidget(top_section)
        
        # Alt kısım - Fotoğraf görüntüleme
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout(bottom_section)
        
        photos_title = QLabel("Biyometrik Fotoğraflar")
        photos_title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        bottom_layout.addWidget(photos_title)
        
        bottom_layout.addWidget(self.scroll_area)
        
        # Alt kısma boşluk ekle
        spacer = QWidget()
        spacer.setMinimumHeight(50)  # Alt kısımda 50 piksel boşluk
        bottom_layout.addWidget(spacer)
        
        edevlet_layout.addWidget(bottom_section)
        
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
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        
        card_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        card.setLayout(card_layout)
        card.setMinimumSize(QSize(200, 100))
        
        parent_layout.addWidget(card)

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
        max_cols = 4  # Her satırda maksimum 4 fotoğraf
        
        for path in photo_paths:
            try:
                photo_label = PhotoLabel()
                pixmap = QPixmap(path)
                
                if pixmap.isNull():
                    print(f"Fotoğraf yüklenemedi: {path}")  # Debug için
                    continue
                    
                photo_label.setPixmap(pixmap)
                
                # Dosya adını göster
                name_label = QLabel(os.path.basename(path))
                name_label.setAlignment(Qt.AlignCenter)
                
                # Fotoğraf ve ismi için container
                container = QWidget()
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
        selected_locations = []
        all_photos = []
        
        for i in range(self.location_tree.topLevelItemCount()):
            sehir_item = self.location_tree.topLevelItem(i)
            sehir = sehir_item.text(0)
            
            if sehir_item.checkState(0) == Qt.Checked:
                print(f"Seçili şehir: {sehir}")  # Debug için
                # Şehrin fotoğraflarını yükle
                photos = self.load_photos_for_city(sehir)
                all_photos.extend(photos)
        
        if not all_photos:
            self.stats_label.setText("Seçili bölgelerde biyometrik veri bulunamadı")
            return
        
        print(f"Toplam bulunan fotoğraf: {len(all_photos)}")  # Debug için
        
        # Fotoğrafları göster
        self.display_photos(all_photos)
        self.stats_label.setText(f"Toplam Kayıtlı Biyometrik Veri: {len(all_photos)}")
        
        # İlerleme çubuğunu güncelle
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(100) 