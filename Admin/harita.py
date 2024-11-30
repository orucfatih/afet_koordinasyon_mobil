import folium
from geopy.geocoders import Nominatim
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QIcon
from styles_dark import MAP_STYLE, REFRESH_BUTTON_STYLE
from styles_light import *


class MapWidget(QWidget):
    def __init__(self, harita):
        super().__init__()
        self.harita = harita
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Üst panel - Başlık ve Yenileme
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



        # Kontrol paneli düzeni
        controls = QHBoxLayout()

        # Ana düzene ekle
        main_layout.addWidget(header)
        main_layout.addLayout(controls)
        
        # Harita görünümü
        self.map_view = self.harita.initialize_map(height=470)
        main_layout.addWidget(self.map_view)

        
        self.setLayout(main_layout)

    def refresh_map(self):
        """Haritayı yeniler"""
        self.harita.initialize_map()
        
    def clear_map(self):
        """Haritayı temizler"""
        self.harita.clear_map()
        self.map_view.reload()



class HaritaYonetimi:
    def __init__(self):
        self.map_view = QWebEngineView()
        self.map = None
        self.marker_cluster = None
        self.markers = []
        self.geocoder = Nominatim(user_agent="afet_yonetim_sistemi")
        
    def initialize_map(self, height=600):
        """Afet yönetimi için gelişmiş harita başlatır"""
        center_coords = [40, 33]  # Türkiye merkezi
        
        self.map = folium.Map(
            location=center_coords,
            zoom_start=6,
            width='100%',
            height=height,
            tiles='OpenStreetMap',
            control_scale=True
        )
        

        data = self.map._repr_html_()
        self.map_view.setHtml(data)
        return self.map_view