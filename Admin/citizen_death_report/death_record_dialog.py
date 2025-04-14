from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QFormLayout, 
                             QMessageBox, QTextEdit, QComboBox, QDateEdit, 
                             QCheckBox, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
from sample_data import CITIZEN_DATA

class DeathRecordDialog(QDialog):
    def __init__(self, tc_no=None, parent=None):
        super().__init__(parent)
        self.tc_no = tc_no
        self.initUI()
        
        # TC numarası varsa, mevcut bilgileri doldur
        if self.tc_no and self.tc_no in CITIZEN_DATA:
            self.load_existing_data()
        
    def initUI(self):
        self.setWindowTitle("Vefat Kaydı Oluştur/Düzenle")
        layout = QVBoxLayout()
        
        # Temel Bilgiler Grubu
        basic_group = QGroupBox("Temel Bilgiler")
        basic_layout = QFormLayout()
        
        # Vefat Tarihi
        self.death_date = QDateEdit()
        self.death_date.setDate(QDate.currentDate())
        self.death_date.setCalendarPopup(True)
        basic_layout.addRow("Vefat Tarihi:", self.death_date)
        
        # Vefat Yeri
        self.death_location = QLineEdit()
        basic_layout.addRow("Vefat Yeri:", self.death_location)
        
        # Ölüm Nedeni
        self.death_cause = QComboBox()
        self.death_cause.addItems([
            "Deprem - Göçük Altında Kalma",
            "Deprem - Bina Çökmesi",
            "Deprem - İkincil Nedenler",
            "Sel Felaketi",
            "Yangın",
            "Diğer Doğal Afetler"
        ])
        basic_layout.addRow("Ölüm Nedeni:", self.death_cause)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Belge Bilgileri Grubu
        doc_group = QGroupBox("Belge Bilgileri")
        doc_layout = QFormLayout()
        
        # Belge No
        self.doc_number = QLineEdit()
        doc_layout.addRow("Belge No:", self.doc_number)
        
        # Düzenleyen Kurum
        self.issuing_inst = QComboBox()
        self.issuing_inst.addItems([
            "AFAD",
            "Hastane",
            "Belediye",
            "Valilik",
            "Diğer"
        ])
        doc_layout.addRow("Düzenleyen Kurum:", self.issuing_inst)
        
        # Onay Durumu
        self.verification = QCheckBox("Belge Onaylı")
        doc_layout.addRow("Onay Durumu:", self.verification)
        
        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)
        
        # Defin Bilgileri Grubu
        burial_group = QGroupBox("Defin Bilgileri")
        burial_layout = QFormLayout()
        
        # Defin Tarihi
        self.burial_date = QDateEdit()
        self.burial_date.setDate(QDate.currentDate())
        self.burial_date.setCalendarPopup(True)
        burial_layout.addRow("Defin Tarihi:", self.burial_date)
        
        # Defin Yeri
        self.burial_location = QLineEdit()
        burial_layout.addRow("Defin Yeri:", self.burial_location)
        
        # Defin İşlemini Gerçekleştiren Kurum
        self.burial_authority = QComboBox()
        self.burial_authority.addItems([
            "Belediye",
            "Din Görevlisi",
            "Mezarlıklar Müdürlüğü",
            "Aile",
            "Afet Koordinasyon Birimi",
            "Diğer"
        ])
        burial_layout.addRow("Defin Gerçekleştiren:", self.burial_authority)
        
        burial_group.setLayout(burial_layout)
        layout.addWidget(burial_group)
        
        # Olay Yeri Detayları Grubu
        location_details_group = QGroupBox("Olay Yeri Detayları")
        location_details_layout = QFormLayout()
        
        # Koordinat Bilgileri
        coord_layout = QHBoxLayout()
        self.latitude = QLineEdit()
        self.latitude.setPlaceholderText("Enlem (ör: 41.0082")
        self.longitude = QLineEdit()
        self.longitude.setPlaceholderText("Boylam (ör: 28.9784)")
        coord_layout.addWidget(self.latitude)
        coord_layout.addWidget(self.longitude)
        location_details_layout.addRow("Koordinatlar:", coord_layout)
        
        # Adres Detayları
        self.address_details = QTextEdit()
        self.address_details.setPlaceholderText("Olayın gerçekleştiği tam adres...")
        self.address_details.setMaximumHeight(60)
        location_details_layout.addRow("Adres Detayları:", self.address_details)
        
        location_details_group.setLayout(location_details_layout)
        layout.addWidget(location_details_group)
        
        # Tanık Bilgileri Grubu
        witness_group = QGroupBox("Tanık Bilgileri")
        witness_layout = QFormLayout()
        
        # Tanık İsim Soyisim
        self.witness_name = QLineEdit()
        witness_layout.addRow("İsim Soyisim:", self.witness_name)
        
        # Tanık TC Kimlik No
        self.witness_tc = QLineEdit()
        self.witness_tc.setPlaceholderText("11 haneli TC Kimlik No")
        self.witness_tc.setMaxLength(11)
        witness_layout.addRow("TC Kimlik No:", self.witness_tc)
        
        # Tanık İletişim Bilgileri
        self.witness_contact = QLineEdit()
        self.witness_contact.setPlaceholderText("Telefon numarası")
        witness_layout.addRow("İletişim:", self.witness_contact)
        
        # Tanık İlişki Durumu
        self.witness_relation = QComboBox()
        self.witness_relation.addItems([
            "Aile Üyesi",
            "Akraba",
            "Arkadaş/Komşu",
            "Görgü Tanığı",
            "Kamu Görevlisi",
            "Diğer"
        ])
        witness_layout.addRow("İlişki Durumu:", self.witness_relation)
        
        witness_group.setLayout(witness_layout)
        layout.addWidget(witness_group)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def load_existing_data(self):
        """Mevcut vatandaş bilgilerini form alanlarına doldur"""
        try:
            data = CITIZEN_DATA[self.tc_no]
            
            # Nüfus kaydından bilgileri al
            registry = data.get("nufus_kayit", {})
            olum_kaydi = registry.get("olum_kaydi", {})
            
            # Ölüm belgesi bilgilerini al
            death_data = data.get("olum_belgesi", {})
            
            # Tarih formatı: YYYY-MM-DD
            if "tarih" in olum_kaydi:
                date_str = olum_kaydi["tarih"]
                try:
                    date_parts = date_str.split("-")
                    if len(date_parts) == 3:
                        year, month, day = map(int, date_parts)
                        self.death_date.setDate(QDate(year, month, day))
                except:
                    # Tarih dönüştürülemezse bugünkü tarihi kullan
                    pass
            
            if "yer" in olum_kaydi:
                self.death_location.setText(olum_kaydi["yer"])
            
            if "neden" in death_data:
                # ComboBox'ta ölüm nedenini seç
                neden = death_data["neden"]
                index = self.death_cause.findText(neden)
                if index >= 0:
                    self.death_cause.setCurrentIndex(index)
            
            if "belge_no" in death_data:
                self.doc_number.setText(death_data["belge_no"])
            
            if "duzenleyen_kurum" in death_data:
                # ComboBox'ta kurumu seç
                kurum = death_data["duzenleyen_kurum"]
                index = self.issuing_inst.findText(kurum)
                if index >= 0:
                    self.issuing_inst.setCurrentIndex(index)
            
            # Diğer alanlar için örnek verilerle doldurabiliriz
            # Gerçek uygulamada, bu veriler veritabanından alınmalıdır
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veri yüklenirken bir hata oluştu: {str(e)}") 