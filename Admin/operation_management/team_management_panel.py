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
from PyQt5.QtGui import QIcon, QBrush, QColor

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
# Firebase veritabanı işlemleri için import
from database import get_database_ref, get_storage_bucket
import time
import uuid

class TeamManagementPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # Firebase referanslarını al
        self.teams_ref = get_database_ref('/operations/teams')
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
            team_id_item = self.team_list.item(row, 0)
            
            if item and team_id_item:
                # Firebase ID'sini UserRole'den al
                firebase_id = team_id_item.data(Qt.UserRole)
                current_status = item.text()
                new_status = "Meşgul" if current_status == "Müsait" else "Müsait"
                
                try:
                    # Firebase'deki ekip durumunu güncelle
                    team_ref = self.teams_ref.child(firebase_id)
                    team_ref.update({
                        'status': new_status,
                        'updated_at': time.time()
                    })
                    
                    # Yeni durum item'ı oluştur
                    new_item = QTableWidgetItem(new_status)
                    new_item.setTextAlignment(Qt.AlignCenter)
                    new_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    new_item.setData(Qt.UserRole, firebase_id)  # Firebase ID'sini koru
                    
                    # Duruma göre arka plan rengini ayarla
                    if new_status == "Meşgul":
                        new_item.setBackground(QBrush(QColor("#FF6B6B")))  # Kırmızı
                    else:
                        new_item.setBackground(QBrush(QColor("#6BCB77")))  # Yeşil
                    
                    # Değişikliği uygula
                    self.team_list.setItem(row, column, new_item)
                    
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Durum güncellenirken hata: {str(e)}")

    def load_team_data(self):
        """Firebase'den ekip verilerini yükler"""
        try:
            # Firebase'den ekip verilerini al
            teams_data = self.teams_ref.get()
            
            # Kurumları topla
            self.institution_filter.clear()
            self.institution_filter.addItem("Tüm Kurumlar")
            institutions = set()
            
            if teams_data:
                # Mevcut verileri temizle
                self.team_list.setRowCount(0)
                
                if hasattr(self.parent, 'team_combo'):
                    self.parent.team_combo.clear()
                
                # Firebase verilerini işle
                for firebase_id, team_info in teams_data.items():
                    # Tablo satırı ekle
                    row = self.team_list.rowCount()
                    self.team_list.insertRow(row)
                    
                    # Veri alanları - Kullanıcının tanımladığı ekip ID'sini kullan
                    team_id = team_info.get('team_id', 'İsimsiz Ekip')
                    leader = team_info.get('leader', 'Belirtilmemiş')
                    institution = team_info.get('institution', 'Belirtilmemiş')
                    status = team_info.get('status', 'Müsait')
                    contact = team_info.get('contact', 'Belirtilmemiş')
                    expertise = team_info.get('expertise', EXPERTISE_OPTIONS[0])
                    personnel = str(team_info.get('personnel_count', '1'))
                    equipment = team_info.get('equipment', EQUIPMENT_STATUS_OPTIONS[0])
                    
                    # Kurum listesine ekle
                    institutions.add(institution)
                    
                    # Tablo sütunlarını doldur
                    team_data = [
                        team_id,  # Kullanıcının tanımladığı ekip ID'si
                        leader,
                        institution,
                        status,
                        contact,
                        expertise,
                        personnel,
                        equipment
                    ]
                    
                    for col, data in enumerate(team_data):
                        item = QTableWidgetItem(str(data))
                        item.setTextAlignment(Qt.AlignCenter)
                        
                        # Durum sütunu için salt okunur yap ve arka plan rengini ayarla
                        if col == 3:  # Durum sütunu
                            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                            # Duruma göre arka plan rengini belirle
                            if data == "Meşgul":
                                item.setBackground(QBrush(QColor("#FF6B6B")))  # Kırmızı
                            else:
                                item.setBackground(QBrush(QColor("#6BCB77")))  # Yeşil
                        
                        # Firebase ID'sini gizli veri olarak sakla
                        item.setData(Qt.UserRole, firebase_id)
                        
                        self.team_list.setItem(row, col, item)
                    
                    # Parent'ta team_combo varsa doldur
                    if hasattr(self.parent, 'team_combo'):
                        # Ekip adı olarak kullanıcının tanımladığı ID'yi göster
                        self.parent.team_combo.addItem(f"{team_id} - {leader} ({institution})", firebase_id)
                
                # Kurum filtresine kurumları ekle
                self.institution_filter.addItems(sorted(institutions))
            else:
                # Firebase'de veri yoksa örnek veriye geri dön
                self._load_legacy_team_data()
        
        except Exception as e:
            print(f"Ekip verisi yüklenirken hata: {str(e)}")
            # Hata durumunda örnek veriyi kullan
            self._load_legacy_team_data()
        
        # Sütunların eşit boyutta olması için
        header = self.team_list.horizontalHeader()
        for column in range(header.count()):
            header.setSectionResizeMode(column, header.Stretch)
    
    def _load_legacy_team_data(self):
        """Örnek ekip verilerini yükler (yedek method)"""
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
                
                # Durum sütunu için salt okunur yap ve arka plan rengini ayarla
                if col == 3:  # Durum sütunu
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    # Duruma göre arka plan rengini belirle
                    if data == "Meşgul":
                        item.setBackground(QBrush(QColor("#FF6B6B")))  # Kırmızı
                    else:
                        item.setBackground(QBrush(QColor("#6BCB77")))  # Yeşil
                
                self.team_list.setItem(row, col, item)
            
            if hasattr(self.parent, 'team_combo'):
                self.parent.team_combo.addItem(f"{team_data[0]} - {team_data[1]} ({team_data[2]})")
        
        # Kurum filtresine kurumları ekle
        self.institution_filter.addItems(sorted(institutions))

    def add_new_team(self):
        """Yeni ekip eklemek için dialog açar"""
        dialog = create_team_dialog(self, self.save_new_team)
        dialog.exec_()

    def save_new_team(self, dialog, team_id_input, leader_input, institution_input, 
                     status_combo, contact_input, expertise_combo, personnel_count, equipment_combo):
        """Yeni ekibi Firebase'e kaydeder"""
        # Form verilerini al
        team_id = team_id_input.text().strip()
        leader_name = leader_input.text().strip()
        institution_name = institution_input.text().strip()
        status = status_combo.currentText()
        contact = contact_input.text().strip()
        expertise = expertise_combo.currentText()
        personnel = personnel_count.value()
        equipment = equipment_combo.currentText()
        
        # Boş alan kontrolü
        if not team_id or not leader_name or not institution_name:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen en azından ekip adı, lider ve kurum bilgilerini doldurunuz.")
            return
        
        try:
            # Benzersiz Firebase ID'si oluştur
            firebase_id = str(uuid.uuid4())
            
            # Firebase'e eklenecek ekip verisi
            team_data = {
                'team_id': team_id,  # Kullanıcının girdiği ID
                'leader': leader_name,
                'institution': institution_name,
                'status': status,
                'contact': contact,
                'expertise': expertise,
                'personnel_count': personnel,
                'equipment': equipment,
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            # Firebase'e ekip ekle
            self.teams_ref.child(firebase_id).set(team_data)
            
            # UI'ı güncelle
            row = self.team_list.rowCount()
            self.team_list.insertRow(row)
            
            # Verileri tabloya ekle
            table_data = [
                team_id,
                leader_name,
                institution_name,
                status,
                contact,
                expertise,
                str(personnel),
                equipment
            ]
            
            for col, data in enumerate(table_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu için salt okunur yap ve arka plan rengini ayarla
                if col == 3:  # Durum sütunu
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    # Duruma göre arka plan rengini belirle
                    if data == "Meşgul":
                        item.setBackground(QBrush(QColor("#FF6B6B")))  # Kırmızı
                    else:
                        item.setBackground(QBrush(QColor("#6BCB77")))  # Yeşil
                
                # Firebase ID'sini sakla
                item.setData(Qt.UserRole, firebase_id)
                
                self.team_list.setItem(row, col, item)
            
            # Parent'ta team_combo varsa güncelle
            if hasattr(self.parent, 'team_combo'):
                self.parent.team_combo.addItem(f"{team_id} - {leader_name} ({institution_name})", firebase_id)
            
            # Kurum filtresi güncelleme
            if institution_name not in [self.institution_filter.itemText(i) for i in range(self.institution_filter.count())]:
                self.institution_filter.addItem(institution_name)
            
            # Dialog'u kapat
            dialog.accept()
            
            QMessageBox.information(self, "Başarılı", f"{team_id} ekibi başarıyla eklendi.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ekip eklenirken hata oluştu: {str(e)}")
            
    def edit_team(self):
        """Seçili ekibi düzenlemek için dialog açar"""
        selected_rows = self.team_list.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek bir ekip seçin.")
            return
        
        row = selected_rows[0].row()
        
        # Tüm verileri al
        team_data = []
        for col in range(8):  # 8 sütun var
            item = self.team_list.item(row, col)
            if item:
                team_data.append(item.text())
            else:
                team_data.append("")  # Boş değer
        
        # Firebase ID'sini gizli veri olarak sakla
        firebase_id = None
        if self.team_list.item(row, 0):
            firebase_id = self.team_list.item(row, 0).data(Qt.UserRole)
        
        # Dialog oluştur
        dialog = create_team_dialog(
            self, 
            lambda dialog, *args: self.save_edited_team(row, dialog, *args),
            team_data
        )
        
        # Firebase ID'sini dialog'a ekstra veri olarak ekle
        if firebase_id:
            dialog.setProperty("firebase_id", firebase_id)
            
        dialog.exec_()

    def save_edited_team(self, row, dialog, team_id_input, leader_input, institution_input, 
                        status_combo, contact_input, expertise_combo, personnel_count, equipment_combo):
        """Düzenlenen ekibi Firebase'e kaydeder"""
        # Firebase ID'sini dialog'dan al
        firebase_id = dialog.property("firebase_id")
        if not firebase_id:
            # Firebase ID bulunamazsa, doğrudan QTableWidget'dan al
            team_id_item = self.team_list.item(row, 0)
            if team_id_item:
                firebase_id = team_id_item.data(Qt.UserRole)
            else:
                QMessageBox.warning(self, "Uyarı", "Ekip verisi bulunamadı. Firebase ID alınamıyor.")
                return
        
        # Yeni ekip bilgileri
        new_team_id = team_id_input.text().strip()
        leader_name = leader_input.text().strip()
        institution_name = institution_input.text().strip()
        status = status_combo.currentText()
        contact = contact_input.text().strip()
        expertise = expertise_combo.currentText()
        personnel = personnel_count.value()
        equipment = equipment_combo.currentText()
        
        # Boş alan kontrolü
        if not new_team_id or not leader_name or not institution_name:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen en azından ekip adı, lider ve kurum bilgilerini doldurunuz.")
            return
        
        try:
            print(f"Ekip güncelleniyor. Firebase ID: {firebase_id}")
            # Firebase'e güncellenecek ekip verisi
            team_data = {
                'team_id': new_team_id,
                'leader': leader_name,
                'institution': institution_name,
                'status': status,
                'contact': contact,
                'expertise': expertise,
                'personnel_count': personnel,
                'equipment': equipment,
                'updated_at': time.time()
            }
            
            # Firebase'deki ekibi güncelle
            self.teams_ref.child(firebase_id).update(team_data)
            
            # UI'ı güncelle
            table_data = [
                new_team_id,  # Kullanıcı tanımlı ID
                leader_name,
                institution_name,
                status,
                contact,
                expertise,
                str(personnel),
                equipment
            ]
            
            for col, data in enumerate(table_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu için salt okunur yap ve arka plan rengini ayarla
                if col == 3:  # Durum sütunu
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    # Duruma göre arka plan rengini belirle
                    if data == "Meşgul":
                        item.setBackground(QBrush(QColor("#FF6B6B")))  # Kırmızı
                    else:
                        item.setBackground(QBrush(QColor("#6BCB77")))  # Yeşil
                
                # Firebase ID'sini koru
                item.setData(Qt.UserRole, firebase_id)
                
                self.team_list.setItem(row, col, item)
            
            # Parent'ta team_combo varsa güncelle
            if hasattr(self.parent, 'team_combo'):
                for i in range(self.parent.team_combo.count()):
                    if self.parent.team_combo.itemData(i) == firebase_id:
                        self.parent.team_combo.setItemText(i, f"{new_team_id} - {leader_name} ({institution_name})")
                        break
            
            # Kurum filtresi güncelleme
            if institution_name not in [self.institution_filter.itemText(i) for i in range(self.institution_filter.count())]:
                self.institution_filter.addItem(institution_name)
            
            # Dialog'u kapat
            dialog.accept()
            
            QMessageBox.information(self, "Başarılı", f"{new_team_id} ekibi başarıyla güncellendi.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ekip güncellenirken hata oluştu: {str(e)}")

    def remove_team(self):
        """Seçili ekibi siler"""
        selected_rows = self.team_list.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bir ekip seçin.")
            return
        
        row = selected_rows[0].row()
        team_id_item = self.team_list.item(row, 0)
        if not team_id_item:
            QMessageBox.warning(self, "Uyarı", "Ekip verisi bulunamadı.")
            return
            
        # Kullanıcı tanımlı ekip ID'si ve Firebase ID'si
        team_name = team_id_item.text()
        firebase_id = team_id_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, 'Ekip Silme Onayı',
            f"{team_name} ekibini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Firebase'den ekibi sil
                self.teams_ref.child(firebase_id).delete()
                
                # UI'ı güncelle
                self.team_list.removeRow(row)
                
                # Parent'ta team_combo varsa güncelle
                if hasattr(self.parent, 'team_combo'):
                    for i in range(self.parent.team_combo.count()):
                        if self.parent.team_combo.itemData(i) == firebase_id:
                            self.parent.team_combo.removeItem(i)
                            break
                
                QMessageBox.information(self, "Başarılı", f"{team_name} ekibi başarıyla silindi.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ekip silinirken hata oluştu: {str(e)}")

    def contact_team(self):
        """Seçili ekiple iletişim kurmak için mesaj penceresini açar"""
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

    def update_team_list(self, teams_data):
        """Parent tarafından çağrılan ekip verilerini güncelleme metodu"""
        try:
            # teams_data bir dictionary veya liste olabilir
            if isinstance(teams_data, dict):
                # Firebase formatındaki veriyi kullan
                self.load_team_data()
            else:
                # Eski veri formatını kullan
                self._load_legacy_team_data()
                
        except Exception as e:
            print(f"Ekip verileri güncellenirken hata: {str(e)}")
            self._load_legacy_team_data()

    def apply_filters(self):
        """Filtreleri uygular"""
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