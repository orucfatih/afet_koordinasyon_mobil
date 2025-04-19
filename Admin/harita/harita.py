import sys
import os
import json
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

firebase_credentials_json = {
    'type': os.getenv('FIREBASE_ADMIN_TYPE'),
    'project_id': os.getenv('FIREBASE_ADMIN_PROJECT_ID'),
    'private_key_id': os.getenv('FIREBASE_ADMIN_PRIVATE_KEY_ID'),
    'private_key': os.getenv('FIREBASE_ADMIN_PRIVATE_KEY'),
    'client_email': os.getenv('FIREBASE_ADMIN_CLIENT_EMAIL'),
    'client_id': os.getenv('FIREBASE_ADMIN_CLIENT_ID'),
    'auth_uri': os.getenv('FIREBASE_ADMIN_AUTH_URI'),
    'token_uri': os.getenv('FIREBASE_ADMIN_TOKEN_URI'),
    'auth_provider_x509_cert_url': os.getenv('FIREBASE_ADMIN_AUTH_PROVIDER_CERT_URL'),
    'client_x509_cert_url': os.getenv('FIREBASE_ADMIN_CLIENT_CERT_URL'),
    'universe_domain': os.getenv('FIREBASE_ADMIN_UNIVERSE_DOMAIN', 'googleapis.com')
}

# Zorunlu değişkenlerin kontrolü
required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
for key in required_keys:
    if not firebase_credentials_json[key]:
        print(f"\033[91mHATA: {key} ortam değişkeni eksik!\033[0m")
        sys.exit(1)

firebase_credentials_json['private_key'] = firebase_credentials_json['private_key'].replace('\\n', '\n')

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials_json)
    firebase_admin.initialize_app(cred)
db = firestore.client()
print("Firebase başarıyla başlatıldı!")
class GoogleMapsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        self.setGeometry(0, 0, 800, 600)
        
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY") or ""
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY") or ""
        
        if not self.api_key:
            print("\033[91mHATA: GOOGLE_MAPS_API_KEY bulunamadı!\033[0m")
            sys.exit(1)
        if not self.openweather_api_key:
            print("\033[93mUYARI: OPENWEATHER_API_KEY bulunamadı, hava durumu ve kalitesi gösterilemeyecek.\033[0m")
        
        self.latitude = 39.9334
        self.longitude = 32.8597
        
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        self.update_map()

    def fetch_earthquakes(self):
        try:
            url = "http://www.koeri.boun.edu.tr/scripts/lst5.asp"
            print(f"Fetching data from {url}")
            response = requests.get(url)
            response.encoding = 'utf-8'
            print(f"Response status: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            pre = soup.find('pre')
            if not pre:
                print("No <pre> tag found in response")
                return []
            
            lines = pre.text.splitlines()
            earthquakes = []
            for line in lines[7:27]:
                parts = line.split()
                if len(parts) >= 8:
                    date = parts[0]
                    time = parts[1]
                    lat = float(parts[2])
                    lon = float(parts[3])
                    mag = float(parts[6])
                    place = ' '.join(parts[8:])
                    earthquakes.append({
                        "date": date,
                        "time": time,
                        "lat": lat,
                        "lon": lon,
                        "magnitude": mag,
                        "place": place
                    })
            print(f"Fetched {len(earthquakes)} earthquakes")
            return earthquakes
        except Exception as e:
            print(f"Deprem verisi çekme hatası: {e}")
            return []

    def get_map_html(self):
        earthquakes = self.fetch_earthquakes()
        html_path = os.path.join(BASE_DIR, "harita.html")
        css_path = os.path.join(BASE_DIR, "harita.css")
        js_path = os.path.join(BASE_DIR, "harita.js")
        
        print(f"HTML Path: {html_path}")
        print(f"CSS Path: {css_path}")
        print(f"JS Path: {js_path}")
        
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                html_content = file.read()
        except FileNotFoundError:
            print(f"\033[91mHATA: harita.html dosyası bulunamadı: {html_path}\033[0m")
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"\033[91mHATA: harita.html dosyası UTF-8 ile okunamadı, latin1 deneniyor\033[0m")
            with open(html_path, "r", encoding="latin1") as file:
                html_content = file.read()
        except Exception as e:
            print(f"\033[91mHATA: HTML dosyası okunurken hata oluştu: {e}\033[0m")
            sys.exit(1)

        try:
            with open(css_path, "r", encoding="utf-8") as file:
                css_content = file.read()
        except FileNotFoundError:
            print(f"\033[91mHATA: harita.css dosyası bulunamadı: {css_path}\033[0m")
            css_content = ""
        except UnicodeDecodeError:
            print(f"\033[91mHATA: harita.css dosyası UTF-8 ile okunamadı, latin1 deneniyor\033[0m")
            with open(css_path, "r", encoding="latin1") as file:
                css_content = file.read()
        except Exception as e:
            print(f"\033[91mHATA: harita.css okunurken hata oluştu: {e}\033[0m")
            css_content = ""

        try:
            with open(js_path, "r", encoding="utf-8") as file:
                js_content = file.read()
        except FileNotFoundError:
            print(f"\033[91mHATA: harita.js dosyası bulunamadı: {js_path}\033[0m")
            js_content = ""
        except UnicodeDecodeError:
            print(f"\033[91mHATA: harita.js dosyası UTF-8 ile okunamadı, latin1 deneniyor\033[0m")
            with open(js_path, "r", encoding="latin1") as file:
                js_content = file.read()
        except Exception as e:
            print(f"\033[91mHATA: harita.js okunurken hata oluştu: {e}\033[0m")
            js_content = ""
        
        html_content = html_content.replace("<!-- CSS_PLACEHOLDER -->", f"<style>{css_content}</style>")
        html_content = html_content.replace("<!-- JS_PLACEHOLDER -->", f"<script>{js_content}</script>")
        html_content = html_content.replace("{{EARTHQUAKES}}", json.dumps(earthquakes, ensure_ascii=False))
        html_content = html_content.replace("{{GOOGLE_MAPS_API_KEY}}", self.api_key)
        html_content = html_content.replace("{{OPENWEATHER_API_KEY}}", self.openweather_api_key)
        html_content = html_content.replace("{{LATITUDE}}", str(self.latitude))
        html_content = html_content.replace("{{LONGITUDE}}", str(self.longitude))
        return html_content

    def update_map(self):
        self.web_view.setHtml(self.get_map_html(), QUrl("http://localhost"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsWindow()
    window.show()
    sys.exit(app.exec_())