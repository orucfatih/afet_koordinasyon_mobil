from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QFormLayout, 
                             QMessageBox, QTextEdit, QComboBox, QDateEdit, 
                             QCheckBox, QDialog)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon
from utils import get_icon_path
from sample_data import CITIZEN_DATA
from .death_record_dialog import DeathRecordDialog
from styles.styles_dark import CITIZEN_GREEN_BUTTON_STYLE

class NewRecordTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # TC Kimlik Grubu
        new_tc_group = QGroupBox("TC Kimlik No")
        new_tc_layout = QHBoxLayout()
        
        self.new_tc_input = QLineEdit()
        self.new_tc_input.setPlaceholderText("11 haneli TC Kimlik No giriniz")
        self.new_tc_input.setMaxLength(11)
        
        new_tc_layout.addWidget(self.new_tc_input)
        new_tc_group.setLayout(new_tc_layout)
        layout.addWidget(new_tc_group)
        
        # Form alanlarını içeren kaydırılabilir alan oluştur
        form_scroll = QWidget()
        form_layout = QVBoxLayout(form_scroll)
        
        # Temel Bilgiler Grubu
        basic_group = QGroupBox("Temel Bilgiler")
        basic_layout = QFormLayout()
        
        # Vefat Tarihi
        self.new_death_date = QDateEdit()
        self.new_death_date.setDate(QDate.currentDate())
        self.new_death_date.setCalendarPopup(True)
        basic_layout.addRow("Vefat Tarihi:", self.new_death_date)
        
        # Vefat Yeri
        self.new_death_location = QLineEdit()
        basic_layout.addRow("Vefat Yeri:", self.new_death_location)
        
        # Ölüm Nedeni
        self.new_death_cause = QComboBox()
        self.new_death_cause.addItems([
            "Deprem - Göçük Altında Kalma",
            "Deprem - Bina Çökmesi",
            "Deprem - İkincil Nedenler",
            "Sel Felaketi",
            "Yangın",
            "Diğer Doğal Afetler"
        ])
        basic_layout.addRow("Ölüm Nedeni:", self.new_death_cause)
        
        basic_group.setLayout(basic_layout)
        form_layout.addWidget(basic_group)
        
        # Belge Bilgileri Grubu
        doc_group = QGroupBox("Belge Bilgileri")
        doc_layout = QFormLayout()
        
        # Belge No
        self.new_doc_number = QLineEdit()
        doc_layout.addRow("Belge No:", self.new_doc_number)
        
        # Düzenleyen Kurum
        self.new_issuing_inst = QComboBox()
        self.new_issuing_inst.addItems([
            "AFAD",
            "Hastane",
            "Belediye",
            "Valilik",
            "Diğer"
        ])
        doc_layout.addRow("Düzenleyen Kurum:", self.new_issuing_inst)
        
        # Onay Durumu
        self.new_verification = QCheckBox("Belge Onaylı")
        doc_layout.addRow("Onay Durumu:", self.new_verification)
        
        doc_group.setLayout(doc_layout)
        form_layout.addWidget(doc_group)
        
        # Defin Bilgileri Grubu
        burial_group = QGroupBox("Defin Bilgileri")
        burial_layout = QFormLayout()
        
        # Defin Tarihi
        self.new_burial_date = QDateEdit()
        self.new_burial_date.setDate(QDate.currentDate())
        self.new_burial_date.setCalendarPopup(True)
        burial_layout.addRow("Defin Tarihi:", self.new_burial_date)
        
        # Defin Yeri
        self.new_burial_location = QLineEdit()
        burial_layout.addRow("Defin Yeri:", self.new_burial_location)
        
        # Defin İşlemini Gerçekleştiren Kurum
        self.new_burial_authority = QComboBox()
        self.new_burial_authority.addItems([
            "Belediye",
            "Din Görevlisi",
            "Mezarlıklar Müdürlüğü",
            "Aile",
            "Afet Koordinasyon Birimi",
            "Diğer"
        ])
        burial_layout.addRow("Defin Gerçekleştiren:", self.new_burial_authority)
        
        burial_group.setLayout(burial_layout)
        form_layout.addWidget(burial_group)
        
        # Olay Yeri Detayları Grubu
        location_details_group = QGroupBox("Olay Yeri Detayları")
        location_details_layout = QFormLayout()
        
        # Koordinat Bilgileri
        coord_layout = QHBoxLayout()
        self.new_latitude = QLineEdit()
        self.new_latitude.setPlaceholderText("Enlem (ör: 41.0082")
        self.new_longitude = QLineEdit()
        self.new_longitude.setPlaceholderText("Boylam (ör: 28.9784)")
        coord_layout.addWidget(self.new_latitude)
        coord_layout.addWidget(self.new_longitude)
        location_details_layout.addRow("Koordinatlar:", coord_layout)
        
        # Adres Detayları
        self.new_address_details = QTextEdit()
        self.new_address_details.setPlaceholderText("Olayın gerçekleştiği tam adres...")
        self.new_address_details.setMaximumHeight(60)
        location_details_layout.addRow("Adres Detayları:", self.new_address_details)
        
        location_details_group.setLayout(location_details_layout)
        form_layout.addWidget(location_details_group)
        
        # Tanık Bilgileri Grubu
        witness_group = QGroupBox("Tanık Bilgileri")
        witness_layout = QFormLayout()
        
        # Tanık İsim Soyisim
        self.new_witness_name = QLineEdit()
        witness_layout.addRow("İsim Soyisim:", self.new_witness_name)
        
        # Tanık TC Kimlik No
        self.new_witness_tc = QLineEdit()
        self.new_witness_tc.setPlaceholderText("11 haneli TC Kimlik No")
        self.new_witness_tc.setMaxLength(11)
        witness_layout.addRow("TC Kimlik No:", self.new_witness_tc)
        
        # Tanık İletişim Bilgileri
        self.new_witness_contact = QLineEdit()
        self.new_witness_contact.setPlaceholderText("Telefon numarası")
        witness_layout.addRow("İletişim:", self.new_witness_contact)
        
        # Tanık İlişki Durumu
        self.new_witness_relation = QComboBox()
        self.new_witness_relation.addItems([
            "Aile Üyesi",
            "Akraba",
            "Arkadaş/Komşu",
            "Görgü Tanığı",
            "Kamu Görevlisi",
            "Diğer"
        ])
        witness_layout.addRow("İlişki Durumu:", self.new_witness_relation)
        
        witness_group.setLayout(witness_layout)
        form_layout.addWidget(witness_group)
        
        layout.addWidget(form_scroll)
        
        # Kaydet Butonu
        save_btn = QPushButton(" Vefat Kaydını Oluştur")
        save_btn.setIcon(QIcon(get_icon_path('add.png')))
        save_btn.setIconSize(QSize(16, 16))
        save_btn.clicked.connect(self.save_new_death_record)
        save_btn.setStyleSheet(CITIZEN_GREEN_BUTTON_STYLE)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)

    def save_new_death_record(self):
        """Yeni vefat kaydını kaydet"""
        tc = self.new_tc_input.text()
        
        if len(tc) != 11:
            QMessageBox.warning(self, "Hata", "TC Kimlik No 11 haneli olmalıdır!")
            return
            
        # Eğer kayıt zaten varsa
        if tc in CITIZEN_DATA:
            reply = QMessageBox.question(
                self,
                "Kayıt Mevcut",
                "Bu TC Kimlik No'ya ait kayıt zaten mevcut. Düzenlemek ister misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                dialog = DeathRecordDialog(tc, self)
                if dialog.exec_() == QDialog.Accepted:
                    QMessageBox.information(self, "Başarılı", "Vefat kaydı güncellendi.")
            return
            
        # Burada veritabanına kayıt işlemi yapılacak
        QMessageBox.information(self, "Başarılı", "Yeni vefat kaydı oluşturuldu.")
        
        # Alanları temizle
        self.new_tc_input.clear()
        
        # DateEdit alanlarını bugüne ayarla
        current_date = QDate.currentDate()
        self.new_death_date.setDate(current_date)
        self.new_burial_date.setDate(current_date)
        
        # LineEdit alanlarını temizle
        self.new_death_location.clear()
        self.new_doc_number.clear()
        self.new_burial_location.clear()
        self.new_latitude.clear()
        self.new_longitude.clear()
        self.new_witness_name.clear()
        self.new_witness_tc.clear()
        self.new_witness_contact.clear()
        
        # TextEdit alanlarını temizle
        self.new_address_details.clear()
        
        # CheckBox'u temizle
        self.new_verification.setChecked(False)
        
        # ComboBox'ların ilk öğelerini seç
        self.new_death_cause.setCurrentIndex(0)
        self.new_issuing_inst.setCurrentIndex(0)
        self.new_burial_authority.setCurrentIndex(0)
        self.new_witness_relation.setCurrentIndex(0) 