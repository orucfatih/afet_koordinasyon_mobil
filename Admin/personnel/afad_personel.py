from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QMessageBox,
                           QTreeWidget, QTreeWidgetItem, QDialog,
                           QTextBrowser, QListWidget, QMenu)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor
from sample_data import AFAD_TEAMS
from styles_dark import *
from styles_light import *

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
        if team_name in self.data_manager.ekipler:
            # Ekip bilgilerini al
            team_info = self.data_manager.ekipler[team_name]
            
            # Ekip detay bilgilerini güncelle
            info_text = f"""
            <h3>{team_name}</h3>
            <p><b>Ekip Türü:</b> {team_info.get('type', '-')}</p>
            <p><b>Personel Sayısı:</b> {len(team_info.get('personnel', []))}</p>
            <p><b>Kurum:</b> {team_info.get('status', 'AFAD')}</p>
            """
            self.team_info.setHtml(info_text)
            
            # Personel tablosunu güncelle
            self.ui.personnel_table.setRowCount(0)
            for person in team_info.get('personnel', []):
                row = self.ui.personnel_table.rowCount()
                self.ui.personnel_table.insertRow(row)
                self.ui.personnel_table.setItem(row, 0, QTableWidgetItem(person['name']))  # Ad Soyad
                self.ui.personnel_table.setItem(row, 1, QTableWidgetItem(person.get('phone', '-')))  # Telefon
                self.ui.personnel_table.setItem(row, 2, QTableWidgetItem(person.get('home_phone', '-')))  # Ev Telefonu
                self.ui.personnel_table.setItem(row, 3, QTableWidgetItem(person.get('email', '-')))  # E-posta
                self.ui.personnel_table.setItem(row, 4, QTableWidgetItem(person.get('address', '-')))  # Adres
                self.ui.personnel_table.setItem(row, 5, QTableWidgetItem(person.get('title', '-')))  # Ünvan
                self.ui.personnel_table.setItem(row, 6, QTableWidgetItem(person.get('specialization', '-')))  # Uzmanlık
                self.ui.personnel_table.setItem(row, 7, QTableWidgetItem(person.get('last_update', '-')))  # Son Güncelleme
            
            # Current team'i güncelle
            self.current_team = team_name

    def show_personnel_details(self, item):
        """Personel detaylarını veya ekip bilgilerini gösterir."""
        if not item.parent():  # Ekip başlığına tıklandıysa
            team_name = item.text(0)
            self.display_team_details(team_name)
        elif ":" in item.text(0):  # Personel satırına tıklandıysa
            personnel_name = item.text(0).split(": ")[1]
            team_name = item.parent().text(0)
            for person in self.data_manager.ekipler[team_name]["personnel"]:
                if person["name"] == personnel_name:
                    dialog = PersonelDetayDialog(person, self)
                    dialog.exec_()
                    return

    def show_team_details(self, item):
        """Ekip bilgilerini gösterir."""
        if not item.parent():  # Ekip başlığına tıklandıysa
            team_name = item.text(0)
            self.display_team_details(team_name)

    def send_team_message(self):
        """Tüm ekibe mesaj gönderme"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        team = self.data_manager.ekipler[self.current_team]
        message_dialog = MesajDialog(f"Ekip: {self.current_team}", self)
        if message_dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{self.current_team} ekibine mesaj gönderildi!")

    def request_team_status(self):
        """Ekipten durum bilgisi isteme"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        msg = "Lütfen mevcut durumunuz hakkında bilgi veriniz."
        dialog = MesajDialog(f"Ekip: {self.current_team}", self)
        dialog.mesaj_text.setText(msg)
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{self.current_team} ekibinden durum bilgisi istendi!")

    def request_team_location(self):
        """Ekipten konum bilgisi isteme"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        msg = "Acil durum brifingi için konum bildiriniz."
        dialog = MesajDialog(f"Ekip: {self.current_team}", self)
        dialog.mesaj_text.setText(msg)
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{self.current_team} ekibinden konum bilgisi istendi!")

    def filter_teams(self):
        """Ekipleri ve personeli arama kutusuna göre filtreler"""
        search_text = self.ui.search_box.text().lower()
        filter_status = self.ui.filter_combo.currentText()
        
        # Tüm öğeleri gizle
        for i in range(self.ui.team_tree.topLevelItemCount()):
            team_item = self.ui.team_tree.topLevelItem(i)
            show_team = False
            
            # Ekip adında arama
            if search_text in team_item.text(0).lower():
                show_team = True
            
            # Ekip durumuna göre filtreleme
            if filter_status == "Tümü":  # Tümü seçiliyse hepsini göster
                show_team = True
            else:  # Belirli bir durum seçiliyse sadece o duruma ait ekipleri göster
                team_name = team_item.text(0)
                if team_name in self.data_manager.ekipler:
                    team_status = self.data_manager.ekipler[team_name].get('status', 'AFAD')
                    if filter_status != team_status:
                        show_team = False
            
            # Personel içinde arama
            for j in range(team_item.childCount()):
                person_item = team_item.child(j)
                if search_text in person_item.text(0).lower():
                    show_team = True
                    person_item.setHidden(False)
                else:
                    person_item.setHidden(True)
            
            team_item.setHidden(not show_team)

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
                            self.ui.personnel_table.setItem(row, 5, QTableWidgetItem(member.get('unvan', '')))
                            self.ui.personnel_table.setItem(row, 6, QTableWidgetItem(member.get('uzmanlik', '')))
                            self.ui.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('sonGuncelleme', '')))
                    
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
       
         
        self.ui.team_tree.clear()

        for team_id, team_data in self.data_manager.ekipler.items():
            # Ekip başlığı
            team_name = team_data.get('name', 'İsimsiz Ekip')
            team_item = QTreeWidgetItem([team_name])
            team_item.setIcon(0, QIcon("icons/group-users.png"))

            # Ekip durumuna göre renklendirme
            team_status = team_data.get('status', 'AFAD')
            if team_status == "STK/DİĞER":
                team_item.setBackground(0, QColor("#4c9161"))
            elif team_status == "AFAD":
                team_item.setBackground(0, QColor("#4c9161"))

            # Personel listesi
            if 'members' in team_data:
                for member in team_data['members']:
                    person_item = QTreeWidgetItem([member.get('name', '')])
                    person_item.setIcon(0, QIcon("icons/user.png"))
                    team_item.addChild(person_item)

            self.ui.team_tree.addTopLevelItem(team_item)
    def quick_create_team(self):
        """Hızlı ekip oluşturur"""
        team_name = self.quick_team_name.text().strip()
        team_type = self.quick_team_type.currentText()  # Ekip tipi (Örn: AFAD)
        team_status = self.quick_team_status.currentText()  # Kullanıcıdan seçilen kurum durumu
        
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen ekip adı girin!")
            return
            
        if team_name in self.data_manager.ekipler:
            QMessageBox.warning(self, "Uyarı", "Bu isimde bir ekip zaten var!")
            return
        
        # Yeni ekip oluştur
        self.data_manager.ekipler[team_name] = {
            "type": team_type,
            "status": team_status,  # Seçilen kurum durumu
            "personnel": []
        }
        
        # Ağacı güncelle
        self.update_team_tree()
        
        # Formu temizle
        self.quick_team_name.clear()
        QMessageBox.information(self, "Başarılı", f"{team_name} ekibi oluşturuldu!")

    def show_personnel_details_from_table(self, item):
        """Tablodan personel detaylarını gösterir"""
        if not self.current_team:
            return
            
        row = item.row()
        personnel_name = self.ui.personnel_table.item(row, 0).text()
        
        # Personel bilgilerini bul
        team_info = self.data_manager.ekipler[self.current_team]
        for person in team_info['personnel']:
            if person['name'] == personnel_name:
                # Personel detay penceresini göster
                dialog = PersonelDetayDialog(person, self)
                dialog.exec_()
                return

    def add_personnel(self):
        """Personel ekleme işlemi"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        dialog = PersonelEkleDialog(self)
        if dialog.exec_():
            self.data_manager.add_personnel(
                self.current_team,
                dialog.get_personnel_data()
            )
            self.refresh_view()

    def remove_personnel(self):
        try:
            current_row = self.ui.personnel_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen çıkarılacak personeli seçin!")
                return
                
            personnel_name = self.ui.personnel_table.item(current_row, 0).text()
            current_team = PersonnelStateManager.get_current_team()
    
            if not current_team:
                QMessageBox.warning(self, "Hata", "Ekip bulunamadı!")
                return
    
            reply = QMessageBox.question(self, 'Personel Sil', 
                                       f'{personnel_name} personelini silmek istediğinize emin misiniz?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Firebase referansı
                db_ref = firebase_db.reference(f'/teams/{current_team}')
                team_data = db_ref.get()
                
                if 'members' in team_data:
                    members = team_data['members']
                    
                    if isinstance(members, list):
                        # Liste tipindeki members için silme
                        new_members = [m for m in members 
                                     if m.get('adSoyad', '') != personnel_name]
                        db_ref.update({'members': new_members})
                        
                    elif isinstance(members, dict):
                        # Dictionary tipindeki members için silme
                        member_to_delete = None
                        for member_id, member in members.items():
                            if member.get('name') == personnel_name:
                                member_to_delete = member_id
                                break
                        
                        if member_to_delete:
                            db_ref.child('members').child(member_to_delete).delete()
    
                    QMessageBox.information(self, "Başarılı", f"{personnel_name} personeli silindi!")
                    self.load_teams()
                    current_item = self.ui.team_tree.currentItem()
                    if current_item:
                        self.on_team_selected(current_item)
                    
        except Exception as e:
            print(f"Silme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Personel silinirken hata oluştu: {str(e)}")
    def edit_personnel(self):
        """Personel bilgilerini düzenleme"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        # Ekip kontrolü
        if self.current_team not in self.data_manager.ekipler:
            QMessageBox.warning(self, "Uyarı", "Seçili ekip artık mevcut değil!")
            self.current_team = None
            return
        
        # Mevcut personel listesini al
        team_personnel = self.data_manager.ekipler[self.current_team]['personnel']
        
        if not team_personnel:
            QMessageBox.warning(self, "Uyarı", "Ekipte personel bulunmamaktadır!")
            return
        
        # Personel seçim dialogu
        dialog = PersonelSecDialog(team_personnel, self, edit_mode=True)
        if dialog.exec_():
            # Seçilen personeli al
            selected_personnel = dialog.get_selected_personnel()
            
            # Personel düzenleme dialogu
            edit_dialog = PersonelDuzenleDialog(selected_personnel, self)
            if edit_dialog.exec_():
                # Güncellenmiş personel bilgilerini al
                updated_personnel = edit_dialog.get_personnel_data()
                
                # Listedeki personeli güncelle
                for i, person in enumerate(team_personnel):
                    if person == selected_personnel:
                        team_personnel[i] = updated_personnel
                        break
                
                # Ekranı güncelle
                self.update_team_tree()
                self.show_team_details(self.ui.team_tree.findItems(self.current_team, Qt.MatchExactly)[0])
                
                QMessageBox.information(self, "Başarılı", f"{updated_personnel['name']} bilgileri güncellendi!")

    def quick_delete_team(self):
        """Hızlı ekip silme"""
        team_name = self.quick_team_name.text().strip()
        
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz ekibin adını girin!")
            return
        
        if team_name not in self.data_manager.ekipler:
            QMessageBox.warning(self, "Uyarı", "Böyle bir ekip bulunmamaktadır!")
            return
        
        # Silme onayı
        reply = QMessageBox.question(
            self, 
            "Ekip Silme Onayı", 
            f"{team_name} ekibini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ekibi sil
            del self.data_manager.ekipler[team_name]
            
            # Ağacı güncelle
            self.update_team_tree()
            
            # Formu temizle
            self.quick_team_name.clear()
            
            QMessageBox.information(self, "Başarılı", f"{team_name} ekibi silindi!")

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
        personnel_name = self.ui.personnel_table.item(row, 0).text()
        dialog = MesajDialog(f"Personel: {personnel_name}", self)
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{personnel_name} personeline mesaj gönderildi!")

    def request_personnel_location(self, row):
        """Seçili personelden konum bilgisi ister"""
        personnel_name = self.ui.personnel_table.item(row, 0).text()
        msg = "Acil durum brifingi için konum bildiriniz."
        dialog = MesajDialog(f"Personel: {personnel_name}", self)
        dialog.mesaj_text.setText(msg)
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{personnel_name} personelinden konum bilgisi istendi!")

