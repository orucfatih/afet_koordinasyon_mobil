"""
Ekip yönetimi paneli
"""
from PyQt5.QtWidgets import (
    # Layout widgets
    QWidget, QVBoxLayout, QHBoxLayout,
    # Container widgets
    QGroupBox, QTableWidget, QTableWidgetItem,
    # Basic widgets
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    # Dialog related
    QDialog, QMessageBox, QDialogButtonBox,
    # Form widgets
    QFormLayout, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Local imports
from sample_data import TEAM_DATA
from styles.styles_dark import *
from styles.styles_light import *
from .op_constant import (
    TEAM_TABLE_HEADERS, EXPERTISE_OPTIONS, TEAM_STATUS_OPTIONS,
    FILTER_ALL_TEXT, EQUIPMENT_STATUS_OPTIONS
)
from .op_utils import get_icon_path
from .op_dialogs import create_team_dialog
from message.message_ui import MessageDialog, ContactItem

class TeamManagementPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        self.load_team_data()

    def initUI(self):
        """Panel arayüzünü oluşturur"""
        # Ana layout
        team_list_layout = QVBoxLayout()
        
        # Tablo widget'ını oluştur
        self.team_list = QTableWidget()
        self.team_list.setColumnCount(len(TEAM_TABLE_HEADERS))
        self.team_list.setHorizontalHeaderLabels(TEAM_TABLE_HEADERS)
        self.team_list.setStyleSheet(TABLE_WIDGET_STYLE)
        
        # Durum sütununa tıklama olayını bağla
        self.team_list.cellClicked.connect(self.handle_cell_click)
        
        # Filtre Paneli
        filter_panel = QWidget()
        filter_layout = QHBoxLayout(filter_panel)
        
        # Kurum Filtresi
        self.institution_filter = QComboBox()
        self.institution_filter.addItem("Tüm Kurumlar")
        self.institution_filter.setStyleSheet(COMBOBOX_STYLE)
        self.institution_filter.currentTextChanged.connect(self.apply_filters)
        
        # Durum Filtresi
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tüm Durumlar", "Müsait", "Meşgul"])
        self.status_filter.setStyleSheet(COMBOBOX_STYLE)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        
        # Uzmanlık Filtresi
        self.expertise_filter = QComboBox()
        self.expertise_filter.addItem("Tüm Uzmanlıklar")
        self.expertise_filter.addItems(EXPERTISE_OPTIONS)
        self.expertise_filter.setStyleSheet(COMBOBOX_STYLE)
        self.expertise_filter.currentTextChanged.connect(self.apply_filters)
        
        # Filtreleri layout'a ekle
        filter_layout.addWidget(QLabel("Kurum:"))
        filter_layout.addWidget(self.institution_filter)
        filter_layout.addWidget(QLabel("Durum:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(QLabel("Uzmanlık:"))
        filter_layout.addWidget(self.expertise_filter)
        
        # Alt butonlar için container
        bottom_buttons = QHBoxLayout()
        
        # Ekip Ekleme Butonu
        add_team_btn = QPushButton(" Yeni Ekip Ekle")
        add_team_btn.setIcon(QIcon(get_icon_path('add-group.png')))
        add_team_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        add_team_btn.clicked.connect(self.add_new_team)
        
        # Ekip Silme Butonu
        remove_team_btn = QPushButton(" Ekip Sil")
        remove_team_btn.setIcon(QIcon(get_icon_path('delete-group.png')))
        remove_team_btn.setStyleSheet(RED_BUTTON_STYLE)
        remove_team_btn.clicked.connect(self.remove_team)
        
        # Ekip Düzenleme Butonu
        edit_team_btn = QPushButton(" Ekip Düzenle")
        edit_team_btn.setIcon(QIcon(get_icon_path('edit.png')))
        edit_team_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_team_btn.clicked.connect(self.edit_team)
        
        # İletişim Butonu
        contact_button = QPushButton(" Ekip ile İletişime Geç")
        contact_button.clicked.connect(self.contact_team)
        contact_button.setStyleSheet(GREEN_BUTTON_STYLE)
        contact_button.setIcon(QIcon(get_icon_path('customer-service.png')))
        
        # Butonları yatay düzende ekle
        bottom_buttons.addWidget(add_team_btn)
        bottom_buttons.addWidget(edit_team_btn)
        bottom_buttons.addWidget(remove_team_btn)
        bottom_buttons.addWidget(contact_button)
        
        # Widget'ları ana layout'a ekle
        team_list_layout.addWidget(filter_panel)
        team_list_layout.addWidget(self.team_list)
        team_list_layout.addLayout(bottom_buttons)
        
        self.setLayout(team_list_layout)

    def handle_cell_click(self, row, column):
        """Tablo hücresine tıklandığında çalışır"""
        if column == 3:  # Durum sütunu
            item = self.team_list.item(row, column)
            if item:
                current_status = item.text()
                new_status = "Meşgul" if current_status == "Müsait" else "Müsait"
                
                # Yeni durum item'ı oluştur
                new_item = QTableWidgetItem(new_status)
                new_item.setTextAlignment(Qt.AlignCenter)
                new_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                
                # Değişikliği uygula
                self.team_list.setItem(row, column, new_item)

    def load_team_data(self):
        """Örnek ekip verilerini yükler"""
        self.team_list.setRowCount(0)
        
        # Kurumları topla
        institutions = set()
        
        for team in TEAM_DATA:
            institutions.add(team[2])  # Kurum adlarını topla
            row = self.team_list.rowCount()
            self.team_list.insertRow(row)
            
            # Eksik alanları varsayılan değerlerle doldur
            team_data = list(team)
            while len(team_data) < 8:  # Tüm sütunlar için
                if len(team_data) == 5:  # Uzmanlık
                    team_data.append(EXPERTISE_OPTIONS[0])
                elif len(team_data) == 6:  # Personel
                    team_data.append("1")
                elif len(team_data) == 7:  # Ekipman
                    team_data.append(EQUIPMENT_STATUS_OPTIONS[0])
            
            for col, data in enumerate(team_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu için salt okunur yap
                if col == 3:  # Durum sütunu
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                
                self.team_list.setItem(row, col, item)
            
            if hasattr(self.parent, 'team_combo'):
                self.parent.team_combo.addItem(f"{team_data[0]} - {team_data[1]} ({team_data[2]})")
        
        # Kurum filtresine kurumları ekle
        self.institution_filter.addItems(sorted(institutions))
        
                # Sütunların eşit boyutta olması için
        header = self.team_list.horizontalHeader()
        for column in range(header.count()):
            header.setSectionResizeMode(column, header.Stretch)

    def add_new_team(self):
        """Yeni ekip eklemek için dialog açar"""
        dialog = create_team_dialog(self, self.save_new_team)
        dialog.exec_()

    def save_new_team(self, dialog, team_id_input, leader_input, institution_input, 
                     status_combo, contact_input, expertise_combo, personnel_count, equipment_combo):
        """Yeni ekibi tabloya kaydeder"""
        data = [
            team_id_input.text(),
            leader_input.text(),
            institution_input.text(),
            status_combo.currentText(),
            contact_input.text(),
            expertise_combo.currentText(),
            str(personnel_count.value()),
            equipment_combo.currentText()
        ]
        
        # Tabloya ekle
        row = self.team_list.rowCount()
        self.team_list.insertRow(row)
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            
            # Durum sütunu için salt okunur yap
            if col == 3:  # Durum sütunu
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            
            self.team_list.setItem(row, col, item)
        
        # Combo box'a da ekle
        if hasattr(self.parent, 'team_combo'):
            self.parent.team_combo.addItem(f"{data[0]} - {data[1]} ({data[2]})")
        
        # Sütunların eşit boyutta olması için
        header = self.team_list.horizontalHeader()
        for column in range(header.count()):
            header.setSectionResizeMode(column, header.Stretch)
            
        dialog.accept()

    def edit_team(self):
        """Seçili ekibi düzenler"""
        selected_items = self.team_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir ekip seçin!")
            return
        
        row = selected_items[0].row()
        
        # Mevcut verileri al ve eksik alanları varsayılan değerlerle doldur
        team_data = []
        for col in range(8):  # Tüm sütunlar
            item = self.team_list.item(row, col)
            if item:
                team_data.append(item.text())
            else:
                # Eksik alanlar için varsayılan değerler
                if col == 5:  # Uzmanlık
                    team_data.append(EXPERTISE_OPTIONS[0])
                elif col == 6:  # Personel
                    team_data.append("1")
                elif col == 7:  # Ekipman
                    team_data.append(EQUIPMENT_STATUS_OPTIONS[0])
                else:
                    team_data.append("")
        
        # Dialog penceresini oluştur
        dialog = create_team_dialog(self, lambda *args: self.save_edited_team(row, *args), team_data)
        dialog.exec_()

    def save_edited_team(self, row, dialog, team_id_input, leader_input, institution_input, 
                        status_combo, contact_input, expertise_combo, personnel_count, equipment_combo):
        """Düzenlenen ekip bilgilerini günceller"""
        # Yeni verileri al
        data = [
            team_id_input.text(),
            leader_input.text(),
            institution_input.text(),
            status_combo.currentText(),
            contact_input.text(),
            expertise_combo.currentText(),
            str(personnel_count.value()),
            equipment_combo.currentText()
        ]
        
        # Tabloyu güncelle
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            
            # Durum sütunu için salt okunur yap
            if col == 3:  # Durum sütunu
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            
            self.team_list.setItem(row, col, item)
        
        # Combo box'ı güncelle
        if hasattr(self.parent, 'team_combo'):
            self.parent.team_combo.setItemText(
                row,
                f"{data[0]} - {data[1]} ({data[2]})"
            )
        
        dialog.accept()

    def remove_team(self):
        """Seçili ekibi siler"""
        selected_items = self.team_list.selectedItems()
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
            team_id = self.team_list.item(row, 0).text()
            
            # Tablodan sil
            self.team_list.removeRow(row)
            
            # Combo box'tan da sil
            if hasattr(self.parent, 'team_combo'):
                for i in range(self.parent.team_combo.count()):
                    if team_id in self.parent.team_combo.itemText(i):
                        self.parent.team_combo.removeItem(i)
                        break

    def contact_team(self):
        """Seçili ekip ile iletişim penceresini açar"""
        selected_items = self.team_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçin!")
            return
            
        row = selected_items[0].row()
        team_id = self.team_list.item(row, 0).text()
        team_leader = self.team_list.item(row, 1).text()
        contact = self.team_list.item(row, 4).text()
        institution = self.team_list.item(row, 2).text()
        
        # Ekip lideri için contact_data oluştur
        leader_data = {
            'id': team_id,
            'name': team_leader,
            'title': f"Ekip Lideri - {institution}",
            'status': '',  # Boş bırakıyorum ileride meşgul müsait durumuna göre renk değiştirilir
            'contact': contact
        }
        
        # Mesajlaşma penceresini aç ve ekip lideriyle sohbeti başlat
        dialog = MessageDialog(self)
        
        # Ekip liderini konuşma listesine ekle ve sohbeti başlat
        item = ContactItem(leader_data)
        dialog.chat_list.addItem(item)
        dialog.current_chat = team_id
        
        # Sistem mesajını ekle
        dialog.chat_messages[team_id] = [
            {
                'sender': 'Sistem',
                'message': f"{team_leader} ({institution}) ile iletişim başlatıldı",
                'type': 'system'
            }
        ]
        
        # Mesaj geçmişini yükle
        dialog.load_chat(item)
        
        dialog.exec_()

    def apply_filters(self):
        """Seçili filtrelere göre ekip listesini filtreler"""
        selected_institution = self.institution_filter.currentText()
        selected_status = self.status_filter.currentText()
        selected_expertise = self.expertise_filter.currentText()
        
        for row in range(self.team_list.rowCount()):
            show_row = True
            institution = self.team_list.item(row, 2).text()
            status = self.team_list.item(row, 3).text()
            expertise = self.team_list.item(row, 5).text() if self.team_list.item(row, 5) else ""
            
            if selected_institution != "Tüm Kurumlar" and institution != selected_institution:
                show_row = False
            if selected_status != "Tüm Durumlar" and status != selected_status:
                show_row = False
            if selected_expertise != "Tüm Uzmanlıklar" and expertise != selected_expertise:
                show_row = False
                
            self.team_list.setRowHidden(row, not show_row) 