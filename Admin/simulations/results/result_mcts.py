import numpy as np
from typing import List, Dict, Tuple
import random
from dataclasses import dataclass
from ..logistics_calculator import LogisticsCalculator
from ..logistic_vehicle_const import lojistik_araclar
from ..sehirler_ve_ilceler import sehirler

@dataclass
class Action:
    """Bir dağıtım aksiyonunu temsil eden sınıf"""
    depot: str  # Kaynağın gönderileceği depo
    district: Tuple[str, str]  # Hedef bölge (şehir, ilçe) çifti
    vehicle_type: str  # Kullanılacak araç tipi
    resources: Dict[str, int]  # Gönderilecek kaynaklar
    total_cost: float = 0.0  # Toplam maliyet

@dataclass
class State:
    """Simülasyon durumunu temsil eden sınıf"""
    unserved_districts: List[Tuple[str, str]]  # Henüz hizmet verilmemiş bölgeler (şehir, ilçe çiftleri)
    depot_resources: Dict[str, Dict[str, int]]  # Her deponun kalan kaynakları
    depot_vehicles: Dict[str, Dict[str, int]]  # Her deponun kalan araçları
    total_time: float = 0.0
    total_cost: float = 0.0
    last_action: Action = None  # Son uygulanan aksiyon

class MCTSNode:
    def __init__(self, state: State, action: Action = None):
        self.state = state
        self.parent = None
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.action = action  # Bu düğüme ulaşmak için kullanılan aksiyon
        self.untried_actions = []  # _get_possible_actions artık dışarıdan çağrılıyor

    def add_child(self, state: State, action: Action) -> 'MCTSNode':
        """Yeni bir çocuk düğüm ekle"""
        child = MCTSNode(state, action)
        child.parent = self
        self.children.append(child)
        return child

    def _get_possible_actions(self) -> List[Action]:
        """Mevcut durumda mümkün olan tüm aksiyonları hesapla"""
        actions = []
        # TODO: Implement action generation logic
        return actions

    def select_child(self) -> 'MCTSNode':
        """UCT formülü kullanarak en iyi çocuk düğümü seç"""
        c = 1.414  # UCT sabiti
        return max(self.children, 
                  key=lambda child: child.value/child.visits + 
                  c * np.sqrt(2 * np.log(self.visits) / child.visits))

