from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QComboBox,
                           QGroupBox, QLineEdit, QFormLayout, 
                           QTableWidget, QTableWidgetItem, QMessageBox,
                           QTreeWidget, QTreeWidgetItem, QDialog,
                           QTextBrowser, QListWidget)
from PyQt5.QtCore import Qt, QDateTime, QRegExp
from PyQt5.QtGui import QIcon, QColor, QRegExpValidator
from sample_data import AFAD_TEAMS
from styles_dark import *
from styles_light import *
import firebase_admin
from firebase_admin import credentials, db
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')  # UTF-8 ayarı
# Firebase JSON kimlik dosyanızın tam yolu
cred = credentials.Certificate("C:/Users/bbase/Downloads/afad-proje-firebase-adminsdk-asriu-b928e577ab.json")
# Firebase bağlantısını başlat
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://afad-proje-default-rtdb.europe-west1.firebasedatabase.app/'
})

print("Firebase bağlantısı başarılı!")

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
            ("TC:", "TC"),
            ("Ad Soyad:", "adSoyad"),
            ("Telefon:", "telefon"),
            ("Ev Telefonu:", "evTelefonu"),
            ("E-posta:", "ePosta"),
            ("Ev Adresi:", "adres"),
            ("Ünvan:", "unvan"),
            ("Uzmanlık:", "uzmanlik"),
            ("Tecrübe (Yıl):", "tecrube"),
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
        ara_btn.setIcon(QIcon('icons/call.png'))
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

    # Örnek şehir ve ilçe verisi
    # Örnek şehir ve ilçe verisi
cities_and_districts = {
    "Ankara": ["Çankaya", "Keçiören", "Mamak", "Etimesgut"],
    "İstanbul": ["Kadıköy", "Üsküdar", "Beşiktaş", "Beyoğlu"],
    "İzmir": ["Konak", "Karşıyaka", "Bornova", "Buca"],
    # Diğer şehirler ve ilçeler
}   

