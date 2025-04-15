from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTabWidget, QWidget, QTableWidget,
                           QTableWidgetItem, QHeaderView, QScrollArea, QGridLayout, QFrame,
                           QComboBox, QStackedWidget)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Dict, Tuple
from .result_mcts import Action
from ..sehirler_ve_ilceler import sehirler
from ..logistic_vehicle_const import RESOURCE_UNITS
import numpy as np

class MCTSResultDialog(QDialog):
    def __init__(self, actions: List[Action], total_cost: float, logistics_calculator, 
                 selected_districts: Dict[Tuple[str, str], int] = None, parent=None):
        super().__init__(parent)
        self.actions = actions
        self.total_cost = total_cost
        self.logistics_calculator = logistics_calculator
        self.selected_districts = selected_districts or {}  # Seçili tüm ilçeler
        self.road_condition = 3  # Varsayılan değer, gelecekte parametre olarak alınabilir
        self.district_data = None
        self.district_widgets = {}
        self.initUI()

    def initUI(self):
        """Dialog penceresinin arayüzünü oluştur"""
        self.setWindowTitle("Afet Lojistik Dağıtım Sonuçları")
        self.setMinimumSize(1200, 800)
        
        layout = QVBoxLayout()
        
        # Üst bilgi alanı
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"<b>Toplam Maliyet:</b> {self.total_cost:,.2f} TL"))
        info_layout.addWidget(QLabel(f"<b>Toplam Rota Sayısı:</b> {len(self.actions)}"))
        info_layout.addWidget(QLabel(f"<b>Toplam İlçe Sayısı:</b> {len(self.selected_districts)}"))
        layout.addLayout(info_layout)
        
        # Sekme widget'ı
        tab_widget = QTabWidget()
        
        # Detaylı analiz sekmesi
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout()
        
        # İlçe verilerini hazırla
        self.district_data = self.aggregate_district_data()
        
        # Seçili tüm ilçeleri ekleyerek verileri doldur
        self.ensure_all_districts_in_data()
        
        # İlçe seçim alanı
        district_selector_layout = QHBoxLayout()
        district_selector_layout.addWidget(QLabel("<b>İlçe Seçin:</b>"))
        
        self.district_combo = QComboBox()
        # Combobox'a ilçeleri ekle - tüm seçili ilçeleri
        for (city, district) in sorted(self.district_data.keys()):
            self.district_combo.addItem(f"{district} ({city})", (city, district))
        
        self.district_combo.currentIndexChanged.connect(self.on_district_changed)
        district_selector_layout.addWidget(self.district_combo)
        district_selector_layout.addStretch()
        
        analysis_layout.addLayout(district_selector_layout)
        
        # İlçe sayısı bilgisi
        district_count_label = QLabel(f"<b>Toplam {len(self.district_data)} ilçe seçildi. Kaynak dağıtımı yapılan ilçe sayısı: {self.count_districts_with_resources()}</b>")
        analysis_layout.addWidget(district_count_label)
        
        # Yatay çizgi ekle
        selector_separator = QFrame()
        selector_separator.setFrameShape(QFrame.HLine)
        selector_separator.setFrameShadow(QFrame.Sunken)
        selector_separator.setStyleSheet("background-color: #e0e0e0; min-height: 2px; margin: 5px 0px;")
        analysis_layout.addWidget(selector_separator)
        
        # İlçe içeriği için bir stacked widget
        self.district_stack = QStackedWidget()
        
        # Her ilçe için bir widget oluştur
        for (city, district), district_info in sorted(self.district_data.items()):
            district_detail = self.create_district_widget(city, district, district_info)
            self.district_widgets[(city, district)] = district_detail
            self.district_stack.addWidget(district_detail)
        
        # İlçe stack'ini scroll area içine yerleştir
        district_scroll = QScrollArea()
        district_scroll.setWidgetResizable(True)
        district_scroll.setWidget(self.district_stack)
        
        analysis_layout.addWidget(district_scroll)
        analysis_tab.setLayout(analysis_layout)
        tab_widget.addTab(analysis_tab, "İlçe Bazlı Detaylı Analiz")
        
        # Maliyet dağılımı grafiği sekmesi
        cost_tab = QWidget()
        cost_layout = QVBoxLayout()
        cost_canvas = self.create_cost_distribution()
        cost_layout.addWidget(cost_canvas)
        cost_tab.setLayout(cost_layout)
        tab_widget.addTab(cost_tab, "Maliyet Analizi")
        
        # Araç kullanım grafiği sekmesi
        vehicle_tab = QWidget()
        vehicle_layout = QVBoxLayout()
        vehicle_canvas = self.create_vehicle_usage()
        vehicle_layout.addWidget(vehicle_canvas)
        vehicle_tab.setLayout(vehicle_layout)
        tab_widget.addTab(vehicle_tab, "Araç Kullanımı")
        
        # Kaynak dağılımı sekmesi
        resource_tab = QWidget()
        resource_layout = QVBoxLayout()
        resource_canvas = self.create_resource_distribution()
        resource_layout.addWidget(resource_canvas)
        resource_tab.setLayout(resource_layout)
        tab_widget.addTab(resource_tab, "Kaynak Dağılımı")
        
        layout.addWidget(tab_widget)
        
        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignRight)
        
        self.setLayout(layout)
        
        # İlk ilçeyi göster
        if self.district_combo.count() > 0:
            self.district_combo.setCurrentIndex(0)
            
    def count_districts_with_resources(self) -> int:
        """Kaynak dağıtımı yapılan ilçe sayısını döndür"""
        count = 0
        for district_data in self.district_data.values():
            if district_data['resources']:
                count += 1
        return count
        
    def ensure_all_districts_in_data(self):
        """Seçilen tüm ilçelerin district_data'da olmasını sağla"""
        for (city, district), population in self.selected_districts.items():
            if (city, district) not in self.district_data:
                # İlçe aksiyonlarda yoksa boş bir veri yapısı oluştur
                self.district_data[(city, district)] = {
                    'resources': {},
                    'vehicles': {},
                    'total_cost': 0,
                    'total_time': 0,
                    'depots': {},
                    'actions': [],
                    'no_resources': True  # Kaynak dağıtımı yapılmadığını belirt
                }

    def on_district_changed(self, index):
        """İlçe seçimi değiştiğinde çağrılır"""
        if index >= 0:
            # ComboBox'tan seçilen şehir ve ilçe
            city, district = self.district_combo.itemData(index)
            
            # İlgili widget'ı stack'te göster
            district_widget = self.district_widgets.get((city, district))
            if district_widget:
                self.district_stack.setCurrentWidget(district_widget)

    def aggregate_district_data(self) -> Dict:
        """İlçelere göre verileri topla"""
        district_data = {}
        
        # Her aksiyondaki verileri ilgili ilçelere ekle
        for action in self.actions:
            district_key = (action.district[0], action.district[1])
            if district_key not in district_data:
                district_data[district_key] = {
                    'resources': {},
                    'vehicles': {},
                    'total_cost': 0,
                    'total_time': 0,
                    'depots': {},
                    'actions': []
                }
            
            # Kaynakları topla
            for resource, amount in action.resources.items():
                if resource not in district_data[district_key]['resources']:
                    district_data[district_key]['resources'][resource] = 0
                district_data[district_key]['resources'][resource] += amount
            
            # Araç sayısını güncelle
            if action.vehicle_type not in district_data[district_key]['vehicles']:
                district_data[district_key]['vehicles'][action.vehicle_type] = 0
            district_data[district_key]['vehicles'][action.vehicle_type] += 1
            
            # Maliyet ekle
            district_data[district_key]['total_cost'] += action.total_cost
            
            # Taşıma süresini hesapla
            min_time, max_time = self.logistics_calculator.get_transport_time(
                action.depot, 
                action.district[0],  # Şehir
                self.road_condition,  # Yol durumu - artık sabit kodlanmadı
                sum(action.resources.values())
            )
            avg_time = (min_time + max_time) / 2
            district_data[district_key]['total_time'] += avg_time
            
            # Depo bazlı dağılımı güncelle
            if action.depot not in district_data[district_key]['depots']:
                district_data[district_key]['depots'][action.depot] = {
                    'resources': {},
                    'vehicles': {},
                    'cost': 0,
                    'time': 0
                }
            
            # Depoya özgü verileri ekle
            depot_data = district_data[district_key]['depots'][action.depot]
            for resource, amount in action.resources.items():
                if resource not in depot_data['resources']:
                    depot_data['resources'][resource] = 0
                depot_data['resources'][resource] += amount
            
            if action.vehicle_type not in depot_data['vehicles']:
                depot_data['vehicles'][action.vehicle_type] = 0
            depot_data['vehicles'][action.vehicle_type] += 1
            
            depot_data['cost'] += action.total_cost
            depot_data['time'] += avg_time
            
            # Aksiyonu kaydet
            district_data[district_key]['actions'].append(action)
            
        return district_data

    def create_district_widget(self, city: str, district: str, data: Dict) -> QWidget:
        """İlçe için detaylı bilgi widget'ı oluştur"""
        district_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # İlçe başlığı ve dağıtım durumu
        header_layout = QVBoxLayout()
        district_label = QLabel(f"<h2>{district} ({city})</h2>")
        district_label.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        header_layout.addWidget(district_label)
        
        # Kaynak dağıtımı yapılmadıysa uyarı göster
        if data.get('no_resources', False):
            no_resource_label = QLabel("<h3 style='color: red;'>Bu ilçeye kaynak dağıtımı gerçekleşmedi!</h3>")
            header_layout.addWidget(no_resource_label)
        
        main_layout.addLayout(header_layout)
        
        # İlçe nüfusunu al
        population = sehirler[city][district]
        
        # Özet bilgi alanı
        summary_widget = QWidget()
        summary_layout = QGridLayout()
        
        # Toplam kaynak miktarı
        total_resources = sum(data.get('resources', {}).values())
        
        # Toplam araç sayısı
        total_vehicles = sum(data.get('vehicles', {}).values())
        
        # Özet bilgi alanını doldur
        summary_layout.addWidget(QLabel("<b>Nüfus:</b>"), 0, 0)
        summary_layout.addWidget(QLabel(f"{population:,} kişi"), 0, 1)
        
        summary_layout.addWidget(QLabel("<b>Toplam Maliyet:</b>"), 0, 2)
        summary_layout.addWidget(QLabel(f"{data.get('total_cost', 0):,.2f} TL"), 0, 3)
        
        summary_layout.addWidget(QLabel("<b>Dağıtım Süresi:</b>"), 1, 0)
        summary_layout.addWidget(QLabel(f"{data.get('total_time', 0):.1f} saat"), 1, 1)
        
        summary_layout.addWidget(QLabel("<b>Toplam Kaynak Miktarı:</b>"), 1, 2)
        summary_layout.addWidget(QLabel(f"{total_resources:,} birim"), 1, 3)
        
        summary_layout.addWidget(QLabel("<b>Kullanılan Araçlar:</b>"), 2, 0)
        summary_layout.addWidget(QLabel(f"{total_vehicles} araç"), 2, 1)
        
        summary_layout.addWidget(QLabel("<b>Kaynak Depoları:</b>"), 2, 2)
        summary_layout.addWidget(QLabel(f"{', '.join(data.get('depots', {}).keys()) or 'Yok'}"), 2, 3)
        
        summary_widget.setLayout(summary_layout)
        main_layout.addWidget(summary_widget)
        
        # Kaynak dağıtımı yapılmadıysa sadece günlük ihtiyaç tablosunu göster
        if data.get('no_resources', False):
            main_layout.addWidget(QLabel("<b>Günlük İhtiyaç Tablosu</b>"))
            needs_scroll = QScrollArea()
            needs_scroll.setWidgetResizable(True)
            needs_table = self.create_needs_table(population)
            needs_scroll.setWidget(needs_table)
            needs_scroll.setMinimumHeight(150)
            main_layout.addWidget(needs_scroll)
            
            district_widget.setLayout(main_layout)
            return district_widget
        
        # Kaynak tablosu - scrollbar ekle
        main_layout.addWidget(QLabel("<b>Kaynak Dağılımı ve Karşılama Oranları</b>"))
        resource_scroll = QScrollArea()
        resource_scroll.setWidgetResizable(True)
        resource_table = self.create_resource_table(population, data)
        resource_scroll.setWidget(resource_table)
        resource_scroll.setMinimumHeight(150)
        main_layout.addWidget(resource_scroll)
        
        # Depo bazlı dağılım tablosu - scrollbar ekle
        main_layout.addWidget(QLabel("<b>Depo Bazlı Dağılım</b>"))
        depot_scroll = QScrollArea()
        depot_scroll.setWidgetResizable(True)
        depot_table = self.create_depot_distribution_table(data)
        depot_scroll.setWidget(depot_table)
        depot_scroll.setMinimumHeight(120)
        main_layout.addWidget(depot_scroll)
        
        # Araç dağılım tablosu - scrollbar ekle
        main_layout.addWidget(QLabel("<b>Araç Kullanımı</b>"))
        vehicle_scroll = QScrollArea()
        vehicle_scroll.setWidgetResizable(True)
        vehicle_table = self.create_vehicle_table(data)
        vehicle_scroll.setWidget(vehicle_table)
        vehicle_scroll.setMinimumHeight(120)
        main_layout.addWidget(vehicle_scroll)
        
        district_widget.setLayout(main_layout)
        return district_widget
        
    def create_resource_table(self, population: int, data: Dict) -> QTableWidget:
        """Kaynak tablosu oluştur"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Kaynak Türü",
            "Birim",
            "Gönderilen Miktar",
            "Günlük İhtiyaç",
            "Karşılama Oranı (%)",
            "Kişi Başı Miktar",
            "Kullanılan Araçlar",
            "Maliyet Payı (%)"
        ])
        
        # Günlük ihtiyaçları hesapla
        daily_needs = self.logistics_calculator.calculate_daily_needs(population)
        
        # Toplam maliyet
        total_cost = data['total_cost']
        
        # Tablo satırlarını doldur
        table.setRowCount(len(data['resources']))
        for i, (resource, amount) in enumerate(data['resources'].items()):
            # Kaynak türü
            table.setItem(i, 0, QTableWidgetItem(resource))
            
            # Birim
            unit = RESOURCE_UNITS.get(resource, "-")
            table.setItem(i, 1, QTableWidgetItem(unit))
            
            # Gönderilen miktar
            table.setItem(i, 2, QTableWidgetItem(f"{amount:,}"))
            
            # Günlük ihtiyaç
            daily_need = daily_needs.get(resource, 0)
            table.setItem(i, 3, QTableWidgetItem(f"{daily_need:,}"))
            
            # Karşılama oranı
            if daily_need > 0:
                coverage = (amount / daily_need) * 100
                coverage_item = QTableWidgetItem(f"{coverage:.1f}%")
                # Renklendirme ekle
                if coverage < 50:
                    coverage_item.setBackground(Qt.red)
                elif coverage < 80:
                    coverage_item.setBackground(Qt.yellow)
                else:
                    coverage_item.setBackground(Qt.green)
                table.setItem(i, 4, coverage_item)
            else:
                table.setItem(i, 4, QTableWidgetItem("N/A"))
            
            # Kişi başı miktar
            per_person = amount / population if population > 0 else 0
            table.setItem(i, 5, QTableWidgetItem(f"{per_person:.2f}"))
            
            # Kullanılan araçlar
            vehicle_text = ", ".join(f"{count} {vehicle}" 
                                   for vehicle, count in data['vehicles'].items())
            table.setItem(i, 6, QTableWidgetItem(vehicle_text))
            
            # Maliyet payı - tahmini değer, gerçek maliyet dağılımı daha karmaşık olabilir
            cost_ratio = (amount / sum(data['resources'].values())) * 100 if sum(data['resources'].values()) > 0 else 0
            table.setItem(i, 7, QTableWidgetItem(f"{cost_ratio:.1f}%"))
        
        # Tablo stilini ayarla
        header = table.horizontalHeader()
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        return table
    
    def create_depot_distribution_table(self, data: Dict) -> QTableWidget:
        """Depo bazlı dağılım tablosu oluştur"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Depo Adı",
            "Gönderilen Kaynaklar",
            "Kullanılan Araçlar",
            "Maliyet",
            "Teslim Süresi"
        ])
        
        # Tablo satırlarını doldur
        table.setRowCount(len(data['depots']))
        for i, (depot, depot_data) in enumerate(data['depots'].items()):
            # Depo adı
            table.setItem(i, 0, QTableWidgetItem(depot))
            
            # Gönderilen kaynaklar
            resources_text = ", ".join(f"{amount:,} {resource}" 
                                     for resource, amount in depot_data['resources'].items())
            table.setItem(i, 1, QTableWidgetItem(resources_text))
            
            # Kullanılan araçlar
            vehicles_text = ", ".join(f"{count} {vehicle}" 
                                    for vehicle, count in depot_data['vehicles'].items())
            table.setItem(i, 2, QTableWidgetItem(vehicles_text))
            
            # Maliyet
            cost_pct = (depot_data['cost'] / data['total_cost']) * 100 if data['total_cost'] > 0 else 0
            table.setItem(i, 3, QTableWidgetItem(f"{depot_data['cost']:,.2f} TL ({cost_pct:.1f}%)"))
            
            # Teslim süresi
            table.setItem(i, 4, QTableWidgetItem(f"{depot_data['time']:.1f} saat"))
        
        # Tablo stilini ayarla
        header = table.horizontalHeader()
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        return table
    
    def create_vehicle_table(self, data: Dict) -> QTableWidget:
        """Araç kullanım tablosu oluştur"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Araç Tipi",
            "Kullanım Sayısı",
            "Taşınan Toplam Kaynak",
            "Maliyet Payı (%)"
        ])
        
        # Araç başına taşınan kaynak miktarını hesapla
        vehicle_resources = {}
        for action in data['actions']:
            if action.vehicle_type not in vehicle_resources:
                vehicle_resources[action.vehicle_type] = 0
            vehicle_resources[action.vehicle_type] += sum(action.resources.values())
        
        # Tablo satırlarını doldur
        table.setRowCount(len(data['vehicles']))
        for i, (vehicle, count) in enumerate(data['vehicles'].items()):
            # Araç tipi
            table.setItem(i, 0, QTableWidgetItem(vehicle))
            
            # Kullanım sayısı
            table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            # Taşınan toplam kaynak
            vehicle_resource = vehicle_resources.get(vehicle, 0)
            table.setItem(i, 2, QTableWidgetItem(f"{vehicle_resource:,}"))
            
            # Maliyet payı - tahmini değer
            cost_ratio = (count / sum(data['vehicles'].values())) * 100 if sum(data['vehicles'].values()) > 0 else 0
            table.setItem(i, 3, QTableWidgetItem(f"{cost_ratio:.1f}%"))
        
        # Tablo stilini ayarla
        header = table.horizontalHeader()
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        return table

    def create_cost_distribution(self) -> FigureCanvas:
        """Maliyet dağılımı grafiğini oluştur"""
        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Depo bazında maliyetleri hesapla
        depot_costs = {}
        for action in self.actions:
            if action.depot not in depot_costs:
                depot_costs[action.depot] = 0
            depot_costs[action.depot] += action.total_cost
        
        depots = list(depot_costs.keys())
        costs = list(depot_costs.values())
        
        bars = ax.bar(depots, costs, color='#3498db')
        
        # Barların üzerine değerleri yaz
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f} TL',
                   ha='center', va='bottom')
        
        ax.set_title("Depo Bazında Maliyet Dağılımı", pad=20)
        ax.set_xlabel("Depolar")
        ax.set_ylabel("Maliyet (TL)")
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()
        
        return canvas

    def create_vehicle_usage(self) -> FigureCanvas:
        """Araç kullanım grafiğini oluştur"""
        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Araç tipine göre kullanım sayısını hesapla
        vehicle_usage = {}
        for action in self.actions:
            if action.vehicle_type not in vehicle_usage:
                vehicle_usage[action.vehicle_type] = 0
            vehicle_usage[action.vehicle_type] += 1
        
        vehicles = list(vehicle_usage.keys())
        counts = list(vehicle_usage.values())
        
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        wedges, texts, autotexts = ax.pie(counts, labels=vehicles, autopct='%1.1f%%',
                                         colors=colors, textprops={'fontsize': 10})
        
        ax.set_title("Araç Tipi Kullanım Dağılımı", pad=20)
        fig.tight_layout()
        
        return canvas

    def create_resource_distribution(self) -> FigureCanvas:
        """Kaynak dağılımı grafiğini oluştur"""
        fig = Figure(figsize=(12, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Bölge bazında kaynak dağılımını hesapla
        resource_dist = {}
        for action in self.actions:
            district_name = f"{action.district[1]}\n({action.district[0]})"
            if district_name not in resource_dist:
                resource_dist[district_name] = {res: 0 for res in action.resources.keys()}
            for res, amount in action.resources.items():
                resource_dist[district_name][res] += amount
        
        districts = list(resource_dist.keys())
        resources = list(resource_dist[districts[0]].keys()) if districts else []
        
        if districts and resources:
            x = np.arange(len(districts))
            width = 0.8 / len(resources)
            
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#34495e']
            for i, resource in enumerate(resources):
                amounts = [resource_dist[d][resource] for d in districts]
                ax.bar(x + i * width, amounts, width, label=resource, color=colors[i % len(colors)])
            
            ax.set_title("Bölgelere Göre Kaynak Dağılımı", pad=20)
            ax.set_xlabel("Bölgeler")
            ax.set_ylabel("Miktar")
            ax.set_xticks(x + width * (len(resources) - 1) / 2)
            ax.set_xticklabels(districts, rotation=45, ha='right')
            ax.legend()
        else:
            ax.text(0.5, 0.5, "Dağıtım verisi bulunamadı", ha='center', va='center')
        
        fig.tight_layout()
        return canvas

    def create_needs_table(self, population: int) -> QTableWidget:
        """İlçe için günlük ihtiyaç tablosu oluştur"""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels([
            "Kaynak Türü",
            "Birim",
            "Günlük İhtiyaç"
        ])
        
        # Günlük ihtiyaçları hesapla
        daily_needs = self.logistics_calculator.calculate_daily_needs(population)
        
        # Tablo satırlarını doldur
        table.setRowCount(len(daily_needs))
        for i, (resource, amount) in enumerate(daily_needs.items()):
            # Kaynak türü
            table.setItem(i, 0, QTableWidgetItem(resource))
            
            # Birim
            unit = RESOURCE_UNITS.get(resource, "-")
            table.setItem(i, 1, QTableWidgetItem(unit))
            
            # Günlük ihtiyaç
            table.setItem(i, 2, QTableWidgetItem(f"{amount:,}"))
        
        # Tablo stilini ayarla
        header = table.horizontalHeader()
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        return table 