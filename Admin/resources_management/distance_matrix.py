"""
Türkiye'deki şehirler arası mesafe ve lojistik verilerini içeren modül.
Mesafeler karayolu üzerinden km cinsindendir.
"""

from typing import Dict, List, Tuple
import random

class LogisticsData:
    def __init__(self):
        # Örnek mesafe matrisi (gerçek verilerle değiştirilmeli)
        self.distances: Dict[str, Dict[str, int]] = {}
        self.road_conditions: Dict[str, Dict[str, float]] = {}
        self.depot_capacities: Dict[str, Dict[str, int]] = {}
        
        self._initialize_data()
    
    def _initialize_data(self):
        """Başlangıç verilerini yükle"""
        # Gerçek veriler bir CSV veya veritabanından yüklenebilir
        # Şimdilik örnek veriler kullanıyoruz
        
        # Depo kapasiteleri (her kaynak türü için)
        self.depot_capacities = {
            "Adana": {
                "Su": 1000000,  # Litre
                "Gıda": 500000,  # Kg
                "İlaç": 100000,  # Kutu
                "Çadır": 10000,  # Adet
                "Battaniye": 50000,  # Adet
                "Diğer": 100000  # Adet
            },
            # Diğer depolar için benzer veriler eklenecek
        }
        
        # Yol durumu faktörleri (1: Çok kötü, 5: Çok iyi)
        self.road_conditions = {
            "Adana": {
                "İstanbul": 4.5,
                "Ankara": 4.0,
                "İzmir": 4.0,
                # Diğer şehirler...
            },
            # Diğer başlangıç noktaları...
        }
    
    def get_distance(self, city1: str, city2: str) -> int:
        """İki şehir arasındaki mesafeyi döndür"""
        # Gerçek veri yoksa rastgele mesafe üret (300-1500 km arası)
        if city1 not in self.distances or city2 not in self.distances[city1]:
            distance = random.randint(300, 1500)
            
            # Mesafeyi kaydet
            if city1 not in self.distances:
                self.distances[city1] = {}
            if city2 not in self.distances:
                self.distances[city2] = {}
                
            self.distances[city1][city2] = distance
            self.distances[city2][city1] = distance
            
            return distance
            
        return self.distances[city1][city2]
    
    def get_road_condition(self, city1: str, city2: str) -> float:
        """İki şehir arasındaki yol durumu faktörünü döndür"""
        # Gerçek veri yoksa rastgele durum üret (3.0-5.0 arası)
        if city1 not in self.road_conditions or city2 not in self.road_conditions[city1]:
            condition = round(random.uniform(3.0, 5.0), 1)
            
            # Durumu kaydet
            if city1 not in self.road_conditions:
                self.road_conditions[city1] = {}
            if city2 not in self.road_conditions:
                self.road_conditions[city2] = {}
                
            self.road_conditions[city1][city2] = condition
            self.road_conditions[city2][city1] = condition
            
            return condition
            
        return self.road_conditions[city1][city2]
    
    def get_transport_time(self, city1: str, city2: str, resource_amount: int) -> Tuple[float, float]:
        """
        İki şehir arasındaki taşıma süresini hesapla
        Returns: (minimum_time, maximum_time) in hours
        """
        distance = self.get_distance(city1, city2)
        road_condition = self.get_road_condition(city1, city2)
        
        # Temel parametreler
        avg_speed = 60 * (road_condition / 5.0)  # km/saat
        loading_time = 1.0  # saat
        unloading_time = 1.0  # saat
        
        # Kaynak miktarına göre yükleme/boşaltma süresini ayarla
        if resource_amount > 10000:
            loading_time *= 2
            unloading_time *= 2
        
        # Minimum ve maksimum süreleri hesapla
        base_time = distance / avg_speed
        min_time = base_time + loading_time + unloading_time
        max_time = min_time * 1.5  # %50 gecikme payı
        
        return (min_time, max_time)
    
    def get_depot_capacity(self, depot: str, resource_type: str) -> int:
        """Deponun belirli bir kaynak türü için kapasitesini döndür"""
        if depot in self.depot_capacities and resource_type in self.depot_capacities[depot]:
            return self.depot_capacities[depot][resource_type]
        
        # Varsayılan değerler
        default_capacities = {
            "Su": 500000,
            "Gıda": 250000,
            "İlaç": 50000,
            "Çadır": 5000,
            "Battaniye": 25000,
            "Diğer": 50000
        }
        
        return default_capacities.get(resource_type, 10000) 