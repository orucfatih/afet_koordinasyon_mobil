from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

def create_status_item(status, status_colors):
    """Durum hücresi oluşturur ve renklendirir"""
    item = QTableWidgetItem(status)
    item.setTextAlignment(Qt.AlignCenter)
    if status in status_colors:
        item.setBackground(QBrush(QColor(status_colors[status])))
    return item

def sync_tables(source_table, target_table, row_mapping):
    """İki tablo arasında senkronizasyon sağlar"""
    for source_row in range(source_table.rowCount()):
        target_row = row_mapping.get(source_row, source_row)
        if target_row >= target_table.rowCount():
            target_table.insertRow(target_row)
        
        for col in range(source_table.columnCount()):
            if source_table.item(source_row, col):
                target_table.setItem(
                    target_row, 
                    col, 
                    QTableWidgetItem(source_table.item(source_row, col).text())
                ) 