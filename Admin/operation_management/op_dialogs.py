"""
Operation Management modülü için dialog pencereleri
"""
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, 
                           QPushButton, QLabel, QVBoxLayout, QTextEdit,
                           QDialogButtonBox, QHBoxLayout, QSpinBox)
from PyQt5.QtGui import QIcon, QBrush, QColor
from PyQt5.QtCore import Qt

from .op_constant import (TASK_PRIORITIES, TEAM_STATUS_OPTIONS, 
                         EXPERTISE_OPTIONS, EQUIPMENT_STATUS_OPTIONS)
from .op_utils import get_icon_path
from styles.styles_dark import *
from styles.styles_light import *

def create_team_dialog(parent, save_callback, team_data=None):
    """
    Yeni ekip eklemek veya mevcut ekibi düzenlemek için dialog oluşturur
    
    Args:
        parent: Ebeveyn widget
        save_callback: Kaydetme işlemi için callback fonksiyonu
        team_data: Düzenlenecek ekip verisi (düzenleme modunda)
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Ekip Düzenle" if team_data else "Ekip Ekle")
    dialog.setFixedSize(500, 400)

    layout = QFormLayout()

    # Form alanları
    team_id_input = QLineEdit()
    leader_input = QLineEdit()
    institution_input = QLineEdit()
    status_combo = QComboBox()
    status_combo.addItems(TEAM_STATUS_OPTIONS)
    contact_input = QLineEdit()
    
    # Yeni alanlar
    expertise_combo = QComboBox()
    expertise_combo.addItems(EXPERTISE_OPTIONS)
    
    personnel_count = QSpinBox()
    personnel_count.setRange(1, 100)
    personnel_count.setValue(1)
    
    equipment_combo = QComboBox()
    equipment_combo.addItems(EQUIPMENT_STATUS_OPTIONS)

    # Eğer düzenleme modundaysa, mevcut verileri doldur
    if team_data:
        team_id_input.setText(team_data[0])
        leader_input.setText(team_data[1])
        institution_input.setText(team_data[2])
        status_combo.setCurrentText(team_data[3])
        contact_input.setText(team_data[4])
        if len(team_data) > 5:  # Eğer ek veriler varsa
            expertise_combo.setCurrentText(team_data[5] or EXPERTISE_OPTIONS[0])
            personnel_count.setValue(int(team_data[6]) if team_data[6] else 1)
            equipment_combo.setCurrentText(team_data[7] or EQUIPMENT_STATUS_OPTIONS[0])

    # Form alanlarını düzenle
    layout.addRow("Ekip ID:", team_id_input)
    layout.addRow("Ekip Lideri:", leader_input)
    layout.addRow("Kurum:", institution_input)
    layout.addRow("Durum:", status_combo)
    layout.addRow("İletişim:", contact_input)
    layout.addRow("Uzmanlık:", expertise_combo)
    layout.addRow("Personel Sayısı:", personnel_count)
    layout.addRow("Ekipman Durumu:", equipment_combo)

    # Butonlar
    button_box = QDialogButtonBox(
        QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    )
    button_box.accepted.connect(
        lambda: save_callback(dialog, team_id_input, leader_input, 
                            institution_input, status_combo, contact_input,
                            expertise_combo, personnel_count, equipment_combo)
    )
    button_box.rejected.connect(dialog.reject)
    button_box.setStyleSheet(BUTTON_STYLE)

    layout.addRow(button_box)
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
    send_button.setIcon(QIcon(get_icon_path('paper-plane.png')))
    
    layout.addWidget(info_label)
    layout.addWidget(message_input)
    layout.addWidget(send_button)
    
    contact_dialog.setLayout(layout)
    return contact_dialog

def create_task_edit_dialog(parent, item=None, save_callback=None):
    """Görev düzenleme/ekleme dialogu oluşturur"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Görev Düzenle" if item else "Yeni Görev")
    dialog.setMinimumWidth(400)
    
    layout = QVBoxLayout()
    
    task_edit = QTextEdit()
    if item:
        task_edit.setPlainText(item.text())
    
    # Öncelik seçimi için combobox ekle
    priority_layout = QHBoxLayout()
    priority_label = QLabel("Öncelik Seviyesi:")
    priority_combo = QComboBox()
    priority_combo.addItems(TASK_PRIORITIES)
    
    # Mevcut önceliği seç
    if item and item.data(Qt.UserRole):
        priority_combo.setCurrentText(item.data(Qt.UserRole))
    else:
        priority_combo.setCurrentText("Orta (2)")
    
    priority_layout.addWidget(priority_label)
    priority_layout.addWidget(priority_combo)
    
    buttons = QDialogButtonBox(
        QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    )
    
    def on_save():
        if save_callback:
            save_callback(item, task_edit.toPlainText(), dialog, priority_combo.currentText())
    
    buttons.accepted.connect(on_save)
    buttons.rejected.connect(dialog.reject)
    
    layout.addLayout(priority_layout)
    layout.addWidget(task_edit)
    layout.addWidget(buttons)
    
    dialog.setLayout(layout)
    return dialog 