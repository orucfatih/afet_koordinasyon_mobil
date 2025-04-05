# afad_personel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QComboBox,
                            QGroupBox, QLineEdit, QFormLayout, 
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QTreeWidget, QTreeWidgetItem, QDialog,
                            QTextBrowser, QListWidget)
from PyQt5.QtCore import Qt, QDateTime, QRegExp
from PyQt5.QtGui import QIcon, QColor, QRegExpValidator
from styles.styles_dark import *
from styles.styles_light import *
from .data_manager import DatabaseManager  # Import from data_manager
import sys
import re
import os  # Added for file path operations
import csv  # Added for reading personel.txt
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')  # UTF-8 ayarı

# Örnek şehir ve ilçe verisi
cities_and_districts = {
    "Ankara": ["Çankaya", "Keçiören", "Mamak", "Etimesgut"],
    "İstanbul": ["Kadıköy", "Üsküdar", "Beşiktaş", "Beyoğlu"],
    "İzmir": ["Konak", "Karşıyaka", "Bornova", "Buca"],
}

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
        
        detay_group = QGroupBox("Kişisel Bilgiler")
        detay_layout = QFormLayout()
        
        fields = [
            ("TC:", "TC"),
            ("Ad Soyad:", "adSoyad"),
            ("Telefon:", "telefon"),
            ("Ev Telefonu:", "evTelefonu"),
            ("E-posta:", "ePosta"),
            ("Ev Adresi:", "adres"),
            ("Ünvan:", "unvan"),
            ("Uzmanlık:", "uzmanlik"),
            ("Tecrübe (Yıl):", "tecrube"),
            ("Son Güncelleme:", "sonGuncelleme"),
        ]
        
        for label, key in fields:
            value = self.personel_data.get(key, "-")
            text = QLabel(str(value))
            text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            detay_layout.addRow(label, text)
        
        detay_group.setLayout(detay_layout)
        layout.addWidget(detay_group)
        
        iletisim_group = QGroupBox("Hızlı İletişim")
        iletisim_layout = QHBoxLayout()
        
        ara_btn = QPushButton("Ara")
        ara_btn.setStyleSheet(BUTTON_STYLE)
        ara_btn.setIcon(QIcon('icons/call.png'))
        ara_btn.clicked.connect(lambda: self.ara(self.personel_data.get("telefon", "")))
        
        mesaj_btn = QPushButton("Mesaj Gönder")
        mesaj_btn.setStyleSheet(BUTTON_STYLE)
        mesaj_btn.setIcon(QIcon("icons/message.png"))
        mesaj_btn.clicked.connect(lambda: self.mesaj_gonder(self.personel_data.get("telefon", "")))
        
        konum_iste_btn = QPushButton("Konum İste")
        konum_iste_btn.setStyleSheet(BUTTON_STYLE)
        konum_iste_btn.setIcon(QIcon("icons/location.png"))
        konum_iste_btn.clicked.connect(lambda: self.konum_iste(self.personel_data.get("telefon", "")))
        
        iletisim_layout.addWidget(ara_btn)
        iletisim_layout.addWidget(mesaj_btn)
        iletisim_layout.addWidget(konum_iste_btn)
        
        iletisim_group.setLayout(iletisim_layout)
        layout.addWidget(iletisim_group)
        
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
        self.data_manager = DatabaseManager(
            "C:/Users/bbase/Downloads/afad-proje-firebase-adminsdk-asriu-b928e577ab.json",
            "https://afad-proje-default-rtdb.europe-west1.firebasedatabase.app/"
        )
        self.ekipler = {}
        self.current_team = None
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Ekip veya personel ara...")
        self.search_box.textChanged.connect(self.filter_teams)
        search_layout.addWidget(self.search_box)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Hepsi", "AFAD", "STK", "DİĞER"])
        self.filter_combo.currentTextChanged.connect(self.filter_teams)
        search_layout.addWidget(self.filter_combo)
        
        left_layout.addLayout(search_layout)
        
        self.team_tree = QTreeWidget()
        self.team_tree.setStyleSheet(TEAM_TREE_STYLE)
        self.team_tree.setHeaderLabels(["Ekipler ve Personel"])
        self.team_tree.itemClicked.connect(self.display_team_details)
        self.team_tree.itemDoubleClicked.connect(self.show_personnel_details2)
        self.team_tree.setAlternatingRowColors(True)
        left_layout.addWidget(self.team_tree)
        
        quick_team_group = QGroupBox("Hızlı Ekip Oluştur")
        quick_team_layout = QFormLayout()
        
        self.quick_team_name = QLineEdit()
        self.quick_team_type = QComboBox()
        self.quick_team_type.addItems([
            "Arama Kurtarma Ekibi", "Sağlık Ekibi", "Lojistik Ekibi",
            "İlk Yardım Ekibi", "Koordinasyon Ekibi", "Teknik Ekip"
        ])
        self.quick_team_location_city = QComboBox()
        self.quick_team_location_district = QComboBox()
        self.quick_team_location_city.addItems(cities_and_districts.keys())
        self.quick_team_location_city.currentTextChanged.connect(self.update_districts)
        self.quick_team_status = QComboBox()
        self.quick_team_status.addItems(["AFAD", "STK", "DİĞER"])
        
        quick_team_layout.addRow("Ekip Adı:", self.quick_team_name)
        quick_team_layout.addRow("Tür:", self.quick_team_type)
        quick_team_layout.addRow("Kurum Durumu:", self.quick_team_status)
        quick_team_layout.addRow("Şehir:", self.quick_team_location_city)
        quick_team_layout.addRow("İlçe:", self.quick_team_location_district)
        
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Ekip Oluştur")
        create_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        create_btn.setIcon(QIcon('icons/add-group.png'))
        create_btn.clicked.connect(self.quick_create_team)
        delete_btn = QPushButton("Ekip Sil")
        delete_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_btn.setIcon(QIcon('icons/delete.png'))
        delete_btn.clicked.connect(self.quick_delete_team)
        
        button_layout.addWidget(create_btn)
        button_layout.addWidget(delete_btn)
        quick_team_layout.addRow(button_layout)
        
        quick_team_group.setLayout(quick_team_layout)
        left_layout.addWidget(quick_team_group)
        
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        
        self.team_info_group = QGroupBox("Ekip Bilgileri")
        team_info_layout = QVBoxLayout()
        self.team_info_text = QTextBrowser()
        team_info_layout.addWidget(self.team_info_text)
        
        quick_actions = QHBoxLayout()
        mesaj_btn = QPushButton("Tüm Ekibe Mesaj")
        mesaj_btn.setStyleSheet(BUTTON_STYLE)
        mesaj_btn.setIcon(QIcon('icons/message.png'))
        mesaj_btn.clicked.connect(self.send_team_message)
        durum_btn = QPushButton("Durum Bilgisi İste")
        durum_btn.setStyleSheet(BUTTON_STYLE)
        durum_btn.setIcon(QIcon('icons/share.png'))
        durum_btn.clicked.connect(self.request_team_status)
        konum_btn = QPushButton("Konum Bilgisi İste")
        konum_btn.setStyleSheet(BUTTON_STYLE)
        konum_btn.setIcon(QIcon('Admin/icons/location-info.png'))
        konum_btn.clicked.connect(self.request_team_location)
        
        quick_actions.addWidget(mesaj_btn)
        quick_actions.addWidget(durum_btn)
        quick_actions.addWidget(konum_btn)
        
        team_info_layout.addLayout(quick_actions)
        self.team_info_group.setLayout(team_info_layout)
        middle_layout.addWidget(self.team_info_group)
        
        self.personnel_table = QTableWidget()
        self.personnel_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.personnel_table.setColumnCount(10)
        self.personnel_table.setHorizontalHeaderLabels([
            "TC", "Ad Soyad", "Telefon", "Ev Telefonu", "E-posta", "Adres", "Ünvan", "Uzmanlık", "Tecrübe", "Son Güncelleme"
        ])
        self.personnel_table.itemDoubleClicked.connect(self.show_personnel_details_from_table)
        middle_layout.addWidget(self.personnel_table)
        
        personel_action_layout = QHBoxLayout()
        add_personel_btn = QPushButton("Personel Ekle")
        add_personel_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        add_personel_btn.setIcon(QIcon('icons/add.png'))
        add_personel_btn.clicked.connect(self.add_personnel)
        remove_personel_btn = QPushButton("Personel Çıkar")
        remove_personel_btn.setStyleSheet(RED_BUTTON_STYLE)
        remove_personel_btn.setIcon(QIcon('icons/delete.png'))
        remove_personel_btn.clicked.connect(self.remove_personnel)
        edit_personel_btn = QPushButton("Personel Düzenle")
        edit_personel_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_personel_btn.setIcon(QIcon('icons/custom.png'))
        edit_personel_btn.clicked.connect(self.edit_personnel)
        
        personel_action_layout.addWidget(add_personel_btn)
        personel_action_layout.addWidget(remove_personel_btn)
        personel_action_layout.addWidget(edit_personel_btn)
        
        middle_layout.addLayout(personel_action_layout)
        
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(middle_panel, stretch=2)
        
        self.setLayout(layout)
        self.load_teams()

    def update_districts(self):
        city = self.quick_team_location_city.currentText()
        districts = cities_and_districts.get(city, [])
        self.quick_team_location_district.clear()
        self.quick_team_location_district.addItems(districts)

    def display_team_details(self, item):
        if not item or item.parent():
            return
        team_name = item.text(0)
        teams_data = self.data_manager.get_teams()
        for team_id, team_data in teams_data.items():
            if team_data.get("name") == team_name:
                self.current_team = team_id
                info_text = f"""
                <h3>{team_name}</h3>
                <p><b>Ekip Türü:</b> {team_data.get('type', '-')}</p>
                <p><b>Kurum:</b> {team_data.get('status', '-')}</p>
                <p><b>Lokasyon:</b> {team_data.get('location', '-')}</p>
                <p><b>Personel Sayısı:</b> {len(team_data.get('members', []))}</p>
                """
                self.team_info_text.setHtml(info_text)
                self.personnel_table.setRowCount(0)
                for member in team_data.get('members', []):
                    row = self.personnel_table.rowCount()
                    self.personnel_table.insertRow(row)
                    self.personnel_table.setItem(row, 0, QTableWidgetItem(str(member.get('TC', '-')))
)
                    self.personnel_table.setItem(row, 1, QTableWidgetItem(member.get('adSoyad', '-')))
                    self.personnel_table.setItem(row, 2, QTableWidgetItem(member.get('telefon', '-')))
                    self.personnel_table.setItem(row, 3, QTableWidgetItem(member.get('evTelefonu', '-')))
                    self.personnel_table.setItem(row, 4, QTableWidgetItem(member.get('ePosta', '-')))
                    self.personnel_table.setItem(row, 5, QTableWidgetItem(member.get('adres', '-')))
                    self.personnel_table.setItem(row, 6, QTableWidgetItem(member.get('unvan', '-')))
                    self.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('uzmanlik', '-')))
                    self.personnel_table.setItem(row, 8, QTableWidgetItem(member.get('tecrube', '-')))
                    self.personnel_table.setItem(row, 9, QTableWidgetItem(member.get('sonGuncelleme', '-')))
                self.personnel_table.resizeColumnsToContents()
                break

    def show_personnel_details2(self, item, column):
        parent = item.parent()
        if not parent:
            return
        personnel_name = item.text(0)
        team_name = parent.text(0)
        teams_data = self.data_manager.get_teams()
        selected_person = None
        for team_id, team_info in teams_data.items():
            if team_info.get("name") == team_name:
                for member in team_info.get("members", []):
                    if member.get("adSoyad") == personnel_name:
                        selected_person = member
                        break
                break
        if selected_person:
            dialog = PersonelDetayDialog(selected_person, self)
            dialog.exec_()

    def send_team_message(self):
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        team_data = self.data_manager.get_team(self.current_team)
        team_name = team_data.get("name", "Bilinmeyen Ekip") if team_data else "Bilinmeyen Ekip"
        message_dialog = MesajDialog(f"Ekip: {team_name}", self)
        if message_dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{team_name} ekibine mesaj gönderildi!")

    def request_team_status(self):
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        team_data = self.data_manager.get_team(self.current_team)
        team_name = team_data.get("name", "Bilinmeyen Ekip") if team_data else "Bilinmeyen Ekip"
        msg = "Lütfen mevcut durumunuz hakkında bilgi veriniz."
        dialog = MesajDialog(f"Ekip: {team_name}", self)
        dialog.mesaj_text.setText(msg)
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{team_name} ekibinden durum bilgisi istendi!")

    def request_team_location(self):
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        team_data = self.data_manager.get_team(self.current_team)
        team_name = team_data.get("name", "Bilinmeyen Ekip") if team_data else "Bilinmeyen Ekip"
        msg = "Acil durum brifingi için konum bildiriniz."
        dialog = MesajDialog(f"Ekip: {team_name}", self)
        dialog.mesaj_text.setText(msg)
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", f"{team_name} ekibinden konum bilgisi istendi!")

    def filter_teams(self):
        search_text = self.search_box.text().lower()
        filter_status = self.filter_combo.currentText().strip()
        for i in range(self.team_tree.topLevelItemCount()):
            team_item = self.team_tree.topLevelItem(i)
            show_team = False
            if search_text in team_item.text(0).lower():
                show_team = True
            team_name = team_item.text(0)
            teams_data = self.data_manager.get_teams()
            team_data = next((data for data in teams_data.values() if data.get('name') == team_name), None)
            if team_data and filter_status != "Hepsi" and filter_status != "DİĞER" and team_data.get('status', 'AFAD') != filter_status:
                show_team = False
            for j in range(team_item.childCount()):
                person_item = team_item.child(j)
                if search_text in person_item.text(0).lower():
                    show_team = True
                    person_item.setHidden(False)
                else:
                    person_item.setHidden(True)
            team_item.setHidden(not show_team)

    def load_teams(self):
        teams_data = self.data_manager.get_teams()
        if isinstance(teams_data, dict):
            self.ekipler = teams_data
            self.team_tree.clear()
            for team_id, team_info in teams_data.items():
                self.add_team_to_tree(team_id, team_info)
            QMessageBox.information(self, "Bilgi", "Ekipler başarıyla yüklendi!")
        else:
            QMessageBox.warning(self, "Hata", "Ekip verileri yüklenemedi veya henüz kayıtlı ekip yok.")

    def add_team_to_tree(self, team_id, team_info):
        team_name = team_info.get("name", "Bilinmeyen Ekip")
        team_item = QTreeWidgetItem([team_name])
        team_item.setData(0, Qt.UserRole, str(team_id))
        status = team_info.get("status", "").upper()
        if status == "AFAD":
            team_item.setBackground(0, QColor("#4c9161"))
        elif status == "STK":
            team_item.setBackground(0, QColor("#D14D1D"))
        for member in team_info.get("members", []):
            member_name = member.get("adSoyad", "Bilinmeyen Üye")  # TC burada gösterilmiyor
            member_item = QTreeWidgetItem([member_name])
            member_item.setData(0, Qt.UserRole, str(member.get("Members_ID", "0")))
            member_item.setIcon(0, QIcon("icons/person.png"))
            team_item.addChild(member_item)
        self.team_tree.addTopLevelItem(team_item)
        team_item.setExpanded(True)

    def quick_create_team(self):
        team_name = self.quick_team_name.text().strip()
        team_type = self.quick_team_type.currentText().strip()
        city = self.quick_team_location_city.currentText().strip()
        district = self.quick_team_location_district.currentText().strip()
        status = self.quick_team_status.currentText().strip()
        location = f"{city}, {district}"
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Ekip adı boş olamaz!")
            return
        if not city or not district:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir şehir ve ilçe seçiniz!")
            return
        teams_data = self.data_manager.get_teams()
        if any(data.get("name") == team_name for data in teams_data.values()):
            QMessageBox.warning(self, "Uyarı", "Bu isimde bir ekip zaten var!")
            return
        last_id = max([int(data.get("Ekip_ID", 0)) for data in teams_data.values() if str(data.get("Ekip_ID", "")).isdigit()], default=0)
        new_team_id = str(last_id + 1)
        team_data = {
            "Ekip_ID": new_team_id,
            "name": team_name,
            "status": status,
            "type": team_type,
            "location": location,
            "members": []
        }
        if self.data_manager.add_team(new_team_id, team_data):
            self.ekipler[new_team_id] = team_data
            self.reload_teams_tree()
            QMessageBox.information(self, "Başarılı", f"Ekip başarıyla oluşturuldu: {team_name}")
        else:
            QMessageBox.warning(self, "Hata", "Ekip oluşturulamadı!")

    def reload_teams_tree(self):
        self.team_tree.clear()
        for team_id, team_data in self.ekipler.items():
            self.add_team_to_tree(team_id, team_data)

    def get_selected_team_id(self):
        selected_item = self.team_tree.currentItem()
        if selected_item and not selected_item.parent():
            return selected_item.data(0, Qt.UserRole)
        return None

    def show_personnel_details_from_table(self, item):
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Uyarı", "Herhangi bir ekip seçilmedi.")
            return
        row = item.row()
        personnel_tc = self.personnel_table.item(row, 0).text()
        team_info = self.data_manager.get_team(team_id)
        if not team_info:
            return
        for person in team_info.get('members', []):
            if str(person.get('TC', '')) == personnel_tc:
                dialog = PersonelDetayDialog(person, self)
                dialog.exec_()
                return

    def add_personnel(self):
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
            return
        team_name = self.team_tree.currentItem().text(0)
        dialog = PersonelEkleDialog(team_name=team_name, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            personnel_info = dialog.collect_personnel_info()
            if not personnel_info:
                return
            tc_number = personnel_info.get("tc", "")
            exists, existing_team_id = self.data_manager.check_personnel_exists(tc_number)
            if exists:
                QMessageBox.warning(self, "Uyarı", f"{tc_number} TC Kimlik Numarasına sahip kişi başka bir ekipte kayıtlı!")
                return
            team_data = self.data_manager.get_team(team_id)
            personnel_list = team_data.get("members", [])
            last_member_id = max([int(person.get("Members_ID", 0)) for person in personnel_list], default=0)
            new_member_id = last_member_id + 1
            new_personnel = {
                "Members_ID": new_member_id,
                "TC": tc_number,
                "adSoyad": personnel_info.get("name", ""),
                "telefon": personnel_info.get("phone", ""),
                "evTelefonu": personnel_info.get("home_phone", ""),
                "ePosta": personnel_info.get("email", ""),
                "adres": personnel_info.get("address", ""),
                "unvan": personnel_info.get("title", ""),
                "uzmanlik": personnel_info.get("specialization", ""),
                "tecrube": personnel_info.get("experience", ""),
                "sonGuncelleme": personnel_info.get("last_update", "")
            }
            if self.data_manager.add_personnel(team_id, new_personnel):
                self.ekipler[team_id]["members"].append(new_personnel)
                self.reload_teams_tree()
                self.display_team_details(self.team_tree.currentItem())  # Tabloyu yenile
                QMessageBox.information(self, "Başarılı", f"{new_personnel['adSoyad']} başarıyla {team_name} ekibine eklendi.")
            else:
                QMessageBox.warning(self, "Hata", "Personel eklenemedi!")

    def remove_personnel(self):
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
            return
        team_data = self.data_manager.get_team(team_id)
        personnel_list = team_data.get("members", [])
        if not personnel_list:
            QMessageBox.warning(self, "Uyarı", "Bu ekipte kayıtlı personel bulunmamaktadır.")
            return
        dialog = PersonelSecDialog(personnel_list=personnel_list, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            selected_personnel = dialog.get_selected_personnel()
            if selected_personnel and self.data_manager.remove_personnel(team_id, selected_personnel):
                self.ekipler[team_id]["members"] = [p for p in personnel_list if p.get("Members_ID") != selected_personnel.get("Members_ID")]
                self.reload_teams_tree()
                self.display_team_details(self.team_tree.currentItem())  # Tabloyu yenile
                QMessageBox.information(self, "Başarılı", f"{selected_personnel['adSoyad']} başarıyla çıkarıldı.")
            else:
                QMessageBox.warning(self, "Hata", "Personel çıkarılamadı!")

    def edit_personnel(self):
        """Personel düzenleme işlemi"""
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
            return
        
        team_data = self.data_manager.get_team(team_id)
        personnel_list = team_data.get("members", [])
        if not personnel_list:
            QMessageBox.warning(self, "Uyarı", "Bu ekipte kayıtlı personel bulunmamaktadır.")
            return
        
        dialog = PersonelSecDialog(personnel_list=personnel_list, edit_mode=True, parent=self)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        selected_personnel = dialog.get_selected_personnel()
        if not selected_personnel:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir personel seçiniz!")
            return
        
        edit_dialog = PersonelDuzenleDialog(personnel=selected_personnel, parent=self)
        if edit_dialog.exec_() == QDialog.Accepted:
            updated_personnel = edit_dialog.get_updated_personnel()
            if updated_personnel:
                if self.data_manager.update_personnel(team_id, selected_personnel, updated_personnel):
                    index = next((i for i, p in enumerate(self.ekipler[team_id]["members"]) if p.get("Members_ID") == selected_personnel.get("Members_ID")), None)
                    if index is not None:
                        self.ekipler[team_id]["members"][index] = updated_personnel
                        self.reload_teams_tree()
                        self.display_team_details(self.team_tree.currentItem())  # Tabloyu yenile
                        QMessageBox.information(self, "Başarılı", f"{updated_personnel['adSoyad']} başarıyla güncellendi.")
                    else:
                        QMessageBox.warning(self, "Hata", "Personel yerel listede bulunamadı.")
                else:
                    QMessageBox.warning(self, "Hata", "Personel güncellenemedi!")

    def quick_delete_team(self):
        team_id = self.get_selected_team_id()
        if not team_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
            return
        team_data = self.data_manager.get_team(team_id)
        team_name = team_data.get("name", "Bilinmeyen Ekip")
        reply = QMessageBox.question(self, "Ekip Silme Onayı", f"{team_name} ekibini silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.Yes:
            if self.data_manager.delete_team(team_id):
                del self.ekipler[team_id]
                self.reload_teams_tree()
                self.team_info_text.clear()
                self.personnel_table.setRowCount(0)
                self.current_team = None
                QMessageBox.information(self, "Başarılı", f"{team_name} ekibi silindi!")
            else:
                QMessageBox.warning(self, "Hata", "Ekip silinemedi!")

class PersonnelFormFields:
    INPUT_KEYS = [
        ("tc", "TC:"),
        ("name", "Ad Soyad:"),
        ("phone", "Telefon:"),
        ("home_phone", "Ev Telefonu:"),
        ("email", "E-posta:"),
        ("address", "Ev Adresi:"),
        ("title", "Ünvan:"),
        ("specialization", "Uzmanlık:"),
        ("experience", "Tecrübe (Yıl):"),
    ]

    @staticmethod
    def create_input_fields(defaults=None):
        fields = {}
        defaults = defaults or {}
        for key, _ in PersonnelFormFields.INPUT_KEYS:
            input_field = QLineEdit(str(defaults.get(key, "")))
            if key == "tc":
                regex = QRegExp(r"^\d{11}$")  # 11 haneli TC
                validator = QRegExpValidator(regex)
                input_field.setValidator(validator)
            elif key in ["phone", "home_phone"]:
                regex = QRegExp(r"^\d{10}$")  # 10 haneli telefon
                validator = QRegExpValidator(regex)
                input_field.setValidator(validator)
            elif key == "email":
                regex = QRegExp(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")  # Email formatı
                validator = QRegExpValidator(regex)
                input_field.setValidator(validator)
            fields[f"{key}_input"] = input_field
        return fields

    @staticmethod
    def add_form_rows(layout, input_fields):
        for key, label_text in PersonnelFormFields.INPUT_KEYS:
            layout.addRow(label_text, input_fields[f"{key}_input"])

    @staticmethod
    def collect_personnel_info(input_fields):
        personnel_data = {}
        for key, _ in PersonnelFormFields.INPUT_KEYS:
            value = input_fields[f"{key}_input"].text().strip()
            if key == "tc":
                if not value or len(value) != 11 or not value.isdigit():
                    QMessageBox.warning(None, "Geçersiz TC", "TC numarası 11 haneli olmalı ve sadece rakamlardan oluşmalı!")
                    return None
            if key in ["phone", "home_phone"] and value and (len(value) != 10 or not value.isdigit()):
                QMessageBox.warning(None, "Geçersiz Telefon", "Telefon numarası 10 haneli olmalı ve sadece rakamlardan oluşmalı!")
                return None
            if key == "email" and value and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
                QMessageBox.warning(None, "Geçersiz E-posta", "Geçerli bir e-posta adresi giriniz (ör: example@domain.com)!")
                return None
            if key == "name" and not value:
                QMessageBox.warning(None, "Hata", "Ad Soyad alanı boş olamaz!")
                return None
            personnel_data[key] = value
        personnel_data["last_update"] = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        return personnel_data

    @staticmethod
    def is_valid_phone(phone):
        return bool(re.match(r"^\d{10}$", phone))

class PersonelEkleDialog(QDialog):
    def __init__(self, team_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{team_name} - Personel Ekle")
        self.team_name = team_name
        self.personel_file = os.path.join(os.path.dirname(__file__), 'personel.csv')
        self.input_fields = PersonnelFormFields.create_input_fields()
        self.setupUI()
        self.load_personel_data()

    def setupUI(self):
        layout = QFormLayout()

        # TC field with Search button
        tc_layout = QHBoxLayout()
        self.input_fields["tc_input"].setPlaceholderText("11 haneli TC giriniz")
        tc_layout.addWidget(self.input_fields["tc_input"])
        search_btn = QPushButton("Ara")
        search_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        search_btn.setIcon(QIcon('icons/search.png'))
        search_btn.setFixedWidth(80)
        search_btn.clicked.connect(self.search_and_fill)
        tc_layout.addWidget(search_btn)
        layout.addRow("TC:", tc_layout)

        # Add remaining fields
        for key, label in PersonnelFormFields.INPUT_KEYS:
            if key != "tc":  # Skip TC since it's already added
                layout.addRow(label, self.input_fields[f"{key}_input"])

        # Buttons
        btn_layout = QHBoxLayout()
        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        kaydet_btn.setIcon(QIcon('icons/save.png'))
        kaydet_btn.clicked.connect(self.accept)
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)
        iptal_btn.clicked.connect(self.reject)
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)
        layout.addRow(btn_layout)

        self.setLayout(layout)

    def load_personel_data(self):
        """Load personnel data from personel.csv"""
        self.personel_data = {}
        try:
            with open(self.personel_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.personel_data[row['TC']] = {
                        'name': row['Ad Soyad'],
                        'phone': row['Telefon'],
                        'home_phone': row['Ev Telefonu'],
                        'email': row['E-posta'],
                        'address': row['Ev Adresi'],
                        'title': row['Ünvan'],
                        'specialization': row['Uzmanlık'],
                        'experience': row['Tecrübe (Yıl)']
                    }
        except FileNotFoundError:
            QMessageBox.warning(self, "Hata", f"'personel.csv' bulunamadı! Beklenen yol: {self.personel_file}")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"'personel.csv' okunamadı: {str(e)}")

    def search_and_fill(self):
        """Fill fields based on TC when Search button is clicked"""
        tc_text = self.input_fields["tc_input"].text().strip()
        if len(tc_text) != 11 or not tc_text.isdigit():
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir 11 haneli TC numarası giriniz!")
            return

        personel = self.personel_data.get(tc_text, {})
        if personel:
            for key, value in personel.items():
                if key in [k for k, _ in PersonnelFormFields.INPUT_KEYS]:
                    self.input_fields[f"{key}_input"].setText(str(value))
            QMessageBox.information(self, "Bulundu", f"{personel['name']} bilgileri yüklendi.")
        else:
            # Clear fields if TC not found
            for key, _ in PersonnelFormFields.INPUT_KEYS:
                if key != "tc":
                    self.input_fields[f"{key}_input"].clear()
            QMessageBox.warning(self, "Bulunamadı", f"TC: {tc_text} kayıtlı değil!")

    def collect_personnel_info(self):
        return PersonnelFormFields.collect_personnel_info(self.input_fields)

class PersonelDuzenleDialog(QDialog):
    def __init__(self, personnel, parent=None):
        super().__init__(parent)
        self.personnel = personnel
        self.updated_personnel = None
        self.setWindowTitle(f"Personel Düzenle: {personnel.get('adSoyad', 'Bilinmeyen')}")
        self.input_fields = self.create_input_fields(personnel)
        self.setupUI()

    def create_input_fields(self, personnel):
        fields = {
            "TC": QLineEdit(str(personnel.get("TC", ""))),
            "adSoyad": QLineEdit(str(personnel.get("adSoyad", ""))),
            "telefon": QLineEdit(str(personnel.get("telefon", ""))),
            "ePosta": QLineEdit(str(personnel.get("ePosta", ""))),
            "adres": QLineEdit(str(personnel.get("adres", ""))),
            "evTelefonu": QLineEdit(str(personnel.get("evTelefonu", ""))),
            "uzmanlik": QLineEdit(str(personnel.get("uzmanlik", ""))),
            "unvan": QLineEdit(str(personnel.get("unvan", ""))),
            "tecrube": QLineEdit(str(personnel.get("tecrube", ""))),
        }
        fields["TC"].setValidator(QRegExpValidator(QRegExp(r"^\d{11}$")))
        fields["telefon"].setValidator(QRegExpValidator(QRegExp(r"^\d{10}$")))
        fields["evTelefonu"].setValidator(QRegExpValidator(QRegExp(r"^\d{10}$")))
        fields["ePosta"].setValidator(QRegExpValidator(QRegExp(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")))
        return fields

    def setupUI(self):
        layout = QFormLayout()
        for field_name, field_widget in self.input_fields.items():
            label = field_name.capitalize().replace("Soyad", " Soyad").replace("Telefonu", " Telefonu")
            if field_name == "TC" or field_name == "adSoyad":  # TC ve Ad Soyad düzenlenemez
                field_widget.setReadOnly(True)
                field_widget.setStyleSheet("background-color: #d3d3d3; color: #000000;")
            else:
                field_widget.setReadOnly(False)
            layout.addRow(label + ":", field_widget)

        btn_layout = QHBoxLayout()
        kaydet_btn = QPushButton("Güncelle")
        kaydet_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        kaydet_btn.setIcon(QIcon("icons/save.png"))
        kaydet_btn.clicked.connect(self.save_changes)
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)
        iptal_btn.clicked.connect(self.reject)
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)
        layout.addRow(btn_layout)
        self.setLayout(layout)

    def save_changes(self):
        updated_data = {}
        for field_name, field_widget in self.input_fields.items():
            value = field_widget.text().strip()
            if field_name == "telefon" and value and (len(value) != 10 or not value.isdigit()):
                QMessageBox.warning(self, "Hata", "Telefon numarası 10 haneli olmalı ve sadece rakamlardan oluşmalı!")
                return
            if field_name == "evTelefonu" and value and (len(value) != 10 or not value.isdigit()):
                QMessageBox.warning(self, "Hata", "Ev telefonu numarası 10 haneli olmalı ve sadece rakamlardan oluşmalı!")
                return
            if field_name == "ePosta" and value and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
                QMessageBox.warning(self, "Hata", "Geçerli bir e-posta adresi giriniz!")
                return
            updated_data[field_name] = value

        updated_data["Members_ID"] = self.personnel.get("Members_ID", 0)
        updated_data["sonGuncelleme"] = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        self.updated_personnel = updated_data
        self.accept()

    def get_updated_personnel(self):
        return self.updated_personnel
    
# ... (After PersonelEkleDialog, before PersonelDuzenleDialog) ...

class PersonelSecDialog(QDialog):
    def __init__(self, personnel_list, parent=None, edit_mode=False):
        super().__init__(parent)
        self.personnel_list = personnel_list
        self.edit_mode = edit_mode
        self.setWindowTitle("Personel Seç" if not edit_mode else "Personel Düzenle")
        self.selected_personnel = None
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        self.personel_listesi = QListWidget()
        if not self.personnel_list:
            self.personel_listesi.addItem("Kayıtlı personel bulunamadı.")
        else:
            for person in self.personnel_list:
                tc = str(person.get("TC", "Bilinmiyor"))
                name = person.get("adSoyad", "Bilinmiyor")
                self.personel_listesi.addItem(f"{tc} - {name}")
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
        selected_index = self.personel_listesi.currentRow()
        if selected_index < 0 or not self.personnel_list:
            return None
        return self.personnel_list[selected_index]

# ... (Replace remove_personnel and edit_personnel with the corrected versions above) ...    