import sys
import os
import json
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Ortam değişkenlerini yükle
load_dotenv()

# Firebase kimlik bilgileri (sabit JSON)
FIREBASE_CREDENTIALS = {
  "type": "service_account",
  "project_id": "afad-proje",
  "private_key_id": "04ee79448796d76585d2eef07a22808fbdc56fdc",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDkvdvOZoWPydvo\nFTptAv0dMUFiotm+24vqN+A5YIayfMw9jSauFnZmQQKPFuevedL8siF1QOhs9dJb\nnNB+0kWbESUPDI2Aky6pz5rYAXm2sYtoNCFOdPrcH8+GXwSGq6X/gLtk3k8Ryc5E\nNL3XmmO5ftyaF9TTcSIeLmG6QAGH0Jh9bXJilTMX09SyNI1p3TpmjD+MnAjyoWY2\nAfqGN5GDlzQKqkWaIoJHpb//KBCccL/BYJPP5iXEfTHSIoy6XQhCt6WPs4kMnftF\naJ1JnisfRlfkwD4x4IYlcG3enODzdgsqzdYmwnxwUTOe0LZUs9PJh8MWzl8UCWvw\n7GaENnXHAgMBAAECggEAUeTVdtqGs/mhxUAgaFn7FAIH9k/2pFnHCIaTvQcdgnai\nyuCnugkpv6dDysX5Ef6MNtNxniCsdiI2e30zukv/BqsHORGV8bQAL2S3++DfWjTL\ng/Wx/PxtufSboHCRVsPKjSTiMpVS+rvlIM8/LptEW+ubAIJKvJ7TB7o0W/HBeoVb\nYv+egzGwzu1juK2eKrp491+mZmdcZNhhXnvHx/pK2EJWHi2yEHehQ7X7g9J3SLTq\nDYgb5Ow7rWS0Zm0LlAQxZnAQXhDXjIkG3vQX/FR8xZrW1kuTKxCEMumJdAk4IsLX\nDaJXSoY+STZh4iGFikV2xEPmmSYcLK1cscZT++IUxQKBgQD0FWZdp2p5jbm8oLKP\nkH2n3TCKadlwmhQ9+xr65RdeEiPAYdTecOseiCVZom5tVuspNTkuf4Mol68ZJySC\nrl/iQf1oZqS1LjhWttWUby4Am4YiSEaqCcWkyiD40e1CO28IGWXuue1oK8oO+iMX\nXnHP+yeLz/yGBH+p0pgHZ+Hi3QKBgQDv6LZU77W/RCbzU4pOoIyyRYgM8YMwyTos\nrXj31Ltg3P/4ZE0KREW+02IkdCDmT0SsP8oB8hoGAt27w1hmhir34IOy+gf2r4kM\ncSu3uSDk7nilzZb7rLAqqmBss8HxQepUhAAsMiTgKi65Dzy9BzwS2tKuHSv8yMFk\ng+gbz9+28wKBgQDM/DfnCVW7VdIZ3x92wFM3KeS9KZ4KGexMDVmgQct5HmTWCZNb\naJudHZu4hliVDP0bs24dZctByPmtdxkLguRVwTPPfPxwiKuZ75y5NxH8QqDIo8hs\nvx40gehk7vCBwiZCOApKDe2aocPlBh94XcHZeETC/15FMvwAJDO3bH/hJQKBgGOo\nb9Vonj8NuIBru5Bd8RQ8/f8idDTX4mqcxRtuK0hZhZtRTw9svOxAMwyhkOkbFJPZ\nC7kzMMw+dI2C4D32jfLaONsoMhavZGbevCJdrORsi4GUnZt+aM/QZq3BHldx4j2p\nd8jkK51S6IXHZpu/XZ0XeV0KkTM40d1HTiv/dhcxAoGAHhaIKIV5lyWaVrpgBaO4\nK1A1jBrSVM5S6w0ZSVRy4WkNC1UNp7/L8Uxg9OTGuJ8qAfQwjV8PhSVLVGwgVhOb\ncnPgqXc8BNpJ4U4sUhxDPG4mVhaJhvOC5pA/gbnPS1rI9U09FbzwNTOrvsM6MalP\n+1ubmDFyy3y+n6NIbegWSrE=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-asriu@afad-proje.iam.gserviceaccount.com",
  "client_id": "101664159944164540965",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-asriu%40afad-proje.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Firebase başlatma
try:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {"storageBucket": "your-firebase-app.appspot.com"})
    db = firestore.client()
    bucket = storage.bucket()
except Exception as e:
    print(f"\033[91mHATA: Firebase başlatılamadı: {e}\033[0m")
    sys.exit(1)

