import sys
import os

# Ana dizine göreceli yol ekleme
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
                             QGroupBox, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                             QComboBox, QMessageBox, QDialog, QFormLayout, QListWidgetItem, QTabWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from styles_dark import *
from styles_light import *
from sample_data import EQUIPMENT_DATA  # Ekipman verilerini import et

class MessageItem(QListWidgetItem):
    """Özel Mesaj Item Sınıfı"""
    def __init__(self, sender, message, timestamp):
        super().__init__()
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        self.setText(f"{sender} - {timestamp}\n{message}")
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Unchecked)

def create_team_dialog(parent, save_callback):
    """Yeni ekip eklemek için dialog oluşturur"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Ekip Ekle")
    dialog.setFixedSize(400, 300)

    layout = QFormLayout()

    team_id_input = QLineEdit()
    leader_input = QLineEdit()
    institution_input = QLineEdit()
    status_combo = QComboBox()
    status_combo.addItems(["Müsait", "Meşgul"])
    contact_input = QLineEdit()

    save_button = QPushButton(" Kaydet")
    save_button.setIcon(QIcon('icons/save.png'))
    save_button.clicked.connect(
        lambda: save_callback(dialog, team_id_input, leader_input, 
                            institution_input, status_combo, contact_input))
    save_button.setStyleSheet(BUTTON_STYLE)

    layout.addRow("Ekip ID:", team_id_input)
    layout.addRow("Ekip Lideri:", leader_input)
    layout.addRow("Kurum:", institution_input)
    layout.addRow("Durum:", status_combo)
    layout.addRow("İletişim:", contact_input)
    layout.addRow(save_button)

    dialog.setLayout(layout)
    return dialog

def create_contact_dialog(parent, team_id, team_leader, contact):
    """Ekip iletişim dialogu oluşturur"""
    contact_dialog = QDialog(parent)
    contact_dialog.setWindowTitle("Ekip İletişim")
    contact_dialog.setFixedSize(400, 300)
    
    layout = QVBoxLayout()
    
    info_label = QLabel(f"Ekip: {team_id}\nLider: {team_leader}\nİletişim: {contact}")
    info_label.setStyleSheet(DIALOG_INFO_LABEL_STYLE)        

    message_input = QTextEdit()
    message_input.setPlaceholderText("Mesajınızı yazın...")
    message_input.setStyleSheet(TEXT_EDIT_STYLE)
    
    send_button = QPushButton(" Mesaj Gönder")
    send_button.setStyleSheet(GREEN_BUTTON_STYLE)
    send_button.setIcon(QIcon('icons/paper-plane.png'))
    
    layout.addWidget(info_label)
    layout.addWidget(message_input)
    layout.addWidget(send_button)
    
    contact_dialog.setLayout(layout)
    return contact_dialog

def create_task_edit_dialog(parent, current_item, save_callback):
    """Görev düzenleme dialogu oluşturur"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Görev Düzenle")
    dialog.setFixedSize(400, 200)
    
    layout = QVBoxLayout()
    
    task_edit = QTextEdit()
    task_edit.setText(current_item.text())
    task_edit.setStyleSheet(TEXT_EDIT_STYLE)
    
    save_btn = QPushButton(" Kaydet")
    save_btn.setIcon(QIcon('icons/save.png'))
    save_btn.setStyleSheet(GREEN_BUTTON_STYLE)
    save_btn.clicked.connect(lambda: save_callback(current_item, task_edit.toPlainText(), dialog))
    
    layout.addWidget(task_edit)
    layout.addWidget(save_btn)
    
    dialog.setLayout(layout)
    return dialog

class TeamManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Ana pencereye referans
        self.setWindowTitle("Ekip Yönetimi")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.initUI()
        self.load_team_data()  # Mevcut ekip verilerini yükle
        self.load_equipment_data()  # Ekipman verilerini yükle

    def initUI(self):
        layout = QVBoxLayout()
        
        # Ekip detayları ve yönetim seçenekleri
        tabs = QTabWidget()
        
        # Ekip Listesi Tab'ı
        team_list_tab = QWidget()
        team_list_layout = QVBoxLayout(team_list_tab)
        
        self.team_table = QTableWidget()
        self.team_table.setColumnCount(8)
        self.team_table.setHorizontalHeaderLabels([
            "Ekip ID", "Ekip Lideri", "Kurum", "Durum", "İletişim",
            "Uzmanlık", "Personel Sayısı", "Ekipman Durumu"
        ])
        
        # Butonları alt kısma taşı
        team_buttons = QHBoxLayout()
        
        add_team_btn = QPushButton(" Yeni Ekip Ekle")
        add_team_btn.setIcon(QIcon('icons/add-group.png'))
        add_team_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        add_team_btn.clicked.connect(self.add_new_team)
        
        remove_team_btn = QPushButton(" Ekip Sil")
        remove_team_btn.setIcon(QIcon('icons/delete-group.png'))
        remove_team_btn.setStyleSheet(RED_BUTTON_STYLE)
        remove_team_btn.clicked.connect(self.remove_team)
        
        edit_team_btn = QPushButton(" Ekip Bilgilerini Düzenle")
        edit_team_btn.setIcon(QIcon('icons/edit-group.png'))
        edit_team_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_team_btn.clicked.connect(self.edit_team)
        
        team_buttons.addWidget(add_team_btn)
        team_buttons.addWidget(remove_team_btn)
        team_buttons.addWidget(edit_team_btn)
        
        team_list_layout.addWidget(self.team_table)
        team_list_layout.addLayout(team_buttons)  # Butonları tablonun altına ekle
        
        tabs.addTab(team_list_tab, "Ekip Listesi")
        
        # Personel Yönetimi Tab'ı
        personnel_tab = QWidget()
        personnel_layout = QVBoxLayout(personnel_tab)
        
        personnel_buttons = QHBoxLayout()
        add_personnel_btn = QPushButton(" Personel Ekle")
        edit_personnel_btn = QPushButton(" Personel Düzenle")
        remove_personnel_btn = QPushButton(" Personel Çıkar")
        
        personnel_buttons.addWidget(add_personnel_btn)
        personnel_buttons.addWidget(edit_personnel_btn)
        personnel_buttons.addWidget(remove_personnel_btn)
        
        self.personnel_table = QTableWidget()
        self.personnel_table.setColumnCount(6)
        self.personnel_table.setHorizontalHeaderLabels([
            "Ad Soyad", "Görevi", "Uzmanlık", "İletişim",
            "Deneyim (Yıl)", "Durum"
        ])
        
        personnel_layout.addLayout(personnel_buttons)
        personnel_layout.addWidget(self.personnel_table)
        tabs.addTab(personnel_tab, "Personel Yönetimi")
        
        # Ekipman Yönetimi Tab'ı
        equipment_tab = QWidget()
        equipment_layout = QVBoxLayout(equipment_tab)
        
        equipment_buttons = QHBoxLayout()
        add_equipment_btn = QPushButton(" Ekipman Ekle")
        add_equipment_btn.setIcon(QIcon('icons/add-tool.png'))
        add_equipment_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        
        edit_equipment_btn = QPushButton(" Ekipman Düzenle")
        edit_equipment_btn.setIcon(QIcon('icons/edit-tool.png'))
        edit_equipment_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        
        remove_equipment_btn = QPushButton(" Ekipman Çıkar")
        remove_equipment_btn.setIcon(QIcon('icons/delete-tool.png'))
        remove_equipment_btn.setStyleSheet(RED_BUTTON_STYLE)
        
        equipment_buttons.addWidget(add_equipment_btn)
        equipment_buttons.addWidget(edit_equipment_btn)
        equipment_buttons.addWidget(remove_equipment_btn)
        
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Ekipman ID", "Ekipman Adı", "Tür", "Durum",
            "Son Kontrol", "Sorumlu Personel"
        ])
        self.equipment_table.setStyleSheet(TABLE_WIDGET_STYLE)
        
        equipment_layout.addLayout(equipment_buttons)
        equipment_layout.addWidget(self.equipment_table)
        tabs.addTab(equipment_tab, "Ekipman Yönetimi")
        
        # Görev Geçmişi Tab'ı
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Tarih", "Görev Tipi", "Konum", "Süre",
            "Sonuç", "Detaylar"
        ])
        
        history_layout.addWidget(self.history_table)
        tabs.addTab(history_tab, "Görev Geçmişi")
        
        # Ana layout'a sadece tab widget'ı ekle
        layout.addWidget(tabs)
        
        self.setLayout(layout)

    def load_team_data(self):
        """Ana penceredeki ekip verilerini yükler"""
        parent_table = self.parent.team_list
        self.team_table.setRowCount(0)
        
        for row in range(parent_table.rowCount()):
            self.team_table.insertRow(row)
            for col in range(parent_table.columnCount()):
                if parent_table.item(row, col):
                    item = QTableWidgetItem(parent_table.item(row, col).text())
                    if col == 3:  # Durum sütunu için renklendirme
                        if item.text() == "Müsait":
                            item.setBackground(QBrush(QColor("#4CAF50")))
                        else:
                            item.setBackground(QBrush(QColor("#f44336")))
                    self.team_table.setItem(row, col, item)

    def load_equipment_data(self):
        """Örnek ekipman verilerini yükler"""
        self.equipment_table.setRowCount(0)
        
        for equipment in EQUIPMENT_DATA:
            row = self.equipment_table.rowCount()
            self.equipment_table.insertRow(row)
            
            for col, data in enumerate(equipment):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu için renklendirme
                if col == 3:  # Durum sütunu
                    if data == "Aktif":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    elif data == "Bakımda":
                        item.setBackground(QBrush(QColor("#FFA500")))
                    else:  # Onarımda
                        item.setBackground(QBrush(QColor("#f44336")))
                
                self.equipment_table.setItem(row, col, item)
        
        self.equipment_table.resizeColumnsToContents()

    def add_new_team(self):
        """Yeni ekip eklemek için dialog açar"""
        dialog = create_team_dialog(self, self.save_new_team)
        dialog.exec_()
    
    def save_new_team(self, dialog, team_id_input, leader_input, institution_input, status_combo, contact_input):
        """Yeni ekibi her iki tabloya da kaydeder"""
        team_id = team_id_input.text()
        leader = leader_input.text()
        institution = institution_input.text()
        status = status_combo.currentText()
        contact = contact_input.text()
        
        # Dialog tablosuna ekle
        row = self.team_table.rowCount()
        self.team_table.insertRow(row)
        self.team_table.setItem(row, 0, QTableWidgetItem(team_id))
        self.team_table.setItem(row, 1, QTableWidgetItem(leader))
        self.team_table.setItem(row, 2, QTableWidgetItem(institution))
        
        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        if status == "Müsait":
            status_item.setBackground(QBrush(QColor("#4CAF50")))
        else:
            status_item.setBackground(QBrush(QColor("#f44336")))
        self.team_table.setItem(row, 3, status_item)
        
        self.team_table.setItem(row, 4, QTableWidgetItem(contact))
        
        # Ana pencere tablosuna da ekle
        parent_row = self.parent.team_list.rowCount()
        self.parent.team_list.insertRow(parent_row)
        self.parent.team_list.setItem(parent_row, 0, QTableWidgetItem(team_id))
        self.parent.team_list.setItem(parent_row, 1, QTableWidgetItem(leader))
        self.parent.team_list.setItem(parent_row, 2, QTableWidgetItem(institution))
        
        parent_status_item = QTableWidgetItem(status)
        parent_status_item.setTextAlignment(Qt.AlignCenter)
        if status == "Müsait":
            parent_status_item.setBackground(QBrush(QColor("#4CAF50")))
        else:
            parent_status_item.setBackground(QBrush(QColor("#f44336")))
        self.parent.team_list.setItem(parent_row, 3, parent_status_item)
        
        self.parent.team_list.setItem(parent_row, 4, QTableWidgetItem(contact))
        
        # Combo box'a da ekle
        self.parent.team_combo.addItem(f"{team_id} - {leader} ({institution})")
        
        self.team_table.resizeColumnsToContents()
        self.parent.team_list.resizeColumnsToContents()
        dialog.accept()

    def remove_team(self):
        """Seçili ekibi her iki tablodan da siler"""
        selected_items = self.team_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ekip seçin!")
            return
        
        reply = QMessageBox.question(
            self,
            'Ekip Silme Onayı',
            'Seçili ekibi silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            team_id = self.team_table.item(row, 0).text()
            
            # Dialog tablosundan sil
            self.team_table.removeRow(row)
            
            # Ana pencere tablosundan bul ve sil
            for parent_row in range(self.parent.team_list.rowCount()):
                if self.parent.team_list.item(parent_row, 0).text() == team_id:
                    self.parent.team_list.removeRow(parent_row)
                    break
            
            # Combo box'tan da sil
            for i in range(self.parent.team_combo.count()):
                if team_id in self.parent.team_combo.itemText(i):
                    self.parent.team_combo.removeItem(i)
                    break

    def edit_team(self):
        """Seçili ekibi düzenler"""
        selected_items = self.team_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir ekip seçin!")
            return
        
        row = selected_items[0].row()
        dialog = QDialog(self)
        dialog.setWindowTitle("Ekip Düzenle")
        layout = QFormLayout()

        team_id = QLineEdit(self.team_table.item(row, 0).text())
        leader = QLineEdit(self.team_table.item(row, 1).text())
        institution = QLineEdit(self.team_table.item(row, 2).text())
        status_combo = QComboBox()
        status_combo.addItems(["Müsait", "Meşgul"])
        status_combo.setCurrentText(self.team_table.item(row, 3).text())
        contact = QLineEdit(self.team_table.item(row, 4).text())

        layout.addRow("Ekip ID:", team_id)
        layout.addRow("Ekip Lideri:", leader)
        layout.addRow("Kurum:", institution)
        layout.addRow("Durum:", status_combo)
        layout.addRow("İletişim:", contact)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(lambda: self.save_edited_team(
            dialog, row, team_id, leader, institution, status_combo, contact
        ))
        buttons.rejected.connect(dialog.reject)

        layout.addRow(buttons)
        dialog.setLayout(layout)
        dialog.exec_()

    def save_edited_team(self, dialog, row, team_id, leader, institution, status_combo, contact):
        """Düzenlenen ekip bilgilerini her iki tabloda da günceller"""
        # Dialog tablosunu güncelle
        self.team_table.setItem(row, 0, QTableWidgetItem(team_id.text()))
        self.team_table.setItem(row, 1, QTableWidgetItem(leader.text()))
        self.team_table.setItem(row, 2, QTableWidgetItem(institution.text()))
        
        status_item = QTableWidgetItem(status_combo.currentText())
        if status_combo.currentText() == "Müsait":
            status_item.setBackground(QBrush(QColor("#4CAF50")))
        else:
            status_item.setBackground(QBrush(QColor("#f44336")))
        self.team_table.setItem(row, 3, status_item)
        
        self.team_table.setItem(row, 4, QTableWidgetItem(contact.text()))
        
        # Ana pencere tablosunda ilgili satırı bul ve güncelle
        old_team_id = self.team_table.item(row, 0).text()
        for parent_row in range(self.parent.team_list.rowCount()):
            if self.parent.team_list.item(parent_row, 0).text() == old_team_id:
                self.parent.team_list.setItem(parent_row, 0, QTableWidgetItem(team_id.text()))
                self.parent.team_list.setItem(parent_row, 1, QTableWidgetItem(leader.text()))
                self.parent.team_list.setItem(parent_row, 2, QTableWidgetItem(institution.text()))
                
                parent_status_item = QTableWidgetItem(status_combo.currentText())
                if status_combo.currentText() == "Müsait":
                    parent_status_item.setBackground(QBrush(QColor("#4CAF50")))
                else:
                    parent_status_item.setBackground(QBrush(QColor("#f44336")))
                self.parent.team_list.setItem(parent_row, 3, parent_status_item)
                
                self.parent.team_list.setItem(parent_row, 4, QTableWidgetItem(contact.text()))
                
                # Combo box'ı da güncelle
                self.parent.team_combo.setItemText(
                    parent_row,
                    f"{team_id.text()} - {leader.text()} ({institution.text()})"
                )
                break
        
        dialog.accept() 