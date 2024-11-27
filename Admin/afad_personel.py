from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QMessageBox,
                           QTreeWidget, QTreeWidgetItem, QDialog,
                           QTextBrowser, QListWidget)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor
from sample_data import AFAD_TEAMS
from styles import *

class PersonelDetayDialog(QDialog):
    """Personel detaylarını gösteren dialog"""
    def __init__(self, personel_data, parent=None):
        super().__init__(parent)
        self.personel_data = personel_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Personel Detayları")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # Detay bilgileri
        detay_group = QGroupBox("Kişisel Bilgiler")
        detay_layout = QFormLayout()
        
        fields = [
            ("Ad Soyad:", "name"),
            ("Telefon:", "phone"),
            ("Ev Telefonu:", "home_phone"),
            ("E-posta:", "email"),
            ("Ev Adresi:", "address"),
            ("Ünvan:", "title"),
            ("Uzmanlık:", "specialization"),
            ("Tecrübe (Yıl):", "experience"),
        ]
        
        for label, key in fields:
            value = self.personel_data.get(key, "-")
            text = QLabel(str(value))
            text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            detay_layout.addRow(label, text)
        
        detay_group.setLayout(detay_layout)
        layout.addWidget(detay_group)
        
        # İletişim butonları
        iletisim_group = QGroupBox("Hızlı İletişim")
        iletisim_layout = QHBoxLayout()
        
        ara_btn = QPushButton(" Ara")
        ara_btn.setStyleSheet(BUTTON_STYLE)
        ara_btn.setIcon(QIcon("icons/call.png"))  # Icon eklenebilir
        ara_btn.clicked.connect(lambda: self.ara(self.personel_data["phone"]))
        
        mesaj_btn = QPushButton(" Mesaj Gönder")
        mesaj_btn.setStyleSheet(BUTTON_STYLE)
        mesaj_btn.setIcon(QIcon("icons/message.png"))  # Icon eklenebilir
        mesaj_btn.clicked.connect(lambda: self.mesaj_gonder(self.personel_data["phone"]))
        
        konum_iste_btn = QPushButton(" Konum İste")
        konum_iste_btn.setStyleSheet(BUTTON_STYLE)
        konum_iste_btn.setIcon(QIcon("icons/location.png"))  # Icon eklenebilir
        konum_iste_btn.clicked.connect(lambda: self.konum_iste(self.personel_data["phone"]))
        
        iletisim_layout.addWidget(ara_btn)
        iletisim_layout.addWidget(mesaj_btn)
        iletisim_layout.addWidget(konum_iste_btn)
        
        iletisim_group.setLayout(iletisim_layout)
        layout.addWidget(iletisim_group)
        
        # Notlar
        if self.personel_data.get("notes"):
            notes_group = QGroupBox("Notlar")
            notes_layout = QVBoxLayout()
            notes_text = QTextBrowser()
            notes_text.setText(self.personel_data["notes"])
            notes_layout.addWidget(notes_text)
            notes_group.setLayout(notes_layout)
            layout.addWidget(notes_group)
        
        self.setLayout(layout)
    
    def ara(self, telefon):
        QMessageBox.information(self, "Arama", f"Arama fonksiyonu: {telefon}")
        
    def mesaj_gonder(self, telefon):
        QMessageBox.information(self, "Mesaj", f"Mesaj gönderme fonksiyonu: {telefon}")
        
    def konum_iste(self, telefon):
        QMessageBox.information(self, "Konum", f"Konum isteme fonksiyonu: {telefon}")

