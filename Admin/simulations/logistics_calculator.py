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
    
    def get_all_depot_resources(self) -> Dict[str, Dict[str, int]]:
        """Tüm depoların kaynak kapasitelerini döndür"""
        return self.depot_capacities.copy()
    
    def get_all_depot_vehicles(self) -> Dict[str, Dict[str, int]]:
        """Tüm depoların araç kapasitelerini döndür"""
        return self.depot_vehicles.copy()
    
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

    def get_district_city_distance(self, district_pair: Tuple[str, str], city: str) -> int:
        """İlçe ile şehir arasındaki mesafeyi hesapla (şehir merkezini baz alır)"""
        # İlçe bilgisini (şehir, ilçe) çiftinden al
        district_city, district_name = district_pair
        
        # Eğer ilçe hedef şehrin kendi ilçesiyse, mesafeyi 0 kabul et
        if district_city == city:
            return 0
        
        # İlçenin şehri ile hedef şehir arasındaki mesafeyi döndür
        return self.get_distance(district_city, city)

    def calculate_transport_cost(self, depot: str, district: Tuple[str, str],
                               vehicle_type: str, resources: Dict[str, int], road_condition: int) -> Tuple[float, float]:
        """Taşıma maliyetini hesapla"""
        # Mesafeyi hesapla
        distance = self.get_district_city_distance(district, depot)
        
        # Araç başına km maliyeti (yakıt, bakım, vs.)
        cost_per_km = {
            "Hafif Tonaj": 2.5,
            "Orta Tonaj": 3.5,
            "Ağır Tonaj (TIR)": 5.0
        }
        
        # Toplam kaynak miktarı
        total_resources = sum(resources.values())
        
        # Baz maliyet
        base_cost = distance * cost_per_km[vehicle_type]
        
        # Yol durumuna göre ek maliyet
        condition_multiplier = 1 + (5 - road_condition) * 0.2  # Kötü yol = daha yüksek maliyet
        
        # Minimum ve maksimum maliyetler
        min_cost = base_cost * condition_multiplier
        max_cost = min_cost * 1.3  # %30 beklenmeyen giderler
        
        return (min_cost, max_cost)

    def calculate_daily_needs(self, population: int) -> Dict[str, int]:
        """Nüfusa göre günlük ihtiyaçları hesapla"""
        daily_needs_per_person = {
            "Su": 3,        # litre/gün
            "Gıda": 2,      # öğün/gün
            "İlaç": 0.2,    # kutu/gün
            "Çadır": 0.2,   # adet/kişi (5 kişilik aile varsayımı)
            "Battaniye": 1, # adet/kişi
            "Diğer": 0.5    # paket/gün
        }
        
        return {
            resource: int(population * amount)
            for resource, amount in daily_needs_per_person.items()
        }

    def calculate_transport_details(self, depot: str, district: Tuple[str, str], 
                                  road_condition: int) -> Dict[str, float]:
        """Taşıma detaylarını hesapla (mesafe, süre, hız)"""
        distance = self.get_district_city_distance(district, depot)
        avg_speed = self.calculate_average_speed(road_condition)
        
        # Sabit yükleme/boşaltma süreleri
        loading_time = 1.0  # saat
        unloading_time = 1.0  # saat
        
        # Yolculuk süresi
        travel_time = distance / avg_speed
        
        # Toplam süre
        total_time = travel_time + loading_time + unloading_time
        
        return {
            "distance": distance,
            "average_speed": avg_speed,
            "loading_time": loading_time,
            "unloading_time": unloading_time,
            "travel_time": travel_time,
            "total_time": total_time
        } 