class ResourceDistributionMCTS:
    def __init__(self, logistics_calculator: LogisticsCalculator, 
                 districts: List[str], road_condition: int):
        self.logistics_calculator = logistics_calculator
        self.districts = districts
        self.road_condition = road_condition

    def _get_possible_actions(self, state: State) -> List[Action]:
        """Mevcut durumda mümkün olan tüm aksiyonları hesapla"""
        actions = []
        
        # Eğer tüm bölgelere hizmet verilmişse, aksiyon yok
        if not state.unserved_districts:
            return actions
        
        # Her depo için olası aksiyonları hesapla
        for depot, resources in state.depot_resources.items():
            # Her hizmet verilmemiş bölge için
            for district_pair in state.unserved_districts:
                # Her araç tipi için
                for vehicle_type, count in state.depot_vehicles[depot].items():
                    # Eğer depoda bu tipte araç kalmamışsa, atla
                    if count <= 0:
                        continue
                    
                    # Aracın kapasitelerini al
                    vehicle_capacities = lojistik_araclar[vehicle_type]
                    
                    # Deponun mevcut kaynaklarına göre gönderilebilecek miktarları hesapla
                    possible_resources = {}
                    can_send = False
                    
                    for resource_type, capacity in vehicle_capacities.items():
                        # Depoda kalan miktar ile araç kapasitesinden küçük olanı seç
                        available = state.depot_resources[depot].get(resource_type, 0)
                        sendable = min(available, capacity)
                        
                        if sendable > 0:
                            possible_resources[resource_type] = sendable
                            can_send = True
                    
                    # Eğer gönderilecek kaynak varsa, aksiyonu ekle
                    if can_send:
                        action = Action(
                            depot=depot,
                            district=district_pair,
                            vehicle_type=vehicle_type,
                            resources=possible_resources,
                            total_cost=0.0
                        )
                        actions.append(action)
        
        return actions

    def get_initial_state(self) -> State:
        """Başlangıç durumunu oluştur"""
        return State(
            unserved_districts=self.districts.copy(),
            depot_resources=self.logistics_calculator.get_all_depot_resources(),
            depot_vehicles=self.logistics_calculator.get_all_depot_vehicles()
        )

    def simulate(self, iterations: int) -> Tuple[List[Action], float]:
        """Monte Carlo Tree Search simülasyonunu çalıştır"""
        root = MCTSNode(self.get_initial_state())
        root.untried_actions = self._get_possible_actions(root.state)
        
        for i in range(iterations):
            node = root
            
            # Selection
            while node.untried_actions == [] and node.children:
                node = node.select_child()
            
            # Expansion
            if node.untried_actions:
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                new_state = self._apply_action(node.state, action)
                node = node.add_child(new_state, action)
                node.untried_actions = self._get_possible_actions(node.state)
            
            # Simulation
            terminal_state = self._rollout(node.state)
            
            # Backpropagation
            reward = self._calculate_reward(terminal_state)
            while node:
                node.visits += 1
                node.value += reward
                node = node.parent
            
            # İlerleme çubuğunu güncelle
            progress = (i + 1) / iterations * 100
            if hasattr(self, 'progress_callback'):
                self.progress_callback(progress)
        
        # En iyi aksiyonları seç
        best_actions = self._get_best_actions(root)
        total_cost = sum(action.total_cost for action in best_actions)
        
        return best_actions, total_cost

    def _apply_action(self, state: State, action: Action) -> State:
        """Bir aksiyonu uygulayarak yeni durumu oluştur"""
        # Yeni durum nesnesi oluştur
        new_state = State(
            unserved_districts=state.unserved_districts.copy(),
            depot_resources={k: v.copy() for k, v in state.depot_resources.items()},
            depot_vehicles={k: v.copy() for k, v in state.depot_vehicles.items()},
            total_time=state.total_time,
            total_cost=state.total_cost,
            last_action=action
        )
        
        # Kaynakları depolardan düş
        for resource_type, amount in action.resources.items():
            new_state.depot_resources[action.depot][resource_type] -= amount
        
        # Araç sayısını güncelle
        new_state.depot_vehicles[action.depot][action.vehicle_type] -= 1
        
        # Hizmet verilen bölgeyi listeden çıkar
        if action.district in new_state.unserved_districts:
            new_state.unserved_districts.remove(action.district)
        
        # Süre ve maliyeti hesapla
        min_time, max_time = self.logistics_calculator.get_transport_time(
            action.depot,
            action.district[0],  # Şehir bilgisini kullan
            self.road_condition,
            sum(action.resources.values())
        )
        
        min_cost, max_cost = self.logistics_calculator.calculate_transport_cost(
            action.depot,
            action.district,  # (şehir, ilçe) çiftini gönder
            action.vehicle_type,
            action.resources,
            self.road_condition
        )
        
        # Ortalama değerleri kullan
        avg_time = (min_time + max_time) / 2
        avg_cost = (min_cost + max_cost) / 2
        
        new_state.total_time += avg_time
        new_state.total_cost += avg_cost
        
        # Aksiyonun maliyetini kaydet
        action.total_cost = avg_cost
        
        return new_state

    def _rollout(self, state: State) -> State:
        """Rastgele aksiyonlarla simülasyonu sonuna kadar çalıştır"""
        current_state = state
        while not self._is_terminal(current_state):
            possible_actions = self._get_possible_actions(current_state)
            if not possible_actions:
                break
            action = random.choice(possible_actions)
            current_state = self._apply_action(current_state, action)
        return current_state

    def _is_terminal(self, state: State) -> bool:
        """Durumun terminal (son) olup olmadığını kontrol et"""
        return len(state.unserved_districts) == 0

    def _calculate_reward(self, state: State) -> float:
        """Terminal durum için ödül hesapla"""
        # Daha düşük maliyet ve süre daha yüksek ödül anlamına gelir
        if state.total_cost == 0:
            return 0
        return 1.0 / (state.total_cost * state.total_time)

    def _get_best_actions(self, root: MCTSNode) -> List[Action]:
        """En çok ziyaret edilen yolu takip ederek en iyi aksiyonları bul"""
        actions = []
        node = root
        
        while node.children:
            # En çok ziyaret edilen çocuğu seç
            node = max(node.children, key=lambda c: c.visits)
            if node.action:  # None değilse ekle
                actions.append(node.action)
        
        return actions 
