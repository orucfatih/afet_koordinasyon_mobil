from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QGroupBox,
                           QScrollArea, QWidget, QTabWidget, QFileDialog,
                           QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import numpy as np
import json
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from styles.styles_dark import *
from styles.styles_light import *

class SimulationResultDialog(QDialog):
    def __init__(self, analysis_results, simulation_params, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simülasyon Sonuçları")
        self.analysis = analysis_results
        self.params = simulation_params
        self.setup_ui()
        self.resize(1200, 800)

    def _calculate_resource_need(self, resource_type: str, population: int) -> float:
        """Nüfusa göre günlük kaynak ihtiyacını hesapla"""
        daily_needs = {
            "Su": 3.0,  # Litre/kişi/gün
            "Gıda": 2.0,  # Kg/kişi/gün
            "İlaç": 0.1,  # Kutu/kişi/gün
            "Çadır": 0.2,  # Adet/kişi (5 kişilik çadır)
            "Battaniye": 2.0,  # Adet/kişi
            "Diğer": 1.0  # Adet/kişi
        }
        return population * daily_needs.get(resource_type, 1.0)

    def _plot_coverage_chart(self, fig):
        """Karşılama oranları grafiğini çiz"""
        ax = fig.add_subplot(111)
        
        districts = list(self.analysis['district_analysis'].keys())
        coverage_values = []
        std_devs = []
        
        for district in districts:
            values = self.analysis['district_analysis'][district]['coverage']['values']
            coverage_values.append(np.mean(values) * 100)
            std_devs.append(np.std(values) * 100)
        
        bars = ax.bar(districts, coverage_values, yerr=std_devs, capsize=5)
        ax.set_title('İlçe Bazlı Kaynak Karşılama Oranları')
        ax.set_ylabel('Karşılama Oranı (%)')
        ax.set_xticklabels(districts, rotation=45, ha='right')
        
        for bar, std in zip(bars, std_devs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'%{height:.1f}\n(±%{std:.1f})',
                   ha='center', va='bottom')
        
        fig.tight_layout()

    def _plot_delivery_chart(self, fig):
        """Teslimat süreleri grafiğini çiz"""
        ax = fig.add_subplot(111)
        
        districts = list(self.analysis['district_analysis'].keys())
        delivery_values = []
        std_devs = []
        
        for district in districts:
            values = self.analysis['district_analysis'][district]['delivery_time']['values']
            delivery_values.append(np.mean(values))
            std_devs.append(np.std(values))
        
        bars = ax.bar(districts, delivery_values, yerr=std_devs, capsize=5)
        ax.set_title('İlçe Bazlı Ortalama Teslimat Süreleri')
        ax.set_ylabel('Süre (Saat)')
        ax.set_xticklabels(districts, rotation=45, ha='right')
        
        for bar, std in zip(bars, std_devs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}s\n(±{std:.1f}s)',
                   ha='center', va='bottom')
        
        fig.tight_layout()

    def _plot_risk_chart(self, fig):
        """Risk faktörleri grafiğini çiz"""
        ax = fig.add_subplot(111)
        
        districts = list(self.analysis['district_analysis'].keys())
        time_risks = [data['risk_factors']['time_risk'] * 100 for data in self.analysis['district_analysis'].values()]
        coverage_risks = [data['risk_factors']['coverage_risk'] * 100 for data in self.analysis['district_analysis'].values()]
        road_risks = [data['risk_factors']['road_risk'] * 100 for data in self.analysis['district_analysis'].values()]
        
        x = np.arange(len(districts))
        width = 0.25
        
        ax.bar(x - width, time_risks, width, label='Teslimat Süresi Riski')
        ax.bar(x, coverage_risks, width, label='Kaynak Karşılama Riski')
        ax.bar(x + width, road_risks, width, label='Yol Durumu Riski')
        
        ax.set_title('İlçe Bazlı Risk Faktörleri')
        ax.set_ylabel('Risk Oranı (%)')
        ax.set_xticks(x)
        ax.set_xticklabels(districts, rotation=45, ha='right')
        ax.legend()
        
        fig.tight_layout()

    def _get_risk_color(self, risk_value: float):
        """Risk değerine göre renk döndür"""
        if risk_value <= 25:
            return QColor("#c8e6c9")  # Yeşil - Düşük risk
        elif risk_value <= 50:
            return QColor("#fff3c4")  # Sarı - Orta risk
        elif risk_value <= 75:
            return QColor("#ffccbc")  # Turuncu - Yüksek risk
        else:
            return QColor("#ffcdd2")  # Kırmızı - Kritik risk 

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Sekme widget'ı oluştur
        tabs = QTabWidget()
        
        # Kaynak Dağıtımı Sekmesi
        distribution_tab = QWidget()
        distribution_layout = QVBoxLayout()
        
        # Özet bilgiler
        summary_group = QGroupBox("Dağıtım Özeti")
        summary_layout = QGridLayout()
        
        total_population = sum(self.params['target_districts'].values())
        summary_layout.addWidget(QLabel("Toplam Nüfus:"), 0, 0)
        summary_layout.addWidget(QLabel(f"{total_population:,} kişi"), 0, 1)
        
        summary_layout.addWidget(QLabel("Dağıtım Merkezi:"), 1, 0)
        summary_layout.addWidget(QLabel(self.params['depot']), 1, 1)
        
        # Yol durumu gösterimini daha detaylı hale getir
        road_condition = self.params['road_condition']
        road_status = {
            1: "Çok Kötü (Ağır hasarlı, çok sayıda engel)",
            2: "Kötü (Hasarlı, bazı engeller mevcut)",
            3: "Orta (Kullanılabilir, dikkatli seyir gerekli)",
            4: "İyi (Küçük sorunlar mevcut)",
            5: "Çok İyi (Sorunsuz)"
        }
        summary_layout.addWidget(QLabel("Yol Durumu:"), 2, 0)
        summary_layout.addWidget(QLabel(f"{road_condition}/5 - {road_status[road_condition]}"), 2, 1)
        
        # Yol durumuna göre ortalama hız bilgisi
        avg_speed = {
            1: "30-40",
            2: "40-50",
            3: "50-60",
            4: "60-70",
            5: "70-80"
        }
        summary_layout.addWidget(QLabel("Tahmini Ortalama Hız:"), 3, 0)
        summary_layout.addWidget(QLabel(f"{avg_speed[road_condition]} km/saat"), 3, 1)
        
        # Tır analizi bilgileri
        truck_analysis = self.analysis['truck_analysis']['total_trucks']
        summary_layout.addWidget(QLabel("Toplam Gereken Tır Sayısı:"), 4, 0)
        summary_layout.addWidget(QLabel(
            f"Ortalama: {truck_analysis['mean']:.1f} tır\n"
            f"Minimum: {truck_analysis['min']:.1f} tır\n"
            f"Maksimum: {truck_analysis['max']:.1f} tır"
        ), 4, 1)
        
        summary_group.setLayout(summary_layout)
        distribution_layout.addWidget(summary_group)
        
        # İlçe bazlı dağıtım tablosu
        table_group = QGroupBox("İlçe Bazlı Kaynak Dağıtımı")
        table_layout = QVBoxLayout()
        
        district_table = QTableWidget()
        headers = ["İlçe", "Nüfus"]
        for resource in self.params['resources'].keys():
            headers.extend([f"{resource} (İhtiyaç)", f"{resource} (Dağıtılan)", "Karşılama Oranı"])
        district_table.setColumnCount(len(headers))
        district_table.setHorizontalHeaderLabels(headers)
        
        # İlçe verilerini tabloya ekle
        district_table.setRowCount(len(self.analysis['district_analysis']))
        for row, (district, data) in enumerate(self.analysis['district_analysis'].items()):
            col = 0
            # İlçe adı
            district_table.setItem(row, col, QTableWidgetItem(district))
            col += 1
            
            # Nüfus
            population = self.params['target_districts'][district]
            district_table.setItem(row, col, QTableWidgetItem(f"{population:,}"))
            col += 1
            
            # Her kaynak türü için veriler
            for resource, total_amount in self.params['resources'].items():
                # İhtiyaç
                daily_need = self._calculate_resource_need(resource, population)
                district_table.setItem(row, col, QTableWidgetItem(f"{daily_need:,.1f}"))
                col += 1
                
                # Dağıtılan miktar (ortalama)
                allocated = data['allocated_resources'][resource]['mean']
                district_table.setItem(row, col, QTableWidgetItem(f"{allocated:,.1f}"))
                col += 1
                
                # Karşılama oranı
                coverage = min(100, (allocated / daily_need) * 100)
                district_table.setItem(row, col, QTableWidgetItem(f"%{coverage:.1f}"))
                col += 1
        
        district_table.resizeColumnsToContents()
        table_layout.addWidget(district_table)
        table_group.setLayout(table_layout)
        distribution_layout.addWidget(table_group)
        
        # Grafik gösterimi
        charts_group = QGroupBox("Dağıtım Grafikleri")
        charts_layout = QHBoxLayout()
        
        # Karşılama oranları grafiği
        coverage_fig = Figure(figsize=(6, 4))
        coverage_canvas = FigureCanvas(coverage_fig)
        self._plot_coverage_chart(coverage_fig)
        charts_layout.addWidget(coverage_canvas)
        
        # Teslimat süreleri grafiği
        delivery_fig = Figure(figsize=(6, 4))
        delivery_canvas = FigureCanvas(delivery_fig)
        self._plot_delivery_chart(delivery_fig)
        charts_layout.addWidget(delivery_canvas)
        
        charts_group.setLayout(charts_layout)
        distribution_layout.addWidget(charts_group)
        
        distribution_tab.setLayout(distribution_layout)
        tabs.addTab(distribution_tab, "Kaynak Dağıtımı")
        
        # Risk Analizi Sekmesi
        risk_tab = QWidget()
        risk_layout = QVBoxLayout()
        
        # Risk faktörleri tablosu
        risk_table_group = QGroupBox("İlçe Bazlı Risk Analizi")
        risk_table_layout = QVBoxLayout()
        
        risk_table = QTableWidget()
        risk_table.setColumnCount(5)
        risk_table.setHorizontalHeaderLabels([
            "İlçe",
            "Teslimat Süresi Riski",
            "Kaynak Karşılama Riski",
            "Yol Durumu Riski",
            "Toplam Risk"
        ])
        
        risk_table.setRowCount(len(self.analysis['district_analysis']))
        for row, (district, data) in enumerate(self.analysis['district_analysis'].items()):
            risk_table.setItem(row, 0, QTableWidgetItem(district))
            risks = data['risk_factors']
            
            # Teslimat süresi riski
            time_risk = risks['time_risk'] * 100
            risk_table.setItem(row, 1, QTableWidgetItem(f"%{time_risk:.1f}"))
            
            # Kaynak karşılama riski
            coverage_risk = risks['coverage_risk'] * 100
            risk_table.setItem(row, 2, QTableWidgetItem(f"%{coverage_risk:.1f}"))
            
            # Yol durumu riski
            road_risk = risks['road_risk'] * 100
            risk_table.setItem(row, 3, QTableWidgetItem(f"%{road_risk:.1f}"))
            
            # Toplam risk
            total_risk = data['total_risk'] * 100
            risk_table.setItem(row, 4, QTableWidgetItem(f"%{total_risk:.1f}"))
        
        risk_table.resizeColumnsToContents()
        risk_table_layout.addWidget(risk_table)
        risk_table_group.setLayout(risk_table_layout)
        risk_layout.addWidget(risk_table_group)
        
        # Risk grafiği
        risk_chart_group = QGroupBox("Risk Faktörleri Grafiği")
        risk_chart_layout = QVBoxLayout()
        
        risk_fig = Figure(figsize=(12, 4))
        risk_canvas = FigureCanvas(risk_fig)
        self._plot_risk_chart(risk_fig)
        risk_chart_layout.addWidget(risk_canvas)
        
        risk_chart_group.setLayout(risk_chart_layout)
        risk_layout.addWidget(risk_chart_group)
        
        risk_tab.setLayout(risk_layout)
        tabs.addTab(risk_tab, "Risk Analizi")
        
        layout.addWidget(tabs)
        
        # Kaydet butonu ekle
        save_layout = QHBoxLayout()
        
        save_pdf_btn = QPushButton("PDF Olarak Kaydet")
        save_pdf_btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        save_pdf_btn.clicked.connect(self.save_as_pdf)
        
        save_txt_btn = QPushButton("TXT Olarak Kaydet")
        save_txt_btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        save_txt_btn.clicked.connect(self.save_as_txt)
        
        save_json_btn = QPushButton("JSON Olarak Kaydet")
        save_json_btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        save_json_btn.clicked.connect(self.save_as_json)
        
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet(RESOURCE_ADD_BUTTON_STYLE)
        close_btn.clicked.connect(self.accept)
        
        save_layout.addWidget(save_pdf_btn)
        save_layout.addWidget(save_txt_btn)
        save_layout.addWidget(save_json_btn)
        save_layout.addWidget(close_btn)
        
        layout.addLayout(save_layout)
        
        self.setLayout(layout) 

    def save_as_pdf(self):
        """Sonuçları PDF olarak kaydet"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "PDF Kaydet", 
            f"afet_simulasyon_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Dosyaları (*.pdf)"
        )
        
        if file_path:
            try:
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Başlık
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30
                )
                story.append(Paragraph("Afet Simülasyonu Raporu", title_style))
                story.append(Spacer(1, 12))
                
                # Genel Bilgiler
                story.append(Paragraph("Genel Bilgiler", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                general_info = [
                    ["Parametre", "Değer"],
                    ["Dağıtım Merkezi", self.params['depot']],
                    ["Toplam Nüfus", f"{sum(self.params['target_districts'].values()):,} kişi"],
                    ["Yol Durumu", f"{self.params['road_condition']}/5"],
                    ["İterasyon Sayısı", str(self.params['iterations'])],
                    ["Güven Aralığı", f"%{self.params['confidence_level']*100:.0f}"]
                ]
                
                t = Table(general_info)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 20))
                
                # Tır Analizi
                story.append(Paragraph("TIR ANALİZİ", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                truck_data = [["İlçe", "Ortalama Tır", "Minimum", "Maksimum"]]
                for district, data in self.analysis['truck_analysis']['by_district'].items():
                    truck_data.append([
                        district,
                        f"{data['mean']:.1f}",
                        f"{data['min']:.1f}",
                        f"{data['max']:.1f}"
                    ])
                
                t = Table(truck_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 20))
                
                # Risk Analizi
                story.append(Paragraph("RİSK ANALİZİ", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                risk_data = [["İlçe", "Teslimat Riski", "Karşılama Riski", "Yol Riski", "Toplam Risk"]]
                for district, data in self.analysis['district_analysis'].items():
                    risks = data['risk_factors']
                    risk_data.append([
                        district,
                        f"%{risks['time_risk']*100:.1f}",
                        f"%{risks['coverage_risk']*100:.1f}",
                        f"%{risks['road_risk']*100:.1f}",
                        f"%{data['total_risk']*100:.1f}"
                    ])
                
                t = Table(risk_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(t)
                
                doc.build(story)
                QMessageBox.information(self, "Başarılı", "PDF raporu başarıyla kaydedildi.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF kaydedilirken bir hata oluştu:\n{str(e)}")

    def save_as_txt(self):
        """Sonuçları TXT olarak kaydet"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "TXT Kaydet", 
            f"afet_simulasyon_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Metin Dosyaları (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("AFET SİMÜLASYONU RAPORU\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Genel Bilgiler
                    f.write("GENEL BİLGİLER\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Dağıtım Merkezi: {self.params['depot']}\n")
                    f.write(f"Toplam Nüfus: {sum(self.params['target_districts'].values()):,} kişi\n")
                    f.write(f"Yol Durumu: {self.params['road_condition']}/5\n")
                    f.write(f"İterasyon Sayısı: {self.params['iterations']}\n")
                    f.write(f"Güven Aralığı: %{self.params['confidence_level']*100:.0f}\n\n")
                    
                    # Tır Analizi
                    f.write("TIR ANALİZİ\n")
                    f.write("-" * 20 + "\n")
                    f.write("İlçe Bazlı Tır Gereksinimleri:\n")
                    for district, data in self.analysis['truck_analysis']['by_district'].items():
                        f.write(f"{district}:\n")
                        f.write(f"  Ortalama: {data['mean']:.1f} tır\n")
                        f.write(f"  Minimum: {data['min']:.1f} tır\n")
                        f.write(f"  Maksimum: {data['max']:.1f} tır\n")
                    f.write("\n")
                    
                    # Risk Analizi
                    f.write("RİSK ANALİZİ\n")
                    f.write("-" * 20 + "\n")
                    for district, data in self.analysis['district_analysis'].items():
                        f.write(f"{district}:\n")
                        risks = data['risk_factors']
                        f.write(f"  Teslimat Riski: %{risks['time_risk']*100:.1f}\n")
                        f.write(f"  Karşılama Riski: %{risks['coverage_risk']*100:.1f}\n")
                        f.write(f"  Yol Riski: %{risks['road_risk']*100:.1f}\n")
                        f.write(f"  Toplam Risk: %{data['total_risk']*100:.1f}\n")
                        f.write("\n")
                
                QMessageBox.information(self, "Başarılı", "TXT raporu başarıyla kaydedildi.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"TXT kaydedilirken bir hata oluştu:\n{str(e)}")

    def save_as_json(self):
        """Sonuçları JSON olarak kaydet"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "JSON Kaydet", 
            f"afet_simulasyon_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                # NumPy değerlerini normal Python tiplerine çevir
                def convert_numpy(obj):
                    if isinstance(obj, np.integer):
                        return int(obj)
                    elif isinstance(obj, np.floating):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    return obj
                
                # Sonuçları hazırla
                export_data = {
                    'parameters': self.params,
                    'analysis': self.analysis
                }
                
                # JSON'a çevir ve kaydet
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, default=convert_numpy, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Başarılı", "JSON raporu başarıyla kaydedildi.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"JSON kaydedilirken bir hata oluştu:\n{str(e)}") 