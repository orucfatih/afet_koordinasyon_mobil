"""
daha gerçekçi bir simülasyon için lojistik kaynak depolarının her birinin 81 ile olan uzaklıkları girilmeli
yine her bir ilçenin maksimum kapasitesi girilmeli
ulaşım-trafik veya zaman kısıtları girilmeli
havaalanlarının kapasitesi ve havaalanlarının durumu girilmeli
"""



from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QComboBox, QListWidget, 
                           QGroupBox, QSpinBox, QMessageBox, QListWidgetItem,
                           QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from styles_dark import *
from utils import get_icon_path # sonraki versiyonlarda istenirse
from .sehirler_ve_ilceler import sehirler

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

        # İlçe arama ve liste
        district_search_layout = QHBoxLayout()
        self.district_search = QLineEdit()
        self.district_search.setPlaceholderText("İlçe ara...")
        self.district_search.setStyleSheet(RESOURCE_INPUT_STYLE)
        self.district_search.textChanged.connect(self.filter_districts)
        district_search_layout.addWidget(self.district_search)
        city_layout.addLayout(district_search_layout)

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

        # Dağıtım Merkezi Seçimi
        distribution_layout = QHBoxLayout()
        self.distribution_center_combo = QComboBox()
        self.distribution_center_combo.addItems(sorted(DISTRIBUTION_CENTERS))
        self.distribution_center_combo.setStyleSheet(COMBO_BOX_STYLE)
        distribution_layout.addWidget(QLabel("Dağıtım Merkezi:"))
        distribution_layout.addWidget(self.distribution_center_combo)
        params_layout.addLayout(distribution_layout)

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

    def filter_districts(self, text):
        """İlçeleri filtrele"""
        for i in range(self.district_list.count()):
            item = self.district_list.item(i)
            district_name = item.text().split(" (")[0]  # İlçe adını nüfustan ayır
            item.setHidden(text.lower() not in district_name.lower())

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

    def run_simulation(self):
        """Simülasyonu başlatır"""
        if not self.selected_districts:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir ilçe seçin!")
            return

        # Kaynak miktarlarını kontrol et
        resources_str = "\n".join(
            f"- {resource}: {self.resource_inputs[resource].value():,} {unit}"
            for resource, unit in RESOURCES.items()
            if self.resource_inputs[resource].value() > 0
        )

        if not resources_str:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kaynak miktarı girin!")
            return

        total_population = sum(self.selected_districts.values())
        selected_districts_str = "\n".join(
            f"- {district}: {population:,} kişi" 
            for district, population in self.selected_districts.items()
        )
        
        QMessageBox.information(
            self,
            "Simülasyon Başlatıldı",
            f"Seçilen İlçeler:\n{selected_districts_str}\n\n"
            f"Toplam Nüfus: {total_population:,} kişi\n"
            f"Dağıtım Merkezi: {self.distribution_center_combo.currentText()}\n\n"
            f"Kaynak Miktarları:\n{resources_str}\n\n"
            f"İterasyon sayısı: {self.iteration_spin.value()}\n"
            f"Güven aralığı: {self.confidence_combo.currentText()}"
        ) 