from PyQt5.QtWidgets import (QComboBox, QMessageBox, QDialog, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from .equipment_dialogs import InventoryDialog

class InventoryTab:
    """Envanter Dağılımı sekmesi için işlemler"""
    def __init__(self, parent):
        self.parent = parent
        self.inventory_table = parent.inventory_table
        self.location_combo = parent.location_combo
        self.add_inventory_btn = parent.add_inventory_btn
        self.edit_inventory_btn = parent.edit_inventory_btn
        self.delete_inventory_btn = parent.delete_inventory_btn
        
        # Bağlantıları kur
        self.setup_connections()
        
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        self.location_combo.currentTextChanged.connect(self.filter_inventory)
        self.add_inventory_btn.clicked.connect(self.add_inventory)
        self.edit_inventory_btn.clicked.connect(self.edit_inventory)
        self.delete_inventory_btn.clicked.connect(self.delete_inventory)
        
    def filter_inventory(self):
        """Envanter verilerini lokasyona göre filtrele"""
        selected_location = self.location_combo.currentText()
        
        for row in range(self.inventory_table.rowCount()):
            location_item = self.inventory_table.item(row, 0)
            if location_item:
                should_show = (selected_location == "Tüm Lokasyonlar" or 
                            location_item.text() == selected_location)
                self.inventory_table.setRowHidden(row, not should_show)
                
    def add_inventory(self):
        """Yeni envanter kaydı eklemek için dialog açar"""
        dialog = InventoryDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            
            for col, value in enumerate(dialog.get_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Kritik seviye için renklendirme
                if col == 4 and int(value) > 0:  # Kritik seviye sütunu
                    item.setBackground(QBrush(QColor("#f44336")))
                    item.setForeground(QBrush(QColor("white")))
                
                self.inventory_table.setItem(row, col, item)

    def edit_inventory(self):
        """Seçili envanter kaydını düzenler"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.parent, "Uyarı", "Lütfen düzenlemek için bir kayıt seçin!")
            return
        
        dialog = InventoryDialog(self.parent)
        dialog.set_values([
            self.inventory_table.item(current_row, col).text()
            for col in range(self.inventory_table.columnCount())
        ])
        
        if dialog.exec_() == QDialog.Accepted:
            for col, value in enumerate(dialog.get_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # Kritik seviye için renklendirme
                if col == 4 and int(value) > 0:  # Kritik seviye sütunu
                    item.setBackground(QBrush(QColor("#f44336")))
                    item.setForeground(QBrush(QColor("white")))
                
                self.inventory_table.setItem(current_row, col, item)

    def delete_inventory(self):
        """Seçili envanter kaydını siler"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.parent, "Uyarı", "Lütfen silmek için bir kayıt seçin!")
            return
        
        reply = QMessageBox.question(
            self.parent,
            'Envanter Kaydı Silme Onayı',
            'Seçili envanter kaydını silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.inventory_table.removeRow(current_row)
            
    def add_item_to_inventory_table(self, row, col, value):
        """Envanter tablosuna bir hücre ekler ve formatlar"""
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        
        # Kritik seviye için renklendirme
        if col == 4 and int(value) > 0:  # Kritik seviye sütunu
            item.setBackground(QBrush(QColor("#f44336")))
            item.setForeground(QBrush(QColor("white")))
        
        self.inventory_table.setItem(row, col, item) 