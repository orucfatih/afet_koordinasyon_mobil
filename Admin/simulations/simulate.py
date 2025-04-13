from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QSpinBox, QTabWidget,
                           QFormLayout, QGroupBox, QTextEdit, QLineEdit,
                           QProgressBar, QMessageBox, QTreeWidget, QTreeWidgetItem,
                           QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .logistics_calculator import LogisticsCalculator
from .sehirler_ve_ilceler import sehirler, DISTRIBUTION_CENTERS, bolgelere_gore_iller
from .logistic_vehicle_const import lojistik_araclar, RESOURCE_UNITS



class ResultDialog(QDialog):
    """Simülasyon sonuçlarını gösteren dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simülasyon Sonuçları")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Sonuç metni
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class SimulationTab(QWidget):
    """Simülasyon Sekmesi"""
    def __init__(self):
        super().__init__()
        self.logistics_calculator = LogisticsCalculator()
        #########################################################
        #self.disaster_simulation = DisasterSimulation(self.logistics_calculator)
        #########################################################
        self.selected_districts = {}  # {(il, ilçe): nüfus}
        self.total_population = 0
        
        # Widget'ları başlangıçta tanımla
        self.city_tree = None
        self.selected_areas_text = None
        self.total_population_label = None
        self.depot_list = None  # Depo listesi widget'ı
        self.depot_capacity_inputs = {}  # Depo kapasite giriş alanları
        self.depot_vehicle_inputs = {}  # Depo araç kapasitesi giriş alanları
        self.road_condition = None
        self.iterations = None
        self.resource_inputs = {}
        self.progress_bar = None
        
        # Afet etki simülasyonu widget'ları
        self.disaster_type = None
        self.intensity = None
        self.region_combo = None
        self.population_density = None
        self.building_quality = None
        self.impact_iterations = None
        self.impact_results_text = None
        self.impact_progress_bar = None
        
        self.initUI()

    def initUI(self):
        """Ana arayüzü oluştur"""
        main_layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Afet Simülasyonları")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Kaynak Dağıtım Simülasyonu sekmesi
        resource_tab = self.create_resource_distribution_tab()
        tabs.addTab(resource_tab, "Kaynak Dağıtım Simülasyonu")
        
        # Afet Etki Simülasyonu sekmesi
        impact_tab = self.create_disaster_impact_tab()
        tabs.addTab(impact_tab, "Afet Etki Simülasyonu")
        
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

    def create_resource_distribution_tab(self):
        """Kaynak dağıtım simülasyonu sekmesini oluştur"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Üst kısım - Şehir seçimi ve toplam nüfus
        top_layout = QHBoxLayout()
        
        # Sol taraf - Şehir ağacı
        city_group = QGroupBox("Afet Bölgeleri")
        city_layout = QVBoxLayout()
        
        self.city_tree = QTreeWidget()
        self.city_tree.setHeaderLabel("Şehirler ve İlçeler")
        self.city_tree.setMinimumHeight(300)
        
        city_layout.addWidget(self.city_tree)
        city_group.setLayout(city_layout)
        top_layout.addWidget(city_group)
        
        # Sağ taraf - Seçim özeti
        summary_group = QGroupBox("Seçim Özeti")
        summary_layout = QVBoxLayout()
        
        self.selected_areas_text = QTextEdit()
        self.selected_areas_text.setReadOnly(True)
        self.selected_areas_text.setMinimumHeight(100)
        
        self.total_population_label = QLabel("Toplam Nüfus: 0")
        self.total_population_label.setFont(QFont('Arial', 10, QFont.Bold))
        
        summary_layout.addWidget(self.selected_areas_text)
        summary_layout.addWidget(self.total_population_label)
        
        summary_group.setLayout(summary_layout)
        top_layout.addWidget(summary_group)
        
        layout.addLayout(top_layout)
        
        # Orta kısım - Depo seçimi ve kapasiteleri
        depot_group = QGroupBox("AFAD Lojistik Depoları")
        depot_layout = QVBoxLayout()
        
        # Depo listesi
        self.depot_list = QTreeWidget()
        header_labels = ["Depo"]
        # Kaynak başlıkları
        for resource, unit in RESOURCE_UNITS.items():
            header_labels.append(f"{resource} ({unit})")
        # Araç başlıkları
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
            # Varsayılan değer olarak en büyük araç kapasitesinin 10 katını kullan
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
            
            # Araç tipini ve kapasitelerini gösteren detaylı label
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
        layout.addWidget(depot_group)
        
        # Alt kısım - Simülasyon parametreleri
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
        layout.addWidget(params_group)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Simülasyon başlatma butonu
        start_btn = QPushButton("Dağıtımı Simüle Et")
        start_btn.clicked.connect(self.run_resource_simulation)
        layout.addWidget(start_btn)
        
        tab.setLayout(layout)
        
        # Tüm widget'lar oluşturulduktan sonra ağacı doldur ve sinyali bağla
        self.populate_city_tree()
        self.city_tree.itemChanged.connect(self.on_district_selection_changed)
        
        return tab

    def populate_city_tree(self):
        """Şehir ağacını bölgelere göre doldur"""
        self.city_tree.clear()
        
        # Önce bölgeleri ekle
        for bolge, bolge_sehirleri in bolgelere_gore_iller.items():
            bolge_item = QTreeWidgetItem(self.city_tree)
            bolge_item.setText(0, bolge)
            bolge_item.setFlags(bolge_item.flags() | Qt.ItemIsUserCheckable)
            bolge_item.setCheckState(0, Qt.Unchecked)
            
            # Bölgedeki şehirleri ekle
            for sehir in sorted(bolge_sehirleri):
                if sehir in sehirler:
                    sehir_item = QTreeWidgetItem(bolge_item)
                    sehir_item.setText(0, sehir)
                    sehir_item.setFlags(sehir_item.flags() | Qt.ItemIsUserCheckable)
                    sehir_item.setCheckState(0, Qt.Unchecked)
                    
                    # Şehrin ilçelerini ekle
                    for ilce, nufus in sorted(sehirler[sehir].items()):
                        ilce_item = QTreeWidgetItem(sehir_item)
                        ilce_item.setText(0, f"{ilce} ({nufus:,} kişi)")
                        ilce_item.setFlags(ilce_item.flags() | Qt.ItemIsUserCheckable)
                        ilce_item.setCheckState(0, Qt.Unchecked)
                        ilce_item.setData(0, Qt.UserRole, nufus)

    def on_district_selection_changed(self, item, column):
        """Bölge, şehir veya ilçe seçimi değiştiğinde"""
        # Sinyal döngüsünü engellemek için
        self.city_tree.blockSignals(True)
        
        if item.parent() is None:  # Bölge seçimi
            check_state = item.checkState(0)
            # Tüm şehirleri ve ilçeleri seç/kaldır
            for i in range(item.childCount()):
                sehir_item = item.child(i)
                sehir_item.setCheckState(0, check_state)
                for j in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(j)
                    ilce_item.setCheckState(0, check_state)
        
        elif item.parent().parent() is None:  # Şehir seçimi
            check_state = item.checkState(0)
            # Önce tüm ilçelerin durumunu güncelle
            for i in range(item.childCount()):
                ilce_item = item.child(i)
                ilce_item.setCheckState(0, check_state)
            
            # Bölgenin durumunu kontrol et ve güncelle
            bolge_item = item.parent()
            tum_sehirler_secili = True
            for i in range(bolge_item.childCount()):
                if bolge_item.child(i).checkState(0) != Qt.Checked:
                    tum_sehirler_secili = False
                    break
            bolge_item.setCheckState(0, Qt.Checked if tum_sehirler_secili else Qt.Unchecked)
        
        else:  # İlçe seçimi
            # Şehrin durumunu kontrol et ve güncelle
            sehir_item = item.parent()
            tum_ilceler_secili = True
            for i in range(sehir_item.childCount()):
                if sehir_item.child(i).checkState(0) != Qt.Checked:
                    tum_ilceler_secili = False
                    break
            sehir_item.setCheckState(0, Qt.Checked if tum_ilceler_secili else Qt.Unchecked)
            
            # Bölgenin durumunu kontrol et ve güncelle
            bolge_item = sehir_item.parent()
            tum_sehirler_secili = True
            for i in range(bolge_item.childCount()):
                if bolge_item.child(i).checkState(0) != Qt.Checked:
                    tum_sehirler_secili = False
                    break
            bolge_item.setCheckState(0, Qt.Checked if tum_sehirler_secili else Qt.Unchecked)
        
        # Sinyalleri tekrar etkinleştir
        self.city_tree.blockSignals(False)
        
        # Seçili bölgeleri güncelle
        self.update_selected_areas()

    def update_selected_areas(self):
        """Seçili bölgeleri ve toplam nüfusu güncelle"""
        self.selected_districts.clear()
        self.total_population = 0
        text = ""
        
        # Bölgeleri dolaş
        for i in range(self.city_tree.topLevelItemCount()):
            bolge_item = self.city_tree.topLevelItem(i)
            bolge = bolge_item.text(0)
            
            selected_cities = []
            for j in range(bolge_item.childCount()):
                sehir_item = bolge_item.child(j)
                sehir = sehir_item.text(0)
                
                selected_districts = []
                for k in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(k)
                    if ilce_item.checkState(0) == Qt.Checked:
                        ilce_name = ilce_item.text(0).split(" (")[0]
                        population = ilce_item.data(0, Qt.UserRole)
                        self.selected_districts[(sehir, ilce_name)] = population
                        self.total_population += population
                        selected_districts.append(f"{ilce_name} ({population:,} kişi)")
                
                if selected_districts:
                    if not selected_cities:
                        text += f"{bolge}:\n"
                    selected_cities.append(sehir)
                    text += f"  {sehir}:\n"
                    text += "\n".join(f"    - {d}" for d in selected_districts)
                    text += "\n\n"
        
        self.selected_areas_text.setText(text)
        self.total_population_label.setText(f"Toplam Nüfus: {self.total_population:,} kişi")

    def add_depot(self):
        """Yeni bir depo ekle"""
        depot = self.depot_combo.currentText()
        
        # Depo kapasitelerini al
        capacities = {}
        for resource, spinbox in self.depot_capacity_inputs.items():
            capacities[resource] = spinbox.value()
        
        # Araç kapasitelerini al
        vehicles = {}
        for vehicle_type, spinbox in self.depot_vehicle_inputs.items():
            vehicles[vehicle_type] = spinbox.value()
        
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

    def run_resource_simulation(self):
        """Kaynak dağıtım simülasyonunu başlat"""
        if not self.selected_districts:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir bölge seçin!")
            return
            
        if not self.logistics_calculator.get_all_depots():
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir depo ekleyin!")
            return
        
        # Simülasyon parametrelerini al
        road_condition = self.road_condition.value()
        iterations = self.iterations.value()
        
        # İlerleme çubuğunu göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            # Simülasyonu çalıştır
            results = self.disaster_simulation.simulate_resource_distribution(
                target_districts=self.selected_districts,
                road_condition=road_condition,
                iterations=iterations
            )
            
            # Sonuç penceresini göster
            dialog = ResultDialog(self)
            dialog.result_text.setText("Simülasyon sonuçları burada gösterilecek")
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Simülasyon çalıştırılırken hata oluştu: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)

    def create_disaster_impact_tab(self):
        """Afet etki simülasyonu sekmesini oluştur"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Üst kısım - Şehir seçimi ve toplam nüfus
        top_layout = QHBoxLayout()
        
        # Sol taraf - Şehir ağacı
        city_group = QGroupBox("Afet Bölgeleri")
        city_layout = QVBoxLayout()
        
        # Önce ağacı oluştur
        self.impact_city_tree = QTreeWidget()
        self.impact_city_tree.setHeaderLabel("Şehirler ve İlçeler")
        self.impact_city_tree.setMinimumHeight(300)
        
        city_layout.addWidget(self.impact_city_tree)
        city_group.setLayout(city_layout)
        top_layout.addWidget(city_group)
        
        # Sağ taraf - Seçim özeti
        summary_group = QGroupBox("Seçim Özeti")
        summary_layout = QVBoxLayout()
        
        self.impact_selected_areas_text = QTextEdit()
        self.impact_selected_areas_text.setReadOnly(True)
        self.impact_selected_areas_text.setMinimumHeight(100)
        
        self.impact_total_population_label = QLabel("Toplam Nüfus: 0")
        self.impact_total_population_label.setFont(QFont('Arial', 10, QFont.Bold))
        
        summary_layout.addWidget(self.impact_selected_areas_text)
        summary_layout.addWidget(self.impact_total_population_label)
        
        summary_group.setLayout(summary_layout)
        top_layout.addWidget(summary_group)
        
        layout.addLayout(top_layout)
        
        # Afet parametreleri grubu
        params_group = QGroupBox("Afet Parametreleri")
        params_layout = QFormLayout()
        
        # Afet türü seçimi
        self.disaster_type = QComboBox()
        self.disaster_type.addItems(["Deprem", "Sel", "Yangın", "Heyelan"])
        params_layout.addRow("Afet Türü:", self.disaster_type)
        
        # Afet şiddeti
        self.intensity = QSpinBox()
        self.intensity.setRange(1, 10)
        self.intensity.setValue(7)
        params_layout.addRow("Afet Şiddeti (1-10):", self.intensity)
        
        # Nüfus yoğunluğu
        self.population_density = QSpinBox()
        self.population_density.setRange(1, 5)
        self.population_density.setValue(3)
        self.population_density.setToolTip("1: Çok düşük, 5: Çok yüksek")
        params_layout.addRow("Nüfus Yoğunluğu (1-5):", self.population_density)
        
        # Yapı kalitesi
        self.building_quality = QSpinBox()
        self.building_quality.setRange(1, 5)
        self.building_quality.setValue(3)
        self.building_quality.setToolTip("1: Çok kötü, 5: Çok iyi")
        params_layout.addRow("Ortalama Yapı Kalitesi (1-5):", self.building_quality)
        
        # Monte Carlo iterasyon sayısı
        self.impact_iterations = QSpinBox()
        self.impact_iterations.setRange(100, 10000)
        self.impact_iterations.setValue(1000)
        self.impact_iterations.setSingleStep(100)
        params_layout.addRow("Simülasyon İterasyonu:", self.impact_iterations)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # İlerleme çubuğu
        self.impact_progress_bar = QProgressBar()
        self.impact_progress_bar.setVisible(False)
        layout.addWidget(self.impact_progress_bar)
        
        # Simülasyon başlatma butonu
        impact_start_btn = QPushButton("Afeti Simüle Et")
        impact_start_btn.clicked.connect(self.run_impact_simulation)
        layout.addWidget(impact_start_btn)
        
        tab.setLayout(layout)
        
        # Tüm widget'lar oluşturulduktan sonra ağacı doldur ve sinyali bağla
        self.populate_impact_city_tree()
        self.impact_city_tree.itemChanged.connect(self.on_impact_district_selection_changed)
        
        return tab

    def populate_impact_city_tree(self):
        """Afet etki simülasyonu için şehir ağacını bölgelere göre doldur"""
        self.impact_city_tree.clear()
        
        # Önce bölgeleri ekle
        for bolge, bolge_sehirleri in bolgelere_gore_iller.items():
            bolge_item = QTreeWidgetItem(self.impact_city_tree)
            bolge_item.setText(0, bolge)
            bolge_item.setFlags(bolge_item.flags() | Qt.ItemIsUserCheckable)
            bolge_item.setCheckState(0, Qt.Unchecked)
            
            # Bölgedeki şehirleri ekle
            for sehir in sorted(bolge_sehirleri):
                if sehir in sehirler:
                    sehir_item = QTreeWidgetItem(bolge_item)
                    sehir_item.setText(0, sehir)
                    sehir_item.setFlags(sehir_item.flags() | Qt.ItemIsUserCheckable)
                    sehir_item.setCheckState(0, Qt.Unchecked)
                    
                    # Şehrin ilçelerini ekle
                    for ilce, nufus in sorted(sehirler[sehir].items()):
                        ilce_item = QTreeWidgetItem(sehir_item)
                        ilce_item.setText(0, f"{ilce} ({nufus:,} kişi)")
                        ilce_item.setFlags(ilce_item.flags() | Qt.ItemIsUserCheckable)
                        ilce_item.setCheckState(0, Qt.Unchecked)
                        ilce_item.setData(0, Qt.UserRole, nufus)

    def on_impact_district_selection_changed(self, item, column):
        """Afet etki simülasyonu için bölge, şehir veya ilçe seçimi değiştiğinde"""
        # Sinyal döngüsünü engellemek için
        self.impact_city_tree.blockSignals(True)
        
        if item.parent() is None:  # Bölge seçimi
            check_state = item.checkState(0)
            # Tüm şehirleri ve ilçeleri seç/kaldır
            for i in range(item.childCount()):
                sehir_item = item.child(i)
                sehir_item.setCheckState(0, check_state)
                for j in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(j)
                    ilce_item.setCheckState(0, check_state)
        
        elif item.parent().parent() is None:  # Şehir seçimi
            check_state = item.checkState(0)
            # Önce tüm ilçelerin durumunu güncelle
            for i in range(item.childCount()):
                ilce_item = item.child(i)
                ilce_item.setCheckState(0, check_state)
            
            # Bölgenin durumunu kontrol et ve güncelle
            bolge_item = item.parent()
            tum_sehirler_secili = True
            for i in range(bolge_item.childCount()):
                if bolge_item.child(i).checkState(0) != Qt.Checked:
                    tum_sehirler_secili = False
                    break
            bolge_item.setCheckState(0, Qt.Checked if tum_sehirler_secili else Qt.Unchecked)
        
        else:  # İlçe seçimi
            # Şehrin durumunu kontrol et ve güncelle
            sehir_item = item.parent()
            tum_ilceler_secili = True
            for i in range(sehir_item.childCount()):
                if sehir_item.child(i).checkState(0) != Qt.Checked:
                    tum_ilceler_secili = False
                    break
            sehir_item.setCheckState(0, Qt.Checked if tum_ilceler_secili else Qt.Unchecked)
            
            # Bölgenin durumunu kontrol et ve güncelle
            bolge_item = sehir_item.parent()
            tum_sehirler_secili = True
            for i in range(bolge_item.childCount()):
                if bolge_item.child(i).checkState(0) != Qt.Checked:
                    tum_sehirler_secili = False
                    break
            bolge_item.setCheckState(0, Qt.Checked if tum_sehirler_secili else Qt.Unchecked)
        
        # Sinyalleri tekrar etkinleştir
        self.impact_city_tree.blockSignals(False)
        
        # Seçili bölgeleri güncelle
        self.update_impact_selected_areas()

    def update_impact_selected_areas(self):
        """Afet etki simülasyonu için seçili bölgeleri ve toplam nüfusu güncelle"""
        total_population = 0
        text = ""
        
        # Bölgeleri dolaş
        for i in range(self.impact_city_tree.topLevelItemCount()):
            bolge_item = self.impact_city_tree.topLevelItem(i)
            bolge = bolge_item.text(0)
            
            selected_cities = []
            for j in range(bolge_item.childCount()):
                sehir_item = bolge_item.child(j)
                sehir = sehir_item.text(0)
                
                selected_districts = []
                for k in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(k)
                    if ilce_item.checkState(0) == Qt.Checked:
                        ilce_name = ilce_item.text(0).split(" (")[0]
                        population = ilce_item.data(0, Qt.UserRole)
                        total_population += population
                        selected_districts.append(f"{ilce_name} ({population:,} kişi)")
                
                if selected_districts:
                    if not selected_cities:
                        text += f"{bolge}:\n"
                    selected_cities.append(sehir)
                    text += f"  {sehir}:\n"
                    text += "\n".join(f"    - {d}" for d in selected_districts)
                    text += "\n\n"
        
        self.impact_selected_areas_text.setText(text)
        self.impact_total_population_label.setText(f"Toplam Nüfus: {total_population:,} kişi")

    def run_impact_simulation(self):
        """Afet etki simülasyonunu başlat"""
        # Seçili bölge kontrolü
        if self.impact_selected_areas_text.toPlainText().strip() == "":
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir bölge seçin!")
            return
        
        # Simülasyon parametrelerini al
        disaster_type = self.disaster_type.currentText()
        intensity = self.intensity.value()
        population = self.population_density.value()
        building_quality = self.building_quality.value()
        iterations = self.impact_iterations.value()
        
        # İlerleme çubuğunu göster
        self.impact_progress_bar.setVisible(True)
        self.impact_progress_bar.setValue(0)
        
        try:
            # Sonuç penceresini göster
            dialog = ResultDialog(self)
            dialog.result_text.setText("Afet etki simülasyonu sonuçları burada gösterilecek")
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Simülasyon çalıştırılırken hata oluştu: {str(e)}")
        
        finally:
            self.impact_progress_bar.setVisible(False) 