class PersonelYonetimTab(QWidget):
    """Personel Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()

                # Firebase'e bağlanma
        try:
            cred = credentials.Certificate("C:/Users/bbase/Downloads/afad-proje-firebase-adminsdk-asriu-b928e577ab.json")
            if not firebase_admin._apps:  # Zaten başlatılmışsa tekrar başlatma
                firebase_admin.initialize_app(cred, {
    "databaseURL": "https://afad-proje-default-rtdb.europe-west1.firebasedatabase.app/"
                })
            self.db = db.reference()  # Veritabanı referansı
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Firebase başlatılamadı: {e}")
            return
        
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
        self.team_tree.itemClicked.connect(self.display_team_details)
        self.team_tree.itemDoubleClicked.connect(self.show_personnel_details2)
        self.team_tree.setAlternatingRowColors(True)
        left_layout.addWidget(self.team_tree)
        
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

        self.quick_team_location_city = QComboBox()  # Şehir ComboBox'ı
        self.quick_team_location_district = QComboBox()  # İlçe ComboBox'ı

        self.quick_team_location_city.addItems(cities_and_districts.keys())  # Şehirleri ekle
        self.quick_team_location_city.currentTextChanged.connect(self.update_districts)  # Şehir değiştiğinde ilçeleri güncelle
        
        # Kurum durumu (Yeni eklenen QComboBox)
        self.quick_team_status = QComboBox()  # QComboBox nesnesi tanımlandı
        status_options = ["AFAD", "STK", "DİĞER"]
        self.quick_team_status.addItems(status_options)
        
        # Layout'a ekleyin
        quick_team_layout.addRow("Ekip Adı:", self.quick_team_name)
        quick_team_layout.addRow("Tür:", self.quick_team_type)
        quick_team_layout.addRow("Kurum Durumu:", self.quick_team_status)  # Yeni satır eklendi
        quick_team_layout.addRow("Şehir:", self.quick_team_location_city)
        quick_team_layout.addRow("İlçe:", self.quick_team_location_district)
        
        create_btn = QPushButton(" Ekip Oluştur")
        create_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        create_btn.setIcon(QIcon('icons/add-group.png'))
        create_btn.clicked.connect(self.quick_create_team)
        quick_team_layout.addRow(create_btn)

        delete_btn = QPushButton(" Ekip Sil")
        delete_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_btn.setIcon(QIcon('icons/delete.png'))
        delete_btn.clicked.connect(self.quick_delete_team)

        # Butonları yan yana eklemek için yatay layout
        button_layout = QHBoxLayout()
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
            "TC", "Ad Soyad", "Telefon", "Ev Telefonu", "E-posta", "Adres", "Ünvan", "Uzmanlık", "Tecrübe", "Son Güncelleme"
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


##############################################################################################
    def update_districts(self):
        """Şehir seçildiğinde, o şehre ait ilçeleri ComboBox'a ekler."""
        city = self.quick_team_location_city.currentText()
        districts = cities_and_districts.get(city, [])
        self.quick_team_location_district.clear()  # İlçeleri temizle
        self.quick_team_location_district.addItems(districts)  # Yeni ilçeleri ekle 

    def display_team_details(self, item):
     """Ekip detaylarını gösterir"""
     if not item or not item.parent():  # Eğer ekip başlığına tıklandıysa
        team_name = item.text(0)
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Ekip adı alınamadı.")
            return


        try:
            # Firebase'den ekip detaylarını al
            teams_ref = db.reference('teams')
            existing_teams = teams_ref.get()


            if not existing_teams:
                QMessageBox.warning(self, "Uyarı", "Veritabanında hiç ekip bulunmuyor!")
                return

            # İlgili ekibi bul
            team_data = None
            for team_id, team_info in existing_teams.items():
                if team_info.get("name", "").strip().lower() == team_name.strip().lower():
                    team_data = team_info
                    break

            if not team_data:
                QMessageBox.warning(self, "Uyarı", "Ekip bilgileri bulunamadı!")
                return

            # Ekip detaylarını göster
            info_text = f"""
            <h3>{team_name}</h3>
            <p><b>Ekip Türü:</b> {team_data.get('status', '-')}</p>
            <p><b>Lokasyon:</b> {team_data.get('location', '-')}</p>
            <p><b>Personel Sayısı:</b> {len(team_data.get('members', []))}</p>
            """
            self.team_info_text.setHtml(info_text)

            # Personel tablosunu güncelle
            self.personnel_table.setRowCount(0)  # Her tıklamada tabloyu sıfırlıyoruz
            for member in team_data.get('members', []):
                row = self.personnel_table.rowCount()
                self.personnel_table.insertRow(row)
                self.personnel_table.setItem(row, 0, QTableWidgetItem(str(member.get('TC', '-'))))
                self.personnel_table.setItem(row, 1, QTableWidgetItem(member.get('adSoyad', '-')))
                self.personnel_table.setItem(row, 2, QTableWidgetItem(member.get('telefon', '-')))
                self.personnel_table.setItem(row, 3, QTableWidgetItem(member.get('evTelefonu', '-')))
                self.personnel_table.setItem(row, 4, QTableWidgetItem(member.get('ePosta', '-')))
                self.personnel_table.setItem(row, 5, QTableWidgetItem(member.get('adres', '-')))
                self.personnel_table.setItem(row, 6, QTableWidgetItem(member.get('unvan', '-')))
                self.personnel_table.setItem(row, 7, QTableWidgetItem(member.get('uzmanlik', '-')))
                self.personnel_table.setItem(row, 8, QTableWidgetItem(member.get('tecrube', '-')))
                self.personnel_table.setItem(row, 9, QTableWidgetItem(member.get('sonGuncelleme', '-')))

            # Şu anki ekip adını güncelle
            self.current_team = team_name

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ekip detayları alınırken bir hata oluştu:\n{e}")


    def show_personnel_details(self, item):
     """
     Ağacın bir öğesine çift tıklandığında çalışır.
     Eğer öğe bir personelse, detaylarını gösterir.
     """
     parent = item.parent()  # Parent öğesini kontrol et
     if parent is None:
        # Parent yoksa bu bir ekip düğümüdür, işlem yapma
        return

     personnel_name = item.text(0)  # Tıklanan öğenin adı
     team_name = parent.text(0)  # Ebeveyn öğenin adı (Ekip adı)

     try:
        # Firebase'den ekip bilgilerini al
        teams_data = self.db.child("teams").get()
        selected_person = None

        if teams_data:
            for team_id, team_info in teams_data.items():
                if team_info.get("name") == team_name:  # Ekip adına göre eşleştir
                    for member in team_info.get("members", []):  # Üyeler arasında ara
                        if (
                            member.get("adSoyad") == personnel_name
                            and member.get("tc") == item.data(0, Qt.UserRole)  # TC kontrolü
                        ):  # Ad-Soyad ve TC kimlik eşleşmesi
                            selected_person = member
                            break
                if selected_person:
                    break

        if not selected_person:
            QMessageBox.warning(self, "Uyarı", "Seçilen personel bilgisi bulunamadı.")
            return

        # Personel detaylarını dialogda göster
        dialog = PersonelDetayDialog(selected_person, self)
        dialog.exec_()

     except Exception as e:
        QMessageBox.critical(
            self,
            "Hata",
            f"Personel bilgileri alınırken bir hata oluştu:\n{e}"
        )

                
    def show_personnel_details2(self, item, column):
     """
     Ağacın bir öğesine çift tıklandığında çalışır.
     Eğer öğe bir personelse, detaylarını gösterir.
     """
     parent = item.parent()  # Parent öğesini kontrol et
     if parent is None:
        # Parent yoksa bu bir ekip düğümüdür, işlem yapma
        return

     personnel_name = item.text(0)  # Tıklanan öğenin adı
     team_name = parent.text(0)  # Ebeveyn öğenin adı (Ekip adı)

     try:
        # Firebase'den ekip bilgilerini al
        teams_data = self.db.child("teams").get()
        selected_person = None

        if teams_data:
            for team_id, team_info in teams_data.items():
                if team_info.get("name") == team_name:  # Ekip adına göre eşleştir
                    for member in team_info.get("members", []):  # Üyeler arasında ara
                        if member.get("adSoyad") == personnel_name:  # Ad-Soyad eşleşmesi
                            selected_person = member
                            break
                if selected_person:
                    break

        if not selected_person:
            QMessageBox.warning(self, "Uyarı", "Seçilen personel bilgisi bulunamadı.")
            return

        # Personel detaylarını dialogda göster
        dialog = PersonelDetayDialog(selected_person, self)
        dialog.exec_()

     except Exception as e:
        QMessageBox.critical(self, "Hata", f"Personel bilgileri alınırken bir hata oluştu:\n{e}")


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

