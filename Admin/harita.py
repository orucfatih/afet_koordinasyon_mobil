import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

class GoogleMapsWindow(QMainWindow):
    """AFAD Afet Yönetim Haritası"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AFAD Afet Yönetim Haritası")
        self.setGeometry(100, 100, 1200, 800)
        
        # Google Maps API key'i ortam değişkeninden al
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            print("\033[91mHATA: API_KEY ortam değişkeni bulunamadı!\033[0m")
            print("\033[93mLütfen .env dosyasında API_KEY değişkenini tanımlayın.\033[0m")
            sys.exit(1)
        
        self.latitude = 39.9334  # Türkiye merkezi (Ankara civarı)
        self.longitude = 32.8597
        
        # Web view setup
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.update_map()

    def get_map_html(self):
        """Generate enhanced Google Maps HTML content with modern AFAD-specific design"""
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
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key}&libraries=places,directions"></script>
    <script>
        let map, markers = [], infoWindow, autocomplete, directionsService, directionsRenderer, trafficLayer, currentPolygon = null;
        let selectedMarkerType = 'default';
        let userLocation = null;

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
                fields: ['geometry', 'name']
            }});
            autocomplete.bindTo('bounds', map);

            autocomplete.addListener('place_changed', () => {{
                const place = autocomplete.getPlace();
                if (!place.geometry) {{
                    alert("Girilen yer için detay bulunamadı: '" + place.name + "'");
                    return;
                }}
                focusOnNeighborhood(place);
            }});

            map.addListener('click', (e) => {{
                addMarker(e.latLng, selectedMarkerType === 'default' ? 'Olay Yeri' : selectedMarkerType);
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
                }});
            }});

            document.getElementById('add-team-btn').addEventListener('click', () => {{
                const teamName = prompt("Ekip adını girin (örneğin: Takım 1):");
                if (!teamName) return;

                const teamType = prompt("Ekip türünü girin (Ambulans, Polis, Sağlıkçı, Jandarma):");
                if (!teamType) return;

                const status = prompt("Ekip durumunu girin (Aktif, Görevde, Hazır):") || "Aktif";

                const center = map.getCenter();
                addCustomTeamMarker(center, teamName, teamType, status);
            }});

            document.getElementById('avoid-tolls').addEventListener('change', findShortestRoute);
            document.getElementById('avoid-highways').addEventListener('change', findShortestRoute);

            getCurrentLocation();
            setInterval(updateTrafficInfo, 60000);
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
                alert("Bu mahalle için poligon verisi bulunamadı: " + place.name);
                map.setCenter(place.geometry.location);
                map.setZoom(14);
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

        function addMarker(location, title) {{
            const markerIcons = {{
                'default': 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'Ambulans': 'https://cdn-icons-png.flaticon.com/512/3097/3097378.png',
                'Polis': 'https://cdn-icons-png.flaticon.com/512/3063/3063173.png',
                'Sağlıkçı': 'https://cdn-icons-png.flaticon.com/512/2888/2888679.png',
                'Jandarma': 'https://cdn-icons-png.flaticon.com/512/2997/2997328.png'
            }};

            const marker = new google.maps.Marker({{
                position: location,
                map: map,
                title: title,
                draggable: true,
                animation: google.maps.Animation.DROP,
                icon: {{
                    url: markerIcons[selectedMarkerType] || markerIcons['default'],
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
                        <button onclick="centerMap(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png"> Merkeze Al</button>
                        <button onclick="routeToMarker(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/478/478614.png"> Buraya Git</button>
                        <button onclick="sendEmergencyAlert('${{title}}', ${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/2688/2688212.png"> Acil Durum Bildir</button>
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

        function addCustomTeamMarker(location, name, type, status) {{
            const markerIcons = {{
                'Ambulans': 'https://cdn-icons-png.flaticon.com/512/3097/3097378.png',
                'Polis': 'https://cdn-icons-png.flaticon.com/512/3063/3063173.png',
                'Sağlıkçı': 'https://cdn-icons-png.flaticon.com/512/2888/2888679.png',
                'Jandarma': 'https://cdn-icons-png.flaticon.com/512/2997/2997328.png',
                'default': 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
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
                        <button onclick="centerMap(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png"> Merkeze Al</button>
                        <button onclick="routeToMarker(${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/478/478614.png"> Buraya Git</button>
                        <button onclick="sendEmergencyAlert('${{name}}', ${{location.lat()}}, ${{location.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/2688/2688212.png"> Acil Durum Bildir</button>
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
                        <button onclick="centerMap(${{marker.position.lat()}}, ${{marker.position.lng()}})"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png"> Git</button>
                        <button onclick="removeMarker(${{index}})"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png"> Sil</button>
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
                    const route = response.routes[0];
                    let distance = 0, duration = 0;
                    route.legs.forEach(leg => {{
                        distance += leg.distance.value;
                        duration += leg.duration.value;
                    }});
                    let info = '<strong>En Kısa Yol:</strong> ' + (distance / 1000).toFixed(2) + ' km, <strong>Süre:</strong> ' + Math.round(duration / 60) + ' dk';
                    if (response.routes.length > 1) {{
                        info += '<br><em>' + (response.routes.length - 1) + ' alternatif rota mevcut.</em>';
                    }}
                    document.getElementById('info-panel').innerHTML = info;
                }} else {{
                    alert('Yol bulunamadı: ' + status);
                }}
            }});
        }}

        function getCurrentLocation() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(position => {{
                    userLocation = {{ lat: position.coords.latitude, lng: position.coords.longitude }};
                    map.setCenter(userLocation);
                    const existingMarker = markers.find(m => m.title === 'Mevcut Konum');
                    if (!existingMarker) {{
                        addMarker(userLocation, 'Mevcut Konum');
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
                    const route = response.routes[0];
                    let distance = route.legs[0].distance.value;
                    let duration = route.legs[0].duration.value;
                    let info = '<strong>Hedefe Yol:</strong> ' + (distance / 1000).toFixed(2) + ' km, <strong>Süre:</strong> ' + Math.round(duration / 60) + ' dk';
                    if (response.routes.length > 1) {{
                        info += '<br><em>' + (response.routes.length - 1) + ' alternatif rota mevcut.</em>';
                    }}
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
<body onload="initMap()">
    <div id="map"></div>
    <button id="toggle-btn">☰</button>
    <div id="marker-toolbar">
        <button class="marker-btn" data-type="Ambulans"><img src="https://cdn-icons-png.flaticon.com/512/3097/3097378.png"> Ambulans</button>
        <button class="marker-btn" data-type="Polis"><img src="https://cdn-icons-png.flaticon.com/512/3063/3063173.png"> Polis</button>
        <button class="marker-btn" data-type="Sağlıkçı"><img src="https://cdn-icons-png.flaticon.com/512/2888/2888679.png"> Sağlıkçı</button>
        <button class="marker-btn" data-type="Jandarma"><img src="https://cdn-icons-png.flaticon.com/512/2997/2997328.png"> Jandarma</button>
        <button class="marker-btn" id="add-team-btn"><img src="https://cdn-icons-png.flaticon.com/512/992/992651.png"> Ekip Ekle</button>
    </div>
    <div id="sidebar">
        <div class="control-panel">
            <h2>Afet Kontrol Paneli</h2>
            <input id="search-input" type="text" placeholder="Mahalle ara...">
            <button onclick="clearMarkers()"><img src="https://cdn-icons-png.flaticon.com/512/1214/1214428.png"> Tüm İşaretçileri Temizle</button>
            <button onclick="zoomToFit()"><img src="https://cdn-icons-png.flaticon.com/512/3161/3161358.png"> İşaretçilere Yakınlaştır</button>
            <button onclick="findShortestRoute()"><img src="https://cdn-icons-png.flaticon.com/512/478/478614.png"> En Kısa Yolu Bul</button>
            <button onclick="getCurrentLocation()"><img src="https://cdn-icons-png.flaticon.com/512/684/684908.png"> Mevcut Konum</button>
            <button id="traffic-btn" onclick="toggleTraffic()"><img src="https://cdn-icons-png.flaticon.com/512/2965/2965879.png"> Trafik Göster</button>
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
        <div id="info-panel">Afet Yönetim Bilgi Paneli</div>
    </div>
</body>
</html>"""

    def update_map(self):
        """Load HTML content into web view"""
        self.web_view.setHtml(self.get_map_html(), QUrl("http://localhost/"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsWindow()
    window.show()
    sys.exit(app.exec_())