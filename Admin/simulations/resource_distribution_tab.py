from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QSpinBox, QProgressBar,
                           QFormLayout, QGroupBox, QMessageBox, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt

from .logistics_calculator import LogisticsCalculator
from .sehirler_ve_ilceler import DISTRIBUTION_CENTERS
from .logistic_vehicle_const import lojistik_araclar, RESOURCE_UNITS
from .base_components import BaseSimulationTab

class ResourceDistributionTab(BaseSimulationTab):
    """Kaynak Dağıtım Simülasyonu Sekmesi"""
    def __init__(self, parent=None):
        # Önce kendi değişkenlerimizi tanımlayalım
        self.logistics_calculator = LogisticsCalculator()
        self.depot_list = None
        self.depot_combo = None
        self.depot_capacity_inputs = {}
        self.depot_vehicle_inputs = {}
        self.road_condition = None
        self.iterations = None
        
        # Şimdi üst sınıfın init metodunu çağıralım
        super().__init__(parent)

    def initUI(self):
        """Ana arayüzü oluştur"""
        layout = QVBoxLayout()
        
        # Üst kısım - Şehir seçimi ve toplam nüfus (BaseSimulationTab'dan geliyor)
        layout.addLayout(self.create_city_selection_ui())
        
        # Orta kısım - Depo seçimi ve kapasiteleri
        layout.addWidget(self.create_depot_management_ui())
        
        # Alt kısım - Simülasyon parametreleri
        layout.addWidget(self.create_simulation_parameters_ui())
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Simülasyon başlatma butonu
        start_btn = QPushButton("Dağıtımı Simüle Et")
        start_btn.clicked.connect(self.run_simulation)
        layout.addWidget(start_btn)
        
        self.setLayout(layout)

    def create_depot_management_ui(self):
        """Depo yönetimi arayüzünü oluştur"""
        depot_group = QGroupBox("AFAD Lojistik Depoları")
        depot_layout = QVBoxLayout()
        
        # Depo listesi
        self.depot_list = QTreeWidget()
        header_labels = ["Depo"]
        header_labels.extend(f"{resource} ({unit})" for resource, unit in RESOURCE_UNITS.items())
        header_labels.extend(lojistik_araclar.keys())
        
        self.depot_list.setHeaderLabels(header_labels)
        self.depot_list.setMinimumHeight(150)
        depot_layout.addWidget(self.depot_list)
        
        # Depo ekleme alanı
        add_depot_layout = QHBoxLayout()
        
        # Depo seçimi
        depot_select_layout = QVBoxLayout()
        depot_select_layout.addWidget(QLabel("Depo Seçimi:"))
        self.depot_combo = QComboBox()
        self.depot_combo.addItems(DISTRIBUTION_CENTERS)
        depot_select_layout.addWidget(self.depot_combo)
        add_depot_layout.addLayout(depot_select_layout)
        
        # Kaynak kapasiteleri
        resource_capacity_layout = QVBoxLayout()
        capacity_inputs_layout = QHBoxLayout()
        self.depot_capacity_inputs = {}
        for resource, unit in RESOURCE_UNITS.items():
            input_layout = QVBoxLayout()
            label = QLabel(f"{resource}\n({unit})")
            label.setAlignment(Qt.AlignCenter)
            input_layout.addWidget(label)
            
            spinbox = QSpinBox()
            spinbox.setRange(0, 1000000)
            spinbox.setSingleStep(1000)
            default_value = max(vehicle[resource] for vehicle in lojistik_araclar.values()) * 10
            spinbox.setValue(default_value)
            self.depot_capacity_inputs[resource] = spinbox
            input_layout.addWidget(spinbox)
            
            capacity_inputs_layout.addLayout(input_layout)
        
        resource_capacity_layout.addLayout(capacity_inputs_layout)
        add_depot_layout.addLayout(resource_capacity_layout)
        
        # Araç kapasiteleri
        vehicle_capacity_layout = QVBoxLayout()
        vehicle_inputs_layout = QHBoxLayout()
        self.depot_vehicle_inputs = {}
        
        for vehicle_type in lojistik_araclar.keys():
            input_layout = QVBoxLayout()
            
            vehicle_info = [f"{resource}: {capacity} {RESOURCE_UNITS[resource]}"
                          for resource, capacity in lojistik_araclar[vehicle_type].items()]
            tooltip = "\n".join(vehicle_info)
            
            label = QLabel(vehicle_type)
            label.setAlignment(Qt.AlignCenter)
            label.setToolTip(tooltip)
            input_layout.addWidget(label)
            
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setSingleStep(1)
            spinbox.setValue(5)
            spinbox.setToolTip(tooltip)
            self.depot_vehicle_inputs[vehicle_type] = spinbox
            input_layout.addWidget(spinbox)
            
            vehicle_inputs_layout.addLayout(input_layout)
        
        vehicle_capacity_layout.addLayout(vehicle_inputs_layout)
        add_depot_layout.addLayout(vehicle_capacity_layout)
        
        # Depo ekle/kaldır butonları
        button_layout = QVBoxLayout()
        add_depot_btn = QPushButton("Depo Ekle")
        add_depot_btn.clicked.connect(self.add_depot)
        button_layout.addWidget(add_depot_btn)
        
        remove_depot_btn = QPushButton("Depo Kaldır")
        remove_depot_btn.clicked.connect(self.remove_depot)
        button_layout.addWidget(remove_depot_btn)
        
        add_depot_layout.addLayout(button_layout)
        
        depot_layout.addLayout(add_depot_layout)
        depot_group.setLayout(depot_layout)
        
        return depot_group

    def create_simulation_parameters_ui(self):
        """Simülasyon parametreleri arayüzünü oluştur"""
        params_group = QGroupBox("Simülasyon Parametreleri")
        params_layout = QFormLayout()
        
        # Yol durumu
        self.road_condition = QSpinBox()
        self.road_condition.setRange(1, 5)
        self.road_condition.setValue(3)
        self.road_condition.setToolTip("1: En kötü yol durumu, 5: En iyi yol durumu")
        params_layout.addRow("Yol Durumu (1-5):", self.road_condition)
        
        # Monte Carlo iterasyon sayısı
        self.iterations = QSpinBox()
        self.iterations.setRange(100, 10000)
        self.iterations.setValue(1000)
        self.iterations.setSingleStep(100)
        params_layout.addRow("Simülasyon İterasyonu:", self.iterations)
        
        params_group.setLayout(params_layout)
        return params_group

    def add_depot(self):
        """Yeni bir depo ekle"""
        depot = self.depot_combo.currentText()
        
        # Depo kapasitelerini al
        capacities = {resource: spinbox.value() 
                     for resource, spinbox in self.depot_capacity_inputs.items()}
        
        # Araç kapasitelerini al
        vehicles = {vehicle_type: spinbox.value()
                   for vehicle_type, spinbox in self.depot_vehicle_inputs.items()}
        
        # Depoyu LogisticsCalculator'a ekle
        self.logistics_calculator.add_depot(depot, capacities, vehicles)
        
        # Depo listesini güncelle
        self.update_depot_list()
        
        # Depoyu combo box'tan kaldır
        self.depot_combo.removeItem(self.depot_combo.currentIndex())

    def remove_depot(self):
        """Seçili depoyu kaldır"""
        selected_items = self.depot_list.selectedItems()
        if not selected_items:
            return
        
        depot = selected_items[0].text(0)
        
        # Depoyu LogisticsCalculator'dan kaldır
        self.logistics_calculator.remove_depot(depot)
        
        # Depoyu combo box'a geri ekle
        self.depot_combo.addItem(depot)
        
        # Depo listesini güncelle
        self.update_depot_list()

    def update_depot_list(self):
        """Depo listesini güncelle"""
        self.depot_list.clear()
        
        for depot in self.logistics_calculator.get_all_depots():
            item = QTreeWidgetItem([depot])
            
            # Kaynak kapasiteleri
            for i, resource in enumerate(RESOURCE_UNITS.keys()):
                capacity = self.logistics_calculator.get_depot_capacity(depot, resource)
                item.setText(i + 1, f"{capacity:,}")
            
            # Araç kapasiteleri
            vehicles = self.logistics_calculator.get_depot_vehicles(depot)
            for i, vehicle_type in enumerate(lojistik_araclar.keys()):
                count = vehicles.get(vehicle_type, 0)
                item.setText(i + len(RESOURCE_UNITS) + 1, str(count))
            
            self.depot_list.addTopLevelItem(item)
        
        # Sütun genişliklerini ayarla
        for i in range(self.depot_list.columnCount()):
            self.depot_list.resizeColumnToContents(i)

    def run_simulation(self):
        """Kaynak dağıtım simülasyonunu başlat"""
        if not self.city_tree_manager.get_selected_districts():
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir bölge seçin!")
            return
            
        if not self.logistics_calculator.get_all_depots():
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir depo ekleyin!")
            return
        
        # Simülasyon parametrelerini al
        road_condition = self.road_condition.value()
        iterations = self.iterations.value()
        selected_districts = self.city_tree_manager.get_selected_districts()
        
        # İlerleme çubuğunu göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            # TODO: Monte Carlo Tree Search simülasyonunu burada implement et
            QMessageBox.information(self, "Bilgi", "Monte Carlo Tree Search simülasyonu henüz implement edilmedi.")
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Simülasyon çalıştırılırken hata oluştu: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)