from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QGroupBox, QTextEdit, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .sehirler_ve_ilceler import sehirler, bolgelere_gore_iller

class CityTreeManager:
    """Şehir ağacı yönetimi için yardımcı sınıf"""
    def __init__(self, tree_widget, selected_areas_text, total_population_label):
        self.city_tree = tree_widget
        self.selected_areas_text = selected_areas_text
        self.total_population_label = total_population_label
        self.selected_districts = {}
        self.total_population = 0
        
        # Ağacı doldur ve sinyali bağla
        self.populate_city_tree()
        self.city_tree.itemChanged.connect(self.on_district_selection_changed)
    
    def populate_city_tree(self):
        """Şehir ağacını bölgelere göre doldur"""
        self.city_tree.clear()
        
        for bolge, bolge_sehirleri in bolgelere_gore_iller.items():
            bolge_item = QTreeWidgetItem(self.city_tree)
            bolge_item.setText(0, bolge)
            bolge_item.setFlags(bolge_item.flags() | Qt.ItemIsUserCheckable)
            bolge_item.setCheckState(0, Qt.Unchecked)
            
            for sehir in sorted(bolge_sehirleri):
                if sehir in sehirler:
                    sehir_item = QTreeWidgetItem(bolge_item)
                    sehir_item.setText(0, sehir)
                    sehir_item.setFlags(sehir_item.flags() | Qt.ItemIsUserCheckable)
                    sehir_item.setCheckState(0, Qt.Unchecked)
                    
                    for ilce, nufus in sorted(sehirler[sehir].items()):
                        ilce_item = QTreeWidgetItem(sehir_item)
                        ilce_item.setText(0, f"{ilce} ({nufus:,} kişi)")
                        ilce_item.setFlags(ilce_item.flags() | Qt.ItemIsUserCheckable)
                        ilce_item.setCheckState(0, Qt.Unchecked)
                        ilce_item.setData(0, Qt.UserRole, nufus)
    
    def on_district_selection_changed(self, item, column):
        """Bölge, şehir veya ilçe seçimi değiştiğinde"""
        self.city_tree.blockSignals(True)
        
        if item.parent() is None:  # Bölge seçimi
            self._handle_region_selection(item)
        elif item.parent().parent() is None:  # Şehir seçimi
            self._handle_city_selection(item)
        else:  # İlçe seçimi
            self._handle_district_selection(item)
        
        self.city_tree.blockSignals(False)
        self.update_selected_areas()
    
    def _handle_region_selection(self, item):
        """Bölge seçimini işle"""
        check_state = item.checkState(0)
        for i in range(item.childCount()):
            sehir_item = item.child(i)
            sehir_item.setCheckState(0, check_state)
            for j in range(sehir_item.childCount()):
                ilce_item = sehir_item.child(j)
                ilce_item.setCheckState(0, check_state)
    
    def _handle_city_selection(self, item):
        """Şehir seçimini işle"""
        check_state = item.checkState(0)
        # İlçeleri güncelle
        for i in range(item.childCount()):
            ilce_item = item.child(i)
            ilce_item.setCheckState(0, check_state)
        
        # Bölge durumunu güncelle
        self._update_parent_state(item.parent())
    
    def _handle_district_selection(self, item):
        """İlçe seçimini işle"""
        sehir_item = item.parent()
        self._update_parent_state(sehir_item)
        self._update_parent_state(sehir_item.parent())
    
    def _update_parent_state(self, parent_item):
        """Üst öğenin durumunu alt öğelere göre güncelle"""
        all_checked = True
        for i in range(parent_item.childCount()):
            if parent_item.child(i).checkState(0) != Qt.Checked:
                all_checked = False
                break
        parent_item.setCheckState(0, Qt.Checked if all_checked else Qt.Unchecked)
    
    def update_selected_areas(self):
        """Seçili bölgeleri ve toplam nüfusu güncelle"""
        self.selected_districts.clear()
        self.total_population = 0
        text = ""
        
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
    
    def get_selected_districts(self):
        """Seçili ilçeleri döndür"""
        return self.selected_districts
    
    def get_total_population(self):
        """Toplam nüfusu döndür"""
        return self.total_population

class BaseSimulationTab(QWidget):
    """Simülasyon sekmeleri için temel sınıf"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.city_tree = None
        self.selected_areas_text = None
        self.total_population_label = None
        self.progress_bar = None
        self.city_tree_manager = None
        
        # Alt sınıflar bu metodu override etmeli
        self.initUI()
    
    def create_city_selection_ui(self):
        """Şehir seçimi arayüzünü oluştur"""
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
        
        # Şehir ağacı yöneticisini oluştur
        self.city_tree_manager = CityTreeManager(
            self.city_tree,
            self.selected_areas_text,
            self.total_population_label
        )
        
        return top_layout 