from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QTextEdit, QHBoxLayout,
                           QMessageBox, QLabel, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from sample_data import TASK_HISTORY_DATA, TASK_HISTORY_DETAILS
from styles.styles_dark import *
from styles.styles_light import *
import os
from .op_constant import HISTORY_TABLE_HEADERS
# Firebase veritabanı işlemleri için import
from database import get_database_ref, get_storage_bucket
import time
import datetime


def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

class MissionHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Görev Geçmişi")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Firebase referansı
        self.history_ref = get_database_ref('/operations/task_history')
        
        self.initUI()
        self.load_history_data()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(len(HISTORY_TABLE_HEADERS))
        self.history_table.setHorizontalHeaderLabels(HISTORY_TABLE_HEADERS)
        self.history_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.history_table.itemDoubleClicked.connect(self.show_history_details)
        self.history_table.setSelectionMode(QTableWidget.MultiSelection)  # Çoklu seçim özelliği

        # Tablonun düzenlenebilirliğini kapat
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Butonlar için yatay layout
        button_layout = QHBoxLayout()

        # Seçili geçmişi silme butonu
        delete_selected_btn = QPushButton(" Seçili Geçmişi Sil")
        delete_selected_btn.setIcon(QIcon(get_icon_path('bin.png')))
        delete_selected_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_selected_btn.clicked.connect(self.delete_selected_history)

        # Tüm geçmişi temizleme butonu
        clear_all_btn = QPushButton(" Geçmişi Temizle")
        clear_all_btn.setIcon(QIcon(get_icon_path('delete-database.png')))
        clear_all_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        clear_all_btn.clicked.connect(self.clear_all_history)

        # Butonları layout'a ekle
        button_layout.addWidget(delete_selected_btn)
        button_layout.addWidget(clear_all_btn)

        layout.addWidget(self.history_table)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_history_data(self):
        """Firebase'den görev geçmişi verilerini yükler"""
        try:
            # Firebase'den görevi tamamlanmış görevleri al
            history_data = self.history_ref.get()
            
            # Tablo verilerini temizle
            self.history_table.setRowCount(0)
            
            if history_data:
                # Verileri tarih sırasına göre sırala (en yeni en üstte)
                sorted_tasks = sorted(
                    [(task_id, task_info) for task_id, task_info in history_data.items()],
                    key=lambda x: x[1].get('completed_at', 0),
                    reverse=True
                )
                
                for task_id, task_info in sorted_tasks:
                    # Tamamlanma tarihini formatlı göster
                    completed_time = task_info.get('completed_at', 0)
                    completed_date = datetime.datetime.fromtimestamp(
                        completed_time
                    ).strftime('%Y-%m-%d %H:%M')
                    
                    # Tablo verilerini hazırla
                    row_data = [
                        completed_date,
                        task_info.get('title', 'İsimsiz Görev'),
                        task_info.get('location', 'Belirtilmemiş'),
                        str(task_info.get('duration', 'N/A')),
                        task_info.get('priority', 'Normal'),
                        task_info.get('status', 'Tamamlandı')
                    ]
                    
                    # Tabloya yeni satır ekle
                    row = self.history_table.rowCount()
                    self.history_table.insertRow(row)
                    
                    # Task ID'sini gizli veri olarak tut
                    for col, data in enumerate(row_data):
                        item = QTableWidgetItem(str(data))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setData(Qt.UserRole, task_id)  # ID'yi sakla
                        self.history_table.setItem(row, col, item)
            else:
                # Firebase'de veri yoksa örnek veriyi kullan
                self._load_legacy_history_data()
                
        except Exception as e:
            print(f"Görev geçmişi yüklenirken hata: {str(e)}")
            # Hata durumunda örnek veriyi kullan
            self._load_legacy_history_data()
        
        self.history_table.resizeColumnsToContents()

    def _load_legacy_history_data(self):
        """Örnek görev geçmişi verilerini yükler (yedek method)"""
        self.history_table.setRowCount(0)
        
        for task in TASK_HISTORY_DATA:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            for col, data in enumerate(task):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(row, col, item)

    def delete_selected_history(self):
        """Seçili görev geçmişi kayıtlarını Firebase'den siler"""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için görev geçmişi seçin!")
            return

        # Tekrarlı seçimleri önle
        selected_rows = set()
        task_ids = set()
        
        for item in selected_items:
            selected_rows.add(item.row())
            task_ids.add(item.data(Qt.UserRole))

        reply = QMessageBox.question(
            self,
            'Görev Geçmişi Silme Onayı',
            f'{len(selected_rows)} adet görev geçmişini silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Firebase'den görevleri sil
                for task_id in task_ids:
                    if task_id:
                        self.history_ref.child(task_id).delete()
                
                # UI'ı güncelle - seçili satırları tersten sil (indeks karışıklığı olmaması için)
                for row in sorted(selected_rows, reverse=True):
                    self.history_table.removeRow(row)
                
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Seçili görev geçmişi kayıtları başarıyla silindi."
                )
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Görev geçmişi silinirken hata oluştu: {str(e)}")

    def clear_all_history(self):
        """Tüm görev geçmişini Firebase'den temizler"""
        if self.history_table.rowCount() == 0:
            QMessageBox.information(self, "Bilgi", "Görev geçmişi zaten boş!")
            return

        reply = QMessageBox.question(
            self,
            'Görev Geçmişi Temizleme Onayı',
            'Tüm görev geçmişini temizlemek istediğinizden emin misiniz?\nBu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Firebase'den tüm geçmişi temizle
                self.history_ref.delete()
                
                # UI'ı güncelle
                self.history_table.setRowCount(0)
                
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Tüm görev geçmişi başarıyla temizlendi."
                )
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Görev geçmişi temizlenirken hata oluştu: {str(e)}")

    def show_history_details(self, item):
        """Görev geçmişi detaylarını Firebase'den gösterir"""
        task_id = item.data(Qt.UserRole)
        
        try:
            # Firebase'den görev detaylarını al
            task_data = self.history_ref.child(task_id).get()
            
            if task_data:
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Görev Detayı: {task_data.get('title', 'Görev')}")
                dialog.setMinimumWidth(500)
                dialog.setMinimumHeight(400)
                
                layout = QVBoxLayout()
                
                # Görev bilgilerini düzenli göster
                form_layout = QFormLayout()
                form_layout.addRow("Başlık:", QLabel(task_data.get('title', '')))
                form_layout.addRow("Ekip:", QLabel(task_data.get('team', '')))
                form_layout.addRow("Lokasyon:", QLabel(task_data.get('location', '')))
                form_layout.addRow("Öncelik:", QLabel(task_data.get('priority', '')))
                form_layout.addRow("Tahmini Süre:", QLabel(f"{task_data.get('duration', '')} saat"))
                
                # Tamamlanma zamanını formatlı göster
                completed_time = task_data.get('completed_at', 0)
                if completed_time:
                    completed_date = datetime.datetime.fromtimestamp(
                        completed_time
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    form_layout.addRow("Tamamlanma Tarihi:", QLabel(completed_date))
                
                # Görev detayları için text edit
                details_text = QTextEdit()
                details_text.setReadOnly(True)
                details_text.setText(task_data.get('details', ''))
                details_text.setMinimumHeight(150)
                
                # Kapatma butonu
                close_btn = QPushButton("Kapat")
                close_btn.clicked.connect(dialog.accept)
                
                layout.addLayout(form_layout)
                layout.addWidget(QLabel("Detaylar:"))
                layout.addWidget(details_text)
                layout.addWidget(close_btn)
                
                dialog.setLayout(layout)
                dialog.exec_()
            else:
                # Firebase'de veri yoksa örnek veriyi dene
                self._show_legacy_history_details(item)
                
        except Exception as e:
            print(f"Görev geçmişi detayı görüntülenirken hata: {str(e)}")
            # Hata durumunda örnek veriyi kullan
            self._show_legacy_history_details(item)
    
    def _show_legacy_history_details(self, item):
        """Örnek görev geçmişi detaylarını gösterir (yedek method)"""
        row = item.row()
        date = self.history_table.item(row, 0).text()
        task_type = self.history_table.item(row, 1).text()
        task_key = f"{date} {task_type}"
        
        if task_key in TASK_HISTORY_DETAILS:
            details = TASK_HISTORY_DETAILS[task_key]
            detail_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Görev Detayları")
            dialog.setMinimumWidth(400)
            layout = QVBoxLayout()
            
            text_edit = QTextEdit()
            text_edit.setPlainText(detail_text)
            text_edit.setReadOnly(True)
            
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(dialog.accept)
            
            layout.addWidget(text_edit)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Bilgi", "Bu görev için detaylı bilgi bulunamadı.") 