"""
şehir yoğunluklarını kullanıcının girmesine gerek yok bunun verisi araştırılmalı eklenmeli
    afet şiddeti farklı olmalı şimdilik arayüz ön testi
    ortalama bina yaşı daha mantıklı olabilir
    burası için istatistik formülü araştırılmalı
    deprem merkezi seçimi yapılabilir
    hangi bölgelerin ne oranda etkileneceği sorulabilir
    türkiyedeki aktif fay hatları verisine araştırılmalı ona göre bölgelere ayrılabilir

"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QSpinBox,
                           QFormLayout, QGroupBox, QTextEdit,
                           QProgressBar, QMessageBox, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .sehirler_ve_ilceler import sehirler, bolgelere_gore_iller
from .base_components import BaseSimulationTab

class DisasterImpactTab(BaseSimulationTab):
    """Afet Etki Simülasyonu Sekmesi"""
    def __init__(self, parent=None):
        self.disaster_type = None
        self.intensity = None
        self.population_density = None
        self.building_quality = None
        self.iterations = None
        super().__init__(parent)

    def initUI(self):
        """Ana arayüzü oluştur"""
        layout = QVBoxLayout()
        
        # Üst kısım - Şehir seçimi ve toplam nüfus
        layout.addLayout(self.create_city_selection_ui())
        
        # Afet parametreleri grubu
        layout.addWidget(self.create_disaster_parameters_ui())
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Simülasyon başlatma butonu
        start_btn = QPushButton("Afeti Simüle Et")
        start_btn.clicked.connect(self.run_simulation)
        layout.addWidget(start_btn)
        
        self.setLayout(layout)

    def create_disaster_parameters_ui(self):
        """Afet parametreleri arayüzünü oluştur"""
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
        self.intensity.setToolTip("1: En düşük şiddet, 10: En yüksek şiddet")
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
        self.iterations = QSpinBox()
        self.iterations.setRange(100, 10000)
        self.iterations.setValue(1000)
        self.iterations.setSingleStep(100)
        params_layout.addRow("Simülasyon İterasyonu:", self.iterations)
        
        params_group.setLayout(params_layout)
        return params_group

    def run_simulation(self):
        """Afet etki simülasyonunu başlat"""
        if not self.city_tree_manager.get_selected_districts():
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir bölge seçin!")
            return
        
        # Simülasyon parametrelerini al
        disaster_type = self.disaster_type.currentText()
        intensity = self.intensity.value()
        population_density = self.population_density.value()
        building_quality = self.building_quality.value()
        iterations = self.iterations.value()
        
        # İlerleme çubuğunu göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            # TODO: Monte Carlo simülasyonunu burada implement et
            QMessageBox.information(self, "Bilgi", "Monte Carlo simülasyonu henüz implement edilmedi.")
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Simülasyon çalıştırılırken hata oluştu: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False) 