class MesajDialog(QDialog):
    """Mesaj gönderme dialog penceresi"""
    def __init__(self, alici, parent=None):
        super().__init__(parent)
        self.alici = alici
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Mesaj Gönder")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.alici_label = QLabel(self.alici)
        form_layout.addRow("Alıcı:", self.alici_label)
        
        self.mesaj_text = QTextEdit()
        form_layout.addRow("Mesaj:", self.mesaj_text)
        
        # Hazır mesaj şablonları
        self.mesaj_sablonlari = QComboBox()
        self.mesaj_sablonlari.addItems([
            "Seçiniz...",
            "Acil durum brifingi için konum bildiriniz",
            "Lütfen mevcut durumunuz hakkında bilgi veriniz",
            "Acil toplantı için merkeze geliniz",
            "Yeni görev için hazır olunuz"
        ])
        self.mesaj_sablonlari.currentTextChanged.connect(self.sablon_sec)
        form_layout.addRow("Şablonlar:", self.mesaj_sablonlari)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        gonder_btn = QPushButton("Gönder")
        gonder_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        gonder_btn.clicked.connect(self.mesaj_gonder)
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)
        iptal_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(gonder_btn)
        buttons_layout.addWidget(iptal_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def sablon_sec(self, text):
        if text != "Seçiniz...":
            self.mesaj_text.setText(text)
    
    def mesaj_gonder(self):
        QMessageBox.information(self, "Başarılı", "Mesaj gönderildi")
        self.accept()

class PersonelYonetimTab(QWidget):
    """Personel Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.ekipler = {}
        self.current_team = None
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        
        # Sol Panel - Ekipler Listesi ve Kurum Özeti
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Arama çubuğu
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Ekip veya personel ara...")
        self.search_box.textChanged.connect(self.filter_teams)
        search_layout.addWidget(self.search_box)
        
        # Filtre combo box
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["AFAD", "STK", "DİĞER"])
        self.filter_combo.currentTextChanged.connect(self.filter_teams)
        search_layout.addWidget(self.filter_combo)
        
        left_layout.addLayout(search_layout)
        
        # Ekipler ağacı
        self.team_tree = QTreeWidget()
        self.team_tree.setStyleSheet(TEAM_TREE_STYLE)
        self.team_tree.setHeaderLabels(["Ekipler ve Personel"])
        self.team_tree.itemClicked.connect(self.show_team_details)
        self.team_tree.itemDoubleClicked.connect(self.show_personnel_details)
        self.team_tree.setAlternatingRowColors(True)
        left_layout.addWidget(self.team_tree)
        
        # Hızlı ekip oluşturma
        quick_team_group = QGroupBox("Hızlı Ekip Oluştur")
        quick_team_layout = QFormLayout()
        
        self.quick_team_name = QLineEdit()
        self.quick_team_type = QComboBox()
        self.quick_team_type.addItems([
            "Arama Kurtarma Ekibi",
            "Sağlık Ekibi",
            "Lojistik Ekibi",
            "İlk Yardım Ekibi",
            "Koordinasyon Ekibi",
            "Teknik Ekip"
        ])
        
        quick_team_layout.addRow("Ekip Adı:", self.quick_team_name)
        quick_team_layout.addRow("Tür:", self.quick_team_type)
        
        create_btn = QPushButton(" Ekip Oluştur")
        create_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        create_btn.setIcon(QIcon('icons/add-group.png'))
        create_btn.clicked.connect(self.quick_create_team)
        quick_team_layout.addRow(create_btn)
        
        quick_team_group.setLayout(quick_team_layout)
        left_layout.addWidget(quick_team_group)
        
        # Orta Panel - Ekip Detayları ve Yönetim
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        
        # Ekip detay kartı
        self.team_info_group = QGroupBox("Ekip Bilgileri")
        team_info_layout = QVBoxLayout()
        
        self.team_info_text = QTextBrowser()
        team_info_layout.addWidget(self.team_info_text)
        
        # Hızlı iletişim butonları
        quick_actions = QHBoxLayout()
        
        mesaj_btn = QPushButton(" Tüm Ekibe Mesaj")
        mesaj_btn.setStyleSheet(BUTTON_STYLE)
        mesaj_btn.setIcon(QIcon('icons/message.png'))
        mesaj_btn.clicked.connect(self.send_team_message)
        
        durum_btn = QPushButton(" Durum Bilgisi İste")
        durum_btn.setStyleSheet(BUTTON_STYLE)
        durum_btn.setIcon(QIcon('icons/share.png'))
        durum_btn.clicked.connect(self.request_team_status)
        
        konum_btn = QPushButton(" Konum Bilgisi İste")
        konum_btn.setStyleSheet(BUTTON_STYLE)
        konum_btn.setIcon(QIcon('icons/location-info.png'))
        konum_btn.clicked.connect(self.request_team_location)
        
        quick_actions.addWidget(mesaj_btn)
        quick_actions.addWidget(durum_btn)
        quick_actions.addWidget(konum_btn)
        
        team_info_layout.addLayout(quick_actions)
        self.team_info_group.setLayout(team_info_layout)
        middle_layout.addWidget(self.team_info_group)
        
        # Personel listesi
        self.personnel_table = QTableWidget()
        self.personnel_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.personnel_table.setColumnCount(8)
        self.personnel_table.setHorizontalHeaderLabels([
            "Ad Soyad", "Telefon", "Ev Telefonu", "E-posta", "Adres", "Ünvan", "Uzmanlık", "Son Güncelleme"
        ])
        self.personnel_table.itemDoubleClicked.connect(self.show_personnel_details_from_table)
        middle_layout.addWidget(self.personnel_table)
        
        # Personel yönetim butonları
        personel_action_layout = QHBoxLayout()
        
        add_personel_btn = QPushButton(" Personel Ekle")
        add_personel_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        add_personel_btn.setIcon(QIcon('icons/add.png'))
        add_personel_btn.clicked.connect(self.add_personnel)
        
        remove_personel_btn = QPushButton(" Personel Çıkar")
        remove_personel_btn.setStyleSheet(RED_BUTTON_STYLE)
        remove_personel_btn.setIcon(QIcon('icons/delete.png'))
        remove_personel_btn.clicked.connect(self.remove_personnel)
        
        edit_personel_btn = QPushButton(" Personel Düzenle")
        edit_personel_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_personel_btn.setIcon(QIcon('icons/custom.png'))
        edit_personel_btn.clicked.connect(self.edit_personnel)
        
        personel_action_layout.addWidget(add_personel_btn)
        personel_action_layout.addWidget(remove_personel_btn)
        personel_action_layout.addWidget(edit_personel_btn)
        
        middle_layout.addLayout(personel_action_layout)
        
        # Ana layout'a panelleri ekleme
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(middle_panel, stretch=2)
        
        self.setLayout(layout)
        
        # Varolan ekipleri yükle
        self.load_teams()

    def show_personnel_details(self, item):
        """Personel detaylarını gösterir"""
        if not item.parent():  # Eğer ekip başlığına tıklandıysa
            team_name = item.text(0)
            if team_name in self.ekipler:
                # Ekip bilgilerini göster
                team_info = self.ekipler[team_name]
                
                # Ekip detay bilgilerini güncelle
                info_text = f"""
                <h3>{team_name}</h3>
                <p><b>Ekip Türü:</b> {team_info.get('type', '-')}</p>
                <p><b>Personel Sayısı:</b> {len(team_info.get('personnel', []))}</p>
                <p><b>Kurum:</b> {team_info.get('status', 'AFAD')}</p>
                """
                self.team_info_text.setHtml(info_text)
                
                # Personel tablosunu güncelle
                self.personnel_table.setRowCount(0)
                for person in team_info.get('personnel', []):
                    row = self.personnel_table.rowCount()
                    self.personnel_table.insertRow(row)
                    self.personnel_table.setItem(row, 0, QTableWidgetItem(person['name']))
                    self.personnel_table.setItem(row, 1, QTableWidgetItem(person.get('phone', '-')))
                    self.personnel_table.setItem(row, 2, QTableWidgetItem(person.get('home_phone', '-')))
                    self.personnel_table.setItem(row, 3, QTableWidgetItem(person.get('email', '-')))
                    self.personnel_table.setItem(row, 4, QTableWidgetItem(person.get('address', '-')))
                    self.personnel_table.setItem(row, 5, QTableWidgetItem(person.get('title', '-')))
                    self.personnel_table.setItem(row, 6, QTableWidgetItem(person.get('specialization', '-')))
                    self.personnel_table.setItem(row, 7, QTableWidgetItem(person.get('last_update', '-')))
                
                # Current team'i güncelle
                self.current_team = team_name
                return

                
        # Personel detaylarını göster
        if ":" in item.text(0):  # Eğer personel satırına tıklandıysa
            personnel_name = item.text(0).split(": ")[1]
            team_name = item.parent().text(0)
            
            # Personel bilgilerini bul
            for person in self.ekipler[team_name]["personnel"]:
                if person["name"] == personnel_name:
                    # Personel detay penceresini göster
                    dialog = PersonelDetayDialog(person, self)
                    dialog.exec_()
                    return

    def send_team_message(self):
        """Tüm ekibe mesaj gönderme"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        team = self.ekipler[self.current_team]
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
        search_text = self.search_box.text().lower()
        filter_status = self.filter_combo.currentText()
        
        # Tüm öğeleri gizle
        for i in range(self.team_tree.topLevelItemCount()):
            team_item = self.team_tree.topLevelItem(i)
            show_team = False
            
            # Ekip adında arama
            if search_text in team_item.text(0).lower():
                show_team = True
            
            # Ekip durumuna göre filtreleme
            if filter_status != "Tüm Ekipler":
                team_name = team_item.text(0)
                if team_name in self.ekipler:
                    team_status = self.ekipler[team_name].get('status', 'AFAD')
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
        """Kaydedilmiş ekipleri yükler"""
        # Örnek veriyi sample_data modülünden al
        self.ekipler = AFAD_TEAMS
        # Ekipleri ağaca ekle
        self.update_team_tree()

    def update_team_tree(self):
        """Ekipler ağacını günceller"""
        self.team_tree.clear()
        
        for team_name, team_data in self.ekipler.items():
            # Ekip başlığı
            team_item = QTreeWidgetItem([team_name])
            team_item.setIcon(0, QIcon("icons/group-users.png"))  # İkon eklenebilir
            
            # Ekip durumuna göre renklendirme
            if team_data.get('status') == "STK/DİĞER":
                team_item.setBackground(0, QColor("#4c9161"))  
            elif team_data.get('status') == "AFAD":
                team_item.setBackground(0, QColor("#4c9161")) 
            
            # Personel listesi
            for person in team_data.get('personnel', []):
                person_item = QTreeWidgetItem([f"Personel: {person['name']}"])
                person_item.setIcon(0, QIcon("icons/person.png"))  # İkon eklenebilir
                team_item.addChild(person_item)
            
            self.team_tree.addTopLevelItem(team_item)
            team_item.setExpanded(True)

    def quick_create_team(self):
        """Hızlı ekip oluşturur"""
        team_name = self.quick_team_name.text().strip()
        team_type = self.quick_team_type.currentText()
        
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen ekip adı girin!")
            return
            
        if team_name in self.ekipler:
            QMessageBox.warning(self, "Uyarı", "Bu isimde bir ekip zaten var!")
            return
        
        # Yeni ekip oluştur
        self.ekipler[team_name] = {
            "type": team_type,
            "status": "AFAD",
            "personnel": []
        }
        
        # Ağacı güncelle
        self.update_team_tree()
        
        # Formu temizle
        self.quick_team_name.clear()
        QMessageBox.information(self, "Başarılı", f"{team_name} ekibi oluşturuldu!")


    def show_team_details(self, item):
        """Ekip detaylarını gösterir"""
        if not item.parent():  # Eğer ekip başlığına tıklandıysa
            team_name = item.text(0)
            if team_name in self.ekipler:
                # Ekip bilgilerini göster
                team_info = self.ekipler[team_name]
                
                # Ekip detay bilgilerini güncelle
                info_text = f"""
                <h3>{team_name}</h3>
                <p><b>Ekip Türü:</b> {team_info.get('type', '-')}</p>
                <p><b>Personel Sayısı:</b> {len(team_info.get('personnel', []))}</p>
                <p><b>Kurum:</b> {team_info.get('status', 'AFAD')}</p>
                """
                self.team_info_text.setHtml(info_text)
                
                # Personel tablosunu güncelle
                self.personnel_table.setRowCount(0)
                for person in team_info.get('personnel', []):
                    row = self.personnel_table.rowCount()
                    self.personnel_table.insertRow(row)
                    self.personnel_table.setItem(row, 0, QTableWidgetItem(person['name']))  # Ad Soyad
                    self.personnel_table.setItem(row, 1, QTableWidgetItem(person.get('phone', '-')))  # Telefon
                    self.personnel_table.setItem(row, 2, QTableWidgetItem(person.get('home_phone', '-')))  # Ev Telefonu
                    self.personnel_table.setItem(row, 3, QTableWidgetItem(person.get('email', '-')))  # E-posta
                    self.personnel_table.setItem(row, 4, QTableWidgetItem(person.get('address', '-')))  # Adres
                    self.personnel_table.setItem(row, 5, QTableWidgetItem(person.get('title', '-')))  # Ünvan
                    self.personnel_table.setItem(row, 6, QTableWidgetItem(person.get('specialization', '-')))  # Uzmanlık
                    self.personnel_table.setItem(row, 7, QTableWidgetItem(person.get('last_update', '-')))  # Son Güncelleme
                
                # Current team'i güncelle
                self.current_team = team_name


    def show_personnel_details_from_table(self, item):
        """Tablodan personel detaylarını gösterir"""
        if not self.current_team:
            return
            
        row = item.row()
        personnel_name = self.personnel_table.item(row, 0).text()
        
        # Personel bilgilerini bul
        team_info = self.ekipler[self.current_team]
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
        
        dialog = PersonelEkleDialog(self.current_team, self)
        if dialog.exec_():
            # Yeni personel bilgilerini al
            new_personnel = dialog.get_personnel_info()
            
            # Ekibe personel ekle
            self.ekipler[self.current_team]['personnel'].append(new_personnel)
            
            # Ekranı güncelle
            self.update_team_tree()
            self.show_team_details(self.team_tree.findItems(self.current_team, Qt.MatchExactly)[0])
            
            QMessageBox.information(self, "Başarılı", f"{new_personnel['name']} ekibe eklendi!")
    
    def remove_personnel(self):
        """Personel çıkarma işlemi"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        # Mevcut personel listesini al
        team_personnel = self.ekipler[self.current_team]['personnel']
        
        if not team_personnel:
            QMessageBox.warning(self, "Uyarı", "Ekipte personel bulunmamaktadır!")
            return
        
        # Personel seçim dialogu
        dialog = PersonelSecDialog(team_personnel, self)
        if dialog.exec_():
            # Seçilen personeli sil
            selected_personnel = dialog.get_selected_personnel()
            
            # Personeli listeden çıkar
            self.ekipler[self.current_team]['personnel'] = [
                p for p in team_personnel if p != selected_personnel
            ]
            
            # Ekranı güncelle
            self.update_team_tree()
            self.show_team_details(self.team_tree.findItems(self.current_team, Qt.MatchExactly)[0])
            
            QMessageBox.information(self, "Başarılı", f"{selected_personnel['name']} ekipten çıkarıldı!")
    
    def edit_personnel(self):
        """Personel bilgilerini düzenleme"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        # Mevcut personel listesini al
        team_personnel = self.ekipler[self.current_team]['personnel']
        
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
                updated_personnel = edit_dialog.get_updated_personnel()
                
                # Listedeki personeli güncelle
                for i, person in enumerate(team_personnel):
                    if person == selected_personnel:
                        team_personnel[i] = updated_personnel
                        break
                
                # Ekranı güncelle
                self.update_team_tree()
                self.show_team_details(self.team_tree.findItems(self.current_team, Qt.MatchExactly)[0])
                
                QMessageBox.information(self, "Başarılı", f"{updated_personnel['name']} bilgileri güncellendi!")






# Yardımcı Dialog Sınıfları
class PersonelEkleDialog(QDialog):
    """Yeni personel ekleme dialog penceresi"""
    def __init__(self, team_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{team_name} - Personel Ekle")
        self.setupUI()
    
    def setupUI(self):
        layout = QFormLayout()
        
        # Giriş alanlarını tanımlama
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.home_phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.title_input = QLineEdit()
        self.specialization_input = QLineEdit()
        self.experience_input = QLineEdit()
        
        # Formdaki her bir satır için etiket ve giriş alanlarını ekleyin
        layout.addRow("Ad Soyad:", self.name_input)
        layout.addRow("Telefon:", self.phone_input)
        layout.addRow("Ev Telefonu:", self.home_phone_input)
        layout.addRow("E-posta:", self.email_input)
        layout.addRow("Ev Adresi:", self.address_input)
        layout.addRow("Ünvan:", self.title_input)
        layout.addRow("Uzmanlık:", self.specialization_input)
        layout.addRow("Tecrübe (Yıl):", self.experience_input)
        
        # Kaydet ve İptal butonları
        btn_layout = QHBoxLayout()
        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.setStyleSheet(BUTTON_STYLE)
        kaydet_btn.setIcon(QIcon('icons/save.png'))
        kaydet_btn.clicked.connect(self.accept)
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)
        iptal_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)
        
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
    
    def collect_personnel_info(self):
        """Personel bilgilerini toplar"""
        return {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "home_phone": self.home_phone_input.text(),
            "email": self.email_input.text(),
            "address": self.address_input.text(),
            "title": self.title_input.text(),
            "specialization": self.specialization_input.text(),
            "experience": self.experience_input.text(),
            "last_update": QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        }

    def get_personnel_info(self):
        """Girilen personel bilgilerini toplar"""
        return self.collect_personnel_info()


