"""
Türkiye'deki şehirler arası lojistik hesaplamalarını yapan modül.
Mesafeler karayolu üzerinden km cinsindendir.
"""

from typing import Dict, List, Tuple
from .sehirler_ve_ilceler import sehirler, mesafeler, iller

class LogisticsCalculator:
    def __init__(self):
        self.depot_capacities: Dict[str, Dict[str, int]] = {}
        self._initialize_data()
    
    def _initialize_data(self):
        """Başlangıç verilerini yükle"""
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
    
    def get_distance(self, city1: str, city2: str) -> int:
        """İki şehir arasındaki mesafeyi döndür"""
        try:
            idx1 = iller.index(city1)
            idx2 = iller.index(city2)
            return mesafeler[idx1][idx2]
        except (ValueError, IndexError):
            raise ValueError(f"Mesafe verisi bulunamadı: {city1} - {city2}")
    
    def calculate_average_speed(self, road_condition: int) -> float:
        """Yol durumuna göre ortalama hızı hesapla (km/saat)"""
        # Yol durumuna göre hız aralıkları
        speed_ranges = {
            1: (30, 40),  # Çok kötü yol
            2: (40, 50),  # Kötü yol
            3: (50, 60),  # Normal yol
            4: (60, 70),  # İyi yol
            5: (70, 80)   # Çok iyi yol
        }
        min_speed, max_speed = speed_ranges.get(road_condition, (50, 60))
        return (min_speed + max_speed) / 2
    
    def get_transport_time(self, city1: str, city2: str, road_condition: int, resource_amount: int) -> Tuple[float, float]:
        """
        İki şehir arasındaki taşıma süresini hesapla
        Returns: (minimum_time, maximum_time) in hours
        """
        mesafeler = self.get_distance(city1, city2)
        avg_speed = self.calculate_average_speed(road_condition)
        
        # Sabit yükleme/boşaltma süreleri
        loading_time = 1.0  # saat
        unloading_time = 1.0  # saat
        
        # Kaynak miktarına göre yükleme/boşaltma süresini ayarla
        if resource_amount > 10000:
            loading_time *= 2
            unloading_time *= 2
        
        # Minimum ve maksimum süreleri hesapla
        base_time = mesafeler / avg_speed
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