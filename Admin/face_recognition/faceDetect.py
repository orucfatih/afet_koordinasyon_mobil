import face_recognition
import os
from pathlib import Path
import sys
import time
from datetime import timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QComboBox, 
                           QProgressBar, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

class SearchWorker(QThread):
    """Arama işlemini arka planda yürüten thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    status = pyqtSignal(str)
    time_update = pyqtSignal(str)

    def __init__(self, missing_image, search_folder):
        super().__init__()
        self.missing_image = missing_image
        self.search_folder = search_folder

    def run(self):
        start_time = time.time()
        try:
            self.status.emit("Kayıp kişi fotoğrafı işleniyor...")
            missing_encoding = face_recognition.face_encodings(
                face_recognition.load_image_file(self.missing_image)
            )[0]

            image_files = list(Path(self.search_folder).rglob("*.*"))
            valid_files = [f for f in image_files 
                          if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
            total_files = len(valid_files)
            
            self.status.emit(f"Toplam {total_files} fotoğraf taranacak...")
            results = []

            for i, img_path in enumerate(valid_files):
                try:
                    elapsed_time = time.time() - start_time
                    time_str = str(timedelta(seconds=int(elapsed_time)))
                    self.time_update.emit(time_str)

                    image = face_recognition.load_image_file(str(img_path))
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        distance = face_recognition.face_distance(
                            [missing_encoding], 
                            encodings[0]
                        )[0]
                        if distance < 0.63:
                            results.append({
                                'path': img_path,
                                'distance': distance,
                                'match_type': self.get_match_type(distance)
                            })
                    
                    progress = int((i + 1) / total_files * 100)
                    self.progress.emit(progress)
                    
                except Exception as e:
                    print(f"Hata ({img_path}): {e}")

            results.sort(key=lambda x: x['distance'])
            self.finished.emit(results)

        except Exception as e:
            self.status.emit(f"Hata: {str(e)}")

    def get_match_type(self, distance):
        if distance < 0.55:
            return "✅ Güçlü Eşleşme"
        elif distance < 0.63:
            return "⚠️ Şüpheli Eşleşme"
        return "❌ Eşleşme Yok"

class FaceSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yüz Arama Sistemi")
        self.setGeometry(100, 100, 800, 600)

        # Çalışma dizini ve klasörler
        self.work_dir = os.getcwd()
        self.missing_folder = os.path.join(self.work_dir,"Admin","face recagnation","missed_persons")
        self.found_folder = os.path.join(self.work_dir, "Admin","face recagnation","founded_persons")
        

        # Klasörleri kontrol et
        self.check_required_folders()

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Üst bölüm
        top_layout = QHBoxLayout()
        
        # Kayıp kişi seçimi
        self.person_combo = QComboBox()
        self.person_combo.currentIndexChanged.connect(self.on_person_select)
        top_layout.addWidget(QLabel("Kayıp Kişi:"))
        top_layout.addWidget(self.person_combo)
        
        layout.addLayout(top_layout)

        # Fotoğraf önizleme
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(200, 200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        # Arama butonu
        self.search_button = QPushButton("Aramayı Başlat")
        self.search_button.clicked.connect(self.start_search)
        layout.addWidget(self.search_button)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Süre göstergesi
        self.time_label = QLabel("Süre: 00:00:00")
        layout.addWidget(self.time_label)

        # Durum mesajı
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Sonuç ağaçları için iki ayrı bölüm oluştur
        results_layout = QHBoxLayout()
        
        # Güçlü Eşleşmeler Bölümü
        strong_match_widget = QWidget()
        strong_match_layout = QVBoxLayout(strong_match_widget)
        strong_match_label = QLabel("✅ Güçlü Eşleşmeler")
        strong_match_label.setStyleSheet("font-weight: bold; color: green;")
        self.strong_match_tree = QTreeWidget()
        self.strong_match_tree.setHeaderLabels(['Dosya', 'Benzerlik', 'Önizleme'])
        self.strong_match_tree.setColumnWidth(0, 150)
        self.strong_match_tree.setColumnWidth(1, 100)
        self.strong_match_tree.setColumnWidth(2, 200)
        strong_match_layout.addWidget(strong_match_label)
        strong_match_layout.addWidget(self.strong_match_tree)

        # Şüpheli Eşleşmeler Bölümü
        suspicious_match_widget = QWidget()
        suspicious_match_layout = QVBoxLayout(suspicious_match_widget)
        suspicious_match_label = QLabel("⚠️ Şüpheli Eşleşmeler")
        suspicious_match_label.setStyleSheet("font-weight: bold; color: orange;")
        self.suspicious_match_tree = QTreeWidget()
        self.suspicious_match_tree.setHeaderLabels(['Dosya', 'Benzerlik', 'Önizleme'])
        self.suspicious_match_tree.setColumnWidth(0, 150)
        self.suspicious_match_tree.setColumnWidth(1, 100)
        self.suspicious_match_tree.setColumnWidth(2, 200)
        suspicious_match_layout.addWidget(suspicious_match_label)
        suspicious_match_layout.addWidget(self.suspicious_match_tree)

        # Sonuç bölümlerini ana layout'a ekle
        results_layout.addWidget(strong_match_widget)
        results_layout.addWidget(suspicious_match_widget)
        layout.addLayout(results_layout)

        # Kayıp kişi listesini güncelle
        self.update_missing_persons_list()

        # Search worker
        self.search_worker = None

    def check_required_folders(self):
        """Gerekli klasörlerin varlığını kontrol et"""
        for folder in [self.missing_folder, self.found_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def update_missing_persons_list(self):
        """Kaybolanlar klasöründeki fotoğrafları listele"""
        self.person_combo.clear()
        self.person_combo.addItem("Kayıp kişi fotoğrafı seçin")
        
        image_files = [
            f for f in os.listdir(self.missing_folder) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
        ]
        
        self.person_combo.addItems(image_files)

    def on_person_select(self, index):
        """Kayıp kişi seçildiğinde"""
        if index > 0:
            selected = self.person_combo.currentText()
            image_path = os.path.join(self.missing_folder, selected)
            self.show_preview(image_path)

    def show_preview(self, image_path):
        """Seçilen fotoğrafın önizlemesini göster"""
        try:
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
        except Exception as e:
            self.status_label.setText(f"Fotoğraf yüklenemedi: {e}")

    def start_search(self):
        """Arama işlemini başlat"""
        if self.person_combo.currentIndex() == 0:
            self.status_label.setText("Lütfen kayıp kişi fotoğrafı seçin!")
            return

        if self.search_worker and self.search_worker.isRunning():
            return

        self.search_button.setEnabled(False)
        self.strong_match_tree.clear()
        self.suspicious_match_tree.clear()
        self.progress_bar.setValue(0)
        
        # Arama worker'ını başlat
        selected_image = os.path.join(
            self.missing_folder, 
            self.person_combo.currentText()
        )
        self.search_worker = SearchWorker(selected_image, self.found_folder)
        self.search_worker.progress.connect(self.update_progress)
        self.search_worker.finished.connect(self.show_results)
        self.search_worker.status.connect(self.update_status)
        self.search_worker.time_update.connect(self.update_time)
        self.search_worker.start()

    def update_progress(self, value):
        """İlerleme çubuğunu güncelle"""
        self.progress_bar.setValue(value)

    def update_status(self, message):
        """Durum mesajını güncelle"""
        self.status_label.setText(message)

    def update_time(self, time_str):
        """Süre göstergesini güncelle"""
        self.time_label.setText(f"Süre: {time_str}")

    def create_preview_label(self, image_path):
        """Önizleme etiketi oluştur"""
        preview_label = QLabel()
        try:
            pixmap = QPixmap(str(image_path))
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            preview_label.setPixmap(pixmap)
        except Exception as e:
            preview_label.setText("Önizleme\nYüklenemedi")
            print(f"Önizleme hatası: {e}")
        preview_label.setAlignment(Qt.AlignCenter)
        return preview_label

    def show_results(self, results):
        """Sonuçları kategorilere ayırarak göster"""
        # Ağaçları temizle
        self.strong_match_tree.clear()
        self.suspicious_match_tree.clear()

        strong_matches = 0
        suspicious_matches = 0

        for result in results:
            distance = result['distance']
            file_name = os.path.basename(str(result['path']))
            similarity = f"{distance}"
            
            # Yeni QTreeWidgetItem oluştur
            item = QTreeWidgetItem([file_name, similarity])
            
            # Önizleme etiketi oluştur
            preview_label = self.create_preview_label(result['path'])
            
            # Eşleşme tipine göre uygun ağaca ekle
            if distance < 0.55:
                self.strong_match_tree.addTopLevelItem(item)
                self.strong_match_tree.setItemWidget(item, 2, preview_label)
                strong_matches += 1
            elif distance < 0.63:
                self.suspicious_match_tree.addTopLevelItem(item)
                self.suspicious_match_tree.setItemWidget(item, 2, preview_label)
                suspicious_matches += 1

        # Sonuç istatistiklerini göster
        stats = (
            f"Arama tamamlandı. "
            f"Güçlü Eşleşme: {strong_matches}, "
            f"Şüpheli Eşleşme: {suspicious_matches}"
        )
        self.status_label.setText(stats)
        self.search_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = FaceSearchApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
