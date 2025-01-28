import folium
from geopy.geocoders import Nominatim
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QIcon
from styles_dark import MAP_STYLE, REFRESH_BUTTON_STYLE
from styles_light import *
import database as dtb
import sys
import os
import io
import json



sys.stdout.reconfigure(encoding='utf-8')  # UTF-8 ayarı

# Firebase bağlantısını başlat


class HaritaYonetimi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # QWebEngineView bileşenini ekleyin
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Haritayı başlat
        self.initialize_map()

    def initialize_map(self):
        # Firebase'den ekip verilerini alın
        ekipler = self.get_teams_from_firebase()

        # Ekip verilerini JSON formatına dönüştür
        ekipler_json = json.dumps(ekipler)

        # HTML dosyasını yükle ve ekip verilerini ekleyin
        with open('harita.html', 'r') as file:
            html_content = file.read()
            html_content = html_content % ekipler_json

        # QWebEngineView içinde HTML'yi yükle
        self.web_view.setHtml(html_content)

    def get_teams_from_firebase(self):
        # Firebase'den ekip verilerini alın
        ref = dtb.db.reference('teams')
        ekipler = ref.get()
        if ekipler:
            return [ekip for ekip in ekipler.values()]
        return []


# Resim yükleme ve veritabanına kayıt fonksiyonu
def upload_and_save_image(image_path, durum_id, enlem, boylam):
    """Resmi Firebase'e yükler ve URL ile veritabanına kaydeder."""
    try:
        # Firebase Storage bucket'ına bağlan
        bucket = dtb.storage.bucket()
        blob = bucket.blob("images/" + os.path.basename(image_path))
        blob.upload_from_filename(image_path)

        # URL'yi al
        photo_url = blob.public_url
        print("Resim Firebase'e yüklendi. URL:", photo_url)

        # Veritabanına kayıt
        ref = dtb.db.reference('emergencies')
        ref.push({
            'Durum_ID': durum_id,
            'Enlem': enlem,
            'Boylam': boylam,
            'photo': photo_url
        })
        print("Veri başarıyla kaydedildi.")
        return True
    except Exception as e:
        print("Hata oluştu (upload_and_save_image):", e)
        return False

class MapWidget(QWidget):
    def __init__(self, harita):
        super().__init__()
        self.harita = harita
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Üst panel
        header = QWidget()
        header_layout = QHBoxLayout(header)

        title = QLabel("Afet Bölgesi Haritası")
        title.setStyleSheet(MAP_STYLE)

        refresh_btn = QPushButton(" Haritayı Yenile")
        refresh_btn.clicked.connect(self.refresh_map)
        refresh_btn.setIcon(QIcon('icons/refresh.png'))
        refresh_btn.setStyleSheet(REFRESH_BUTTON_STYLE)

        header_layout.addWidget(title)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()

        # Harita görünümü
        self.map_view = self.harita.initialize_map(height=470)
        main_layout.addWidget(header)
        main_layout.addWidget(self.map_view)
        self.setLayout(main_layout)

    def refresh_map(self):
        self.harita.initialize_map()

class HaritaYonetimi:
    def __init__(self):
        self.map_view = QWebEngineView()
        self.map = None
        self.geocoder = Nominatim(user_agent="afet_yonetim_sistemi")

    def initialize_map(self, height=600):
        center_coords = [40, 33]  # Türkiye merkezi
        self.map = folium.Map(
            location=center_coords,
            zoom_start=6,
            width='100%',
            height=height,
            tiles='OpenStreetMap',
            control_scale=True
        )

        # Firebase'den alınan veriler
        example_data = self.get_data_from_firebase()
        for data in example_data:
            self.add_marker_with_photo(data['Enlem'], data['Boylam'], data['photo'])

        data = self.map._repr_html_()
        self.map_view.setHtml(data)
        return self.map_view

    def get_data_from_firebase(self):
        try:
            ref = dtb.db.reference('emergencies')
            data = ref.get()
            emergency_data = []

            if data:
                for entry in data.values():
                    emergency_data.append({
                        'Durum_ID': entry['Durum_ID'],
                        'Enlem': entry['Enlem'],
                        'Boylam': entry['Boylam'],
                        'photo': entry['photo']
                    })
            return emergency_data
        except Exception as e:
            print("Hata oluştu (get_data_from_firebase):", e)
            return []

    def add_marker_with_photo(self, enlem, boylam, photo_url):
        popup_html = f'<img src="{photo_url}" width="300" height="200">'
        folium.Marker(location=[enlem, boylam], popup=popup_html).add_to(self.map)

# Test için
if __name__ == "__main__":
    # Test: Resim yükleme ve veritabanına kayıt
    image_path = "C:/Users/bbase/OneDrive/Desktop/afet_koordinasyon-main3/afet_koordinasyon-main/Admin/icons/add.png"
    if upload_and_save_image(image_path, durum_id="1", enlem=39.92077, boylam=32.85411):
        print("Resim yüklendi ve veritabanına kaydedildi.")
    else:
        print("İşlem başarısız!")

    # PyQt5 uygulaması başlat
    app = QApplication(sys.argv)
    harita_yonetimi = HaritaYonetimi()
    map_widget = MapWidget(harita_yonetimi)
    map_widget.setWindowTitle("Afet Koordinasyon Sistemi")
    map_widget.show()
    sys.exit(app.exec_())
