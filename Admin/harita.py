import folium
from folium import plugins
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import osmnx as ox
import json
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView


class HaritaYonetimi:
    def __init__(self):
        self.map_view = QWebEngineView()
        self.map = None
        self.marker_cluster = None
        self.markers = []
        self.geocoder = Nominatim(user_agent="afet_yonetim_sistemi")
        
    def initialize_map(self, height=600):
        """Afet yönetimi için gelişmiş harita başlatır"""
        center_coords = [39.9334, 32.8597]  # Türkiye merkezi
        
        self.map = folium.Map(
            location=center_coords,
            zoom_start=6,
            width='100%',
            height=height,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Gelişmiş özellikler
        self.marker_cluster = MarkerCluster().add_to(self.map)
        
        # Afet yönetimi için ek katmanlar
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            attr='Humanitarian OpenStreetMap',
            name='Afet Haritası'
        ).add_to(self.map)
        
        # Konum ve çizim araçları
        plugins.Draw(
            export=True,
            position='topleft',
            draw_options={
                'polyline': {'allowIntersection': False},
                'polygon': {'allowIntersection': False},
                'circle': True,
                'rectangle': True,
                'marker': True
            }
        ).add_to(self.map)
        
        # Mesafe ve alan ölçüm aracı
        plugins.MeasureControl(
            position='topleft',
            primary_length_unit='kilometers',
            primary_area_unit='square kilometers'
        ).add_to(self.map)
        
        # Katman kontrolü
        folium.LayerControl().add_to(self.map)
        
        data = self.map._repr_html_()
        self.map_view.setHtml(data)
        return self.map_view
    
    def add_marker(self, lat, lon, popup_text="", icon_type="info"):
        """Afet yönetimi için özelleştirilmiş işaretçi ekler"""
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
        """Konumu detaylı olarak arar ve döndürür"""
        try:
            location = self.geocoder.geocode(address)
            if location:
                self.map.location = [location.latitude, location.longitude]
                self.map.zoom_start = 15
                self._refresh_map()
                return {
                    'lat': location.latitude,
                    'lon': location.longitude,
                    'address': location.address,
                    'raw': location.raw
                }
            return None
        except Exception as e:
            print(f"Konum arama hatası: {e}")
            return None

    def calculate_route(self, start_coords, end_coords):
        """Afet senaryoları için optimize edilmiş rota hesaplama"""
        try:
            # Geniş bir alan için graf oluştur
            graph = ox.graph_from_point(
                start_coords,
                dist=max(geodesic(start_coords, end_coords).kilometers * 1500, 2000),
                network_type='drive'
            )
            
            # En kısa rotayı hesapla
            orig_node = ox.nearest_nodes(graph, start_coords[1], start_coords[0])
            dest_node = ox.nearest_nodes(graph, end_coords[1], end_coords[0])
            route = ox.shortest_path(graph, orig_node, dest_node)
            
            # Rota koordinatlarını topla
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
                weight=5,
                color='red',
                opacity=0.8,
                popup=f'Afet Rota Mesafesi: {distance:.2f} km'
            ).add_to(self.map)
            
            # Başlangıç ve bitiş işaretçileri
            self.add_marker(
                start_coords[0], start_coords[1], 
                "Başlangıç Noktası", "info"
            )
            self.add_marker(
                end_coords[0], end_coords[1], 
                "Hedef Nokta", "danger"
            )
            
            self._refresh_map()
            return distance
        except Exception as e:
            print(f"Rota hesaplama hatası: {e}")
            return self._draw_direct_route(start_coords, end_coords)

    def _draw_direct_route(self, start_coords, end_coords):
        """Alternatif rota çizimi"""
        distance = geodesic(start_coords, end_coords).kilometers
        folium.PolyLine(
            locations=[start_coords, end_coords],
            weight=3,
            color='orange',
            opacity=0.7,
            popup=f'Doğrudan Mesafe: {distance:.2f} km'
        ).add_to(self.map)
        self._refresh_map()
        return distance

    def add_area_highlight(self, coordinates, color='red', popup_text="Afet Bölgesi"):
        """Alan vurgulama fonksiyonu"""
        folium.Polygon(
            locations=coordinates,
            color=color,
            fill=True,
            fill_opacity=0.3,
            popup=popup_text
        ).add_to(self.map)
        self._refresh_map()

    def save_markers(self, filename="afet_isaretcileri.json"):
        """İşaretçileri kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.markers, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False

    def load_markers(self, filename="afet_isaretcileri.json"):
        """İşaretçileri yükle"""
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
        self.initialize_map()
        self.markers = []