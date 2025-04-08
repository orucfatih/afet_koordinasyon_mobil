"""
daha gerçekçi bir simülasyon için lojistik kaynak depolarının her birinin 81 ile olan uzaklıkları girilmeli
yine her bir ilçenin maksimum kapasitesi girilmeli
ulaşım-trafik veya zaman kısıtları girilmeli
havaalanlarının kapasitesi ve havaalanlarının durumu girilmeli
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QComboBox, QListWidget, 
                           QGroupBox, QSpinBox, QMessageBox, QListWidgetItem,
                           QGridLayout, QDoubleSpinBox, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from styles.styles_dark import *
from styles.styles_light import *
from utils import get_icon_path # sonraki versiyonlarda istenirse
from .sehirler_ve_ilceler import sehirler
from .monte_carlo import DisasterSimulation
from .logistics_calculator import LogisticsCalculator
from .simulation_results import SimulationResultDialog

# Afad lojistik depolarının bulunduğu şehirler
DISTRIBUTION_CENTERS = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Balıkesir", "Bursa",
    "Denizli", "Diyarbakır", "Elazığ", "Erzincan", "Erzurum",
    "Kastamonu", "Manisa", "Kahramanmaraş", "Muğla", "Muş",
    "Samsun", "Sivas", "Tekirdağ", "Aksaray", "Kırıkkale",
    "Yalova", "Düzce"
]

# Kaynak türleri ve birimleri
RESOURCES = {
    "Su": "Litre",
    "Gıda": "Kg",
    "İlaç": "Kutu",
    "Çadır": "Adet",
    "Battaniye": "Adet",
    "Diğer": "Adet"
}

class SimulationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Afet Simülasyonu")
        self.selected_districts = {}  # {ilçe_adı: nüfus} şeklinde seçili ilçeleri tutacak
        self.resource_inputs = {}  # Kaynak input'larını tutacak dictionary
        self.setup_ui()
        self.showFullScreen()  # Açılışta tam ekran başlat

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Şehir Seçimi Grubu
        city_group = QGroupBox("Şehir ve İlçe Seçimi")
        city_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        city_layout = QVBoxLayout()

        # Şehir seçimi
        city_layout_h = QHBoxLayout()
        self.city_combo = QComboBox()
        self.city_combo.addItems(sorted(sehirler.keys()))
        self.city_combo.setStyleSheet(COMBO_BOX_STYLE)
        self.city_combo.currentTextChanged.connect(self.update_districts)
        city_layout_h.addWidget(self.city_combo)
        city_layout.addLayout(city_layout_h)

        # İlçe listesi
        self.district_list = QListWidget()
        self.district_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.district_list.itemChanged.connect(self.on_district_selection_changed)
        city_layout.addWidget(self.district_list)

        # Seçili ilçeler ve toplam nüfus
        self.selection_info = QLabel("Seçili İlçe Sayısı: 0 | Toplam Nüfus: 0")
        self.selection_info.setStyleSheet("color: white; font-weight: bold;")
        city_layout.addWidget(self.selection_info)

        city_group.setLayout(city_layout)
        layout.addWidget(city_group)

        # Simülasyon Parametreleri Grubu
        params_group = QGroupBox("Simülasyon Parametreleri")
        params_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        params_layout = QVBoxLayout()

        # Monte Carlo İterasyon Sayısı
        iteration_layout = QHBoxLayout()
        self.iteration_spin = QSpinBox()
        self.iteration_spin.setRange(100, 10000)
        self.iteration_spin.setSingleStep(100)
        self.iteration_spin.setValue(1000)
        self.iteration_spin.setStyleSheet(RESOURCE_INPUT_STYLE)
        iteration_layout.addWidget(QLabel("İterasyon Sayısı:"))
        iteration_layout.addWidget(self.iteration_spin)
        params_layout.addLayout(iteration_layout)

        # Güven Aralığı
        confidence_layout = QHBoxLayout()
        self.confidence_combo = QComboBox()
        self.confidence_combo.addItems(["90%", "95%", "99%"])
        self.confidence_combo.setStyleSheet(COMBO_BOX_STYLE)
        confidence_layout.addWidget(QLabel("Güven Aralığı:"))
        confidence_layout.addWidget(self.confidence_combo)
        params_layout.addLayout(confidence_layout)

        # Yol Durumu ve Lojistik Parametreleri
        road_group = QGroupBox("Yol ve Lojistik Parametreleri")
        road_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        road_layout = QGridLayout()

        # Yol durumu seçimi (1-5 arası)
        self.road_condition_spin = QSpinBox()
        self.road_condition_spin.setRange(1, 5)
        self.road_condition_spin.setValue(3)
        self.road_condition_spin.setStyleSheet(RESOURCE_INPUT_STYLE)
        road_layout.addWidget(QLabel("Yol Durumu (1: Çok Kötü, 5: Çok İyi):"), 0, 0)
        road_layout.addWidget(self.road_condition_spin, 0, 1)

        # Yol durumu açıklaması
        road_info = QLabel("Not: Yol durumu ortalama hızı etkileyecektir.\n1: 30-40 km/s, 2: 40-50 km/s, 3: 50-60 km/s, 4: 60-70 km/s, 5: 70-80 km/s")
        road_info.setStyleSheet("color: #888; font-style: italic;")
        road_info.setWordWrap(True)
        road_layout.addWidget(road_info, 1, 0, 1, 2)

        road_group.setLayout(road_layout)
        params_layout.addWidget(road_group)

        # Dağıtım Merkezi Seçimi
        distribution_layout = QHBoxLayout()
        self.distribution_center_combo = QComboBox()
        self.distribution_center_combo.addItems(sorted(DISTRIBUTION_CENTERS))
        self.distribution_center_combo.setStyleSheet(COMBO_BOX_STYLE)
        self.distribution_center_combo.currentTextChanged.connect(self.update_distance)
        distribution_layout.addWidget(QLabel("Dağıtım Merkezi:"))
        distribution_layout.addWidget(self.distribution_center_combo)
        params_layout.addLayout(distribution_layout)

        # Mesafe bilgisi
        self.distance_label = QLabel("")
        self.distance_label.setStyleSheet("color: #888; font-style: italic;")
        self.distance_label.setWordWrap(True)
        params_layout.addWidget(self.distance_label)

        # Dağıtım merkezi açıklaması
        distribution_info = QLabel("Not: Seçilen dağıtım merkezinden afet bölgesine kaynak dağıtımı simüle edilecektir.")
        distribution_info.setStyleSheet("color: #888; font-style: italic;")
        distribution_info.setWordWrap(True)
        params_layout.addWidget(distribution_info)

        # Kaynak Miktarları Girişi
        resources_group = QGroupBox("Kaynak Miktarları")
        resources_group.setStyleSheet(RESOURCE_GROUP_STYLE)
        resources_layout = QGridLayout()

        # Başlık satırı
        resources_layout.addWidget(QLabel("Kaynak Türü"), 0, 0)
        resources_layout.addWidget(QLabel("Miktar"), 0, 1)
        resources_layout.addWidget(QLabel("Birim"), 0, 2)

        # Her bir kaynak için input alanları
        for row, (resource, unit) in enumerate(RESOURCES.items(), 1):
            # Kaynak adı
            resources_layout.addWidget(QLabel(resource), row, 0)
            
            # Miktar girişi
            amount_input = QSpinBox()
            amount_input.setRange(0, 1000000)
            amount_input.setSingleStep(100)
            amount_input.setStyleSheet(RESOURCE_INPUT_STYLE)
            resources_layout.addWidget(amount_input, row, 1)
            self.resource_inputs[resource] = amount_input  # Input'u kaydet
            
            # Birim
            resources_layout.addWidget(QLabel(unit), row, 2)

        resources_group.setLayout(resources_layout)
        params_layout.addWidget(resources_group)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Butonlar
        buttons_layout = QHBoxLayout()
        
        self.simulate_btn = QPushButton("Simülasyonu Başlat")
        self.simulate_btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        self.simulate_btn.clicked.connect(self.run_simulation)
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.simulate_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # İlk şehir için ilçeleri yükle
        self.update_districts(self.city_combo.currentText())

    def update_districts(self, city_name):
        """Seçili şehrin ilçelerini listele"""
        self.district_list.clear()
        if city_name in sehirler:
            for district, population in sehirler[city_name].items():
                item = QListWidgetItem(f"{district} ({population:,} kişi)")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.district_list.addItem(item)

    def on_district_selection_changed(self, item):
        """İlçe seçimi değiştiğinde toplam nüfusu güncelle"""
        district_name = item.text().split(" (")[0]
        city_name = self.city_combo.currentText()
        
        if item.checkState() == Qt.Checked:
            self.selected_districts[district_name] = sehirler[city_name][district_name]
        else:
            self.selected_districts.pop(district_name, None)
        
        total_population = sum(self.selected_districts.values())
        self.selection_info.setText(
            f"Seçili İlçe Sayısı: {len(self.selected_districts)} | "
            f"Toplam Nüfus: {total_population:,} kişi"
        )

        # Mesafe bilgisini güncelle
        self.update_distance()

    def update_distance(self):
        """Dağıtım merkezi değiştiğinde mesafeyi güncelle"""
        if len(self.selected_districts) > 0:
            calculator = LogisticsCalculator()
            depot = self.distribution_center_combo.currentText()
            target_city = self.city_combo.currentText()
            try:
                distance = calculator.get_distance(depot, target_city)
                self.distance_label.setText(
                    f"Dağıtım Merkezi ({depot}) ile Hedef Şehir ({target_city}) arası mesafe: {distance} km"
                )
            except ValueError:
                self.distance_label.setText("Mesafe verisi bulunamadı")
        else:
            self.distance_label.setText("")

    def run_simulation(self):
        """Simülasyonu başlatır"""
        if not self.selected_districts:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir ilçe seçin!")
            return

        # Kaynak miktarlarını kontrol et ve topla
        resources = {}
        for resource, input_widget in self.resource_inputs.items():
            amount = input_widget.value()
            if amount > 0:
                resources[resource] = amount

        if not resources:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kaynak miktarı girin!")
            return

        # Yol durumu kontrolü
        road_condition = self.road_condition_spin.value()
        if road_condition < 1 or road_condition > 5:
            QMessageBox.warning(self, "Uyarı", "Yol durumu 1-5 arasında olmalıdır!")
            return

        # Simülasyon parametrelerini hazırla
        simulation_params = {
            'depot': self.distribution_center_combo.currentText(),
            'target_districts': self.selected_districts,
            'resources': resources,
            'road_condition': road_condition,  # Yol durumunu simülasyona aktar
            'iterations': self.iteration_spin.value(),
            'confidence_level': float(self.confidence_combo.currentText().strip('%')) / 100
        }

        # Monte Carlo simülasyonunu başlat
        logistics_calc = LogisticsCalculator()
        simulation = DisasterSimulation(logistics_calc)
        
        try:
            # Simülasyonu çalıştır
            analysis = simulation.simulate_resource_distribution(**simulation_params)
            
            # Sonuçları göster
            result_dialog = SimulationResultDialog(analysis, simulation_params, self)
            result_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Simülasyon sırasında bir hata oluştu:\n{str(e)}") 