import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QFileDialog, QSplitter, QMessageBox, QTabWidget)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import torch
from PIL import Image
import torchvision.transforms as transforms
from model_utils import ChangeDetectionModel

class ModelThread(QThread):
    finished_result = pyqtSignal(np.ndarray, np.ndarray)
    error = pyqtSignal(str)
    
    def __init__(self, model_path, pre_image_path, post_image_path):
        super().__init__()
        self.model_path = model_path
        self.pre_image_path = pre_image_path
        self.post_image_path = post_image_path
        
    def run(self):
        try:
            # Model nesnesini oluştur
            print(f"Model yükleniyor: {self.model_path}")
            change_detector = ChangeDetectionModel(self.model_path)
            
            # Değişim tespiti yap
            print("Değişim tespiti yapılıyor...")
            change_map, overlay_map = change_detector.predict_changes(
                self.pre_image_path, 
                self.post_image_path
            )
            
            print("Değişim tespiti tamamlandı, sonuçlar döndürülüyor")
            self.finished_result.emit(change_map, overlay_map)
        except Exception as e:
            self.error.emit(f"Beklenmeyen hata: {str(e)}")
            print(f"Beklenmeyen hata: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pre_image_path = None
        self.post_image_path = None
        self.model_path = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Afet Değişim Tespit Aracı')
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana düzen
        main_layout = QVBoxLayout()
        
        # Model seçme düğmesi
        self.model_btn = QPushButton('Model Dosyası Seç (.ckpt)')
        self.model_btn.clicked.connect(self.select_model)
        self.model_label = QLabel('Model seçilmedi')
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_btn)
        model_layout.addWidget(self.model_label)
        main_layout.addLayout(model_layout)
        
        # Görüntü seçme düğmeleri
        img_buttons_layout = QHBoxLayout()
        
        self.pre_btn = QPushButton('Afet Öncesi Görüntü Seç')
        self.pre_btn.clicked.connect(self.select_pre_image)
        img_buttons_layout.addWidget(self.pre_btn)
        
        self.post_btn = QPushButton('Afet Sonrası Görüntü Seç')
        self.post_btn.clicked.connect(self.select_post_image)
        img_buttons_layout.addWidget(self.post_btn)
        
        self.analyze_btn = QPushButton('Değişimleri Analiz Et')
        self.analyze_btn.clicked.connect(self.analyze_changes)
        self.analyze_btn.setEnabled(False)
        img_buttons_layout.addWidget(self.analyze_btn)
        
        main_layout.addLayout(img_buttons_layout)
        
        # Görüntü gösterme alanı
        splitter = QSplitter(Qt.Horizontal)
        
        # Afet öncesi görüntü
        self.pre_image_container = QLabel('Afet öncesi görüntü burada gösterilecek')
        self.pre_image_container.setAlignment(Qt.AlignCenter)
        self.pre_image_container.setMinimumSize(300, 300)
        self.pre_image_container.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        splitter.addWidget(self.pre_image_container)
        
        # Afet sonrası görüntü
        self.post_image_container = QLabel('Afet sonrası görüntü burada gösterilecek')
        self.post_image_container.setAlignment(Qt.AlignCenter)
        self.post_image_container.setMinimumSize(300, 300)
        self.post_image_container.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        splitter.addWidget(self.post_image_container)
        
        # Sonuçlar için sekmeli pencere
        self.result_tabs = QTabWidget()
        self.result_tabs.setMinimumSize(300, 300)
        self.result_tabs.setStyleSheet("border: 1px solid black; background-color: #f0f0f0;")
        
        # Değişim haritası sekmesi
        self.change_map_container = QLabel('Değişim haritası burada gösterilecek')
        self.change_map_container.setAlignment(Qt.AlignCenter)
        self.result_tabs.addTab(self.change_map_container, "Değişim Haritası")
        
        # Değişim bindirme sekmesi
        self.overlay_container = QLabel('Değişimlerin orijinal görüntü üzerine bindirmesi')
        self.overlay_container.setAlignment(Qt.AlignCenter)
        self.result_tabs.addTab(self.overlay_container, "Bindirme Görünümü")
        
        splitter.addWidget(self.result_tabs)
        
        splitter.setSizes([400, 400, 400])
        main_layout.addWidget(splitter)
        
        # Durum çubuğu
        self.statusBar().showMessage('Hazır')
        
        # Ana pencereye yerleştirme
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
    def select_model(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Model Dosyası Seç", "", 
            "Model Dosyaları (*.ckpt *.pth *.pt);;Tüm Dosyalar (*)", 
            options=options
        )
        if file_name:
            self.model_path = file_name
            self.model_label.setText(os.path.basename(file_name))
            self.update_analyze_button()
    
    def select_pre_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Afet Öncesi Görüntü Seç", "", 
            "Görüntü Dosyaları (*.png *.jpg *.jpeg *.tif *.tiff);;Tüm Dosyalar (*)", 
            options=options
        )
        if file_name:
            self.pre_image_path = file_name
            self.display_image(file_name, self.pre_image_container)
            self.update_analyze_button()
    
    def select_post_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Afet Sonrası Görüntü Seç", "", 
            "Görüntü Dosyaları (*.png *.jpg *.jpeg *.tif *.tiff);;Tüm Dosyalar (*)", 
            options=options
        )
        if file_name:
            self.post_image_path = file_name
            self.display_image(file_name, self.post_image_container)
            self.update_analyze_button()
    
    def display_image(self, file_path, container):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(container.width(), container.height(), 
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            container.setPixmap(pixmap)
        else:
            container.setText("Görüntü yüklenemedi!")
    
    def update_analyze_button(self):
        self.analyze_btn.setEnabled(
            self.pre_image_path is not None and 
            self.post_image_path is not None and 
            self.model_path is not None
        )
    
    def analyze_changes(self):
        if not (self.pre_image_path and self.post_image_path and self.model_path):
            QMessageBox.warning(self, "Hata", "Lütfen önce tüm dosyaları seçin.")
            return
        
        self.statusBar().showMessage('Değişimler analiz ediliyor...')
        self.analyze_btn.setEnabled(False)
        
        # Model işleme thread'i başlat
        self.thread = ModelThread(self.model_path, self.pre_image_path, self.post_image_path)
        self.thread.finished_result.connect(self.process_results)
        self.thread.error.connect(self.handle_error)
        self.thread.start()
    
    def process_results(self, change_map, overlay_map):
        # Değişim haritasını göster
        self.display_array_as_image(change_map, self.change_map_container)
        
        # Overlay haritasını göster
        self.display_array_as_image(overlay_map, self.overlay_container)
        
        self.statusBar().showMessage('Analiz tamamlandı')
        self.analyze_btn.setEnabled(True)
    
    def display_array_as_image(self, array, container):
        height, width, channel = array.shape
        bytes_per_line = 3 * width
        q_img = QImage(array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        pixmap = pixmap.scaled(container.width(), container.height(), 
                              Qt.KeepAspectRatio, Qt.SmoothTransformation)
        container.setPixmap(pixmap)
    
    def handle_error(self, error_msg):
        QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu: {error_msg}")
        self.statusBar().showMessage('Hata: İşlem tamamlanamadı')
        self.analyze_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 