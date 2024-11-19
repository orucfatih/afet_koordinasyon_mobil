from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QMessageBox,
                           QTreeWidget, QTreeWidgetItem, QDialog,
                           QTextBrowser)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
import os
from datetime import datetime

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
        
        ara_btn = QPushButton("Ara")
        ara_btn.setIcon(QIcon("icons/call.png"))  # Icon eklenebilir
        ara_btn.clicked.connect(lambda: self.ara(self.personel_data["phone"]))
        
        mesaj_btn = QPushButton("Mesaj Gönder")
        mesaj_btn.setIcon(QIcon("icons/message.png"))  # Icon eklenebilir
        mesaj_btn.clicked.connect(lambda: self.mesaj_gonder(self.personel_data["phone"]))
        
        konum_iste_btn = QPushButton("Konum İste")
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
        gonder_btn.clicked.connect(self.mesaj_gonder)
        iptal_btn = QPushButton("İptal")
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
        
        # Sol Panel - Ekipler Listesi ve Durum Özeti
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
        self.filter_combo.addItems(["Tüm Ekipler", "Aktif Görevde", "Müsait"])
        self.filter_combo.currentTextChanged.connect(self.filter_teams)
        search_layout.addWidget(self.filter_combo)
        
        left_layout.addLayout(search_layout)
        
        # Ekipler ağacı
        self.team_tree = QTreeWidget()
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
        
        create_btn = QPushButton("Ekip Oluştur")
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
        
        mesaj_btn = QPushButton("Tüm Ekibe Mesaj")
        mesaj_btn.clicked.connect(self.send_team_message)
        
        durum_btn = QPushButton("Durum Bilgisi İste")
        durum_btn.clicked.connect(self.request_team_status)
        
        konum_btn = QPushButton("Konum Bilgisi İste")
        konum_btn.clicked.connect(self.request_team_location)
        
        quick_actions.addWidget(mesaj_btn)
        quick_actions.addWidget(durum_btn)
        quick_actions.addWidget(konum_btn)
        
        team_info_layout.addLayout(quick_actions)
        self.team_info_group.setLayout(team_info_layout)
        middle_layout.addWidget(self.team_info_group)
        
        # Personel listesi
        self.personnel_table = QTableWidget()
        self.personnel_table.setColumnCount(6)
        self.personnel_table.setHorizontalHeaderLabels([
            "Ad Soyad", "Görevi", "Telefon", "Durum", "Son Konum", "Son Güncelleme"
        ])
        self.personnel_table.itemDoubleClicked.connect(self.show_personnel_details_from_table)
        middle_layout.addWidget(self.personnel_table)
        
        # Sağ Panel - Görev Yönetimi
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Aktif görev bilgisi
        active_task_group = QGroupBox("Aktif Görev")
        active_task_layout = QVBoxLayout()
        
        self.active_task_text = QTextBrowser()
        active_task_layout.addWidget(self.active_task_text)
        
        task_buttons = QHBoxLayout()
        
        update_task_btn = QPushButton("Görevi Güncelle")
        update_task_btn.clicked.connect(self.update_task)
        
        complete_task_btn = QPushButton("Görevi Tamamla")
        complete_task_btn.clicked.connect(self.complete_task)
        
        task_buttons.addWidget(update_task_btn)
        task_buttons.addWidget(complete_task_btn)
        
        active_task_layout.addLayout(task_buttons)
        active_task_group.setLayout(active_task_layout)
        right_layout.addWidget(active_task_group)
        
        # Yeni görev atama
        new_task_group = QGroupBox("Yeni Görev Ata")
        new_task_layout = QFormLayout()
        
        self.task_location = QLineEdit()
        self.task_description = QTextEdit()
        self.task_priority = QComboBox()
        self.task_priority.addItems(["Normal", "Öncelikli", "Acil"])
        
        new_task_layout.addRow("Görev Lokasyonu:", self.task_location)
        new_task_layout.addRow("Görev Açıklaması:", self.task_description)
        new_task_layout.addRow("Öncelik:", self.task_priority)
        
        assign_task_btn = QPushButton("Görevi Ata")
        assign_task_btn.clicked.connect(self.assign_task)
        new_task_layout.addRow(assign_task_btn)
        
        new_task_group.setLayout(new_task_layout)
        right_layout.addWidget(new_task_group)
        
        # Ana layout'a panelleri ekleme
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(middle_panel, stretch=2)
        layout.addWidget(right_panel, stretch=1)
        
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
                <p><b>Aktif Görev:</b> {team_info.get('active_task', 'Görev Yok')}</p>
                <p><b>Durum:</b> {team_info.get('status', 'Müsait')}</p>
                """
                self.team_info_text.setHtml(info_text)
                
                # Personel tablosunu güncelle
                self.personnel_table.setRowCount(0)
                for person in team_info.get('personnel', []):
                    row = self.personnel_table.rowCount()
                    self.personnel_table.insertRow(row)
                    self.personnel_table.setItem(row, 0, QTableWidgetItem(person['name']))
                    self.personnel_table.setItem(row, 1, QTableWidgetItem(person.get('title', '-')))
                    self.personnel_table.setItem(row, 2, QTableWidgetItem(person.get('phone', '-')))
                    self.personnel_table.setItem(row, 3, QTableWidgetItem(person.get('status', 'Müsait')))
                    self.personnel_table.setItem(row, 4, QTableWidgetItem(person.get('last_location', '-')))
                    self.personnel_table.setItem(row, 5, QTableWidgetItem(person.get('last_update', '-')))
                
                # Aktif görev bilgisini güncelle
                if 'active_task' in team_info:
                    task_text = f"""
                    <h3>Aktif Görev Detayları</h3>
                    <p><b>Görev:</b> {team_info['active_task']}</p>
                    <p><b>Lokasyon:</b> {team_info.get('task_location', '-')}</p>
                    <p><b>Başlangıç:</b> {team_info.get('task_start_time', '-')}</p>
                    <p><b>Öncelik:</b> {team_info.get('task_priority', 'Normal')}</p>
                    """
                    self.active_task_text.setHtml(task_text)
                
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
                    team_status = self.ekipler[team_name].get('status', 'Müsait')
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
        # Örnek veri - gerçek uygulamada bir veritabanından yüklenebilir
        self.ekipler = {
            "Arama Kurtarma Ekibi 1": {
                "type": "Arama Kurtarma Ekibi",
                "status": "Aktif Görevde",
                "active_task": "Deprem bölgesinde arama çalışması",
                "task_location": "Kahramanmaraş Merkez",
                "task_start_time": "2024-03-16 08:00",
                "task_priority": "Acil",
                "personnel": [
                    {
                        "name": "Ahmet Yılmaz",
                        "title": "Ekip Lideri",
                        "phone": "555-0001",
                        "home_phone": "312-0001",
                        "email": "ahmet@example.com",
                        "address": "Ankara, Çankaya",
                        "specialization": "Arama Kurtarma Uzmanı",
                        "experience": "10",
                        "status": "Aktif",
                        "last_location": "Kahramanmaraş",
                        "last_update": "10 dk önce"
                    },
                    {
                        "name": "Mehmet Demir",
                        "title": "Kurtarma Uzmanı",
                        "phone": "555-0002",
                        "home_phone": "312-0002",
                        "email": "mehmet@example.com",
                        "address": "Ankara, Keçiören",
                        "specialization": "Teknik Kurtarma",
                        "experience": "8",
                        "status": "Aktif",
                        "last_location": "Kahramanmaraş",
                        "last_update": "15 dk önce"
                    }
                ]
            }
        }
        
        # Ekipleri ağaca ekle
        self.update_team_tree()

    def update_team_tree(self):
        """Ekipler ağacını günceller"""
        self.team_tree.clear()
        
        for team_name, team_data in self.ekipler.items():
            # Ekip başlığı
            team_item = QTreeWidgetItem([team_name])
            team_item.setIcon(0, QIcon("icons/team.png"))  # İkon eklenebilir
            
            # Ekip durumuna göre renklendirme
            if team_data.get('status') == "Aktif Görevde":
                team_item.setBackground(0, QColor("#4c9161"))  
            elif team_data.get('status') == "Müsait":
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
            "status": "Müsait",
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
                <p><b>Aktif Görev:</b> {team_info.get('active_task', 'Görev Yok')}</p>
                <p><b>Durum:</b> {team_info.get('status', 'Müsait')}</p>
                """
                self.team_info_text.setHtml(info_text)
                
                # Personel tablosunu güncelle
                self.personnel_table.setRowCount(0)
                for person in team_info.get('personnel', []):
                    row = self.personnel_table.rowCount()
                    self.personnel_table.insertRow(row)
                    self.personnel_table.setItem(row, 0, QTableWidgetItem(person['name']))
                    self.personnel_table.setItem(row, 1, QTableWidgetItem(person.get('title', '-')))
                    self.personnel_table.setItem(row, 2, QTableWidgetItem(person.get('phone', '-')))
                    self.personnel_table.setItem(row, 3, QTableWidgetItem(person.get('status', 'Müsait')))
                    self.personnel_table.setItem(row, 4, QTableWidgetItem(person.get('last_location', '-')))
                    self.personnel_table.setItem(row, 5, QTableWidgetItem(person.get('last_update', '-')))
                
                # Aktif görev bilgisini güncelle
                if 'active_task' in team_info:
                    task_text = f"""
                    <h3>Aktif Görev Detayları</h3>
                    <p><b>Görev:</b> {team_info['active_task']}</p>
                    <p><b>Lokasyon:</b> {team_info.get('task_location', '-')}</p>
                    <p><b>Başlangıç:</b> {team_info.get('task_start_time', '-')}</p>
                    <p><b>Öncelik:</b> {team_info.get('task_priority', 'Normal')}</p>
                    """
                    self.active_task_text.setHtml(task_text)
                else:
                    self.active_task_text.setHtml("<p>Aktif görev bulunmuyor.</p>")
                
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

    def update_task(self):
        """Aktif görevi günceller"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
        
        # Burada görev güncelleme dialogu açılabilir
        QMessageBox.information(self, "Bilgi", "Bu özellik henüz eklenmedi.")

    def complete_task(self):
        """Aktif görevi tamamlar"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        team = self.ekipler[self.current_team]
        if 'active_task' not in team:
            QMessageBox.warning(self, "Uyarı", "Aktif görev bulunmuyor!")
            return
            
        reply = QMessageBox.question(self, 'Onay', 
                                f"{self.current_team} ekibinin aktif görevi tamamlandı olarak işaretlensin mi?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                
        if reply == QMessageBox.Yes:
            # Görevi tamamla
            team.pop('active_task', None)
            team.pop('task_location', None)
            team.pop('task_start_time', None)
            team.pop('task_priority', None)
            team['status'] = 'Müsait'
            
            # Arayüzü güncelle
            self.show_team_details(self.team_tree.findItems(self.current_team, Qt.MatchExactly)[0])
            QMessageBox.information(self, "Başarılı", "Görev tamamlandı olarak işaretlendi!")

    def assign_task(self):
        """Yeni görev atar"""
        if not self.current_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir ekip seçin!")
            return
            
        location = self.task_location.text().strip()
        description = self.task_description.toPlainText().strip()
        priority = self.task_priority.currentText()
        
        if not location or not description:
            QMessageBox.warning(self, "Uyarı", "Lütfen görev lokasyonu ve açıklaması girin!")
            return
            
        team = self.ekipler[self.current_team]
        
        # Aktif görev varsa uyar
        if 'active_task' in team:
            reply = QMessageBox.question(self, 'Uyarı', 
                                    f"{self.current_team} ekibinin aktif bir görevi var. Yeni görev atamak istiyor musunuz?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # Yeni görevi ata
        team['active_task'] = description
        team['task_location'] = location
        team['task_start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        team['task_priority'] = priority
        team['status'] = 'Aktif Görevde'
        
        # Arayüzü güncelle
        self.show_team_details(self.team_tree.findItems(self.current_team, Qt.MatchExactly)[0])
        
        # Formu temizle
        self.task_location.clear()
        self.task_description.clear()
        self.task_priority.setCurrentIndex(0)
        
        QMessageBox.information(self, "Başarılı", f"{self.current_team} ekibine yeni görev atandı!")