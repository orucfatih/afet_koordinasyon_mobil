from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QMessageBox,
                           QTreeWidget, QTreeWidgetItem, QDialog,
                           QTextBrowser, QListWidget, QMenu)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor
from sample_data import AFAD_TEAMS
from styles.styles_dark import *
from styles.styles_light import *

from .data_manager import PersonnelDataManager
from .personnel_ui import PersonnelUI
from .personnel_dialogs import (PersonelDetayDialog, MesajDialog, 
                              PersonelEkleDialog, PersonelDuzenleDialog,
                              PersonelSecDialog, PersonnelFormFields)
from .constants import PERSONNEL_TABLE_HEADERS, TEAM_STATUS, INSTITUTIONS
from database import db
from firebase_admin import db as firebase_db
from .state_manager import PersonnelStateManager

class PersonelYonetimTab(QWidget):
    """Personel Yönetim Sekmesi"""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.data_manager = PersonnelDataManager()
        self.ui = PersonnelUI(self)  # UI sınıfını oluştur
        self.current_team = None  # Seçili ekibi tutacak değişken
        self.setup_ui()
        self.setup_connections()
        self.ui.team_tree.itemClicked.connect(self.on_team_selected)

    def set_current_team(self, team_id):
        PersonnelStateManager.set_current_team(team_id)
    
    def handle_team_selection(self, item):
        # Ekip seçildiğinde çağrılır
        if item and not item.parent():  # Eğer bir üst seviye öğeyse (ekip)
            team_id = self.get_team_id(item.text(0))
            self.set_current_team(team_id)
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Sol Panel - Ekipler Listesi ve Kurum Özeti
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Arama ve filtre layout'u
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.ui.search_box)
        search_layout.addWidget(self.ui.filter_combo)
        left_layout.addLayout(search_layout)
        
        # Ekipler ağacı
        left_layout.addWidget(self.ui.team_tree)
        
        # Hızlı ekip oluşturma
        quick_team_group = QGroupBox("Hızlı Ekip Oluştur")
        quick_team_layout = QFormLayout()
        
        # Ekip adı
        self.quick_team_name = QLineEdit()
        
        # Ekip tipi
        self.quick_team_type = QComboBox()
        self.quick_team_type.addItems([
            "Arama Kurtarma Ekibi",
            "Sağlık Ekibi",
            "Lojistik Ekibi",
            "İlk Yardım Ekibi",
            "Koordinasyon Ekibi",
            "Teknik Ekip"
        ])
        
        # Kurum durumu
        self.quick_team_status = QComboBox()
        self.quick_team_status.addItems(["AFAD", "STK", "DİĞER"])
        
        quick_team_layout.addRow("Ekip Adı:", self.quick_team_name)
        quick_team_layout.addRow("Tür:", self.quick_team_type)
        quick_team_layout.addRow("Kurum Durumu:", self.quick_team_status)
        
        # Butonlar
        button_layout = QHBoxLayout()
        create_btn = QPushButton(" Ekip Oluştur")
        create_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        create_btn.setIcon(QIcon('icons/add-group.png'))
        create_btn.clicked.connect(self.quick_create_team)

        delete_btn = QPushButton(" Ekip Sil")
        delete_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_btn.setIcon(QIcon('icons/delete.png'))
        delete_btn.clicked.connect(self.quick_delete_team)

        button_layout.addWidget(create_btn)
        button_layout.addWidget(delete_btn)
        quick_team_layout.addRow(button_layout)
        
        quick_team_group.setLayout(quick_team_layout)
        left_layout.addWidget(quick_team_group)
        
        # Orta Panel - Ekip Detayları ve Yönetim
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        
        # Ekip detay kartı
        self.team_info_group = QGroupBox("Ekip Bilgileri")
        team_info_layout = QVBoxLayout()
        
        self.team_info = QTextBrowser()
        team_info_layout.addWidget(self.team_info)
        
        # Hızlı iletişim butonları
        quick_actions = QHBoxLayout()
        
        mesaj_btn = QPushButton(" Tüm Ekibe Mesaj")
        mesaj_btn.setStyleSheet(COMMUNICATION_BUTTON_STYLE)
        mesaj_btn.setIcon(QIcon('icons/message.png'))
        mesaj_btn.clicked.connect(self.send_team_message)
        
        durum_btn = QPushButton(" Durum Bilgisi İste")
        durum_btn.setStyleSheet(COMMUNICATION_BUTTON_STYLE)
        durum_btn.setIcon(QIcon('icons/share.png'))
        durum_btn.clicked.connect(self.request_team_status)
        
        konum_btn = QPushButton(" Konum Bilgisi İste")
        konum_btn.setStyleSheet(COMMUNICATION_BUTTON_STYLE)
        konum_btn.setIcon(QIcon('icons/location-info.png'))
        konum_btn.clicked.connect(self.request_team_location)
        
        quick_actions.addWidget(mesaj_btn)
        quick_actions.addWidget(durum_btn)
        quick_actions.addWidget(konum_btn)
        
        team_info_layout.addLayout(quick_actions)
        self.team_info_group.setLayout(team_info_layout)
        middle_layout.addWidget(self.team_info_group)
        
        # Personel tablosu
        middle_layout.addWidget(self.ui.personnel_table)
        
        # Personel yönetim butonları
        personel_action_layout = QHBoxLayout()
        personel_action_layout.addWidget(self.ui.add_button)
        personel_action_layout.addWidget(self.ui.remove_button)
        personel_action_layout.addWidget(self.ui.edit_button)
        middle_layout.addLayout(personel_action_layout)
        
        # Ana layout'a panelleri ekleme
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(middle_panel, stretch=2)
        
        self.setLayout(layout)
        
        # Varolan ekipleri yükle
        self.load_teams()

    def setup_connections(self):
        # UI bileşenlerinin sinyallerini bağla
        self.ui.add_button.clicked.connect(self.add_personnel)
        self.ui.edit_button.clicked.connect(self.edit_personnel)
        self.ui.remove_button.clicked.connect(self.remove_personnel)
        self.ui.team_tree.itemClicked.connect(self.show_team_details)
        self.ui.team_tree.itemDoubleClicked.connect(self.show_personnel_details)
        self.ui.personnel_table.itemDoubleClicked.connect(self.show_personnel_details_from_table)
        self.ui.search_box.textChanged.connect(self.filter_teams)
        self.ui.filter_combo.currentTextChanged.connect(self.filter_teams)
        
        # Context menu bağlantısı
        self.ui.personnel_table.customContextMenuRequested.connect(self.show_context_menu)

    def display_team_details(self, team_name):
        """Belirtilen ekibin detaylarını gösterir."""
        try:
            # Ekip ID'sini bul
            teams_ref = firebase_db.reference('/teams')
            teams_data = teams_ref.get() or {}
            found_team_id = None
            team_data = None
            
            for team_id, data in teams_data.items():
                if isinstance(data, dict) and data.get('name') == team_name:
                    found_team_id = team_id
                    team_data = data
                    break
            
            if not found_team_id or not team_data:
                QMessageBox.warning(self, "Hata", f"{team_name} ekibi bulunamadı!")
                return
            
            # Ekip ID'sini state'e kaydet
            PersonnelStateManager.set_current_team(found_team_id)
            
            # Ekip detay bilgilerini güncelle
            info_text = f"""
            <h3>{team_name}</h3>
            <p><b>Ekip Türü:</b> {team_data.get('type', 'Belirtilmemiş')}</p>
            <p><b>Ekip ID:</b> {found_team_id}</p>
            <p><b>Kurum:</b> {team_data.get('status', 'AFAD')}</p>
            <p><b>Oluşturulma Tarihi:</b> {team_data.get('created_at', 'Belirtilmemiş')}</p>
            """
            
            if 'location' in team_data:
                info_text += f"<p><b>Konum:</b> {team_data.get('location', '')}</p>"
                
            if 'latitude' in team_data and 'longitude' in team_data:
                info_text += f"<p><b>Koordinatlar:</b> {team_data.get('latitude', '')}, {team_data.get('longitude', '')}</p>"
            
            # Personel sayısı
            members_count = 0
            if 'members' in team_data:
                members = team_data['members']
                if isinstance(members, list):
                    members_count = len(members)
                elif isinstance(members, dict):
                    members_count = len(members.keys())
                
            info_text += f"<p><b>Personel Sayısı:</b> {members_count}</p>"
            
            self.team_info.setHtml(info_text)
            
            # Personel tablosunu güncelle
            self.ui.personnel_table.setRowCount(0)
            
            if 'members' in team_data:
                members = team_data['members']
                if isinstance(members, list):
                    # Liste formatındaki members
                    for member in members:
                        row = self.ui.personnel_table.rowCount()
                        self.ui.personnel_table.insertRow(row)
                        
                        # Türkçe alan adları için
                        self.ui.personnel_table.setItem(row, 0, QTableWidgetItem(member.get('adSoyad', member.get('name', '-'))))
                        self.ui.personnel_table.setItem(row, 1, QTableWidgetItem(member.get('telefon', member.get('phone', '-'))))
                        self.ui.personnel_table.setItem(row, 2, QTableWidgetItem(member.get('evTelefonu', member.get('home_phone', '-'))))
                        self.ui.personnel_table.setItem(row, 3, QTableWidgetItem(member.get('ePosta', member.get('email', '-'))))
                        self.ui.personnel_table.setItem(row, 4, QTableWidgetItem(member.get('adres', member.get('address', '-'))))
                        self.ui.personnel_table.setItem(row, 5, QTableWidgetItem(member.get('unvan', member.get('title', '-'))))
                        self.ui.personnel_table.setItem(row, 6, QTableWidgetItem(member.get('uzmanlik', member.get('specialization', '-'))))
                        self.ui.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('sonGuncelleme', member.get('last_update', '-'))))
                
                elif isinstance(members, dict):
                    # Sözlük formatındaki members
                    for member_id, member in members.items():
                        row = self.ui.personnel_table.rowCount()
                        self.ui.personnel_table.insertRow(row)
                        
                        self.ui.personnel_table.setItem(row, 0, QTableWidgetItem(member.get('name', '-')))
                        self.ui.personnel_table.setItem(row, 1, QTableWidgetItem(member.get('phone', '-')))
                        self.ui.personnel_table.setItem(row, 2, QTableWidgetItem(member.get('home_phone', '-')))
                        self.ui.personnel_table.setItem(row, 3, QTableWidgetItem(member.get('email', '-')))
                        self.ui.personnel_table.setItem(row, 4, QTableWidgetItem(member.get('address', '-')))
                        self.ui.personnel_table.setItem(row, 5, QTableWidgetItem(member.get('title', '-')))
                        self.ui.personnel_table.setItem(row, 6, QTableWidgetItem(member.get('specialization', '-')))
                        self.ui.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('last_update', '-')))
            
        except Exception as e:
            print(f"Ekip detayları gösterme hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", f"Ekip detayları gösterilirken hata oluştu: {str(e)}")

    def show_personnel_details(self, item):
        """Personel detaylarını veya ekip bilgilerini gösterir."""
        try:
            if not item.parent():  # Ekip başlığına tıklandıysa
                team_name = item.text(0)
                # Ekip seçilmiş olarak işaretle ve detayları göster
                current_team_id = item.data(0, Qt.UserRole)
                if current_team_id:
                    # Ekip ID'si varsa kullan
                    PersonnelStateManager.set_current_team(current_team_id)
                else:
                    # Yoksa ekip adına göre ara
                    teams_ref = firebase_db.reference('/teams')
                    teams_data = teams_ref.get() or {}
                    
                    for team_id, team_data in teams_data.items():
                        if isinstance(team_data, dict) and team_data.get('name') == team_name:
                            PersonnelStateManager.set_current_team(team_id)
                            break
                
                # Ekip detaylarını göster
                self.on_team_selected(item)
            else:  # Personel satırına tıklandıysa
                personnel_name = item.text(0)
                team_item = item.parent()
                team_name = team_item.text(0)
                
                # Mevcut ekip ID'sini al
                current_team_id = PersonnelStateManager.get_current_team()
                if not current_team_id:
                    # Ekip ID'sini almaya çalış
                    team_id = team_item.data(0, Qt.UserRole)
                    if team_id:
                        current_team_id = team_id
                    else:
                        # Ekip adından bul
                        teams_ref = firebase_db.reference('/teams')
                        teams_data = teams_ref.get() or {}
                        
                        for id, data in teams_data.items():
                            if isinstance(data, dict) and data.get('name') == team_name:
                                current_team_id = id
                                break
                                
                if not current_team_id:
                    QMessageBox.warning(self, "Hata", "Ekip bilgisi bulunamadı!")
                    return
                                
                # Firebase'den ekip verilerini al
                teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
                team_data = teams_ref.get()
                
                if not team_data or 'members' not in team_data:
                    QMessageBox.warning(self, "Hata", "Personel bilgisi bulunamadı!")
                    return
                    
                # Personeli bul
                personnel_data = None
                
                members = team_data['members']
                if isinstance(members, list):
                    for member in members:
                        if member.get('adSoyad', '') == personnel_name or member.get('name', '') == personnel_name:
                            # Türkçe alanları İngilizce karşılıklarına çevir
                            personnel_data = {
                                'name': member.get('adSoyad', member.get('name', '')),
                                'phone': member.get('telefon', member.get('phone', '')),
                                'home_phone': member.get('evTelefonu', member.get('home_phone', '')),
                                'email': member.get('ePosta', member.get('email', '')),
                                'address': member.get('adres', member.get('address', '')),
                                'title': member.get('unvan', member.get('title', '')),
                                'specialization': member.get('uzmanlik', member.get('specialization', '')),
                                'experience': member.get('tecrube', member.get('experience', '')),
                                'status': team_data.get('status', 'AFAD')
                            }
                            break
                elif isinstance(members, dict):
                    for member_id, member in members.items():
                        if member.get('name', '') == personnel_name:
                            personnel_data = member.copy()  # Kopyasını al
                            personnel_data['status'] = team_data.get('status', 'AFAD')
                            break
                
                if personnel_data:
                    # Personel detay penceresini göster
                    dialog = PersonelDetayDialog(personnel_data, self)
                    dialog.exec_()
                else:
                    QMessageBox.warning(self, "Bilgi", f"{personnel_name} personeline ait detaylı bilgi bulunamadı.")
                    
        except Exception as e:
            print(f"Personel detayları gösterme hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", f"Personel detayları gösterilirken hata oluştu: {str(e)}")

    def show_team_details(self, item):
        """Ekip bilgilerini gösterir."""
        if not item.parent():  # Ekip başlığına tıklandıysa
            team_name = item.text(0)
            self.display_team_details(team_name)

    def send_team_message(self):
        """Tüm ekibe mesaj gönderme"""
        current_team_id = PersonnelStateManager.get_current_team()
        if not current_team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        try:
            # Firebase'den ekip bilgilerini al
            teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
            team_data = teams_ref.get()
            
            if not team_data:
                QMessageBox.warning(self, "Hata", "Ekip bilgileri bulunamadı!")
                return
            
            team_name = team_data.get('name', 'İsimsiz Ekip')
            
            # Mesaj dialogunu göster
            message_dialog = MesajDialog(f"Ekip: {team_name}", self)
            if message_dialog.exec_():
                message_text = message_dialog.mesaj_text.toPlainText()
                
                # Mesajı veritabanına kaydet
                messages_ref = firebase_db.reference('/messages')
                
                import uuid
                from datetime import datetime
                
                message_data = {
                    'team_id': current_team_id,
                    'team_name': team_name,
                    'message': message_text,
                    'type': 'team_message',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'sent'
                }
                
                messages_ref.child(str(uuid.uuid4())).set(message_data)
                
                # Başarı mesajı
                QMessageBox.information(self, "Başarılı", f"{team_name} ekibine mesaj gönderildi!")
                
        except Exception as e:
            print(f"Mesaj gönderme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Mesaj gönderilirken hata oluştu: {str(e)}")

    def request_team_status(self):
        """Ekipten durum bilgisi isteme"""
        current_team_id = PersonnelStateManager.get_current_team()
        if not current_team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        try:
            # Firebase'den ekip bilgilerini al
            teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
            team_data = teams_ref.get()
            
            if not team_data:
                QMessageBox.warning(self, "Hata", "Ekip bilgileri bulunamadı!")
                return
            
            team_name = team_data.get('name', 'İsimsiz Ekip')
            
            # Hazır mesaj metni
            msg = "Lütfen mevcut durumunuz hakkında bilgi veriniz."
            
            # Mesaj dialogunu göster
            dialog = MesajDialog(f"Ekip: {team_name}", self)
            dialog.mesaj_text.setText(msg)
            
            if dialog.exec_():
                message_text = dialog.mesaj_text.toPlainText()
                
                # Durum talebini veritabanına kaydet
                requests_ref = firebase_db.reference('/requests')
                
                import uuid
                from datetime import datetime
                
                request_data = {
                    'team_id': current_team_id,
                    'team_name': team_name,
                    'message': message_text,
                    'type': 'status_request',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'pending'
                }
                
                requests_ref.child(str(uuid.uuid4())).set(request_data)
                
                # Başarı mesajı
                QMessageBox.information(self, "Başarılı", f"{team_name} ekibinden durum bilgisi istendi!")
                
        except Exception as e:
            print(f"Durum talebi hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Durum bilgisi istenirken hata oluştu: {str(e)}")

    def request_team_location(self):
        """Ekipten konum bilgisi isteme"""
        current_team_id = PersonnelStateManager.get_current_team()
        if not current_team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        try:
            # Firebase'den ekip bilgilerini al
            teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
            team_data = teams_ref.get()
            
            if not team_data:
                QMessageBox.warning(self, "Hata", "Ekip bilgileri bulunamadı!")
                return
            
            team_name = team_data.get('name', 'İsimsiz Ekip')
            
            # Hazır mesaj metni
            msg = "Acil durum brifingi için konum bildiriniz."
            
            # Mesaj dialogunu göster
            dialog = MesajDialog(f"Ekip: {team_name}", self)
            dialog.mesaj_text.setText(msg)
            
            if dialog.exec_():
                message_text = dialog.mesaj_text.toPlainText()
                
                # Konum talebini veritabanına kaydet
                requests_ref = firebase_db.reference('/requests')
                
                import uuid
                from datetime import datetime
                
                request_data = {
                    'team_id': current_team_id,
                    'team_name': team_name,
                    'message': message_text,
                    'type': 'location_request',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'pending'
                }
                
                requests_ref.child(str(uuid.uuid4())).set(request_data)
                
                # Başarı mesajı
                QMessageBox.information(self, "Başarılı", f"{team_name} ekibinden konum bilgisi istendi!")
                
        except Exception as e:
            print(f"Konum talebi hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Konum bilgisi istenirken hata oluştu: {str(e)}")

    def filter_teams(self):
        """Ekipleri ve personeli arama kutusuna göre filtreler"""
        try:
            search_text = self.ui.search_box.text().lower()
            filter_status = self.ui.filter_combo.currentText()
            
            # Tüm öğeleri gizle/göster mantığıyla çalışır
            for i in range(self.ui.team_tree.topLevelItemCount()):
                team_item = self.ui.team_tree.topLevelItem(i)
                team_name = team_item.text(0)
                show_team = False
                
                # Ekip adında arama
                if search_text in team_name.lower():
                    show_team = True
                
                # Ekip durumuna göre filtreleme (Firebase'den ekip durumu alınmalı)
                if filter_status == "Tümü":  # Tümü seçiliyse hepsini göster
                    pass  # show_team durumunu korur
                else:
                    # Ekip ID'sini bulma
                    found_team_id = None
                    teams_ref = firebase_db.reference('/teams')
                    teams_data = teams_ref.get() or {}
                    
                    for team_id, team_data in teams_data.items():
                        if isinstance(team_data, dict) and team_data.get('name') == team_name:
                            team_status = team_data.get('status', 'AFAD')
                            
                            if filter_status != team_status:
                                show_team = False
                            break
                
                # Personel içinde arama
                for j in range(team_item.childCount()):
                    person_item = team_item.child(j)
                    if search_text in person_item.text(0).lower():
                        show_team = True  # Ekibi de göster
                        person_item.setHidden(False)
                    else:
                        person_item.setHidden(search_text != '')  # Arama varsa gizle, yoksa göster
                
                team_item.setHidden(not show_team and search_text != '')  # Arama yoksa tüm ekipleri göster
                
        except Exception as e:
            print(f"Ekip filtreleme hatası: {str(e)}")

    def load_teams(self):
        """Firebase'den ekipleri yükler"""
        try:
            print("Loading teams...")
            teams_ref = firebase_db.reference('/teams')
            
            teams_data = teams_ref.get()
            
            
            if teams_data:
                self.ui.team_tree.clear()
                for team_id, team_data in teams_data.items():
                    # Ekip başlığı
                    team_name = team_data['name'] if isinstance(team_data, dict) else str(team_data)
                    team_item = QTreeWidgetItem([team_name])
                    team_item.setIcon(0, QIcon("icons/group-users.png"))
                    
                    # Üyeleri ekle
                    if isinstance(team_data, dict) and 'members' in team_data:
                        members = team_data['members']
                        if isinstance(members, list):
                            # Liste formatındaki üyeler
                            for member in members:
                                member_name = member.get('adSoyad', member.get('name', ''))
                                member_item = QTreeWidgetItem([member_name])
                                member_item.setIcon(0, QIcon("icons/user.png"))
                                team_item.addChild(member_item)
                        elif isinstance(members, dict):
                            # Dictionary formatındaki üyeler
                            for member_id, member in members.items():
                                member_name = member.get('name', '')
                                member_item = QTreeWidgetItem([member_name])
                                member_item.setIcon(0, QIcon("icons/user.png"))
                                team_item.addChild(member_item)
                    
                    self.ui.team_tree.addTopLevelItem(team_item)
                return True
                
            else:
                QMessageBox.warning(self, "Uyarı", "Hiç ekip bulunamadı!")
                return False
                
        except Exception as e:
            print(f"Error loading teams: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Ekipler yüklenirken hata oluştu: {str(e)}")
            return False
    def on_team_selected(self, item):
        try:
            team_item = item if not item.parent() else item.parent()
            team_name = team_item.text(0)
            
            teams_ref = firebase_db.reference('/teams')
            teams_data = teams_ref.get()
            
            for team_id, team_data in teams_data.items():
                if team_data.get('name') == team_name:
                    # Ekip detayları
                    self.team_info.setText(f"""
                        Ekip Adı: {team_data.get('name', '')}
                        Ekip ID: {team_data.get('Ekip_ID', '')}
                        Konum: {team_data.get('location', '')}
                        Tip: {team_data.get('type', '')}
                        Durum: {team_data.get('status', '')}
                        Enlem: {team_data.get('latitude', '')}
                        Boylam: {team_data.get('longtidute', '')}
                    """)
                    
                    # Personel tablosunu temizle
                    self.ui.personnel_table.setRowCount(0)
                    
                    members = team_data.get('members', {})
                    if isinstance(members, list):
                        for member in members:
                            row = self.ui.personnel_table.rowCount()
                            self.ui.personnel_table.insertRow(row)
                            self.ui.personnel_table.setItem(row, 0, QTableWidgetItem(member.get('adSoyad', '')))
                            self.ui.personnel_table.setItem(row, 1, QTableWidgetItem(member.get('telefon', '')))
                            self.ui.personnel_table.setItem(row, 2, QTableWidgetItem(member.get('evTelefonu', '')))
                            self.ui.personnel_table.setItem(row, 3, QTableWidgetItem(member.get('ePosta', '')))
                            self.ui.personnel_table.setItem(row, 4, QTableWidgetItem(member.get('adres', '')))
                            self.ui.personnel_table.setItem(row, 5, QTableWidgetItem(member.get('title', '-')))
                            self.ui.personnel_table.setItem(row, 6, QTableWidgetItem(member.get('specialization', '-')))
                            self.ui.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('last_update', '-')))
                    
                    elif isinstance(members, dict):
                        for member_id, member in members.items():
                            row = self.ui.personnel_table.rowCount()
                            self.ui.personnel_table.insertRow(row)
                            self.ui.personnel_table.setItem(row, 0, QTableWidgetItem(member.get('name', '')))
                            self.ui.personnel_table.setItem(row, 1, QTableWidgetItem(member.get('phone', '')))
                            self.ui.personnel_table.setItem(row, 2, QTableWidgetItem('-'))
                            self.ui.personnel_table.setItem(row, 3, QTableWidgetItem('-'))
                            self.ui.personnel_table.setItem(row, 4, QTableWidgetItem('-'))
                            self.ui.personnel_table.setItem(row, 5, QTableWidgetItem('-'))
                            self.ui.personnel_table.setItem(row, 6, QTableWidgetItem('-'))
                            self.ui.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('last_update', '')))
                    
                    PersonnelStateManager.set_current_team(team_id)
                    return
                    
        except Exception as e:
            print(f"Error displaying team/member details: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Detaylar gösterilirken hata oluştu: {str(e)}")

    def update_team_tree(self):
        """Ekip ağacını günceller"""
        try:
            self.ui.team_tree.clear()
            
            # Firebase'den ekipleri al
            teams_ref = firebase_db.reference('/teams')
            teams_data = teams_ref.get() or {}
            
            # Her ekip için bir öğe oluştur
            for team_id, team_data in teams_data.items():
                if not isinstance(team_data, dict):
                    continue
                    
                # Ekip başlığı
                team_name = team_data.get('name', 'İsimsiz Ekip')
                team_item = QTreeWidgetItem([team_name])
                team_item.setIcon(0, QIcon("icons/group-users.png"))
                team_item.setData(0, Qt.UserRole, team_id)  # Ekip ID'sini gizli veri olarak sakla
                
                # Ekip durumuna göre renklendirme
                team_status = team_data.get('status', 'AFAD')
                if team_status == "STK":
                    team_item.setBackground(0, QColor("#9fdfaf"))  # Açık yeşil
                elif team_status == "DİĞER":
                    team_item.setBackground(0, QColor("#dfcf9f"))  # Açık sarı
                elif team_status == "AFAD":
                    team_item.setBackground(0, QColor("#9fbfdf"))  # Açık mavi
                
                # Personel listesi
                if 'members' in team_data:
                    members = team_data['members']
                    
                    if isinstance(members, list):
                        # Liste tipindeki üyeler
                        for member in members:
                            member_name = member.get('adSoyad', member.get('name', ''))
                            if member_name:  # Boş isim kontrolü
                                person_item = QTreeWidgetItem([member_name])
                                person_item.setIcon(0, QIcon("icons/user.png"))
                                team_item.addChild(person_item)
                    
                    elif isinstance(members, dict):
                        # Dictionary tipindeki üyeler
                        for member_id, member in members.items():
                            member_name = member.get('name', '')
                            if member_name:  # Boş isim kontrolü
                                person_item = QTreeWidgetItem([member_name])
                                person_item.setIcon(0, QIcon("icons/user.png"))
                                person_item.setData(0, Qt.UserRole, member_id)  # Üye ID'sini gizli veri olarak sakla
                                team_item.addChild(person_item)
                
                # Ekip öğesini ağaca ekle
                self.ui.team_tree.addTopLevelItem(team_item)
                
            # İlk ekibi otomatik olarak seç
            if self.ui.team_tree.topLevelItemCount() > 0:
                first_team = self.ui.team_tree.topLevelItem(0)
                self.ui.team_tree.setCurrentItem(first_team)
                self.on_team_selected(first_team)
                
        except Exception as e:
            print(f"Ekip ağacı güncelleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Ekip ağacı güncellenirken hata oluştu: {str(e)}")

    def quick_create_team(self):
        """Hızlı ekip oluşturur"""
        team_name = self.quick_team_name.text().strip()
        team_type = self.quick_team_type.currentText()
        team_status = self.quick_team_status.currentText()
        
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen ekip adı girin!")
            return
        
        try:
            # Firebase'den tüm ekipleri kontrol et
            teams_ref = firebase_db.reference('/teams')
            teams_data = teams_ref.get() or {}
            
            # Ekip adını kontrol et (aynı isimli ekip var mı?)
            for _, team_data in teams_data.items():
                if isinstance(team_data, dict) and team_data.get('name') == team_name:
                    QMessageBox.warning(self, "Uyarı", "Bu isimde bir ekip zaten var!")
                    return
            
            # Benzersiz bir ID oluştur
            import uuid
            from datetime import datetime
            
            new_team_id = str(uuid.uuid4())
            
            # Yeni ekip verisini hazırla
            new_team_data = {
                'name': team_name,
                'type': team_type,
                'status': team_status,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'members': []  # Boş üye listesi
            }
            
            # Firebase'e ekip ekle
            teams_ref.child(new_team_id).set(new_team_data)
            
            # Formu temizle
            self.quick_team_name.clear()
            
            # Ekipleri yeniden yükle
            self.load_teams()
            
            QMessageBox.information(self, "Başarılı", f"{team_name} ekibi başarıyla oluşturuldu!")
            
        except Exception as e:
            print(f"Ekip oluşturma hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Ekip oluşturulurken hata oluştu: {str(e)}")

    def show_personnel_details_from_table(self, item):
        """Tablodan personel detaylarını gösterir"""
        try:
            row = item.row()
            if row < 0:
                return
                
            personnel_name = self.ui.personnel_table.item(row, 0).text()
            
            # Mevcut ekip ID'sini al
            current_team_id = PersonnelStateManager.get_current_team()
            if not current_team_id:
                QMessageBox.warning(self, "Hata", "Ekip bilgisi bulunamadı!")
                return
            
            # Firebase'den ekip verilerini al
            teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
            team_data = teams_ref.get()
            
            if not team_data:
                QMessageBox.warning(self, "Hata", "Ekip verileri bulunamadı!")
                return
                
            # Personeli bul
            personnel_data = None
            
            if 'members' in team_data:
                members = team_data['members']
                
                if isinstance(members, list):
                    # Liste formatındaki üyeler
                    for member in members:
                        if member.get('adSoyad', '') == personnel_name or member.get('name', '') == personnel_name:
                            # Türkçe alanları İngilizce karşılıklarına çevir
                            personnel_data = {
                                'name': member.get('adSoyad', member.get('name', '')),
                                'phone': member.get('telefon', member.get('phone', '')),
                                'home_phone': member.get('evTelefonu', member.get('home_phone', '')),
                                'email': member.get('ePosta', member.get('email', '')),
                                'address': member.get('adres', member.get('address', '')),
                                'title': member.get('unvan', member.get('title', '')),
                                'specialization': member.get('uzmanlik', member.get('specialization', '')),
                                'experience': member.get('tecrube', member.get('experience', '')),
                                'status': team_data.get('status', 'AFAD')
                            }
                            break
                elif isinstance(members, dict):
                    # Dictionary formatındaki üyeler
                    for member_id, member in members.items():
                        if member.get('name', '') == personnel_name:
                            personnel_data = member
                            break
            
            if personnel_data:
                # Personel detay penceresini göster
                dialog = PersonelDetayDialog(personnel_data, self)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Bilgi", f"{personnel_name} personeline ait detaylı bilgi bulunamadı.")
                
        except Exception as e:
            print(f"Personel detayı gösterme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Personel detayları gösterilirken hata oluştu: {str(e)}")

    def add_personnel(self):
        """Personel ekleme işlemi"""
        # Ekip seçili mi kontrol et
        current_team_id = PersonnelStateManager.get_current_team()
        if not current_team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        # Firebase'den ekip verisini kontrol et
        teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
        team_data = teams_ref.get()
        
        if not team_data:
            QMessageBox.warning(self, "Hata", "Seçili ekibin verileri bulunamadı!")
            return
        
        dialog = PersonelEkleDialog(self)
        if dialog.exec_():
            # Personel eklendi, ekranı güncelle
            self.load_teams()
            # Eğer mevcut bir seçim varsa, o ekibi tekrar seç
            if self.ui.team_tree.topLevelItemCount() > 0:
                for i in range(self.ui.team_tree.topLevelItemCount()):
                    team_item = self.ui.team_tree.topLevelItem(i)
                    if team_data.get('name') == team_item.text(0):
                        self.ui.team_tree.setCurrentItem(team_item)
                        self.on_team_selected(team_item)
                        break

    def remove_personnel(self):
        """Seçili personeli siler"""
        try:
            # Seçili satırı kontrol et
            current_row = self.ui.personnel_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen çıkarılacak personeli seçin!")
                return
                
            # Personel adını al
            personnel_name = self.ui.personnel_table.item(current_row, 0).text()
            if not personnel_name:
                QMessageBox.warning(self, "Uyarı", "Personel ismi alınamadı!")
                return
            
            # Ekip ID'sini kontrol et
            current_team_id = PersonnelStateManager.get_current_team()
            if not current_team_id:
                QMessageBox.warning(self, "Hata", "Ekip bilgisi bulunamadı! Lütfen önce bir ekip seçin.")
                return
            
            # Onay iste
            reply = QMessageBox.question(
                self, 
                'Personel Sil', 
                f'{personnel_name} personelini silmek istediğinize emin misiniz?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Firebase referansı
                db_ref = firebase_db.reference(f'/teams/{current_team_id}')
                team_data = db_ref.get()
                
                if not team_data:
                    QMessageBox.warning(self, "Hata", "Ekip verileri bulunamadı!")
                    return
                
                if 'members' not in team_data:
                    QMessageBox.warning(self, "Hata", "Bu ekipte hiç personel bulunamadı!")
                    return
                
                members = team_data['members']
                
                # Veri yapısına göre silme işlemi gerçekleştir
                if isinstance(members, list):
                    # Liste yapısındaki üyeleri filtrele
                    new_members = []
                    found = False
                    
                    for member in members:
                        # Türkçe veya İngilizce isimle eşleştir
                        if (member.get('adSoyad', '') != personnel_name and 
                            member.get('name', '') != personnel_name):
                            new_members.append(member)
                        else:
                            found = True
                    
                    if found:
                        # Güncellenmiş listeyi kaydet
                        db_ref.update({'members': new_members})
                        QMessageBox.information(self, "Başarılı", f"{personnel_name} personeli silindi!")
                    else:
                        QMessageBox.warning(self, "Uyarı", f"{personnel_name} personeli bulunamadı!")
                        
                elif isinstance(members, dict):
                    # Dict yapısındaki üyelerde ID bul
                    member_to_delete = None
                    for member_id, member in members.items():
                        if member.get('name') == personnel_name:
                            member_to_delete = member_id
                            break
                    
                    if member_to_delete:
                        # ID ile personeli sil
                        db_ref.child('members').child(member_to_delete).delete()
                        QMessageBox.information(self, "Başarılı", f"{personnel_name} personeli silindi!")
                    else:
                        QMessageBox.warning(self, "Uyarı", f"{personnel_name} personeli bulunamadı!")
                else:
                    QMessageBox.warning(self, "Hata", "Personel verileri uygun formatta değil!")
                    return
                
                # Ekranı güncelle
                self.load_teams()
                
                # Eğer mevcut bir ekip seçiliyse, onu tekrar seç
                if self.ui.team_tree.topLevelItemCount() > 0:
                    found = False
                    for i in range(self.ui.team_tree.topLevelItemCount()):
                        team_item = self.ui.team_tree.topLevelItem(i)
                        if team_item.data(0, Qt.UserRole) == current_team_id:
                            self.ui.team_tree.setCurrentItem(team_item)
                            self.on_team_selected(team_item)
                            found = True
                            break
                    
                    # ID ile bulunamadıysa ekip adıyla ara
                    if not found and team_data.get('name'):
                        for i in range(self.ui.team_tree.topLevelItemCount()):
                            team_item = self.ui.team_tree.topLevelItem(i)
                            if team_item.text(0) == team_data.get('name'):
                                self.ui.team_tree.setCurrentItem(team_item)
                                self.on_team_selected(team_item)
                                break
                    
        except Exception as e:
            print(f"Personel silme hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Hata", f"Personel silinirken hata oluştu: {str(e)}")

    def edit_personnel(self):
        """Personel bilgilerini düzenleme"""
        # Seçili personeli kontrol et
        current_row = self.ui.personnel_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz personeli seçin!")
            return
        
        # Ekip kontrolü
        current_team_id = PersonnelStateManager.get_current_team()
        if not current_team_id:
            QMessageBox.warning(self, "Hata", "Ekip bilgisi bulunamadı!")
            return
        
        # Seçili personel bilgilerini al
        personnel_name = self.ui.personnel_table.item(current_row, 0).text()
        personnel_phone = self.ui.personnel_table.item(current_row, 1).text()
        
        # Firebase'den personel bilgilerini al
        teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
        team_data = teams_ref.get()
        
        if not team_data or 'members' not in team_data:
            QMessageBox.warning(self, "Hata", "Ekip personel verileri bulunamadı!")
            return
            
        # Personeli bul
        members = team_data['members']
        personnel_data = None
        
        if isinstance(members, list):
            for member in members:
                if member.get('adSoyad', '') == personnel_name or member.get('name', '') == personnel_name:
                    # Türkçe alanları İngilizce karşılıklarına çevir
                    personnel_data = {
                        'name': member.get('adSoyad', member.get('name', '')),
                        'phone': member.get('telefon', member.get('phone', '')),
                        'home_phone': member.get('evTelefonu', member.get('home_phone', '')),
                        'email': member.get('ePosta', member.get('email', '')),
                        'address': member.get('adres', member.get('address', '')),
                        'title': member.get('unvan', member.get('title', '')),
                        'specialization': member.get('uzmanlik', member.get('specialization', '')),
                        'experience': member.get('tecrube', member.get('experience', '')),
                        'status': team_data.get('status', 'AFAD')
                    }
                    break
        elif isinstance(members, dict):
            for member_id, member in members.items():
                if member.get('name', '') == personnel_name:
                    personnel_data = member
                    personnel_data['status'] = team_data.get('status', 'AFAD')
                    break
        
        if not personnel_data:
            QMessageBox.warning(self, "Hata", f"{personnel_name} personeli bulunamadı!")
            return
        
        # Düzenleme dialogunu göster
        edit_dialog = PersonelDuzenleDialog(personnel_data, self)
        if edit_dialog.exec_():
            # Personel düzenlendi, ekranı güncelle
            self.load_teams()
            # Eğer mevcut bir ekip seçiliyse, onu tekrar seç
            current_item = self.ui.team_tree.currentItem()
            if current_item:
                self.on_team_selected(current_item)

    def quick_delete_team(self):
        """Hızlı ekip silme"""
        team_name = self.quick_team_name.text().strip()
        
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz ekibin adını girin!")
            return
        
        try:
            # Firebase'den tüm ekipleri kontrol et
            teams_ref = firebase_db.reference('/teams')
            teams_data = teams_ref.get() or {}
            
            # Silinecek ekibi bul
            found_team_id = None
            found_team_name = None
            
            for team_id, team_data in teams_data.items():
                if isinstance(team_data, dict) and team_data.get('name') == team_name:
                    found_team_id = team_id
                    found_team_name = team_data.get('name')
                    break
            
            if not found_team_id:
                QMessageBox.warning(self, "Uyarı", "Bu isimde bir ekip bulunamadı!")
                return
            
            # Silme onayı
            reply = QMessageBox.question(
                self, 
                "Ekip Silme Onayı", 
                f"{found_team_name} ekibini silmek istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Firebase'den ekibi sil
                teams_ref.child(found_team_id).delete()
                
                # Formu temizle
                self.quick_team_name.clear()
                
                # Ekipleri yeniden yükle
                self.load_teams()
                
                QMessageBox.information(self, "Başarılı", f"{found_team_name} ekibi silindi!")
                
        except Exception as e:
            print(f"Ekip silme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Ekip silinirken hata oluştu: {str(e)}")

    def refresh_view(self):
        """Ekranı günceller"""
        # Ekipler ağacını güncelle
        self.update_team_tree()
        
        # Eğer bir ekip seçiliyse, ekip detaylarını güncelle
        if hasattr(self, 'current_team') and self.current_team:
            # Seçili ekibi bul
            items = self.ui.team_tree.findItems(self.current_team, Qt.MatchExactly)
            if items:
                self.show_team_details(items[0])

    def show_context_menu(self, position):
        """Sağ tık menüsünü gösterir"""
        menu, actions = self.ui.create_context_menu(position)
        
        # Seçili satırı al
        row = self.ui.personnel_table.currentRow()
        if row >= 0:
            action = menu.exec_(self.ui.personnel_table.mapToGlobal(position))
            if action == actions['detay']:
                self.show_personnel_details_from_table(self.ui.personnel_table.item(row, 0))
            elif action == actions['duzenle']:
                self.edit_personnel()
            elif action == actions['sil']:
                self.remove_personnel()
            elif action == actions['mesaj']:
                self.send_message_to_personnel(row)
            elif action == actions['konum']:
                self.request_personnel_location(row)

    def send_message_to_personnel(self, row):
        """Seçili personele mesaj gönderir"""
        try:
            # Personel bilgilerini al
            personnel_name = self.ui.personnel_table.item(row, 0).text()
            
            # Mevcut ekip ID'sini al
            current_team_id = PersonnelStateManager.get_current_team()
            if not current_team_id:
                QMessageBox.warning(self, "Hata", "Ekip bilgisi bulunamadı!")
                return
            
            # Firebase'den ekip verilerini al
            teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
            team_data = teams_ref.get()
            
            if not team_data:
                QMessageBox.warning(self, "Hata", "Ekip verileri bulunamadı!")
                return
            
            # Personel ID veya bilgisini bul
            personnel_id = None
            
            if 'members' in team_data:
                members = team_data['members']
                
                if isinstance(members, dict):
                    # Dict formatındaki üyeler
                    for member_id, member in members.items():
                        if member.get('name') == personnel_name:
                            personnel_id = member_id
                            break
                elif isinstance(members, list):
                    # Liste formatındaki üyeler
                    for i, member in enumerate(members):
                        if member.get('adSoyad', '') == personnel_name or member.get('name', '') == personnel_name:
                            personnel_id = f"index_{i}"  # Liste indeksi
                            break
            
            if not personnel_id:
                QMessageBox.warning(self, "Hata", f"'{personnel_name}' personeli bulunamadı!")
                return
            
            # Mesaj dialogunu göster
            dialog = MesajDialog(f"Personel: {personnel_name}", self)
            if dialog.exec_():
                message_text = dialog.mesaj_text.toPlainText()
                
                # Mesajı veritabanına kaydet
                messages_ref = firebase_db.reference('/personnel_messages')
                
                import uuid
                from datetime import datetime
                
                message_data = {
                    'team_id': current_team_id,
                    'personnel_id': personnel_id,
                    'personnel_name': personnel_name,
                    'message': message_text,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'sent'
                }
                
                messages_ref.child(str(uuid.uuid4())).set(message_data)
                
                QMessageBox.information(self, "Başarılı", f"{personnel_name} personeline mesaj gönderildi!")
        
        except Exception as e:
            print(f"Personele mesaj gönderme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Mesaj gönderilirken hata oluştu: {str(e)}")

    def request_personnel_location(self, row):
        """Seçili personelden konum bilgisi ister"""
        try:
            # Personel bilgilerini al
            personnel_name = self.ui.personnel_table.item(row, 0).text()
            
            # Mevcut ekip ID'sini al
            current_team_id = PersonnelStateManager.get_current_team()
            if not current_team_id:
                QMessageBox.warning(self, "Hata", "Ekip bilgisi bulunamadı!")
                return
            
            # Firebase'den ekip verilerini al
            teams_ref = firebase_db.reference(f'/teams/{current_team_id}')
            team_data = teams_ref.get()
            
            if not team_data:
                QMessageBox.warning(self, "Hata", "Ekip verileri bulunamadı!")
                return
            
            # Personel ID veya bilgisini bul
            personnel_id = None
            
            if 'members' in team_data:
                members = team_data['members']
                
                if isinstance(members, dict):
                    # Dict formatındaki üyeler
                    for member_id, member in members.items():
                        if member.get('name') == personnel_name:
                            personnel_id = member_id
                            break
                elif isinstance(members, list):
                    # Liste formatındaki üyeler
                    for i, member in enumerate(members):
                        if member.get('adSoyad', '') == personnel_name or member.get('name', '') == personnel_name:
                            personnel_id = f"index_{i}"  # Liste indeksi
                            break
            
            if not personnel_id:
                QMessageBox.warning(self, "Hata", f"'{personnel_name}' personeli bulunamadı!")
                return
                
            # Hazır mesaj metni
            msg = "Acil durum brifingi için konum bildiriniz."
            
            # Mesaj dialogunu göster
            dialog = MesajDialog(f"Personel: {personnel_name}", self)
            dialog.mesaj_text.setText(msg)
            
            if dialog.exec_():
                message_text = dialog.mesaj_text.toPlainText()
                
                # Konum talebini veritabanına kaydet
                requests_ref = firebase_db.reference('/personnel_requests')
                
                import uuid
                from datetime import datetime
                
                request_data = {
                    'team_id': current_team_id,
                    'personnel_id': personnel_id,
                    'personnel_name': personnel_name,
                    'message': message_text,
                    'type': 'location_request',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'pending'
                }
                
                requests_ref.child(str(uuid.uuid4())).set(request_data)
                
                QMessageBox.information(self, "Başarılı", f"{personnel_name} personelinden konum bilgisi istendi!")
        
        except Exception as e:
            print(f"Personelden konum isteme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Konum bilgisi istenirken hata oluştu: {str(e)}")