class GoogleMapsWindow(QMainWindow):
    """AFAD Afet Yönetim Haritası"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AFAD Afet Yönetim Haritası")
        self.setGeometry(100, 100, 1200, 800)
        
        # API key'leri ortam değişkenlerinden al
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY") or ""
        
        if not self.api_key:
            print("\033[91mHATA: GOOGLE_MAPS_API_KEY bulunamadı!\033[0m")
            sys.exit(1)
        if not self.openweather_api_key:
            print("\033[93mUYARI: OPENWEATHER_API_KEY bulunamadı, hava durumu ve kalitesi gösterilemeyecek.\033[0m")
        
        self.latitude = 39.9334  # Türkiye merkezi
        self.longitude = 32.8597
        
        # Web view setup
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.update_map()

    def fetch_earthquakes(self):
        """Kandilli Rasathanesi'nden son 20 depremi çek"""
        try:
            url = "http://www.koeri.boun.edu.tr/scripts/lst5.asp"
            response = requests.get(url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            pre = soup.find('pre')
            if not pre:
                return []
            
            lines = pre.text.splitlines()
            earthquakes = []
            for line in lines[7:27]:  # İlk 7 satır başlık, son 20 depremi al
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
            return earthquakes
        except Exception as e:
            print(f"Deprem verisi çekme hatası: {e}")
            return []

    def get_map_html(self):
        """Google Maps HTML içeriğini oluştur"""
        earthquakes = self.fetch_earthquakes()
        return f"""<!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AFAD Afet Yönetim Haritası</title>
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
                font-family: 'Poppins', sans-serif;
                font-size: 18px;
                overflow: hidden;
                background: #eceff1;
            }}
            #map {{
                height: 100%;
                width: 100%;
                border-radius: 15px;
                box-shadow: 0 6px 30px rgba(0,0,0,0.15);
                border: 2px solid #ff4500;
                z-index: 1;
            }}
            #sidebar {{
                position: fixed;
                top: 0;
                left: -360px;
                width: 360px;
                height: 100%;
                background: linear-gradient(180deg, #ffffff, #f5f6f5);
                box-shadow: 6px 0 25px rgba(0,0,0,0.2);
                transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                padding: 30px;
                z-index: 1000;
                overflow-y: auto;
                border-radius: 0 15px 15px 0;
            }}
            #sidebar.open {{
                left: 0;
            }}
            #toggle-btn {{
                position: fixed;
                top: 30px;
                left: 30px;
                z-index: 1001;
                background: linear-gradient(135deg, #ff4500, #ff7043);
                color: white;
                border: none;
                padding: 15px;
                border-radius: 50%;
                width: 55px;
                height: 55px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 26px;
                text-align: center;
                box-shadow: 0 8px 20px rgba(255, 69, 0, 0.4);
            }}
            #toggle-btn:hover {{
                transform: scale(1.15);
                background: linear-gradient(135deg, #e03d00, #ff4500);
                box-shadow: 0 10px 25px rgba(255, 69, 0, 0.5);
            }}
            .control-panel {{
                margin: 30px 0;
                padding: 25px;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }}
            input, select, button {{
                width: 100%;
                padding: 16px;
                margin: 15px 0;
                border: 2px solid #ddd;
                border-radius: 10px;
                box-sizing: border-box;
                font-size: 20px;
                transition: all 0.3s;
                background: #fafafa;
            }}
            input:focus, select:focus {{
                border-color: #ff4500;
                outline: none;
                box-shadow: 0 0 8px rgba(255, 69, 0, 0.4);
            }}
            button {{
                background: linear-gradient(135deg, #ff4500, #ff7043);
                color: white;
                border: none;
                cursor: pointer;
                font-weight: 600;
                font-size: 20px;
                text-transform: uppercase;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}
            button:hover {{
                background: linear-gradient(135deg, #e03d00, #ff4500);
                transform: translateY(-3px);
                box-shadow: 0 8px 15px rgba(255, 69, 0, 0.4);
            }}
            button img {{
                width: 24px;
                height: 24px;
            }}
            .marker-item {{
                padding: 16px;
                margin: 12px 0;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 18px;
                transition: all 0.3s;
            }}
            .marker-item:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            }}
            .marker-actions button {{
                padding: 10px 16px;
                margin-left: 12px;
                background: #dc3545;
                font-size: 18px;
            }}
            .marker-actions button:hover {{
                background: #c82333;
            }}
            #info-panel {{
                margin-top: 30px;
                padding: 16px;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                font-size: 18px;
                color: #333;
                line-height: 1.5;
            }}
            #marker-toolbar {{
                position: fixed;
                top: 30px;
                right: 30px;
                z-index: 1001;
                background: linear-gradient(135deg, #fff, #f5f6f5);
                padding: 15px;
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                display: flex;
                gap: 20px;
            }}
            .marker-btn {{
                padding: 12px 18px;
                background: linear-gradient(135deg, #ff4500, #ff7043);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 18px;
                font-weight: 600;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .marker-btn:hover, .marker-btn.active {{
                background: linear-gradient(135deg, #e03d00, #ff4500);
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(255, 69, 0, 0.4);
            }}
            .marker-btn img {{
                width: 24px;
                height: 24px;
            }}
            h2 {{
                color: #ff4500;
                margin: 0 0 20px 0;
                font-weight: 600;
                font-size: 28px;
            }}
            h3 {{
                color: #ff4500;
                margin: 0 0 15px 0;
                font-weight: 600;
                font-size: 24px;
            }}
            label {{
                display: flex;
                align-items: center;
                margin: 15px 0;
                font-size: 20px;
                color: #444;
                font-weight: 500;
            }}
            input[type="checkbox"] {{
                width: 24px;
                height: 24px;
                margin-right: 12px;
                cursor: pointer;
                accent-color: #ff4500;
            }}
            .emergency-alert {{
                background: #ffebee;
                color: #c62828;
                padding: 10px;
                border-radius: 8px;
                margin-top: 15px;
                font-size: 18px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .pac-container {{
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                border: none;
                margin-top: 5px;
                font-family: 'Poppins', sans-serif;
                z-index: 1002;
            }}
            .pac-item {{
                padding: 12px 16px;
                font-size: 18px;
                color: #333;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                transition: all 0.2s;
            }}
            .pac-item:hover {{
                background: linear-gradient(135deg, #ff7043, #ff4500);
                color: white;
            }}
            .pac-item:last-child {{
                border-bottom: none;
            }}
            .pac-item-query {{
                font-weight: 500;
                color: inherit;
            }}
            .pac-matched {{
                color: #ff4500;
                font-weight: 600;
            }}
            #search-results {{
                list-style: none;
                padding: 0;
                max-height: 200px;
                overflow-y: auto;
                background: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                margin-top: 5px;
            }}
            #search-results li {{
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                transition: background 0.2s ease;
            }}
            #search-results li:hover {{
                background: #f5f6f5;
            }}
            #marker-modal, #team-modal, #photo-modal {{
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #ffffff;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                z-index: 1003;
                width: 400px;
                text-align: center;
            }}
            #marker-modal h3, #team-modal h3, #photo-modal h3 {{
                color: #ff4500;
                margin-bottom: 15px;
            }}
            #marker-modal .form-input, #team-modal .form-input, #team-modal .form-select, #photo-modal img {{
                margin-bottom: 15px;
                width: 100%;
                max-height: 300px;
                object-fit: contain;
            }}
            #team-modal .form-select {{
                background: #fafafa;
            }}
            #marker-modal .btn-custom, #team-modal .btn-custom, #photo-modal .btn-custom {{
                width: auto;
                padding: 10px 20px;
                margin: 5px;
            }}
            #marker-modal .btn-cancel, #team-modal .btn-cancel, #photo-modal .btn-reject {{
                background: #dc3545;
            }}
            #marker-modal .btn-cancel:hover, #team-modal .btn-cancel:hover, #photo-modal .btn-reject:hover {{
                background: #c82333;
            }}
            #photo-modal .btn-approve {{
                background: #28a745;
            }}
            #photo-modal .btn-approve:hover {{
                background: #218838;
            }}
            @media (max-width: 768px) {{
                #sidebar {{
                    width: 280px;
                }}
                #sidebar.open ~ #toggle-btn {{
                    left: 310px;
                }}
                #marker-toolbar {{
                    flex-wrap: wrap;
                    gap: 10px;
                    padding: 10px;
                }}
                .marker-btn {{
                    font-size: 14px;
                    padding: 8px 12px;
                }}
                .marker-btn img {{
                    width: 20px;
                    height: 20px;
                }}
                #marker-modal, #team-modal, #photo-modal {{
                    width: 90%;
                }}
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-storage-compat.js"></script>
        <script>
            // Google Maps API'yi async ve callback ile yükle
            (function() {{
                const script = document.createElement('script');
                script.src = 'https://maps.googleapis.com/maps/api/js?key={self.api_key}&libraries=places,directions,visualization&callback=initMap';
                script.async = true;
                script.defer = true;
                document.head.appendChild(script);
            }})();

            let map, markers = [], infoWindow, autocomplete, directionsService, directionsRenderer, trafficLayer, currentPolygon = null;
            let selectedMarkerType = null;
            let userLocation = null;
            let pendingMarker = null;
            let pendingTeamMarker = null;
            let heatmapLayer = null;
            let photoMarkers = [];
            let is3D = false;

            // Firebase yapılandırması
            const firebaseConfig = {{
                apiKey: "your-firebase-api-key",
                authDomain: "your-firebase-app.firebaseapp.com",
                projectId: "your-firebase-app",
                storageBucket: "your-firebase-app.appspot.com",
                messagingSenderId: "your-messaging-sender-id",
                appId: "your-app-id"
            }};
            firebase.initializeApp(firebaseConfig);
            const db = firebase.firestore();
            const storage = firebase.storage();

            function initMap() {{
                map = new google.maps.Map(document.getElementById('map'), {{
                    center: {{ lat: {self.latitude}, lng: {self.longitude} }},
                    zoom: 6,
                    mapTypeId: 'roadmap',
                    mapTypeControl: false,
                    streetViewControl: true,
                    fullscreenControl: true,
                    zoomControl: true,
                    styles: [
                        {{ featureType: "water", stylers: [{{ color: "#0288d1" }}] }},
                        {{ featureType: "road", stylers: [{{ color: "#555" }}, {{ lightness: 10 }}] }},
                        {{ featureType: "poi", stylers: [{{ visibility: "simplified" }}, {{ lightness: 20 }}] }},
                        {{ featureType: "landscape", stylers: [{{ lightness: 30 }}] }},
                        {{ featureType: "administrative", stylers: [{{ visibility: "on" }}] }}
                    ]
                }});

                infoWindow = new google.maps.InfoWindow();
                directionsService = new google.maps.DirectionsService();
                directionsRenderer = new google.maps.DirectionsRenderer({{
                    map: map,
                    suppressMarkers: false,
                    polylineOptions: {{ strokeColor: "#FF4500", strokeWeight: 6, strokeOpacity: 0.9 }}
                }});
                trafficLayer = new google.maps.TrafficLayer();

                const searchInput = document.getElementById('search-input');
                autocomplete = new google.maps.places.Autocomplete(searchInput, {{
                    types: ['(regions)'],
                    componentRestrictions: {{ country: 'tr' }},
                    fields: ['geometry', 'name', 'formatted_address', 'place_id']
                }});
                autocomplete.bindTo('bounds', map);

                autocomplete.addListener('place_changed', () => {{
                    const place = autocomplete.getPlace();
                    if (!place.geometry) {{
                        alert("Girilen yer için detay bulunamadı: '" + place.name + "'");
                        return;
                    }}
                    focusOnNeighborhood(place);
                    fetchWeatherAndAirQuality(place.geometry.location.lat(), place.geometry.location.lng());
                }});

                searchInput.addEventListener('input', () => {{
                    const query = searchInput.value;
                    if (query.length > 2) {{
                        const request = {{
                            query: query,
                            fields: ['name', 'geometry', 'formatted_address'],
                            locationBias: {{ lat: {self.latitude}, lng: {self.longitude} }},
                            componentRestrictions: {{ country: 'tr' }}
                        }};
                        const placesService = new google.maps.places.PlacesService(map);
                        placesService.textSearch(request, (searchData, status) => {{
                            if (status === google.maps.places.PlacesServiceStatus.OK && searchData) {{
                                updateSearchResults(searchData);
                            }}
                        }});
                    }} else {{
                        document.getElementById('search-results').innerHTML = '';
                    }}
                }});

                map.addListener('click', (e) => {{
                    if (selectedMarkerType && selectedMarkerType !== 'team') {{
                        pendingMarker = {{ latLng: e.latLng, type: selectedMarkerType }};
                        showMarkerModal();
                    }} else if (selectedMarkerType === 'team') {{
                        pendingTeamMarker = {{ latLng: e.latLng }};
                        showTeamModal();
                    }}
                }});

                document.getElementById('toggle-btn').addEventListener('click', () => {{
                    const sidebar = document.getElementById('sidebar');
                    const btn = document.getElementById('toggle-btn');
                    if (sidebar.classList.contains('open')) {{
                        sidebar.classList.remove('open');
                        btn.style.left = '30px';
                        btn.textContent = '☰';
                    }} else {{
                        sidebar.classList.add('open');
                        btn.style.left = '390px';
                        btn.textContent = '✕';
                    }}
                }});

                document.querySelectorAll('.marker-btn').forEach(btn => {{
                    btn.addEventListener('click', () => {{
                        document.querySelectorAll('.marker-btn').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        selectedMarkerType = btn.dataset.type;
                        if (selectedMarkerType !== 'team') {{
                            alert(selectedMarkerType + ' işaretçisi eklemek için haritaya tıklayın.');
                        }}
                    }});
                }});

                document.getElementById('marker-form').addEventListener('submit', (e) => {{
                    e.preventDefault();
                    const note = document.getElementById('marker-note').value;
                    if (pendingMarker) {{
                        let title, iconUrl;
                        switch (pendingMarker.type) {{
                            case 'Ambulans':
                                title = 'Ambulans';
                                iconUrl = 'https://cdn-icons-png.flaticon.com/512/3097/3097378.png';
                                break;
                            case 'Polis':
                                title = 'Polis';
                                iconUrl = 'https://cdn-icons-png.flaticon.com/512/3063/3063173.png';
                                break;
                            case 'Sağlıkçı':
                                title = 'Sağlıkçı';
                                iconUrl = 'https://cdn-icons-png.flaticon.com/512/2888/2888679.png';
                                break;
                            case 'Jandarma':
                                title = 'Jandarma';
                                iconUrl = 'https://cdn-icons-png.flaticon.com/512/2997/2997328.png';
                                break;
                            default:
                                title = 'Olay Yeri';
                                iconUrl = 'https://maps.google.com/mapfiles/ms/icons/red-dot.png';
                        }}
                        addMarker(pendingMarker.latLng, title, note, iconUrl);
                        map.setCenter(pendingMarker.latLng);
                        map.setZoom(12);
                        closeMarkerModal();
                        selectedMarkerType = null;
                        pendingMarker = null;
                    }}
                }});

                document.getElementById('cancel-marker-btn').addEventListener('click', () => {{
                    closeMarkerModal();
                    selectedMarkerType = null;
                    pendingMarker = null;
                }});

                document.getElementById('team-form').addEventListener('submit', (e) => {{
                    e.preventDefault();
                    const teamName = document.getElementById('team-name').value;
                    const teamType = document.getElementById('team-type').value;
                    const teamStatus = document.getElementById('team-status').value;
                    if (!teamName) {{
                        alert('Lütfen bir ekip adı girin.');
                        return;
                    }}
                    const note = 'Tür: ' + (teamType || 'Belirtilmemiş') + ' | Aktiflik: ' + teamStatus;
                    addCustomTeamMarker(pendingTeamMarker.latLng, teamName, teamType, teamStatus, note);
                    map.setCenter(pendingTeamMarker.latLng);
                    map.setZoom(12);
                    closeTeamModal();
                    selectedMarkerType = null;
                    pendingTeamMarker = null;
                }});

                document.getElementById('cancel-team-btn').addEventListener('click', () => {{
                    closeTeamModal();
                    selectedMarkerType = null;
                    pendingTeamMarker = null;
                }});

                document.getElementById('avoid-tolls').addEventListener('change', findShortestRoute);
                document.getElementById('avoid-highways').addEventListener('change', findShortestRoute);
                document.getElementById('toggle-heatmap').addEventListener('click', toggleHeatmap);
                document.getElementById('toggle-3d').addEventListener('click', toggle3DView);

                getCurrentLocation();
                loadEarthquakes();
                loadPhotosFromFirebase();
                setInterval(updateTrafficInfo, 60000);
            }}

            function loadEarthquakes() {{
                const earthquakes = {json.dumps(earthquakes)};
                const heatmapData = [];
                earthquakes.forEach(eq => {{
                    const latLng = new google.maps.LatLng(eq.lat, eq.lon);
                    const marker = new google.maps.Marker({{
                        position: latLng,
                        map: map,
                        title: `Deprem: ${{eq.place || 'Bilinmiyor'}}`,
                        icon: {{
                            url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                            scaledSize: new google.maps.Size(45, 45)
                        }}
                    }});
                    marker.addListener('click', () => {{
                        infoWindow.setContent(`
                            <div style="padding:15px; font-family: Poppins;">
                                <h3 style="color: #ff4500; font-size: 20px;">Deprem: ${{eq.place ? eq.place : 'Bilinmiyor'}}</h3>
                                <p style="font-size: 16px;">Tarih: ${{eq.date || 'N/A'}} ${{eq.time || ''}}</p>
                                <p style="font-size: 16px;">Büyüklük: ${{(eq.magnitude || 0).toFixed(1)}}</p>
                                <p style="font-size: 16px;">Enlem: ${{(eq.lat || 0).toFixed(6)}}</p>
                                <p style="font-size: 16px;">Boylam: ${{(eq.lon || 0).toFixed(6)}}</p>
                            </div>
                        `);
                        infoWindow.open(map, marker);
                    }});
                    markers.push(marker);
                    heatmapData.push({{location: latLng, weight: eq.magnitude || 1}});
                }});
                heatmapLayer = new google.maps.visualization.HeatmapLayer({{
                    data: heatmapData,
                    map: null,
                    radius: 20,
                    gradient: [
                        'rgba(0, 255, 255, 0)',
                        'rgba(0, 255, 255, 1)',
                        'rgba(0, 191, 255, 1)',
                        'rgba(0, 127, 255, 1)',
                        'rgba(0, 63, 255, 1)',
                        'rgba(0, 0, 255, 1)',
                        'rgba(0, 0, 223, 1)',
                        'rgba(0, 0, 191, 1)',
                        'rgba(0, 0, 159, 1)',
                        'rgba(0, 0, 127, 1)',
                        'rgba(63, 0, 91, 1)',
                        'rgba(127, 0, 63, 1)',
                        'rgba(191, 0, 31, 1)',
                        'rgba(255, 0, 0, 1)'
                    ]
                }});
            }}

            function toggleHeatmap() {{
                if (heatmapLayer.getMap()) {{
                    heatmapLayer.setMap(null);
                    document.getElementById('toggle-heatmap').textContent = 'Heatmap Göster';
                }} else {{
                    heatmapLayer.setMap(map);
                    document.getElementById('toggle-heatmap').textContent = 'Heatmap Gizle';
                }}
            }}

            function toggle3DView() {{
                is3D = !is3D;
                if (is3D) {{
                    map.setTilt(45);
                    map.setHeading(0);
                    document.getElementById('toggle-3d').textContent = '2D Görünüm';
                }} else {{
                    map.setTilt(0);
                    document.getElementById('toggle-3d').textContent = '3D Görünüm';
                }}
            }}

            function getAqiStatus(aqi) {{
                if (aqi === 1) return 'İyi';
                if (aqi === 2) return 'Orta';
                if (aqi === 3) return 'Hassas Gruplar İçin Sağlıksız';
                if (aqi === 4) return 'Sağlıksız';
                if (aqi === 5) return 'Çok Sağlıksız';
                return 'Bilinmiyor';
            }}

            function fetchWeatherAndAirQuality(lat, lng) {{
                const openWeatherApiKey = "{self.openweather_api_key}";
                
                if (openWeatherApiKey) {{
                    // Hava durumu
                    fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${{lat}}&lon=${{lng}}&appid=${{openWeatherApiKey}}&units=metric&lang=tr`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.cod === 200 && data.main && data.weather && data.weather.length > 0) {{
                                const weatherInfo = `
                                    <h3>Hava Durumu</h3>
                                    <p>Sıcaklık: ${{(data.main.temp || 0).toFixed(1)}}°C</p>
                                    <p>Durum: ${{data.weather[0].description || 'Bilinmiyor'}}</p>
                                    <p>Nem: ${{(data.main.humidity || 0)}}%</p>
                                    <p>Rüzgar: ${{(data.wind && data.wind.speed ? data.wind.speed.toFixed(1) : 0)}} m/s</p>
                                `;
                                document.getElementById('weather-info').innerHTML = weatherInfo;
                            }} else {{
                                document.getElementById('weather-info').innerHTML = 'Hava durumu verisi alınamadı.';
                            }}
                        }})
                        .catch(err => {{
                            console.error('Hava durumu hatası:', err);
                            document.getElementById('weather-info').innerHTML = 'Hava durumu yüklenemedi.';
                        }});

                    // Hava kalitesi
                    fetch(`https://api.openweathermap.org/data/2.5/air_pollution?lat=${{lat}}&lon=${{lng}}&appid=${{openWeatherApiKey}}`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.list && data.list.length > 0 && data.list[0].main && data.list[0].main.aqi) {{
                                const aqi = data.list[0].main.aqi;
                                const airInfo = `
                                    <h3>Hava Kalitesi</h3>
                                    <p>AQI: ${{aqi}}</p>
                                    <p>Durum: ${{getAqiStatus(aqi)}}</p>
                                `;
                                document.getElementById('air-quality-info').innerHTML = airInfo;
                            }} else {{
                                document.getElementById('air-quality-info').innerHTML = 'Hava kalitesi verisi alınamadı.';
                            }}
                        }})
                        .catch(err => {{
                            console.error('Hava kalitesi hatası:', err);
                            document.getElementById('air-quality-info').innerHTML = 'Hava kalitesi yüklenemedi.';
                        }});
                }} else {{
                    document.getElementById('weather-info').innerHTML = 'Hava durumu API anahtarı eksik.';
                    document.getElementById('air-quality-info').innerHTML = 'Hava kalitesi API anahtarı eksik.';
                }}
            }}

            function loadPhotosFromFirebase() {{
                db.collection('photos').onSnapshot(snapshot => {{
                    photoMarkers.forEach(marker => marker.setMap(null));
                    photoMarkers = [];
                    snapshot.forEach(doc => {{
                        const data = doc.data();
                        if (data.latitude && data.longitude) {{
                            const latLng = new google.maps.LatLng(data.latitude, data.longitude);
                            const marker = new google.maps.Marker({{
                                position: latLng,
                                map: map,
                                title: 'Fotoğraf',
                                icon: {{
                                    url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                                    scaledSize: new google.maps.Size(45, 45)
                                }},
                                animation: data.status === 'pending' ? google.maps.Animation.BOUNCE : null
                            }});
                            marker.addListener('click', () => {{
                                showPhotoModal(doc.id, data.image_url, data.latitude, data.longitude, data.status);
                            }});
                            photoMarkers.push(marker);
                        }}
                    }});
                }}, err => {{
                    console.error('Firebase fotoğraf yükleme hatası:', err);
                    document.getElementById('info-panel').innerHTML = 'Fotoğraflar yüklenemedi.';
                }});
            }}

            function showPhotoModal(docId, imageUrl, lat, lng, status) {{
                document.getElementById('photo-image').src = imageUrl || '';
                document.getElementById('photo-modal').style.display = 'block';
                document.getElementById('approve-photo-btn').onclick = () => approvePhoto(docId, lat, lng);
                document.getElementById('reject-photo-btn').onclick = () => rejectPhoto(docId, imageUrl);
            }}

            function closePhotoModal() {{
                document.getElementById('photo-modal').style.display = 'none';
            }}

            function approvePhoto(docId, lat, lng) {{
                db.collection('photos').doc(docId).update({{ status: 'approved' }})
                    .then(() => {{
                        photoMarkers.forEach(marker => {{
                            if (marker.position.lat() === lat && marker.position.lng() === lng) {{
                                marker.setAnimation(null);
                            }}
                        }});
                        closePhotoModal();
                        alert('Fotoğraf onaylandı.');
                    }})
                    .catch(err => alert('Onaylama hatası: ' + err));
            }}

            function rejectPhoto(docId, imageUrl) {{
                db.collection('photos').doc(docId).delete()
                    .then(() => {{
                        if (imageUrl) {{
                            const imageRef = storage.refFromURL(imageUrl);
                            imageRef.delete()
                                .then(() => {{
                                    closePhotoModal();
                                    alert('Fotoğraf reddedildi ve silindi.');
                                }})
                                .catch(err => alert('Storage silme hatası: ' + err));
                        }} else {{
                            closePhotoModal();
                            alert('Fotoğraf reddedildi.');
                        }}
                    }})
                    .catch(err => alert('Firestore silme hatası: ' + err));
            }}

            function updateSearchResults(searchData) {{
                const resultList = document.getElementById('search-results');
                resultList.innerHTML = '';
                searchData.forEach(place => {{
                    const li = document.createElement('li');
                    li.textContent = place.name + (place.formatted_address ? ' - ' + place.formatted_address : '');
                    li.style.cursor = 'pointer';
                    li.addEventListener('click', () => {{
                        map.setCenter(place.geometry.location);
                        map.setZoom(14);
                        focusOnNeighborhood(place);
                        fetchWeatherAndAirQuality(place.geometry.location.lat(), place.geometry.location.lng());
                        resultList.innerHTML = '';
                    }});
                    resultList.appendChild(li);
                }});
            }}

            function showMarkerModal() {{
                document.getElementById('marker-modal').style.display = 'block';
                document.getElementById('marker-note').focus();
            }}

            function closeMarkerModal() {{
                document.getElementById('marker-modal').style.display = 'none';
                document.getElementById('marker-form').reset();
            }}

            function showTeamModal() {{
                document.getElementById('team-modal').style.display = 'block';
                document.getElementById('team-name').focus();
            }}

            function closeTeamModal() {{
                document.getElementById('team-modal').style.display = 'none';
                document.getElementById('team-form').reset();
            }}

            function focusOnNeighborhood(place) {{
                if (currentPolygon) {{
                    currentPolygon.setMap(null);
                }}

                const neighborhoods = [
                    {{ 
                        name: "Beyoğlu", 
                        coords: [{{lat: 41.032, lng: 28.977}}, {{lat: 41.038, lng: 28.985}}, {{lat: 41.040, lng: 28.970}}, {{lat: 41.035, lng: 28.965}}], 
                        riskLevel: "Yüksek", 
                        riskDetail: "Deprem ve sel riski yüksek" 
                    }},
                    {{ 
                        name: "Şişli", 
                        coords: [{{lat: 41.050, lng: 28.985}}, {{lat: 41.060, lng: 28.995}}, {{lat: 41.065, lng: 28.975}}, {{lat: 41.055, lng: 28.965}}], 
                        riskLevel: "Orta", 
                        riskDetail: "Deprem riski orta" 
                    }},
                    {{ 
                        name: "Çankaya", 
                        coords: [{{lat: 39.920, lng: 32.850}}, {{lat: 39.925, lng: 32.860}}, {{lat: 39.930, lng: 32.855}}, {{lat: 39.925, lng: 32.845}}], 
                        riskLevel: "Düşük", 
                        riskDetail: "Afet riski düşük" 
                    }},
                    {{ 
                        name: "Konak", 
                        coords: [{{lat: 38.418, lng: 27.128}}, {{lat: 38.423, lng: 27.138}}, {{lat: 38.428, lng: 27.133}}, {{lat: 38.423, lng: 27.123}}], 
                        riskLevel: "Yüksek", 
                        riskDetail: "Deprem riski yüksek" 
                    }},
                    {{ 
                        name: "Seyhan", 
                        coords: [{{lat: 36.987, lng: 35.325}}, {{lat: 36.992, lng: 35.335}}, {{lat: 36.997, lng: 35.330}}, {{lat: 36.992, lng: 35.320}}], 
                        riskLevel: "Orta", 
                        riskDetail: "Sel riski orta" 
                    }},
                    {{ 
                        name: "Muratpaşa", 
                        coords: [{{lat: 36.890, lng: 30.690}}, {{lat: 36.895, lng: 30.700}}, {{lat: 36.900, lng: 30.695}}, {{lat: 36.895, lng: 30.685}}], 
                        riskLevel: "Düşük", 
                        riskDetail: "Afet riski düşük" 
                    }}
                ];

                const neighborhood = neighborhoods.find(n => n.name.toLowerCase() === place.name.toLowerCase());
                if (!neighborhood) {{
                    map.setCenter(place.geometry.location);
                    map.setZoom(14);
                    document.getElementById('info-panel').innerHTML = 'Bu mahalle için poligon verisi bulunamadı: ' + place.name;
                    return;
                }}

                const bounds = new google.maps.LatLngBounds();
                neighborhood.coords.forEach(coord => bounds.extend(coord));
                map.fitBounds(bounds);

                const riskColor = neighborhood.riskLevel === "Yüksek" ? '#FF4500' : 
                                neighborhood.riskLevel === "Orta" ? '#FFA500' : 
                                '#00FF00';

                currentPolygon = new google.maps.Polygon({{
                    paths: neighborhood.coords,
                    strokeColor: riskColor,
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: riskColor,
                    fillOpacity: 0.35,
                    map: map
                }});

                const centerLat = neighborhood.coords.reduce((sum, coord) => sum + coord.lat, 0) / neighborhood.coords.length;
                const centerLng = neighborhood.coords.reduce((sum, coord) => sum + coord.lng, 0) / neighborhood.coords.length;
                const riskMarker = new google.maps.Marker({{
                    position: {{ lat: centerLat, lng: centerLng }},
                    map: map,
                    label: {{
                        text: neighborhood.riskLevel,
                        color: '#FFFFFF',
                        fontSize: '16px',
                        fontWeight: 'bold'
                    }},
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 0
                    }}
                }});

                currentPolygon.addListener('click', (e) => {{
                    infoWindow.setContent(`
                        <div style="padding:15px; font-family: Poppins;">
                            <h3 style="color: #ff4500; font-size: 20px;">${{neighborhood.name}}</h3>
                            <p style="font-size: 16px;"><strong>Risk Seviyesi:</strong> ${{neighborhood.riskLevel}}</p>
                            <p style="font-size: 16px;"><strong>Detay:</strong> ${{neighborhood.riskDetail}}</p>
                        </div>
                    `);
                    infoWindow.setPosition(e.latLng);
                    infoWindow.open(map);
                }});

                document.getElementById('info-panel').innerHTML = `
                    <strong>${{neighborhood.name}}</strong><br>
                    Risk Seviyesi: ${{neighborhood.riskLevel}}<br>
                    Detay: ${{neighborhood.riskDetail}}
                `;
            }}

            function addMarker(location, title, note, iconUrl) {{
                const marker = new google.maps.Marker({{
                    position: location,
                    map: map,
                    title: title,
                    draggable: true,
                    animation: google.maps.Animation.DROP,
                    icon: {{
                        url: iconUrl || 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                        scaledSize: new google.maps.Size(45, 45)
                    }}
                }});

                markers.push(marker);

                marker.addListener('click', () => {{
                    infoWindow.setContent(`
                        <div style="padding:15px; font-family: Poppins;">
                            <h3 style="color: #ff4500; margin: 0 0 8px 0; font-size: 20px;">${{title}}</h3>
                            <p style="font-size: 16px;">Enlem: ${{location.lat().toFixed(6)}}</p>
                            <p style="font-size: 16px;">Boylam: ${{location.lng().toFixed(6)}}</p>
                            <p style="font-size: 16px;">Not: ${{note || 'Yok'}}</p>
                            <button onclick="centerMap(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" alt="center"> Merkeze Al</button>
                            <button onclick="routeToMarker(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/478/478614.png" alt="route"> Buraya Git</button>
                            <button onclick="sendEmergencyAlert('${{title}}', ${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/2688/2688212.png" alt="alert"> Acil Durum Bildir</button>
                        </div>
                    `);
                    infoWindow.open(map, marker);
                }});

                marker.addListener('dragend', () => {{
                    updateMarkerList();
                    findShortestRoute();
                }});

                updateMarkerList();
                if (markers.length >= 2) findShortestRoute();
            }}

            function addCustomTeamMarker(location, name, type, status, note) {{
                const markerIcons = {{
                    'Ambulans': 'https://cdn-icons-png.flaticon.com/512/3097/3097378.png',
                    'Polis': 'https://cdn-icons-png.flaticon.com/512/3063/3063173.png',
                    'Sağlıkçı': 'https://cdn-icons-png.flaticon.com/512/2888/2888679.png',
                    'Jandarma': 'https://cdn-icons-png.flaticon.com/512/2997/2997328.png',
                    'default': 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png'
                }};

                const marker = new google.maps.Marker({{
                    position: location,
                    map: map,
                    title: `${{name}} - ${{status}}`,
                    draggable: true,
                    animation: google.maps.Animation.DROP,
                    icon: {{
                        url: markerIcons[type] || markerIcons['default'],
                        scaledSize: new google.maps.Size(45, 45)
                    }}
                }});

                markers.push(marker);

                marker.addListener('click', () => {{
                    infoWindow.setContent(`
                        <div style="padding:15px; font-family: Poppins;">
                            <h3 style="color: #ff4500; margin: 0 0 8px 0; font-size: 20px;">${{name}} - ${{status}}</h3>
                            <p style="font-size: 16px;">Tür: ${{type}}</p>
                            <p style="font-size: 16px;">Enlem: ${{location.lat().toFixed(6)}}</p>
                            <p style="font-size: 16px;">Boylam: ${{location.lng().toFixed(6)}}</p>
                            <p style="font-size: 16px;">Not: ${{note || 'Yok'}}</p>
                            <button onclick="centerMap(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" alt="center"> Merkeze Al</button>
                            <button onclick="routeToMarker(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/478/478614.png" alt="route"> Buraya Git</button>
                            <button onclick="sendEmergencyAlert('${{name}}', ${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/2688/2688212.png" alt="alert"> Acil Durum Bildir</button>
                        </div>
                    `);
                    infoWindow.open(map, marker);
                }});

                marker.addListener('dragend', () => {{
                    updateMarkerList();
                    findShortestRoute();
                }});

                updateMarkerList();
                if (markers.length >= 2) findShortestRoute();
            }}

            function removeMarker(index) {{
                markers[index].setMap(null);
                markers.splice(index, 1);
                updateMarkerList();
                if (markers.length >= 2) findShortestRoute();
                else directionsRenderer.setDirections({{routes: []}});
            }}

            function centerMap(lat, lng) {{
                map.setCenter({{ lat: lat, lng: lng }});
                map.setZoom(16);
            }}

            function updateMarkerList() {{
                const list = document.getElementById('marker-list');
                list.innerHTML = '';
                markers.forEach((marker, index) => {{
                    const div = document.createElement('div');
                    div.className = 'marker-item';
                    div.innerHTML = `
                        <span>${{marker.title}} (${{marker.position.lat().toFixed(4)}}, ${{marker.position.lng().toFixed(4)}})</span>
                        <div class="marker-actions">
                            <button onclick="centerMap(${{marker.position.lat()}}, ${{marker.position.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" alt="center"> Git</button>
                            <button onclick="removeMarker(${{index}})"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" alt="remove"> Sil</button>
                        </div>
                    `;
                    list.appendChild(div);
                }});
            }}

            function clearMarkers() {{
                markers.forEach(marker => marker.setMap(null));
                markers = [];
                directionsRenderer.setDirections({{routes: []}});
                updateMarkerList();
            }}

            function zoomToFit() {{
                if (markers.length === 0) return;
                const bounds = new google.maps.LatLngBounds();
                markers.forEach(marker => bounds.extend(marker.position));
                map.fitBounds(bounds);
            }}

            function findShortestRoute() {{
                if (markers.length < 2) {{
                    document.getElementById('info-panel').innerHTML = 'En kısa yol için en az 2 işaretçi ekleyin.';
                    return;
                }}

                const origin = markers[0].position;
                const destination = markers[markers.length - 1].position;
                const waypoints = markers.slice(1, -1).map(marker => ({{
                    location: marker.position,
                    stopover: true
                }}));

                directionsService.route({{
                    origin: origin,
                    destination: destination,
                    waypoints: waypoints,
                    optimizeWaypoints: true,
                    travelMode: google.maps.TravelMode.DRIVING,
                    avoidTolls: document.getElementById('avoid-tolls').checked,
                    avoidHighways: document.getElementById('avoid-highways').checked,
                    provideRouteAlternatives: true
                }}, (response, status) => {{
                    if (status === 'OK') {{
                        directionsRenderer.setDirections(response);
                        const routes = response.routes;
                        let info = '<strong>En Kısa Yol:</strong><ul id="route-alternatives">';
                        routes.forEach((route, idx) => {{
                            let distance = 0;
                            let duration = 0;
                            route.legs.forEach(leg => {{
                                distance += leg.distance.value;
                                duration += leg.duration.value;
                            }});
                            info += `
                                <li onclick="selectRoute(${{idx}})">
                                    Rota ${{idx + 1}}: ${{(distance / 1000).toFixed(2)}} km, ${{Math.round(duration / 60)}} dk
                                </li>
                            `;
                        }});
                        info += '</ul>';
                        document.getElementById('info-panel').innerHTML = info;
                    }} else {{
                        alert('Yol bulunamadı: ' + status);
                    }}
                }});
            }}

            function selectRoute(index) {{
                directionsRenderer.setRouteIndex(index);
                const route = directionsRenderer.getDirections().routes[index];
                let distance = 0;
                let duration = 0;
                route.legs.forEach(leg => {{
                    distance += leg.distance.value;
                    duration += leg.duration.value;
                }});
                const info = `
                    <strong>Seçilen Rota:</strong><br>
                    Mesafe: ${{(distance / 1000).toFixed(2)}} km<br>
                    Süre: ${{Math.round(duration / 60)}} dk
                `;
                document.getElementById('info-panel').innerHTML = info;
            }}

            function getCurrentLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(position => {{
                        userLocation = {{ lat: position.coords.latitude, lng: position.coords.longitude }};
                        map.setCenter(userLocation);
                        const existingMarker = markers.find(m => m.title === 'Mevcut Konum');
                        if (!existingMarker) {{
                            addMarker(userLocation, 'Mevcut Konum', '', '');
                        }} else {{
                            existingMarker.setPosition(userLocation);
                        }}
                        map.setZoom(16);
                        document.getElementById('info-panel').innerHTML = 'Mevcut konum başarıyla bulundu.';
                    }}, error => {{
                        let errorMsg = 'Konum alınamadı: ';
                        switch(error.code) {{
                            case error.PERMISSION_DENIED:
                                errorMsg += 'Konum izni reddedildi.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMsg += 'Konum bilgisi kullanılamıyor.';
                                break;
                            case error.TIMEOUT:
                                errorMsg += 'Konum alma zaman aşımına uğradı.';
                                break;
                            default:
                                errorMsg += 'Bilinmeyen bir hata oluştu.';
                        }}
                        alert(errorMsg);
                        document.getElementById('info-panel').innerHTML = errorMsg;
                    }}, {{
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    }});
                }} else {{
                    alert('Tarayıcınız konum servisini desteklemiyor.');
                    document.getElementById('info-panel').innerHTML = 'Konum servisi desteklenmiyor.';
                }}
            }}

            function routeToMarker(lat, lng) {{
                if (!userLocation) {{
                    alert('Önce mevcut konumunuzu belirleyin.');
                    getCurrentLocation();
                    return;
                }}
                directionsService.route({{
                    origin: userLocation,
                    destination: {{ lat: lat, lng: lng }},
                    travelMode: google.maps.TravelMode.DRIVING,
                    optimizeWaypoints: true,
                    avoidTolls: document.getElementById('avoid-tolls').checked,
                    avoidHighways: document.getElementById('avoid-highways').checked,
                    provideRouteAlternatives: true
                }}, (response, status) => {{
                    if (status === 'OK') {{
                        directionsRenderer.setDirections(response);
                        const routes = response.routes;
                        let info = '<strong>Hedefe Yol:</strong><ul id="route-alternatives">';
                        routes.forEach((route, idx) => {{
                            let distance = 0;
                            let duration = 0;
                            route.legs.forEach(leg => {{
                                distance += leg.distance.value;
                                duration += leg.duration.value;
                            }});
                            info += `
                                <li onclick="selectRoute(${{idx}})">
                                    Rota ${{idx + 1}}: ${{(distance / 1000).toFixed(2)}} km, ${{Math.round(duration / 60)}} dk
                                </li>
                            `;
                        }});
                        info += '</ul>';
                        document.getElementById('info-panel').innerHTML = info;
                    }} else {{
                        alert('Yol bulunamadı: ' + status);
                    }}
                }});
            }}

            function toggleTraffic() {{
                if (trafficLayer.getMap()) {{
                    trafficLayer.setMap(null);
                    document.getElementById('traffic-btn').textContent = 'Trafik Göster';
                }} else {{
                    trafficLayer.setMap(map);
                    document.getElementById('traffic-btn').textContent = 'Trafik Gizle';
                    updateTrafficInfo();
                }}
            }}

            function sendEmergencyAlert(title, lat, lng) {{
                const alertDiv = document.createElement('div');
                alertDiv.className = 'emergency-alert';
                alertDiv.innerHTML = `<strong>Acil Durum Bildirimi:</strong> ${{title}} (Enlem: ${{lat.toFixed(4)}}, Boylam: ${{lng.toFixed(4)}}) için acil durum bildirildi!`;
                document.getElementById('info-panel').appendChild(alertDiv);
                setTimeout(() => alertDiv.remove(), 5000);
                alert(`Acil Durum Bildirimi Gönderildi: ${{title}} (Enlem: ${{lat.toFixed(4)}}, Boylam: ${{lng.toFixed(4)}})`);
            }}

            function updateTrafficInfo() {{
                if (trafficLayer.getMap() && markers.length >= 2) {{
                    findShortestRoute();
                }}
            }}
        </script>
    </head>
    <body>
        <div id="map"></div>
        <button id="toggle-btn">☰</button>
        <div id="marker-toolbar">
            <button class="marker-btn" data-type="Ambulans"><img src="https://cdn-icons-png.flaticon.com/512/3097/3097378.png" alt="ambulans"> Ambulans</button>
            <button class="marker-btn" data-type="Polis"><img src="https://cdn-icons-png.flaticon.com/512/3063/3063173.png" alt="polis"> Polis</button>
            <button class="marker-btn" data-type="Sağlıkçı"><img src="https://cdn-icons-png.flaticon.com/512/2888/2888679.png" alt="sağlıkçı"> Sağlıkçı</button>
            <button class="marker-btn" data-type="Jandarma"><img src="https://cdn-icons-png.flaticon.com/512/2997/2997328.png" alt="jandarma"> Jandarma</button>
            <button class="marker-btn" data-type="team"><img src="https://cdn-icons-png.flaticon.com/512/992/992651.png" alt="ekip"> Ekip Ekle</button>
        </div>
        <div id="sidebar">
            <div class="control-panel">
                <h2>Afet Kontrol Paneli</h2>
                <div class="search-container">
                    <input id="search-input" type="text" placeholder="Mahalle ara...">
                </div>
                <ul id="search-results"></ul>
                <button onclick="clearMarkers()"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png" alt="clear"> Tüm İşaretçileri Temizle</button>
                <button onclick="zoomToFit()"><img src="https://cdn-icons-png.flaticon.com/512/3161/3161358.png" alt="zoom"> İşaretçilere Yakınlaştır</button>
                <button onclick="findShortestRoute()"><img src="https://cdn-icons-png.flaticon.com/512/478/478614.png" alt="route"> En Kısa Yolu Bul</button>
                <button onclick="getCurrentLocation()"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" alt="location"> Mevcut Konum</button>
                <button id="traffic-btn" onclick="toggleTraffic()"><img src="https://cdn-icons-png.flaticon.com/512/2965/2965879.png" alt="traffic"> Trafik Göster</button>
                <button id="toggle-heatmap">Heatmap Göster</button>
                <button id="toggle-3d">3D Görünüm</button>
                <select onchange="map.setMapTypeId(this.value)">
                    <option value="roadmap">Yol Haritası</option>
                    <option value="satellite">Uydu</option>
                    <option value="hybrid">Hibrit</option>
                    <option value="terrain">Arazi</option>
                </select>
                <label><input type="checkbox" id="avoid-tolls"> Ücretli Yollardan Kaçın</label>
                <label><input type="checkbox" id="avoid-highways"> Otoyollardan Kaçın</label>
            </div>
            <div class="control-panel">
                <h3>Afet Noktaları</h3>
                <div id="marker-list"></div>
            </div>
            <div class="control-panel">
                <h3>Hava Durumu</h3>
                <div id="weather-info">Hava durumu yükleniyor...</div>
            </div>
            <div class="control-panel">
                <h3>Hava Kalitesi</h3>
                <div id="air-quality-info">Hava kalitesi yükleniyor...</div>
            </div>
            <div id="info-panel">Afet Yönetim Bilgi Paneli</div>
        </div>
        <div id="marker-modal">
            <h3>Marker Notu Ekle</h3>
            <form id="marker-form">
                <input id="marker-note" type="text" class="form-input" placeholder="Not (isteğe bağlı)">
                <button type="submit" class="btn-custom">Ekle</button>
                <button type="button" id="cancel-marker-btn" class="btn-custom btn-cancel">İptal</button>
            </form>
        </div>
        <div id="team-modal">
            <h3>Ekip Bilgileri</h3>
            <form id="team-form">
                <input id="team-name" type="text" class="form-input" placeholder="Ekip Adı (Zorunlu)" required>
                <select id="team-type" class="form-select">
                    <option value="">Ekip Türü Seçin</option>
                    <option value="Ambulans">Ambulans</option>
                    <option value="Polis">Polis</option>
                    <option value="Sağlıkçı">Sağlıkçı</option>
                    <option value="Jandarma">Jandarma</option>
                    <option value="Diğer">Diğer</option>
                </select>
                <select id="team-status" class="form-select">
                    <option value="Aktif">Aktif</option>
                    <option value="Pasif">Pasif</option>
                    <option value="Yolda">Yolda</option>
                </select>
                <button type="submit" class="btn-custom">Ekip Ekle</button>
                <button type="button" id="cancel-team-btn" class="btn-custom btn-cancel">İptal</button>
            </form>
        </div>
        <div id="photo-modal">
            <h3>Fotoğraf Kontrol</h3>
            <img id="photo-image" src="" alt="Fotoğraf">
            <button id="approve-photo-btn" class="btn-custom btn-approve">Onayla</button>
            <button id="reject-photo-btn" class="btn-custom btn-reject">Reddet</button>
            <button type="button" onclick="closePhotoModal()" class="btn-custom btn-cancel">Kapat</button>
        </div>
    </body>
    </html>"""

    def update_map(self):
        """HTML içeriğini web view'a yükle"""
        self.web_view.setHtml(self.get_map_html(), QUrl("http://localhost/"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsWindow()
    window.show()
    sys.exit(app.exec_())