class PersonelSecDialog(QDialog):
    """Personel seçim dialog penceresi"""
    def __init__(self, personnel_list, parent=None, edit_mode=False):
        super().__init__(parent)
        self.personnel_list = personnel_list
        self.edit_mode = edit_mode
        self.setWindowTitle("Personel Seç" if not edit_mode else "Personel Düzenle")
        self.setupUI()
    
    def setupUI(self):
        layout = QVBoxLayout()
        
        self.personel_listesi = QListWidget()
        for person in self.personnel_list:
            self.personel_listesi.addItem(f"{person['name']} - {person['title']}")
        
        layout.addWidget(self.personel_listesi)
        
        btn_layout = QHBoxLayout()
        sec_btn = QPushButton("Seç" if not self.edit_mode else "Düzenle")
        sec_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        sec_btn.clicked.connect(self.accept)
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)
        iptal_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(sec_btn)
        btn_layout.addWidget(iptal_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_selected_personnel(self):
        """Seçilen personeli döner"""
        secili_index = self.personel_listesi.currentRow()
        return self.personnel_list[secili_index]

class PersonelDuzenleDialog(QDialog):
    """Personel bilgileri düzenleme dialog penceresi"""
    def __init__(self, personnel, parent=None):
        super().__init__(parent)
        self.personnel = personnel
        self.setWindowTitle("Personel Bilgilerini Düzenle")
        self.setupUI()
    
    def setupUI(self):
        layout = QFormLayout()
        
        # Yeni giriş alanlarını tanımladık
        self.name_input = QLineEdit(self.personnel['name'])
        self.phone_input = QLineEdit(self.personnel.get('phone', ''))
        self.home_phone_input = QLineEdit(self.personnel.get('home_phone', ''))
        self.email_input = QLineEdit(self.personnel.get('email', ''))
        self.address_input = QLineEdit(self.personnel.get('address', ''))
        self.title_input = QLineEdit(self.personnel.get('title', ''))
        self.specialization_input = QLineEdit(self.personnel.get('specialization', ''))
        self.experience_input = QLineEdit(self.personnel.get('experience', ''))
        
        # Mevcut personel bilgilerini alanlarda göstermek için
        layout.addRow("Ad Soyad:", self.name_input)
        layout.addRow("Telefon:", self.phone_input)
        layout.addRow("Ev Telefonu:", self.home_phone_input)
        layout.addRow("E-posta:", self.email_input)
        layout.addRow("Ev Adresi:", self.address_input)
        layout.addRow("Ünvan:", self.title_input)
        layout.addRow("Uzmanlık:", self.specialization_input)
        layout.addRow("Tecrübe (Yıl):", self.experience_input)
        
        # Kurum seçimi için combo box
        self.status_combo = QComboBox()
        status_options = ["AFAD", "STK", "DİĞER"]
        self.status_combo.addItems(status_options)
        current_status_index = status_options.index(self.personnel.get('status', 'AFAD'))
        self.status_combo.setCurrentIndex(current_status_index)
        
        layout.addRow("Kurum:", self.status_combo)
        
        # Kaydet ve İptal butonları
        btn_layout = QHBoxLayout()
        kaydet_btn = QPushButton(" Kaydet")
        kaydet_btn.setStyleSheet(BUTTON_STYLE)
        kaydet_btn.setIcon(QIcon('icons/save.png'))
        kaydet_btn.clicked.connect(GREEN_BUTTON_STYLE)
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)
        iptal_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)
        
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
    
    def collect_personnel_info(self):
        """Güncellenmiş personel bilgilerini toplar"""
        return {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "home_phone": self.home_phone_input.text(),
            "email": self.email_input.text(),
            "address": self.address_input.text(),
            "title": self.title_input.text(),
            "specialization": self.specialization_input.text(),
            "experience": self.experience_input.text(),
            "status": self.status_combo.currentText(),
            "last_location": self.address_input.text(),  # "last_location" yerine "address" bilgisi alındı
            "last_update": QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        }

    def get_updated_personnel(self):
        """Güncellenmiş personel bilgilerini toplar ve geri döner"""
        updated_personnel = self.personnel.copy()
        updated_personnel.update(self.collect_personnel_info())
        return updated_personnel

    


# personel ekle düzeldikten sonra aynı işlemleri personel düzenle dialog sınıfı içinde yap
# ekle kısmına             ("Ad Soyad:", "name"),
                        # ("Telefon:", "phone"),
                        # ("Ev Telefonu:", "home_phone"),
                        # ("E-posta:", "email"),
                        # ("Ev Adresi:", "address"),
                        # ("Ünvan:", "title"),
                        # ("Uzmanlık:", "specialization"),
                        # ("Tecrübe (Yıl):", "experience"),    bunları ekle