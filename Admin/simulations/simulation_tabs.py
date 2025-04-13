from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .resource_distribution_tab import ResourceDistributionTab
from .disaster_impact_tab import DisasterImpactTab

class SimulationTab(QWidget):
    """Ana Simülasyon Sekmesi - İki farklı simülasyon sekmesini (Kaynak Dağıtım ve Afet Etki) birleştirir"""
    def __init__(self):
        super().__init__()
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
        resource_tab = ResourceDistributionTab()
        tabs.addTab(resource_tab, "Kaynak Dağıtım Simülasyonu")
        
        # Afet Etki Simülasyonu sekmesi
        impact_tab = DisasterImpactTab()
        tabs.addTab(impact_tab, "Afet Etki Simülasyonu")
        
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)