import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QComboBox, QFrame, QSplitter, QMessageBox,
                             QProgressBar, QSlider, QGridLayout, QGroupBox, QCheckBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
import numpy as np
from PIL import Image
import cv2

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from styles.styles_dark import *

# Import the model utility
from .model_utils import ChangeDetectionModel

class ProcessingThread(QThread):
    finished_signal = pyqtSignal(np.ndarray, np.ndarray)
    progress_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    
    def __init__(self, model_path, pre_image_path, post_image_path, threshold=100):
        super().__init__()
        self.model_path = model_path
        self.pre_image_path = pre_image_path
        self.post_image_path = post_image_path
        self.threshold = threshold
        
    def run(self):
        try:
            # Signal the start of processing
            self.progress_signal.emit(10)
            
            # Initialize the model
            self.progress_signal.emit(30)
            change_detector = ChangeDetectionModel(self.model_path)
            
            # Signal model loaded
            self.progress_signal.emit(50)
            
            # Perform change detection
            change_map, overlay_map = change_detector.predict_changes(
                self.pre_image_path,
                self.post_image_path
            )
            
            # Signal completed
            self.progress_signal.emit(100)
            self.finished_signal.emit(change_map, overlay_map)
            
        except Exception as e:
            self.error_signal.emit(f"İşlem sırasında hata: {str(e)}")
            print(f"Processing error: {str(e)}")

class SatelliteDetectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.pre_image_path = None
        self.post_image_path = None
        self.model_path = None
        self.change_map = None
        self.overlay_map = None
        self.threshold = 100  # Default threshold value
        
        # Default model path - if found in the satellite_detection/models directory
        default_model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "models", 
            "unet_siamdiff_resnet50.ckpt"
        )
        if os.path.exists(default_model_path):
            self.model_path = default_model_path
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel("Uydu Görüntülerinden Hasar Tespiti")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E1E1E6;")
        main_layout.addWidget(title_label)
        
        desc_label = QLabel("Afet öncesi ve sonrası uydu görüntülerini karşılaştırarak hasarlı bölgeleri tespit edin.")
        desc_label.setStyleSheet("font-size: 14px; color: #E1E1E6;")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # Model selection section
        model_frame = QFrame()
        model_frame.setStyleSheet("""
            QFrame {
                background-color: #201c2b;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        model_layout = QHBoxLayout(model_frame)
        
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: #E1E1E6;")
        model_layout.addWidget(model_label)
        
        self.model_path_label = QLabel(os.path.basename(self.model_path) if self.model_path else "Model seçilmedi")
        self.model_path_label.setStyleSheet("color: #E1E1E6;")
        model_layout.addWidget(self.model_path_label, 1)
        
        self.select_model_btn = QPushButton("Model Seç")
        self.select_model_btn.setStyleSheet(BUTTON_STYLE)
        self.select_model_btn.clicked.connect(self.select_model)
        model_layout.addWidget(self.select_model_btn)
        
        main_layout.addWidget(model_frame)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Image selection group
        image_selection_group = QGroupBox("Görüntü Seçimi")
        image_selection_group.setStyleSheet(GROUP_STYLE)
        image_layout = QVBoxLayout(image_selection_group)
        
        # Pre-disaster image selection
        pre_layout = QHBoxLayout()
        pre_label = QLabel("Afet Öncesi:")
        pre_label.setStyleSheet("color: #E1E1E6;")
        pre_layout.addWidget(pre_label)
        
        self.pre_path_label = QLabel("Görüntü seçilmedi")
        self.pre_path_label.setStyleSheet("color: #E1E1E6;")
        pre_layout.addWidget(self.pre_path_label, 1)
        
        self.select_pre_btn = QPushButton("Gözat")
        self.select_pre_btn.setStyleSheet(BUTTON_STYLE)
        self.select_pre_btn.clicked.connect(self.select_pre_image)
        pre_layout.addWidget(self.select_pre_btn)
        
        image_layout.addLayout(pre_layout)
        
        # Post-disaster image selection
        post_layout = QHBoxLayout()
        post_label = QLabel("Afet Sonrası:")
        post_label.setStyleSheet("color: #E1E1E6;")
        post_layout.addWidget(post_label)
        
        self.post_path_label = QLabel("Görüntü seçilmedi")
        self.post_path_label.setStyleSheet("color: #E1E1E6;")
        post_layout.addWidget(self.post_path_label, 1)
        
        self.select_post_btn = QPushButton("Gözat")
        self.select_post_btn.setStyleSheet(BUTTON_STYLE)
        self.select_post_btn.clicked.connect(self.select_post_image)
        post_layout.addWidget(self.select_post_btn)
        
        image_layout.addLayout(post_layout)
        
        # Sample images section
        sample_label = QLabel("Örnek Görüntüler:")
        sample_label.setStyleSheet("color: #E1E1E6;")
        image_layout.addWidget(sample_label)
        
        self.sample_combo = QComboBox()
        self.sample_combo.setStyleSheet(COMBOBOX_STYLE)
        self.sample_combo.addItem("Seçiniz...")
        
        # Add sample image pairs from test_pictures directory
        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_pictures")
        if os.path.exists(sample_dir):
            pre_images = [f for f in os.listdir(sample_dir) if f.startswith("pre_")]
            for pre_img in pre_images:
                location = pre_img.replace("pre_", "").split(".")[0]
                post_img = f"post_{location}" + os.path.splitext(pre_img)[1]
                if os.path.exists(os.path.join(sample_dir, post_img)):
                    self.sample_combo.addItem(location.capitalize().replace("_", " "))
        
        self.sample_combo.currentIndexChanged.connect(self.load_sample_images)
        image_layout.addWidget(self.sample_combo)
        
        # Process button
        self.process_btn = QPushButton("Değişimleri Tespit Et")
        self.process_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.detect_changes)
        image_layout.addWidget(self.process_btn)
        
        controls_layout.addWidget(image_selection_group)
        
        # Analysis options group
        analysis_options_group = QGroupBox("Analiz Seçenekleri")
        analysis_options_group.setStyleSheet(GROUP_STYLE)
        analysis_layout = QVBoxLayout(analysis_options_group)
        
        # Threshold slider
        threshold_layout = QVBoxLayout()
        threshold_label = QLabel("Hassasiyet:")
        threshold_label.setStyleSheet("color: #E1E1E6;")
        threshold_layout.addWidget(threshold_label)
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(50)
        self.threshold_slider.setMaximum(200)
        self.threshold_slider.setValue(self.threshold)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(25)
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        
        # Slider labels
        slider_labels_layout = QHBoxLayout()
        low_label = QLabel("Düşük")
        low_label.setStyleSheet("color: #E1E1E6; font-size: 12px;")
        slider_labels_layout.addWidget(low_label)
        
        slider_labels_layout.addStretch()
        
        high_label = QLabel("Yüksek")
        high_label.setStyleSheet("color: #E1E1E6; font-size: 12px;")
        slider_labels_layout.addWidget(high_label)
        
        threshold_layout.addLayout(slider_labels_layout)
        analysis_layout.addLayout(threshold_layout)
        
        # Display options
        self.overlay_checkbox = QCheckBox("Sonuçları orijinal görüntü üzerine göster")
        self.overlay_checkbox.setStyleSheet("color: #E1E1E6;")
        self.overlay_checkbox.setChecked(True)
        self.overlay_checkbox.stateChanged.connect(self.toggle_display_mode)
        analysis_layout.addWidget(self.overlay_checkbox)
        
        # Export options
        self.export_btn = QPushButton("Sonuçları Dışa Aktar")
        self.export_btn.setStyleSheet(BUTTON_STYLE)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_results)
        analysis_layout.addWidget(self.export_btn)
        
        analysis_layout.addStretch()
        
        controls_layout.addWidget(analysis_options_group)
        
        main_layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2d2b38;
                border-radius: 4px;
                text-align: center;
                background-color: #201c2b;
                color: #E1E1E6;
            }
            QProgressBar::chunk {
                background-color: #500073;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Images display layout
        display_layout = QHBoxLayout()
        
        # Create splitter for resizable image views
        splitter = QSplitter(Qt.Horizontal)
        
        # Pre-disaster image container
        pre_frame = QFrame()
        pre_frame.setFrameShape(QFrame.StyledPanel)
        pre_frame.setStyleSheet("""
            QFrame {
                background-color: #13111b;
                border: 1px solid #2d2b38;
                border-radius: 5px;
            }
        """)
        pre_layout = QVBoxLayout(pre_frame)
        
        pre_title = QLabel("Afet Öncesi")
        pre_title.setAlignment(Qt.AlignCenter)
        pre_title.setStyleSheet("color: #E1E1E6; font-weight: bold;")
        pre_layout.addWidget(pre_title)
        
        self.pre_image_label = QLabel()
        self.pre_image_label.setAlignment(Qt.AlignCenter)
        self.pre_image_label.setMinimumSize(300, 300)
        self.pre_image_label.setStyleSheet("background-color: transparent;")
        pre_layout.addWidget(self.pre_image_label)
        
        splitter.addWidget(pre_frame)
        
        # Post-disaster image container
        post_frame = QFrame()
        post_frame.setFrameShape(QFrame.StyledPanel)
        post_frame.setStyleSheet("""
            QFrame {
                background-color: #13111b;
                border: 1px solid #2d2b38;
                border-radius: 5px;
            }
        """)
        post_layout = QVBoxLayout(post_frame)
        
        post_title = QLabel("Afet Sonrası")
        post_title.setAlignment(Qt.AlignCenter)
        post_title.setStyleSheet("color: #E1E1E6; font-weight: bold;")
        post_layout.addWidget(post_title)
        
        self.post_image_label = QLabel()
        self.post_image_label.setAlignment(Qt.AlignCenter)
        self.post_image_label.setMinimumSize(300, 300)
        self.post_image_label.setStyleSheet("background-color: transparent;")
        post_layout.addWidget(self.post_image_label)
        
        splitter.addWidget(post_frame)
        
        # Results container
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.StyledPanel)
        result_frame.setStyleSheet("""
            QFrame {
                background-color: #13111b;
                border: 1px solid #2d2b38;
                border-radius: 5px;
            }
        """)
        result_layout = QVBoxLayout(result_frame)
        
        result_title = QLabel("Hasar Tespiti Sonucu")
        result_title.setAlignment(Qt.AlignCenter)
        result_title.setStyleSheet("color: #E1E1E6; font-weight: bold;")
        result_layout.addWidget(result_title)
        
        self.result_image_label = QLabel()
        self.result_image_label.setAlignment(Qt.AlignCenter)
        self.result_image_label.setMinimumSize(300, 300)
        self.result_image_label.setStyleSheet("background-color: transparent;")
        result_layout.addWidget(self.result_image_label)
        
        splitter.addWidget(result_frame)
        
        # Set equal sizes initially
        splitter.setSizes([int(splitter.width()/3) for _ in range(3)])
        
        display_layout.addWidget(splitter)
        main_layout.addLayout(display_layout)
        
        # Status line
        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("color: #E1E1E6;")
        main_layout.addWidget(self.status_label)
    
    def select_model(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Model Dosyası Seç", "", 
            "Model Dosyaları (*.ckpt *.pth *.pt);;Tüm Dosyalar (*)", 
            options=options
        )
        if file_name:
            self.model_path = file_name
            self.model_path_label.setText(os.path.basename(file_name))
            self.update_process_button()
    
    def select_pre_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Afet Öncesi Görüntü Seç", "", 
            "Görüntü Dosyaları (*.png *.jpg *.jpeg *.tif *.tiff);;Tüm Dosyalar (*)", 
            options=options
        )
        if file_name:
            self.pre_image_path = file_name
            self.pre_path_label.setText(os.path.basename(file_name))
            self.display_image(file_name, self.pre_image_label)
            self.update_process_button()
    
    def select_post_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Afet Sonrası Görüntü Seç", "", 
            "Görüntü Dosyaları (*.png *.jpg *.jpeg *.tif *.tiff);;Tüm Dosyalar (*)", 
            options=options
        )
        if file_name:
            self.post_image_path = file_name
            self.post_path_label.setText(os.path.basename(file_name))
            self.display_image(file_name, self.post_image_label)
            self.update_process_button()
    
    def load_sample_images(self, index):
        if index == 0:  # "Seçiniz..." option
            return
        
        location = self.sample_combo.currentText().lower().replace(" ", "_")
        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_pictures")
        
        # Find the pre image with this location
        pre_files = [f for f in os.listdir(sample_dir) if f.startswith(f"pre_{location}")]
        post_files = [f for f in os.listdir(sample_dir) if f.startswith(f"post_{location}")]
        
        if pre_files and post_files:
            pre_path = os.path.join(sample_dir, pre_files[0])
            post_path = os.path.join(sample_dir, post_files[0])
            
            self.pre_image_path = pre_path
            self.post_image_path = post_path
            
            self.pre_path_label.setText(os.path.basename(pre_path))
            self.post_path_label.setText(os.path.basename(post_path))
            
            self.display_image(pre_path, self.pre_image_label)
            self.display_image(post_path, self.post_image_label)
            
            self.update_process_button()
    
    def display_image(self, file_path, label):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                label.width(), label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            label.setPixmap(pixmap)
        else:
            label.setText("Görüntü yüklenemedi!")
    
    def update_process_button(self):
        self.process_btn.setEnabled(
            self.pre_image_path is not None and 
            self.post_image_path is not None and 
            self.model_path is not None
        )
    
    def update_threshold(self, value):
        self.threshold = value
        # If we already have results, update the visualization
        if self.change_map is not None and self.overlay_map is not None:
            self.display_results()
    
    def toggle_display_mode(self):
        # If we already have results, update the visualization
        if self.change_map is not None and self.overlay_map is not None:
            self.display_results()
    
    def detect_changes(self):
        if not (self.pre_image_path and self.post_image_path):
            QMessageBox.warning(self, "Hata", "Lütfen afet öncesi ve sonrası görüntüleri seçin.")
            return
        
        if not self.model_path:
            QMessageBox.warning(self, "Hata", "Lütfen bir model seçin.")
            return
        
        # Disable the process button and show progress bar
        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("İşleniyor...")
        
        # Start the processing thread
        self.process_thread = ProcessingThread(
            self.model_path,
            self.pre_image_path,
            self.post_image_path,
            self.threshold
        )
        self.process_thread.progress_signal.connect(self.update_progress)
        self.process_thread.finished_signal.connect(self.process_completed)
        self.process_thread.error_signal.connect(self.process_error)
        self.process_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def process_completed(self, change_map, overlay_map):
        self.change_map = change_map
        self.overlay_map = overlay_map
        
        self.display_results()
        
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.status_label.setText("Analiz tamamlandı")
    
    def display_results(self):
        # Based on checkbox state, show either overlay or change map
        if self.overlay_checkbox.isChecked():
            # Display the overlay map (changes on top of post-disaster image)
            self.display_array_as_image(self.overlay_map, self.result_image_label)
        else:
            # Display the raw change map
            self.display_array_as_image(self.change_map, self.result_image_label)
    
    def display_array_as_image(self, array, label):
        # Convert numpy array to QImage
        height, width, channel = array.shape
        bytes_per_line = 3 * width
        q_img = QImage(array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        pixmap = pixmap.scaled(
            label.width(), label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(pixmap)
    
    def process_error(self, error_msg):
        QMessageBox.critical(self, "Hata", error_msg)
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        self.status_label.setText("Hata: İşlem tamamlanamadı")
    
    def export_results(self):
        if self.overlay_map is None:
            QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak sonuç bulunamadı.")
            return
        
        options = QFileDialog.Options()
        file_name, filter_used = QFileDialog.getSaveFileName(
            self, "Sonuçları Kaydet", "", 
            "PNG Dosyası (*.png);;JPEG Dosyası (*.jpg);;Tüm Dosyalar (*)", 
            options=options
        )
        
        if file_name:
            # Ensure file has appropriate extension
            if not (file_name.lower().endswith('.png') or file_name.lower().endswith('.jpg') or 
                  file_name.lower().endswith('.jpeg')):
                # If PNG filter was used or no specific filter
                if "PNG" in filter_used or "Tüm Dosyalar" in filter_used:
                    file_name += '.png'
                else:  # JPEG was selected
                    file_name += '.jpg'
            
            try:
                if self.overlay_checkbox.isChecked():
                    # Save the overlay map
                    Image.fromarray(self.overlay_map).save(file_name)
                else:
                    # Save the change map
                    Image.fromarray(self.change_map).save(file_name)
                
                QMessageBox.information(self, "Başarılı", f"Sonuçlar başarıyla kaydedildi:\n{file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {str(e)}") 