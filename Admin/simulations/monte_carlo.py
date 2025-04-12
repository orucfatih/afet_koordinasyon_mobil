"""
Monte Carlo simülasyonu ile afet kaynaklarının dağıtımını simüle eden modül.
"""

from typing import Dict, List, Tuple
import random
import numpy as np
from .logistics_calculator import LogisticsCalculator

class DisasterSimulation:
    def __init__(self, logistics_data: LogisticsCalculator):
        self.logistics = logistics_data
        # Afadın bölgeye yolladığı tırın taşıma kapasitesi bunları kafama göre yazdım
        # gerçek hayatta bu değerler değişecek
        self.truck_capacity = {
            "Su": 550,  # Litre
            "Gıda": 500,  # Kg
            "İlaç": 200,  # Kutu
            "Çadır": 200,  # Adet
            "Battaniye": 1000,  # Adet
            "Diğer": 500  # Birim
        }
        
    def simulate_resource_distribution(
        self,
        depot: str,
        target_districts: Dict[str, int],  # {ilçe_adı: nüfus}
        resources: Dict[str, int],  # {kaynak_türü: miktar}
        road_condition: int,  # 1-5 arası
        iterations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Kaynak dağıtımını Monte Carlo yöntemi ile simüle eder.
        """
        results = {
            'delivery_times': [],  # Tüm teslimat süreleri
            'resource_coverage': [],  # Kaynak karşılama oranları
            'risks': [],  # Risk faktörleri
            'district_analysis': {},  # İlçe bazlı sonuçlar
            'truck_analysis': {}  # Tır analizi sonuçları
        }
        
        # Her ilçe için başlangıç değerleri
        for district in target_districts:
            results['district_analysis'][district] = {
                'delivery_time': {'values': []},
                'coverage': {'values': []},
                'allocated_resources': {resource: {'values': []} for resource in resources},
                'risk_factors': {'time_risk': 0, 'coverage_risk': 0, 'road_risk': 0},
                'total_risk': 0,
                'required_trucks': {'values': []}  # Her iterasyonda gereken tır sayısı
            }
        
        # Monte Carlo iterasyonları
        for _ in range(iterations):
            iteration_results = self._simulate_single_iteration(
                depot, target_districts, resources, road_condition
            )
            
            # Genel sonuçları kaydet
            results['delivery_times'].append(iteration_results['total_time'])
            results['resource_coverage'].append(iteration_results['coverage'])
            results['risks'].append(iteration_results['risk'])
            
            # İlçe bazlı sonuçları kaydet
            for district, data in iteration_results['distribution'].items():
                dist_analysis = results['district_analysis'][district]
                dist_analysis['delivery_time']['values'].append(data['delivery_time'])
                dist_analysis['coverage']['values'].append(data['coverage_ratio'])
                dist_analysis['required_trucks']['values'].append(data['required_trucks'])
                
                # Kaynak dağıtımlarını kaydet
                for resource, amount in data['allocated_resources'].items():
                    dist_analysis['allocated_resources'][resource]['values'].append(amount)
                
                # Risk faktörlerini güncelle
                for risk_type, risk_value in data['risk_factors'].items():
                    if 'values' not in dist_analysis['risk_factors']:
                        dist_analysis['risk_factors']['values'] = []
                    dist_analysis['risk_factors'][risk_type] = risk_value
        
        # Tır analizi yap
        self._analyze_truck_requirements(results, resources)
        
        # Sonuçları analiz et
        self._analyze_results(results, confidence_level)
        return results
    
    def _simulate_single_iteration(
        self,
        depot: str,
        target_districts: Dict[str, int],
        resources: Dict[str, int],
        road_condition: int
    ) -> Dict:
        """Tek bir Monte Carlo iterasyonunu simüle eder"""
        
        total_population = sum(target_districts.values())
        total_time = 0
        total_coverage = 0
        risk_factor = 0
        distribution = {}
        
        # Her ilçe için kaynak dağıtımını simüle et
        for district, population in target_districts.items():
            population_ratio = population / total_population
            
            district_result = {
                'allocated_resources': {},
                'delivery_time': 0,
                'coverage_ratio': 0,
                'risk_factors': {},
                'required_trucks': 0
            }
            
            # Her kaynak türü için dağıtımı hesapla
            total_coverage_ratio = 0
            required_trucks_by_resource = {}
            
            for resource_type, amount in resources.items():
                # İlçeye düşen teorik miktar
                theoretical_amount = int(amount * population_ratio)
                
                # Yol durumuna göre başarı oranını ayarla
                base_success_rate = 0.8 + (road_condition * 0.04)  # 1: 0.84, 5: 1.0
                delivery_success_rate = random.uniform(base_success_rate, 1.0)
                actual_amount = int(theoretical_amount * delivery_success_rate)
                
                district_result['allocated_resources'][resource_type] = actual_amount
                
                # Bu kaynak için gereken tır sayısını hesapla
                trucks_needed = max(1, actual_amount / self.truck_capacity[resource_type])
                required_trucks_by_resource[resource_type] = trucks_needed
                
                # Minimum ihtiyacı karşılama oranını hesapla
                min_need = self._calculate_minimum_need(resource_type, population)
                coverage = min(1.0, actual_amount / min_need)
                total_coverage_ratio += coverage
            
            # Toplam gereken tır sayısı (en çok tır gerektiren kaynağa göre)
            district_result['required_trucks'] = max(required_trucks_by_resource.values())
            
            # Ortalama karşılama oranını hesapla
            district_result['coverage_ratio'] = total_coverage_ratio / len(resources)
            
            # Teslimat süresini hesapla
            try:
                min_time, max_time = self.logistics.get_transport_time(
                    depot,
                    district.split()[0],  # İlçeden şehir adını al
                    road_condition,
                    sum(district_result['allocated_resources'].values())
                )
            except ValueError:
                # Mesafe verisi bulunamadıysa varsayılan değerler kullan
                min_time = 2.0  # 2 saat minimum
                max_time = 6.0  # 6 saat maksimum
            
            # Yol durumuna göre gecikme olasılığını hesapla
            delay_probability = 1.0 - (road_condition / 5.0)  # 1: 0.8, 5: 0
            if random.random() < delay_probability:
                # Gecikme durumunda maksimum süreyi %50 artır
                max_time *= 1.5
            
            # Rastgele bir teslimat süresi seç
            delivery_time = random.uniform(min_time, max_time)
            district_result['delivery_time'] = delivery_time
            
            # Risk faktörlerini hesapla
            district_result['risk_factors'] = {
                'time_risk': self._calculate_time_risk(delivery_time),
                'coverage_risk': self._calculate_coverage_risk(district_result['coverage_ratio']),
                'road_risk': self._calculate_road_risk(road_condition)
            }
            
            # Toplam risk faktörünü hesapla
            risk = self._calculate_weighted_risk(district_result['risk_factors'])
            district_result['total_risk'] = risk
            
            # Genel sonuçları güncelle
            total_time = max(total_time, delivery_time)
            total_coverage += district_result['coverage_ratio'] * population_ratio
            risk_factor += risk * population_ratio
            
            distribution[district] = district_result
        
        return {
            'total_time': total_time,
            'coverage': total_coverage,
            'risk': risk_factor,
            'distribution': distribution
        }
    
    def _calculate_minimum_need(self, resource_type: str, population: int) -> float:
        """Nüfusa göre minimum kaynak ihtiyacını hesapla"""
        daily_needs = {
            "Su": 3.0,  # Litre/kişi/gün
            "Gıda": 2.0,  # Kg/kişi/gün
            "İlaç": 0.1,  # Kutu/kişi/gün
            "Çadır": 0.2,  # Adet/kişi (5 kişilik çadır)
            "Battaniye": 2.0,  # Adet/kişi
            "Diğer": 1.0  # Adet/kişi
        }
        
        return population * daily_needs.get(resource_type, 1.0)
    
    def _calculate_coverage_risk(self, coverage_ratio: float) -> float:
        """Kaynak karşılama oranına göre risk hesapla
        
        Args:
            coverage_ratio: 0-1 arası karşılama oranı
            
        Returns:
            0-1 arası risk değeri
        """
        # Temel risk = karşılanamayan oran
        base_risk = 1.0 - coverage_ratio
        
        # Risk seviyelerini ayarla:
        # %75-100 karşılama -> %0-25 risk (düşük)
        # %50-75 karşılama -> %26-50 risk (orta)
        # %25-50 karşılama -> %51-75 risk (yüksek)
        # %0-25 karşılama -> %76-100 risk (kritik)
        
        # Rastgele değişim ekle
        variation = 0.15  # %15'lik değişim aralığı
        # Düşük riskte daha az, yüksek riskte daha fazla değişim olsun
        if base_risk < 0.25:  # Düşük risk
            variation = 0.1
        elif base_risk > 0.75:  # Kritik risk
            variation = 0.2
            
        random_factor = random.uniform(-variation, variation)
        final_risk = base_risk + random_factor
        
        # Risk değerini 0-1 aralığında tut
        return max(0.0, min(1.0, final_risk))
    
    def _calculate_time_risk(self, delivery_time: float) -> float:
        """Teslimat süresine göre risk hesapla
        
        Args:
            delivery_time: Saat cinsinden teslimat süresi
            
        Returns:
            0-1 arası risk değeri
        """
        # 72 saat kritik süre (3 gün)
        critical_time = 72.0
        base_risk = delivery_time / critical_time
        
        # Risk seviyelerini ayarla:
        # 0-18 saat -> %0-25 (düşük risk)
        # 18-36 saat -> %26-50 (orta risk)
        # 36-54 saat -> %51-75 (yüksek risk)
        # 54-72+ saat -> %76-100 (kritik risk)
        
        # Rastgele değişim ekle
        variation = 0.15  # %15'lik değişim aralığı
        # Teslimat süresi arttıkça değişim aralığını artır
        if base_risk < 0.25:  # Hızlı teslimat
            variation = 0.1
        elif base_risk > 0.75:  # Geç teslimat
            variation = 0.2
            
        random_factor = random.uniform(-variation, variation)
        final_risk = base_risk + random_factor
        
        # Risk değerini 0-1 aralığında tut
        return max(0.0, min(1.0, final_risk))
    
    def _calculate_road_risk(self, road_condition: int) -> float:
        """Yol durumuna göre risk hesapla
        
        Args:
            road_condition: 1-5 arası yol durumu (1: çok kötü, 5: çok iyi)
            
        Returns:
            0-1 arası risk değeri
        """
        # Yol durumuna göre risk seviyeleri:
        # 5 -> %0-20 (çok iyi)
        # 4 -> %21-40 (iyi)
        # 3 -> %41-60 (orta)
        # 2 -> %61-80 (kötü)
        # 1 -> %81-100 (çok kötü)
        base_risk = (6 - road_condition) / 5  # 1->1.0, 2->0.8, 3->0.6, 4->0.4, 5->0.2
        
        # Her seviye için rastgele bir değer ekle
        variation = 0.15  # %15'lik değişim aralığı
        # Yol durumu kötüleştikçe değişim aralığını artır
        if base_risk < 0.25:  # İyi yol durumu
            variation = 0.1
        elif base_risk > 0.75:  # Kötü yol durumu
            variation = 0.2
            
        random_factor = random.uniform(-variation, variation)
        final_risk = base_risk + random_factor
        
        # Risk değerini 0-1 aralığında tut
        return max(0.0, min(1.0, final_risk))
    
    def _calculate_weighted_risk(self, risk_factors: Dict[str, float]) -> float:
        """Risk faktörlerinin ağırlıklı ortalamasını hesapla"""
        weights = {
            'time_risk': 0.4,    # Teslimat süresi riski
            'coverage_risk': 0.4, # Kaynak karşılama riski
            'road_risk': 0.2     # Yol durumu riski
        }
        return sum(risk * weights[factor] for factor, risk in risk_factors.items())
    
    def _analyze_truck_requirements(self, results: Dict, resources: Dict[str, int]) -> None:
        """Tır gereksinimlerini analiz eder"""
        total_trucks_needed = {}
        
        # Her ilçe için ortalama tır gereksinimini hesapla
        for district, data in results['district_analysis'].items():
            avg_trucks = np.mean(data['required_trucks']['values'])
            total_trucks_needed[district] = {
                'mean': avg_trucks,
                'min': min(data['required_trucks']['values']),
                'max': max(data['required_trucks']['values'])
            }
        
        # Toplam tır ihtiyacını hesapla
        results['truck_analysis'] = {
            'total_trucks': {
                'mean': sum(d['mean'] for d in total_trucks_needed.values()),
                'min': sum(d['min'] for d in total_trucks_needed.values()),
                'max': sum(d['max'] for d in total_trucks_needed.values())
            },
            'by_district': total_trucks_needed
        }
    
    def _analyze_results(self, results: Dict, confidence_level: float) -> None:
        """Simülasyon sonuçlarını analiz eder"""
        def calculate_stats(data: List[float]) -> Dict:
            """Temel istatistikleri hesapla"""
            mean = np.mean(data)
            std = np.std(data)
            z = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}[confidence_level]
            margin = z * (std / np.sqrt(len(data)))
            return {
                'mean': mean,
                'median': np.median(data),
                'std': std,
                'confidence_interval': (mean - margin, mean + margin)
            }
        
        # Genel sonuçları analiz et
        for key in ['delivery_times', 'resource_coverage', 'risks']:
            results[key.rstrip('s')] = calculate_stats(results[key])
        
        # İlçe bazlı sonuçları analiz et
        for district, data in results['district_analysis'].items():
            # Teslimat süresi ve karşılama oranı istatistikleri
            data['delivery_time'].update(calculate_stats(data['delivery_time']['values']))
            data['coverage'].update(calculate_stats(data['coverage']['values']))
            
            # Her kaynak türü için istatistikler
            for resource, resource_data in data['allocated_resources'].items():
                resource_data.update(calculate_stats(resource_data['values'])) 