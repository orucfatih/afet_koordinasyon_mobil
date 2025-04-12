from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QSpinBox, QTabWidget,
                           QFormLayout, QGroupBox, QTextEdit, QLineEdit,
                           QProgressBar, QMessageBox, QTreeWidget, QTreeWidgetItem,
                           QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .logistics_calculator import LogisticsCalculator
from .monte_carlo import DisasterSimulation
from .sehirler_ve_ilceler import sehirler, DISTRIBUTION_CENTERS

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
        self.disaster_simulation = DisasterSimulation(self.logistics_calculator)
        self.selected_districts = {}  # {(il, ilçe): nüfus}
        self.total_population = 0
        
        # Widget'ları başlangıçta tanımla
        self.city_tree = None
        self.selected_areas_text = None
        self.total_population_label = None
        self.depot_combo = None
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
        
        # Önce ağacı oluştur ama sinyali henüz bağlama
        self.city_tree = QTreeWidget()
        self.city_tree.setHeaderLabel("Şehirler ve İlçeler")
        self.city_tree.setMinimumHeight(300)
        
        city_layout.addWidget(self.city_tree)
        city_group.setLayout(city_layout)
        top_layout.addWidget(city_group)
        
        # Sağ taraf - Seçim özeti
        summary_group = QGroupBox("Seçim Özeti")
        summary_layout = QVBoxLayout()
        
        # Önce metin alanını oluştur
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
        
        # Orta kısım - Dağıtım parametreleri
        params_group = QGroupBox("Dağıtım Parametreleri")
        params_layout = QFormLayout()
        
        # Depo seçimi
        self.depot_combo = QComboBox()
        self.depot_combo.addItems(DISTRIBUTION_CENTERS)
        self.depot_combo.currentTextChanged.connect(self.update_selected_areas)
        params_layout.addRow("AFAD Lojistik Deposu:", self.depot_combo)
        
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
        
        # Alt kısım - Kaynak seçimi
        resource_group = QGroupBox("Kaynak Seçimi")
        resource_layout = QFormLayout()
        
        # Kaynak miktarları için spinbox'lar
        self.resource_inputs = {}
        for resource in ["Su", "Gıda", "Çadır", "Battaniye", "İlaç", "Diğer"]:
            spinbox = QSpinBox()
            spinbox.setRange(0, 1000000)
            spinbox.setSingleStep(100)
            spinbox.setSuffix(" birim")
            self.resource_inputs[resource] = spinbox
            resource_layout.addRow(f"{resource}:", spinbox)
        
        resource_group.setLayout(resource_layout)
        layout.addWidget(resource_group)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Simülasyon başlatma butonu
        start_btn = QPushButton("Simülasyonu Başlat")
        start_btn.clicked.connect(self.run_resource_simulation)
        layout.addWidget(start_btn)
        
        tab.setLayout(layout)
        
        # Tüm widget'lar oluşturulduktan sonra ağacı doldur ve sinyali bağla
        self.populate_city_tree()
        self.city_tree.itemChanged.connect(self.on_district_selection_changed)
        
        return tab

    def populate_city_tree(self):
        """Şehir ağacını doldur"""
        self.city_tree.clear()
        
        for city, districts in sehirler.items():
            city_item = QTreeWidgetItem(self.city_tree)
            city_item.setText(0, city)
            city_item.setFlags(city_item.flags() | Qt.ItemIsUserCheckable)
            city_item.setCheckState(0, Qt.Unchecked)
            
            for district, population in districts.items():
                district_item = QTreeWidgetItem(city_item)
                district_item.setText(0, f"{district} ({population:,} kişi)")
                district_item.setFlags(district_item.flags() | Qt.ItemIsUserCheckable)
                district_item.setCheckState(0, Qt.Unchecked)
                # Nüfus bilgisini data olarak sakla
                district_item.setData(0, Qt.UserRole, population)

    def on_district_selection_changed(self, item, column):
        """Şehir veya ilçe seçimi değiştiğinde"""
        if item.parent() is None:  # Şehir seçimi
            city = item.text(0)
            check_state = item.checkState(0)
            
            # Tüm ilçeleri seç/kaldır
            for i in range(item.childCount()):
                district_item = item.child(i)
                district_item.setCheckState(0, check_state)
        
        # Seçili bölgeleri güncelle
        self.update_selected_areas()

    def update_selected_areas(self):
        """Seçili bölgeleri ve toplam nüfusu güncelle"""
        self.selected_districts.clear()
        self.total_population = 0
        text = ""
        
        # Seçili depo
        selected_depot = self.depot_combo.currentText()
        if selected_depot:
            text += f"AFAD Lojistik Deposu: {selected_depot}\n\n"
        
        for i in range(self.city_tree.topLevelItemCount()):
            city_item = self.city_tree.topLevelItem(i)
            city = city_item.text(0)
            
            selected_districts = []
            for j in range(city_item.childCount()):
                district_item = city_item.child(j)
                if district_item.checkState(0) == Qt.Checked:
                    district_name = district_item.text(0).split(" (")[0]
                    population = district_item.data(0, Qt.UserRole)
                    self.selected_districts[(city, district_name)] = population
                    self.total_population += population
                    selected_districts.append(f"{district_name} ({population:,} kişi)")
            
            if selected_districts:
                # Şehir ve seçili ilçeleri göster
                text += f"{city}:\n"
                text += "\n".join(f"  - {d}" for d in selected_districts)
                
                # Depo seçili ise mesafe bilgisini ekle
                if selected_depot:
                    try:
                        distance = self.logistics_calculator.get_distance(selected_depot, city)
                        text += f"\n  Depoya uzaklık: {distance} km"
                    except ValueError:
                        text += "\n  Depoya uzaklık: Hesaplanamadı"
                text += "\n\n"
        
        self.selected_areas_text.setText(text)
        self.total_population_label.setText(f"Toplam Nüfus: {self.total_population:,} kişi")

    def run_resource_simulation(self):
        """Kaynak dağıtım simülasyonunu başlat"""
        if not self.selected_districts:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir bölge seçin!")
            return
        
        # Kaynak miktarlarını topla
        resources = {
            resource: spinbox.value()
            for resource, spinbox in self.resource_inputs.items()
        }
        
        # Simülasyon parametrelerini al
        depot = self.depot_combo.currentText()
        road_condition = self.road_condition.value()
        iterations = self.iterations.value()
        
        # İlerleme çubuğunu göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            # Simülasyonu çalıştır
            results = self.disaster_simulation.simulate_resource_distribution(
                depot=depot,
                target_districts=self.selected_districts,
                resources=resources,
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
        
        # Bölge seçimi
        self.region_combo = QComboBox()
        self.region_combo.addItems(sehirler.keys())
        params_layout.addRow("Etkilenen Bölge:", self.region_combo)
        
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
        
        # Simülasyon sonuçları grubu
        impact_results_group = QGroupBox("Simülasyon Sonuçları")
        impact_results_layout = QVBoxLayout()
        
        self.impact_results_text = QTextEdit()
        self.impact_results_text.setReadOnly(True)
        self.impact_results_text.setMinimumHeight(200)
        impact_results_layout.addWidget(self.impact_results_text)
        
        impact_results_group.setLayout(impact_results_layout)
        layout.addWidget(impact_results_group)
        
        # İlerleme çubuğu
        self.impact_progress_bar = QProgressBar()
        self.impact_progress_bar.setVisible(False)
        layout.addWidget(self.impact_progress_bar)
        
        # Simülasyon başlatma butonu
        impact_start_btn = QPushButton("Simülasyonu Başlat")
        impact_start_btn.clicked.connect(self.run_impact_simulation)
        layout.addWidget(impact_start_btn)
        
        tab.setLayout(layout)
        return tab

    def run_impact_simulation(self):
        """Afet etki simülasyonunu başlat"""
        # Simülasyon parametrelerini al
        disaster_type = self.disaster_type.currentText()
        intensity = self.intensity.value()
        region = self.region_combo.currentText()
        population = self.population_density.value()
        building_quality = self.building_quality.value()
        iterations = self.impact_iterations.value()
        
        # İlerleme çubuğunu göster
        self.impact_progress_bar.setVisible(True)
        self.impact_progress_bar.setValue(0)
        
        # Simülasyon sonuçlarını göster (örnek)
        results = (
            f"Afet Türü: {disaster_type}\n"
            f"Şiddet: {intensity}\n"
            f"Bölge: {region}\n\n"
            "Tahmini Etki:\n"
            "- Bu kısım daha sonra doldurulacak\n"
            "- Monte Carlo simülasyonu eklenecek\n"
            "- Bina hasarları ve can kayıpları hesaplanacak"
        )
        
        self.impact_results_text.setText(results)
        self.impact_progress_bar.setVisible(False) 