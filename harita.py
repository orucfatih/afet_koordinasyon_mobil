from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import folium
from folium import plugins
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import osmnx as ox
import json
import os

class HaritaYonetimi:
    def __init__(self):
        self.map_view = QWebEngineView()
        self.map = None
        self.marker_cluster = None
        self.markers = []
        self.geocoder = Nominatim(user_agent="afet_yonetim_sistemi")
        
    def initialize_map(self, height=400):
        """OpenStreetMap tabanlı haritayı başlatır"""
        # Türkiye'nin merkezi koordinatları
        center_coords = [39.9334, 32.8597]
        
        # Temel haritayı oluştur
        self.map = folium.Map(
            location=center_coords,
            zoom_start=6,
            width='100%',
            height=height,
            tiles='OpenStreetMap',  # OpenStreetMap taban haritası
            control_scale=True      # Ölçek çubuğu
        )
        
        # Marker cluster oluştur
        self.marker_cluster = MarkerCluster().add_to(self.map)
        
        # Alternatif harita katmanları ekle
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            attr='OpenStreetMap Hot',
            name='OSM Hot'
        ).add_to(self.map)
        

        # Katman kontrolü ekle
        folium.LayerControl().add_to(self.map)
        
        # Konum bulma kontrolü
        plugins.LocateControl(
            position='topleft',
            strings={'title': 'Konumumu bul'},
            keepCurrentZoomLevel=True
        ).add_to(self.map)
        
        # Çizim araçları
        plugins.Draw(
            export=True,
            position='topleft',
            draw_options={
                'polyline': {'allowIntersection': False},
                'polygon': {'allowIntersection': False},
                'circle': True,
                'rectangle': True,
                'marker': True,
                'circlemarker': False
            },
            edit_options={'poly': {'allowIntersection': False}}
        ).add_to(self.map)
        
        # Mesafe ölçüm aracı
        plugins.MeasureControl(
            position='topleft',
            primary_length_unit='kilometers',
            secondary_length_unit=None,
            primary_area_unit='square kilometers',
            secondary_area_unit=None
        ).add_to(self.map)
        
        # Haritayı görüntüle
        data = self.map._repr_html_()
        self.map_view.setHtml(data)
        return self.map_view
    
    def add_marker(self, lat, lon, popup_text="", icon_type="info"):
        """Haritaya özel simgeli işaretçi ekler"""
        icon_mapping = {
            "info": "info-sign",
            "warning": "warning-sign",
            "danger": "exclamation-sign",
            "hospital": "plus-sign",
            "fire": "fire",
            "police": "star"
        }
        
        icon = folium.Icon(
            icon=icon_mapping.get(icon_type, "info-sign"),
            prefix='glyphicon',
            color='red' if icon_type in ["danger", "fire"] else 'blue'
        )
        
        marker = folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            icon=icon
        )
        marker.add_to(self.marker_cluster)
        self.markers.append({
            'lat': lat,
            'lon': lon,
            'popup': popup_text,
            'type': icon_type
        })
        self._refresh_map()

    def search_location(self, address):
        """OpenStreetMap üzerinden adres araması yapar"""
        try:
            location = self.geocoder.geocode(address)
            if location:
                # Bulunan konuma haritayı odakla
                self.map.location = [location.latitude, location.longitude]
                self.map.zoom_start = 15
                self._refresh_map()
                return {
                    'lat': location.latitude,
                    'lon': location.longitude,
                    'address': location.address
                }
            return None
        except Exception as e:
            print(f"Arama hatası: {e}")
            return None

    def calculate_route(self, start_coords, end_coords):
        """OpenStreetMap üzerinden iki nokta arası rota hesaplar"""
        try:
            # Graf oluştur
            graph = ox.graph_from_point(
                start_coords,
                dist=max(geodesic(start_coords, end_coords).kilometers * 1000, 1000),
                network_type='drive'
            )
            
            # En kısa rotayı hesapla
            orig_node = ox.nearest_nodes(graph, start_coords[1], start_coords[0])
            dest_node = ox.nearest_nodes(graph, end_coords[1], end_coords[0])
            route = ox.shortest_path(graph, orig_node, dest_node)
            
            # Rotayı haritaya çiz
            route_coords = []
            for node in route:
                point = graph.nodes[node]
                route_coords.append([point['y'], point['x']])
            
            # Mesafeyi hesapla
            distance = sum(
                geodesic(route_coords[i], route_coords[i+1]).kilometers
                for i in range(len(route_coords)-1)
            )
            
            # Rotayı haritaya ekle
            folium.PolyLine(
                route_coords,
                weight=4,
                color='blue',
                opacity=0.8,
                popup=f'Mesafe: {distance:.2f} km'
            ).add_to(self.map)
            
            # Başlangıç ve bitiş işaretçileri
            self.add_marker(
                start_coords[0],
                start_coords[1],
                "Başlangıç Noktası",
                "info"
            )
            self.add_marker(
                end_coords[0],
                end_coords[1],
                "Bitiş Noktası",
                "info"
            )
            
            self._refresh_map()
            return distance
        except Exception as e:
            print(f"Rota hesaplama hatası: {e}")
            # Basit düz çizgi rotası göster
            return self._draw_direct_route(start_coords, end_coords)

    def _draw_direct_route(self, start_coords, end_coords):
        """İki nokta arası düz çizgi çizer (rota hesaplanamadığında)"""
        distance = geodesic(start_coords, end_coords).kilometers
        folium.PolyLine(
            locations=[start_coords, end_coords],
            weight=2,
            color='red',
            opacity=0.8,
            popup=f'Yaklaşık mesafe: {distance:.2f} km (düz çizgi)'
        ).add_to(self.map)
        self._refresh_map()
        return distance

    def add_area_highlight(self, coordinates, color='red', popup_text=""):
        """Belirli bir alanı vurgular"""
        folium.Polygon(
            locations=coordinates,
            color=color,
            fill=True,
            popup=popup_text
        ).add_to(self.map)
        self._refresh_map()

    def save_markers(self, filename="markers.json"):
        """İşaretçileri JSON dosyasına kaydeder"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.markers, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False

    def load_markers(self, filename="markers.json"):
        """İşaretçileri JSON dosyasından yükler"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.markers = json.load(f)
                for marker in self.markers:
                    self.add_marker(
                        marker['lat'],
                        marker['lon'],
                        marker['popup'],
                        marker.get('type', 'info')
                    )
                return True
            return False
        except Exception as e:
            print(f"Yükleme hatası: {e}")
            return False

    def _refresh_map(self):
        """Harita görünümünü günceller"""
        data = self.map._repr_html_()
        self.map_view.setHtml(data)

    def clear_map(self):
        """Haritayı temizler"""
        self.initialize_map(self.map.height)
        self.markers = []