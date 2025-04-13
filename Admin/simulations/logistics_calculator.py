"""
Türkiye'deki şehirler arası lojistik hesaplamalarını yapan modül.
Mesafeler karayolu üzerinden km cinsindendir.
"""

from typing import Dict, List, Tuple
from .sehirler_ve_ilceler import sehirler, mesafeler, iller
from .logistic_vehicle_const import lojistik_araclar, RESOURCE_UNITS

class LogisticsCalculator:
    def __init__(self):
        self.depot_capacities: Dict[str, Dict[str, int]] = {}
        self.depot_vehicles: Dict[str, Dict[str, int]] = {}  # {depot: {"Hafif Tonaj": count, ...}}
    
    def add_depot(self, depot: str, capacities: Dict[str, int], vehicles: Dict[str, int]) -> None:
        """Yeni bir depo ekle veya mevcut depo kapasitelerini güncelle"""
        # Sadece geçerli kaynak türlerini kabul et
        valid_capacities = {k: v for k, v in capacities.items() if k in RESOURCE_UNITS}
        self.depot_capacities[depot] = valid_capacities
        
        # Sadece geçerli araç türlerini kabul et
        valid_vehicles = {k: v for k, v in vehicles.items() if k in lojistik_araclar}
        self.depot_vehicles[depot] = valid_vehicles
    
    def remove_depot(self, depot: str) -> None:
        """Bir depoyu kaldır"""
        if depot in self.depot_capacities:
            del self.depot_capacities[depot]
        if depot in self.depot_vehicles:
            del self.depot_vehicles[depot]
    
    def get_all_depots(self) -> List[str]:
        """Tüm depoları döndür"""
        return list(self.depot_capacities.keys())
    
    def get_depot_capacity(self, depot: str, resource_type: str) -> int:
        """Deponun belirli bir kaynak türü için kapasitesini döndür"""
        if depot in self.depot_capacities and resource_type in self.depot_capacities[depot]:
            return self.depot_capacities[depot][resource_type]
        
        # Varsayılan değerler - en büyük araç kapasitesinin 50 katı
        if resource_type in RESOURCE_UNITS:
            max_capacity = max(vehicle[resource_type] for vehicle in lojistik_araclar.values())
            return max_capacity * 50
        return 10000
    
    def get_depot_vehicles(self, depot: str) -> Dict[str, int]:
        """Deponun araç kapasitelerini döndür"""
        if depot in self.depot_vehicles:
            return self.depot_vehicles[depot]
        return {vehicle_type: 0 for vehicle_type in lojistik_araclar.keys()}
    
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