##############################################################################################



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
     """Ekipleri ve personeli arama kutusuna göre filtreler."""
     search_text = self.search_box.text().lower()  # Arama metnini al
     filter_status = self.filter_combo.currentText().strip()  # Durum filtresi (AFAD, STK, Tüm Ekipler)

     # Tüm öğeleri gizle
     for i in range(self.team_tree.topLevelItemCount()):
        team_item = self.team_tree.topLevelItem(i)
        show_team = False  # Başlangıçta her ekibi gizle
        
        # Ekip adında arama
        if search_text in team_item.text(0).lower():
            show_team = True

        # Durum filtresini uygula
        team_status = team_item.data(0, Qt.UserRole)
        if filter_status != "Tüm Ekipler" and team_status != filter_status:
            show_team = False

        # Personel içinde arama
        for j in range(team_item.childCount()):
            person_item = team_item.child(j)
            if search_text in person_item.text(0).lower():  # Personel adı üzerinde arama
                show_team = True
                person_item.setHidden(False)
            else:
                person_item.setHidden(True)

        # Ekip ve altındaki personel öğelerinin gizlenip gösterilmesi
        team_item.setHidden(not show_team)
        
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
     """Firebase'den ekipleri yükler ve GUI'yi günceller."""
     try:
        # Firebase'den ekip verilerini alıyoruz
        teams_data = self.db.child("teams").get()


        if isinstance(teams_data, dict):  # Gelen veri sözlük formatındaysa
            for team_key, team_info in teams_data.items():
                #Sözlüğe ekleme kısmı
                self.ekipler[team_key] = team_info
                # Ekipleri GUI'ye ekliyoruz
                self.add_team_to_tree(team_key, team_info)
            QMessageBox.information(self, "Bilgi", "Ekipler başarıyla yüklendi!")
        else:
            QMessageBox.information(self, "Bilgi", "Henüz kayıtlı ekip yok.")
     except Exception as e:
        QMessageBox.critical(self, "Hata", f"Ekipler yüklenirken hata oluştu: {e}")

    def update_team_tree(self, team_name, team_info):
     """Firebase'den ekipleri yükler ve GUI'yi günceller."""
     try:
        self.team_tree.clear()  # Mevcut öğeleri temizle
        teams_data = self.db.child("teams").get()  # Firebase'den ekip verilerini al
        
        if isinstance(teams_data, dict):  # Veri varsa
            for team_key, team_info in teams_data.items():
                self.add_team_to_tree(team_key, team_info)  # Ekipleri GUI'ye ekle
        else:
            QMessageBox.information(self, "Bilgi", "Henüz kayıtlı ekip yok.")
     except Exception as e:
        QMessageBox.critical(self, "Hata", f"Ekipler yüklenirken hata oluştu: {e}")

    def quick_create_team(self):
     """Hızlı ekip oluşturma fonksiyonu"""
     try:
        # Giriş alanlarından verileri alıyoruz
        team_name_input = self.quick_team_name.text().strip()  # Ekip adı
        team_type_input = self.quick_team_type.currentText().strip()  # Ekip tipi
        city = self.quick_team_location_city.currentText().strip()  # Şehir
        district = self.quick_team_location_district.currentText().strip()  # İlçe
        status = self.quick_team_status.currentText().strip()  # Ekip durumu
        
        # Şehir ve ilçe adı arasında virgül ve boşluk ile birleştir
        location = f"{city}, {district}"

        # Kontroller
        if not team_name_input:
            QMessageBox.warning(self, "Uyarı", "Ekip adı boş olamaz!")
            return
        if not city or not district:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir şehir ve ilçe seçiniz!")
            return

        # Mevcut ekipleri al
        teams_snapshot = self.db.child("teams").get()
        teams = teams_snapshot or {}

        # Son ID'yi belirle
        if teams:
           try:
               # Mevcut ekip ID'lerini int olarak al ve sıralı değilse sıfırları atla
               last_id = max(int(team.get("Ekip_ID", 0)) for team in teams.values() if str(team.get("Ekip_ID", "")).isdigit())
           except ValueError:
                # Eğer ID'ler geçerli değilse (örneğin string, None, vb.), last_id sıfır yap
                last_id = 0

        # Yeni ekip için ID oluştur
        new_team_id = last_id + 1  # Yeni ID


        # Yeni ekip için başlangıç verileri
        team_data = {
            "Ekip_ID": new_team_id,
            "name": team_name_input,  # Ekip adı
            "status": status,  # Ekip durumu
            "type": team_type_input,  # Ekip tipi
            "location": location,  # Ekip konumu
            "members": []  # Başlangıçta üyeler boş bir liste olacak
        }

        # Firebase'e kayıt yapmadan önce düğüm adı kontrolü
        safe_team_name = team_name_input.replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")

        # Firebase'e kaydet
        self.db.child("teams").child(safe_team_name).set(team_data)

        self.ekipler[new_team_id] = team_data

        print(f"Yeni ekip yerel olarak eklendi: {self.ekipler[new_team_id]}")

        # Kullanıcıya başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", f"Ekip başarıyla oluşturuldu: {team_name_input}")

        # Yeni ekibi ağaç yapısına ekle
        self.reload_teams_tree()

     except Exception as e:
        # Hata durumunda detaylı bilgi
        QMessageBox.critical(self, "Hata", f"Ekip oluşturulurken hata oluştu: {e}")
        print(f"Debug: {e}")

    def get_selected_team_id(self):
     """Seçili ekibin ID'sini al"""
     try:
        selected_item = self.team_tree.currentItem()  # Seçili öğeyi al
        if selected_item:
            team_name = selected_item.text(0)  # Ekip adını al
            # Burada, ID'yi doğrudan eşleşen isimle alabileceğinizi varsayalım
            for team_id, team_data in self.ekipler.items():
                if team_data['name'] == team_name:
                    return team_id
        return None  # Eğer seçili ekip yoksa veya eşleşme bulunamazsa None döndür
     except Exception as e:
        print(f"Debug Hata: {e}")
        return None






    def add_team_to_tree(self, team_id, team_info):
     """
     Ekip bilgilerini GUI'ye ekler.
     :param team_id: Ekip kimliği (benzersiz ID)
     :param team_info: Ekip bilgilerini içeren sözlük
     """
     try:
        # Ekip öğesini oluştur ve ekip adını görünür yap
        team_name = team_info.get("name", "Bilinmeyen Ekip")
        team_item = QTreeWidgetItem([team_name])

        # Ekip kimliğini gizli bir alanda sakla
        team_item.setData(0, Qt.UserRole, str(team_id))

        # Ekip durumuna göre renklendirme
        status = team_info.get("status", "").upper()
        if status == "AFAD":
            team_item.setBackground(0, QColor("#4c9161"))  # Yeşil
        elif status == "STK/DİĞER":
            team_item.setBackground(0, QColor("#D14D1D"))  # Turuncu

        # Üyeleri ekip altına ekle
        for member in team_info.get("members", []):
            member_name = member.get("adSoyad", "Bilinmeyen Üye")
            member_id = member.get("Members_ID", "0")  # Üyenin ID'si
            
            # Üye öğesini oluştur
            member_item = QTreeWidgetItem([member_name])

            # Üyenin kimliğini sakla
            member_item.setData(0, Qt.UserRole, str(member_id))

            # Üye ikonunu ayarla (isteğe bağlı)
            member_item.setIcon(0, QIcon("icons/person.png"))

            # Üyeyi ekip öğesinin altına ekle
            team_item.addChild(member_item)

        # Ekip öğesini TreeWidget'e ekle
        self.team_tree.addTopLevelItem(team_item)

        # Ağacı açık şekilde göster
        team_item.setExpanded(True)

        # Debug: Başarıyla ekleme çıktısı
        print(f"Ekip GUI'ye eklendi: ID={team_id}, Ad={team_info.get('name')}")

     except Exception as e:
        # Hata çıktısı ve kullanıcı bildirimi
        QMessageBox.critical(self, "Hata", f"add_team_to_tree sırasında hata oluştu: {e}")
        print(f"Debug Hata: {e}")

    def reload_teams_tree(self):
     """Ağaç yapısını güncelleme"""
     try:
        self.team_tree.clear()  # Ağaç görünümünü temizle

        # self.ekipler bir sözlük olduğundan items() kullanarak her ekip üzerinde işlem yap
        for team_id, team_data in self.ekipler.items():
            # Ağaç görünümüne her ekibi ekleyin
            self.add_team_to_tree(team_id, team_data)

     except Exception as e:
        print(f"Debug Hata: Ağaç yenilenirken hata oluştu: {e}")
        QMessageBox.critical(self, "Hata", f"Ağaç yenilenirken bir hata oluştu: {e}")




    def show_personnel_details_from_table(self, item):
     """
     Tablodan personel detaylarını TC ve ID'ye göre gösterir.
     """
     # Seçili ekibin ID'sini alın
     team_id = self.get_selected_team_id()
     if not team_id:
        QMessageBox.warning(self, "Uyarı", "Herhangi bir ekip seçilmedi.")
        return

     # Tabloda seçili satırı alın
     row = item.row()
     personnel_name = self.personnel_table.item(row, 1).text()  # İlk sütundaki personel adı
     personnel_tc = self.personnel_table.item(row, 0).text()  # İkinci sütundaki TC bilgisi

     # Ekip bilgilerini alın
     team_info = self.ekipler.get(team_id)
     if not team_info:
        QMessageBox.warning(self, "Uyarı", "Ekip bilgileri bulunamadı.")
        return

     # Seçilen personelin bilgilerini bulun
     for person in team_info.get('members', []):  # "members" ekibin personel listesidir
        if (
            person['adSoyad'] == personnel_name and  # Ad-Soyad eşleşmesi
            person['tc'] == personnel_tc  # TC eşleşmesi
        ):
            # Personel detay penceresini göster
            dialog = PersonelDetayDialog(person, self)
            dialog.exec_()
            return

     # Eğer personel bulunamazsa uyarı göster
     QMessageBox.warning(self, "Uyarı", f"{personnel_name} isimli personel bulunamadı.")




    def add_personnel(self):
     """
     Seçili ekibe personel ekler ve Firebase'e kaydeder.
     """
     # 1. Seçili ekibin ID'sini al
     team_id = self.get_selected_team_id()
     if not team_id:
        QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
        return

     # 2. Seçili ekibin adı
     team_name = self.team_tree.currentItem().text(0)  # Doğru widget adı burada kullanılıyor

     # 3. Personel ekleme dialogunu aç
     dialog = PersonelEkleDialog(team_name=team_name, parent=self)
     if dialog.exec_() == QDialog.Accepted:
        # 4. Dialogdan personel bilgilerini al
        personnel_info = dialog.collect_personnel_info()
        if not personnel_info:
            QMessageBox.warning(self, "Uyarı", "Personel bilgileri alınamadı!")
            return

        # TC Kimlik Numarasını al
        tc_number = personnel_info.get("tc", "")
        if not tc_number or len(tc_number) != 11:  # TC Kimlik Numarası 11 hanelidir
            QMessageBox.warning(self, "Uyarı", "Geçerli bir TC Kimlik Numarası girin!")
            return

        try:
            # 5. Firebase'de ilgili ekibin referansını al
            team_ref = db.reference(f"teams/{team_id}")

            # 6. Mevcut personelleri al
            team_data = team_ref.get()
            if not team_data:
                QMessageBox.warning(self, "Uyarı", "Ekip bilgisi alınamadı!")
                return

            personnel_list = team_data.get("members", [])

            # 7. Aynı ekibe aynı personelin birden fazla kez eklenip eklenmediğini kontrol et
            for person in personnel_list:
                if person.get("TC") == tc_number:  # "TC:" yerine "TC"
                    QMessageBox.warning(self, "Uyarı", f"{tc_number} TC Kimlik Numarasına sahip kişi bu ekipte zaten mevcut!")
                    return

            # 8. Diğer ekiplerde bu personelin bulunup bulunmadığını kontrol et
            all_teams_data = db.reference("teams").get()  # Tüm ekipleri al
            for team_key, team_info in all_teams_data.items():
                for person in team_info.get("members", []):
                    if person.get("TC") == tc_number:  # "TC:" yerine "TC"
                        QMessageBox.warning(self, "Uyarı", f"{tc_number} TC Kimlik Numarasına sahip kişi başka bir ekipte zaten kayıtlı!")
                        return

            # 9. Yeni personelin ID'sini oluştur
            last_member_id = max([person.get("Members_ID", 0) for person in personnel_list], default=0)
            new_member_id = last_member_id + 1

            # 10. Yeni personel bilgilerini yapılandır
            new_personnel = {
                "Members_ID": new_member_id,
                "TC": personnel_info.get("tc", ""),  # "TC:" yerine "TC"
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

            # 11. Yeni personeli listeye ekle ve Firebase'de güncelle
            personnel_list.append(new_personnel)
            team_ref.update({"members": personnel_list})

            # 12. GUI'yi güncelle
            self.update_team_tree(team_name, personnel_list)

            # 13. Başarı mesajı göster
            QMessageBox.information(self, "Başarılı", f"{new_personnel['adSoyad']} başarıyla {team_name} ekibine eklendi.")

        except Exception as e:
            # Hata mesajı göster
            QMessageBox.critical(self, "Hata", f"Personel eklenirken hata oluştu: {e}")
            print(f"Debug: {e}")

    
    def remove_personnel(self):
     """Seçili personeli bir ekipten siler."""
     # 1. Seçili ekibin ID'sini al
     team_id = self.get_selected_team_id()
     if not team_id:
        QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
        return

     # 2. Firebase'den ekibin personel listesini al
     try:
        team_ref = self.db.child("teams").child(team_id)
        personnel_list = team_ref.child("members").get() or []

        if not personnel_list:
            QMessageBox.warning(self, "Uyarı", "Bu ekipte kayıtlı personel bulunmamaktadır.")
            return
     except Exception as e:
        QMessageBox.critical(self, "Hata", f"Personel listesi alınırken hata oluştu: {e}")
        return

     # 3. Personel seçimi için dialog başlat
     dialog = PersonelSecDialog(personnel_list=personnel_list)
     if dialog.exec_() == QDialog.Accepted:  # Kullanıcı bir personel seçtiyse
        selected_personnel = dialog.get_selected_personnel()

        if selected_personnel:
            try:
                # 4. Firebase'den personeli çıkar
                personnel_list = [p for p in personnel_list if p != selected_personnel]
                team_ref.update({"members": personnel_list})  # Firebase'i güncelle

                # 5. Python'daki sözlükten personeli çıkar
                if team_id in self.ekipler:
                    team = self.ekipler[team_id]
                    team['members'] = personnel_list
                    self.ekipler[team_id] = team

                # 6. GUI'yi güncelle
                self.update_team_tree(team_id, self.ekipler[team_id])

                # 7. Başarı mesajı
                QMessageBox.information(
                    self,
                    "Başarılı",
                    f"{selected_personnel['adSoyad']} başarıyla çıkarıldı."
                )
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Personel çıkarılırken hata oluştu: {e}")
        else:
            QMessageBox.warning(self, "Uyarı", "Geçerli bir personel seçilmedi.")
     else:
        QMessageBox.information(self, "İptal", "Personel silme işlemi iptal edildi.")


    
    def edit_personnel(self, team_id):
     """Seçili personeli bir ekipten düzenler.""" 
     # 1. Seçili ekibin ID'sini al
     team_id = self.get_selected_team_id()
     if not team_id:
        QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçiniz!")
        return

     # 2. Firebase'den ekibin personel listesini al
     try:
        team_ref = self.db.child("teams").child(team_id)
        team_info = team_ref.get() or {}
        personnel_list = team_ref.child("members").get() or []

        if not personnel_list:
            QMessageBox.warning(self, "Uyarı", "Bu ekipte kayıtlı personel bulunmamaktadır.")
            return
     except Exception as e:
        QMessageBox.critical(self, "Hata", f"Personel listesi alınırken hata oluştu: {e}")
        return
    
     # Personel seçimi için dialog başlat
     dialog = PersonelSecDialog(personnel_list=personnel_list, edit_mode=True)
     result = dialog.exec_()  # Dialog penceresinin sonucunu al

     # İptal durumu
     if result == QDialog.Rejected:
        QMessageBox.information(self, "Bilgi" ,"Personel Düzenleme İptal Edildi")
        return  # İptal durumunda hiçbir şey yapma

     if result == QDialog.Accepted:
        selected_personnel = dialog.get_selected_personnel()
        if not selected_personnel:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir personel seçiniz!")
            return

        # Seçilen personel ile düzenleme ekranını aç
        edit_dialog = PersonelDuzenleDialog(personnel=selected_personnel, parent=self)
        if edit_dialog.exec_() == QDialog.Accepted:
            updated_personnel = edit_dialog.get_updated_personnel()

            # 3. Güncellenmiş personeli listede değiştir
            try:
                # Mevcut personel bilgilerini güncelle
                index = next((i for i, p in enumerate(personnel_list) if p['Members_ID'] == selected_personnel['Members_ID']), None)

                if index is not None:
                    # ID'yi de güncel personel bilgisiyle beraber tut
                    updated_personnel['Members_ID'] = selected_personnel['Members_ID']  # Member_ID'yi ekle
                    personnel_list[index] = updated_personnel  # Güncel bilgiyi listeye yerleştir

                    # Firebase'e kaydet
                    self.db.child("teams").child(team_id).update({"members": personnel_list})  

                    QMessageBox.information(self, "Başarılı", f"{selected_personnel['adSoyad']} başarıyla güncellendi.")
                    # Ekip ağacını güncelle
                    team_name = team_info.get("team_name", "Bilinmiyor")
                    self.update_team_tree(team_name, team_info)
                else:
                    QMessageBox.warning(self, "Uyarı", "Seçilen personel bulunamadı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Personel düzenlenirken hata oluştu: {e}")







    def quick_delete_team(self):
     """Seçili ekibi silme"""
     try:
        # 1. Seçili ekibin ID'sini al
        team_id = self.get_selected_team_id()
        print(f"Debug: Seçili ekip ID'si: {team_id}")  # team_id'nin doğru alındığını kontrol et

        # 2. ID'yi kontrol et
        if not team_id:  # Eğer team_id geçerli değilse
            print(f"Debug: Seçili ekip ID'si geçerli değil!")
            QMessageBox.warning(self, "Uyarı", f"Seçili ekip ID'si geçerli değil!")
            return

        if team_id not in self.ekipler:
            print(f"Debug: ID {team_id} self.ekipler içinde bulunamadı!")
            QMessageBox.warning(self, "Uyarı", f"Seçili ekip {team_id} bulunamadı!")
            return
        else:
            print(f"Debug: ID {team_id} eşleşti. Ekip bilgisi: {self.ekipler[team_id]}")

        # 3. Seçili ekibin adı
        team_name = self.team_tree.currentItem().text(0)  # İlk sütundaki adı al
        if not team_name:
            QMessageBox.warning(self, "Uyarı", "Seçili ekip adı bulunamadı!")
            return

        # 4. Sözlükte ekip bilgilerini al
        team_info = self.ekipler.get(team_id)
        if not team_info:
            QMessageBox.warning(self, "Uyarı", "Seçili ekip bulunamadı!")
            return

        # 5. Silme onayı
        reply = QMessageBox.question(
            self,
            "Ekip Silme Onayı",
            f"{team_name} ({team_id}) ekibini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 6. Firebase'e güvenli ID ile silme
            safe_team_id = str(team_id).replace(".", "_").replace("#", "_").replace("$", "_").replace("[", "_").replace("]", "_")
            print(f"Debug: Firebase için güvenli team_id: {safe_team_id}")

            self.db.child("teams").child(safe_team_id).delete()  # Firebase'deki "teams/{safe_team_id}" düğümünü siler
            print(f"Debug: {team_name} ({safe_team_id}) Firebase'den silindi.")

            # 7. Python sözlüğünden sil
            del self.ekipler[team_id]

            # 8. GUI'den sil
            self.reload_teams_tree()  # Ekipler ağaç yapısını yeniden yükle

            # 9. Başarı bildirimi
            QMessageBox.information(self, "Başarılı", f"{team_name} ({team_id}) ekibi silindi!")
        else:
            print("Silme işlemi iptal edildi.")

     except Exception as e:
        QMessageBox.critical(self, "Hata", f"Ekip silinirken bir hata oluştu: {e}")
        print(f"Debug Hata: {e}")




class PersonnelFormFields:
    """Personel form alanlarını yöneten yardımcı sınıf"""
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
        """
        Tüm personel giriş alanlarını oluşturur.
        :param defaults: Varsayılan değerleri içeren bir dict.
        :return: Giriş alanları.
        """
        fields = {}
        defaults = defaults or {}

        for key, _ in PersonnelFormFields.INPUT_KEYS:
            input_field = QLineEdit(defaults.get(key, ""))
            # Telefon ve TC için özel doğrulama kuralları
            if key == "tc":
                # TC: 11 haneli rakam olmalı
                regex = QRegExp(r"^\d{11}$")  # 11 haneli sadece rakamlar
                validator = QRegExpValidator(regex)
                input_field.setValidator(validator)
            elif key == "phone" or key == "home_phone":
                # Telefon: 555-555-5555 formatı
                regex = QRegExp(r"^\d{3}-\d{3}-\d{4}$")  # 555-555-5555
                validator = QRegExpValidator(regex)
                input_field.setValidator(validator)

            fields[f"{key}_input"] = input_field

        return fields
        

    @staticmethod
    def add_form_rows(layout, input_fields):
        """Form düzenine giriş alanlarını ekler."""
        for key, label_text in PersonnelFormFields.INPUT_KEYS:
            layout.addRow(label_text, input_fields[f"{key}_input"])
 
    @staticmethod
    def collect_personnel_info(input_fields):
     """Personel bilgilerini toplar ve doğrular."""
     personnel_data = {}
    
     for key, _ in PersonnelFormFields.INPUT_KEYS:
        value = input_fields[f"{key}_input"].text()

        # TC doğrulaması
        if key == "tc" and (len(value) != 11 or not value.isdigit()):
            QMessageBox.warning(None, "Geçersiz TC", "TC numarası 11 haneli olmalı ve sadece rakamlardan oluşmalı.")
            return None  # Geçersizse geri dön

        # Telefon numarası doğrulaması
        if key in ["phone", "home_phone"] and not PersonnelFormFields.is_valid_phone(value):
            QMessageBox.warning(None, "Geçersiz Telefon", "Telefon numarası formatı hatalı (555-555-5555 olmalı).")
            return None  # Geçersizse geri dön

        # Diğer alanları sadece al
        personnel_data[key] = value

     return personnel_data

    @staticmethod
    def is_valid_phone(phone):
     """Telefon numarasının geçerliliğini kontrol eder (555-555-5555 formatı)."""
     import re
     phone_regex = r"^\d{3}-\d{3}-\d{4}$"
     return bool(re.match(phone_regex, phone))


class PersonelEkleDialog(QDialog):
    """Yeni personel ekleme dialog penceresi"""
    def __init__(self, team_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{team_name} - Personel Ekle")  # Ekip ismini başlığa ekler
        self.input_fields = PersonnelFormFields.create_input_fields()  # Form alanlarını oluşturur
        self.setupUI()  # UI'yi yapılandırır

    def setupUI(self):
        layout = QFormLayout()

        # Form alanlarını ekle (ad, soyad, TC numarası vb.)
        PersonnelFormFields.add_form_rows(layout, self.input_fields)

        # Kaydet ve İptal butonlarını oluştur
        btn_layout = QHBoxLayout()
        
        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.setStyleSheet(BUTTON_STYLE)  # Buton stilini belirle
        kaydet_btn.setIcon(QIcon('icons/save.png'))  # Kaydet ikonunu ekle
        kaydet_btn.clicked.connect(self.accept)  # Kaydet butonuna tıklanınca onayla
        
        iptal_btn = QPushButton("İptal")
        iptal_btn.setStyleSheet(RED_BUTTON_STYLE)  # İptal butonunun stilini belirle
        iptal_btn.clicked.connect(self.reject)  # İptal butonuna tıklanınca reddet
        
        btn_layout.addWidget(kaydet_btn)  # Kaydet butonunu yerleştir
        btn_layout.addWidget(iptal_btn)  # İptal butonunu yerleştir
        layout.addRow(btn_layout)  # Butonları formun alt kısmına ekle

        self.setLayout(layout)  # Layout'u pencerede ayarla

    def collect_personnel_info(self):
        """Personel bilgilerini toplar."""
        personnel_data = PersonnelFormFields.collect_personnel_info(self.input_fields)
        personnel_data["last_update"] = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        return personnel_data


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
            tc = person.get("TC", "Bilinmiyor")
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
        """Seçilen personeli döner"""
        secili_index = self.personel_listesi.currentRow()
        if secili_index < 0:
            return None
        return self.personnel_list[secili_index]


class PersonelDuzenleDialog(QDialog):
    """Personel bilgileri düzenleme dialog penceresi"""
    def __init__(self, personnel, parent=None):
        super().__init__(parent)
        self.personnel = personnel
        self.updated_personnel = None
        self.setWindowTitle("Personel Bilgilerini Düzenle")
        self.input_fields = self.create_input_fields(personnel)
        self.setupUI()

    def create_input_fields(self, personnel):
        """Personel bilgilerini doldurmak için form alanları oluşturur."""
        fields = {
            "TC": QLineEdit(personnel.get("TC", "")),            
            "adSoyad": QLineEdit(personnel.get("adSoyad", "")),
            "telefon": QLineEdit(personnel.get("telefon", "")),
            "ePosta": QLineEdit(personnel.get("ePosta", "")),
            "adres": QLineEdit(personnel.get("adres", "")),
            "evTelefonu": QLineEdit(personnel.get("evTelefonu", "")),
            "uzmanlik": QLineEdit(personnel.get("uzmanlik", "")),
            "unvan": QLineEdit(personnel.get("unvan", "")),
            "tecrube": QLineEdit(personnel.get("tecrube", "")),
        }
        return fields

    def setupUI(self):
        layout = QFormLayout()

        # Form alanlarını ekle
        for field_name, field_widget in self.input_fields.items():
            label = field_name.capitalize().replace("Soyad", "Soyad").replace("Telefonu", " Telefonu")
            
            # Düzenlenebilir olmayan alanlar için setReadOnly(True)
            if field_name in ["adres", "evTelefonu", "ePosta", "tecrube", "telefon", "unvan", "uzmanlik"]:  # Bu alanlar düzenlenebilir
                field_widget.setReadOnly(False)
            else:  # Diğerleri yalnızca görüntülenebilir
                field_widget.setReadOnly(True)
                field_widget.setStyleSheet("background-color: #808080;")  # Arka planı gri yaparak değiştirilemez olduğunu gösteriyoruz

            layout.addRow(label + ":", field_widget)

        # Kaydet ve İptal butonları
        btn_layout = QHBoxLayout()
        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.setStyleSheet(BUTTON_STYLE)
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
        """Değişiklikleri kaydet."""
        self.updated_personnel = {
            field_name: field_widget.text()
            for field_name, field_widget in self.input_fields.items()
        }
        self.updated_personnel["sonGuncellleme"] = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")
        self.accept()

    def get_updated_personnel(self):
        """Güncellenmiş personel bilgilerini döner."""
        return self.updated_personnel

