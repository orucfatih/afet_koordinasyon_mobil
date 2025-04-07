from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QTextEdit, QHBoxLayout,
                           QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from sample_data import TASK_HISTORY_DATA, TASK_HISTORY_DETAILS
from styles.styles_dark import *
from styles.styles_light import *
import os
from .op_constant import HISTORY_TABLE_HEADERS


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
        self.initUI()
        self.load_history_data()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
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
        """Görev geçmişi verilerini yükler"""
        self.history_table.setRowCount(0)
        
        for task in TASK_HISTORY_DATA:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            for col, data in enumerate(task):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(row, col, item)
        
        self.history_table.resizeColumnsToContents()

    def delete_selected_history(self):
        """Seçili görev geçmişi kayıtlarını siler"""
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için görev geçmişi seçin!")
            return

        reply = QMessageBox.question(
            self,
            'Görev Geçmişi Silme Onayı',
            f'{len(selected_rows)} adet görev geçmişini silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Seçili satırları tersten sil (indeks karışıklığı olmaması için)
            for row in sorted(selected_rows, reverse=True):
                self.history_table.removeRow(row)
                if row < len(TASK_HISTORY_DATA):
                    TASK_HISTORY_DATA.pop(row)

            QMessageBox.information(
                self,
                "Başarılı",
                "Seçili görev geçmişi kayıtları başarıyla silindi."
            )

    def clear_all_history(self):
        """Tüm görev geçmişini temizler"""
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
            self.history_table.setRowCount(0)
            TASK_HISTORY_DATA.clear()
            QMessageBox.information(
                self,
                "Başarılı",
                "Tüm görev geçmişi başarıyla temizlendi."
            )

    def show_history_details(self, item):
        """Görev geçmişi detaylarını gösterir"""
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