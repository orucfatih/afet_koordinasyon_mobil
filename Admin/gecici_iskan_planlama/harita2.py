import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore
from pathlib import Path

# Proje kökünü içeren klasörü sys.path'e ekle
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Config modülünden Firebase fonksiyonlarını içe aktar
from Admin.config import (
    initialize_firebase, 
    get_firestore_client,
    init_config,
    get_env_file_path
)

# Konfigürasyon ayarlarını başlat
init_config()

# Dotenv dosyasını yükle
dotenv_path = get_env_file_path()
load_dotenv(dotenv_path)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    # Firebase'i başlat
    initialize_firebase()
    # Firestore istemcisini al
    db = get_firestore_client()
    print("Firebase başarıyla başlatıldı!")
except Exception as e:
    print(f"\033[91mHATA: Firebase başlatılamadı: {e}\033[0m")

class GoogleMapsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        
        # API anahtarlarını al
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY") or ""
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY") or ""
        
        if not self.api_key:
            QMessageBox.critical(self, "Hata", "GOOGLE_MAPS_API_KEY bulunamadı!")
            return
            
        # Varsayılan koordinatlar (Türkiye merkezi)
        self.latitude = 39.9334
        self.longitude = 32.8597
        
        # Web view oluştur
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        
        # HTML dosyasını yükle
        self.load_map()

    def load_map(self):
        """Harita HTML dosyasını yükle"""
        try:
            html_path = os.path.join(BASE_DIR, "harita2.html")
            
            if not os.path.exists(html_path):
                QMessageBox.critical(self, "Hata", f"HTML dosyası bulunamadı: {html_path}")
                return
            
            # HTML dosyasını oku
            with open(html_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            
            # API anahtarlarını ve koordinatları yerleştir
            html_content = html_content.replace("{{GOOGLE_MAPS_API_KEY}}", self.api_key)
            html_content = html_content.replace("{{OPENWEATHER_API_KEY}}", self.openweather_api_key or "")
            html_content = html_content.replace("{{LATITUDE}}", str(self.latitude))
            html_content = html_content.replace("{{LONGITUDE}}", str(self.longitude))
            
            # HTML içeriğini web view'a yükle
            self.web_view.setHtml(html_content, QUrl("http://localhost"))
            print("Harita başarıyla yüklendi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Harita yüklenirken hata oluştu: {e}")
            print(f"\033[91mHATA: Harita yüklenirken hata oluştu: {e}\033[0m")

    def update_map(self):
        """Haritayı güncelle"""
        self.load_map()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsWindow()
    window.setGeometry(100, 100, 800, 600)  # Pencere boyutunu ayarla
    window.setWindowTitle("Geçici İskan Planlama Haritası")  # Pencere başlığını ayarla
    window.show()
    sys.exit(app.exec_())