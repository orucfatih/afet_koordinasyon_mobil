import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from dotenv import load_dotenv
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Project root directory (top-level folder)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# Base directory (directory containing the Python script)
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from root directory
dotenv_path = ROOT_DIR / ".env"
if not dotenv_path.exists():
    print(f"\033[91mERROR: .env file not found at {dotenv_path}\033[0m")
load_dotenv(dotenv_path)

class GoogleMapsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        
        # Get API keys from environment variables
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY") or ""
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY") or ""
        
        if not self.api_key:
            QMessageBox.critical(self, "Error", "GOOGLE_MAPS_API_KEY not found in .env file!")
            return
        if not self.openweather_api_key:
            QMessageBox.warning(self, "Warning", "OPENWEATHER_API_KEY not found. Weather features may not work.")
        
        # Default coordinates (Ankara, Turkey)
        self.latitude = 39.9334
        self.longitude = 32.8597
        
        # Create web view
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        
        # Load the map
        self.load_map()

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

    def load_map(self):
        """Load the map HTML file into the web view"""
        try:
            html_path = BASE_DIR / "harita2.html"
            css_path = BASE_DIR / "harita2.css"
            js_path = BASE_DIR / "harita2.js"
            json_path = BASE_DIR / "cadirkent.json"
            assembly_path = BASE_DIR / "toplanma.json"
            
            # Check if required files exist
            for path in [html_path, css_path, js_path, json_path, assembly_path]:
                if not path.exists():
                    QMessageBox.critical(self, "Error", f"File not found: {path}")
                    return
            
            # Read HTML file
            with open(html_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            
            # Read cadirkent.json
            with open(json_path, "r", encoding="utf-8") as file:
                tentcity_data = json.load(file)
            
            # Read toplanma.json
            with open(assembly_path, "r", encoding="utf-8") as file:
                assembly_data = json.load(file)
            
            # Fetch earthquake data
            earthquake_data = self.fetch_earthquakes()
            
            # Inject API keys and data
            html_content = html_content.replace("YOUR_GOOGLE_MAPS_API_KEY", self.api_key)
            html_content = html_content.replace("YOUR_OPENWEATHERMAP_API_KEY", self.openweather_api_key)
            html_content = html_content.replace(
                "</head>",
                f"""
                <script>
                    window.TENTCITY_DATA = {json.dumps(tentcity_data, ensure_ascii=False)};
                    window.ASSEMBLY_DATA = {json.dumps(assembly_data, ensure_ascii=False)};
                    window.EARTHQUAKE_DATA = {json.dumps(earthquake_data, ensure_ascii=False)};
                </script>
                </head>
                """
            )
            
            # Load HTML content into web view
            self.web_view.setHtml(html_content, QUrl.fromLocalFile(str(html_path)))
            print("Map successfully loaded!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load map: {e}")
            print(f"\033[91mERROR: Failed to load map: {e}\033[0m")

    def update_map(self):
        """Reload the map"""
        self.load_map()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsWindow()
    window.setGeometry(100, 100, 1200, 800)  # Adjusted window size for better map visibility
    window.setWindowTitle("AFAD Afet Yönetim Haritası")
    window.show()
    sys.exit(app.exec_())