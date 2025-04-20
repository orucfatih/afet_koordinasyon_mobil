import sys
import os
import requests
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtCore import QUrl
from dotenv import load_dotenv
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ortam değişkenlerini yükle
load_dotenv()

class GoogleMapsWindow(QMainWindow):
    """AFAD Afet Yönetim Haritası"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AFAD Afet Yönetim Haritası")
        self.setGeometry(100, 100, 1200, 800)
        
        # Google Maps ve OpenWeatherMap API key'lerini ortam değişkeninden al
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.google_api_key:
            print("\033[91mHATA: GOOGLE_MAPS_API_KEY ortam değişkeni bulunamadı!\033[0m")
            print("\033[93mLütfen .env dosyasında GOOGLE_MAPS_API_KEY değişkenini tanımlayın.\033[0m")
            sys.exit(1)
        if not self.weather_api_key:
            print("\033[91mHATA: OPENWEATHER_API_KEY ortam değişkeni bulunamadı!\033[0m")
            print("\033[93mLütfen .env dosyasında OPENWEATHER_API_KEY değişkenini tanımlayın.\033[0m")
            sys.exit(1)
        
        self.latitude = 39.9334  # Türkiye merkezi (Ankara civarı)
        self.longitude = 32.8597
        
        # Son 20 depremi al
        self.earthquakes = self.fetch_earthquakes()
        
        # Web view setup
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.update_map()

    def fetch_earthquakes(self):
        """Fetch the last 20 earthquakes from Kandilli Observatory"""
        url = "http://www.koeri.boun.edu.tr/scripts/lasteq.asp"
        earthquakes = []
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'ISO-8859-9'
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_tag = soup.find('pre')
            if not pre_tag:
                print("Deprem verisi bulunamadı.")
                return earthquakes

            lines = pre_tag.text.strip().split('\n')[6:26]  # İlk 6 satır başlık, son 20 deprem
            for line in lines:
                parts = re.split(r'\s+', line.strip())
                if len(parts) < 8:
                    continue
                try:
                    date = parts[0]
                    time = parts[1]
                    lat = float(parts[2])
                    lng = float(parts[3])
                    depth = float(parts[4])
                    magnitude = float(parts[6])
                    location = ' '.join(parts[8:]).split('Revize')[0].strip()
                    earthquakes.append({
                        'date': date,
                        'time': time,
                        'lat': lat,
                        'lng': lng,
                        'depth': depth,
                        'magnitude': magnitude,
                        'location': location
                    })
                except (ValueError, IndexError) as e:
                    print(f"Veri parse hatası: {line}, Hata: {e}")
                    continue
        except requests.RequestException as e:
            print(f"Deprem verisi alınamadı: {e}")
            return earthquakes
        return earthquakes

    def update_map(self):
        """Load HTML content into web view"""
        html_path = os.path.join(BASE_DIR, 'harita2.html')
        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except FileNotFoundError:
            print(f"\033[91mHATA: {html_path} dosyası bulunamadı!\033[0m")
            sys.exit(1)
        
        # API anahtarını HTML içeriğine enjekte et
        html_content = html_content.replace('{GOOGLE_MAPS_API_KEY}', self.google_api_key)
        
        # Web view'e HTML içeriğini yükle
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(html_path))

        # JavaScript ile API anahtarı ve deprem verilerini enjekte et
        script = f"""
            window.WEATHER_API_KEY = '{self.weather_api_key}';
            window.EARTHQUAKES = {json.dumps(self.earthquakes)};
        """
        web_script = QWebEngineScript()
        web_script.setSourceCode(script)
        web_script.setName("InjectAPIData")
        web_script.setWorldId(QWebEngineScript.MainWorld)
        web_script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        self.web_view.page().scripts().insert(web_script)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsWindow()
    window.show()
    sys.exit(app.exec_())