"""
test amaçlıdır bu dosya içerikler kullanılmayacaktır

"""






from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QFormLayout, 
                             QMessageBox, QTextEdit, QTabWidget, QComboBox,
                             QDateEdit, QCheckBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QValidator
from sample_data import CITIZEN_DATA
import datetime

class TCValidator(QValidator):
    def validate(self, input_str, pos):
        if not input_str:  # boş string için
            return QValidator.Acceptable, input_str, pos
            
        # Sadece rakamları kabul et
        if not input_str.isdigit():
            return QValidator.Invalid, input_str, pos
            
        # 11 haneden uzun olmasına izin verme
        if len(input_str) > 11:
            return QValidator.Invalid, input_str, pos
            
        # 11 haneden kısaysa devam etmesine izin ver
        if len(input_str) < 11:
            return QValidator.Intermediate, input_str, pos
            
        # 11 hane tamam ve hepsi rakam
        if len(input_str) == 11:
            return QValidator.Acceptable, input_str, pos
            
        return QValidator.Invalid, input_str, pos

class DeathRecordDialog(QDialog):
    def __init__(self, tc_no=None, parent=None):
        super().__init__(parent)
        self.tc_no = tc_no
        self.initUI()
        
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
        
        # Doğrulama Notları
        note_group = QGroupBox("Doğrulama Notları")
        note_layout = QVBoxLayout()
        self.verification_notes = QTextEdit()
        self.verification_notes.setPlaceholderText("Doğrulama süreciyle ilgili notlar...")
        note_layout.addWidget(self.verification_notes)
        note_group.setLayout(note_layout)
        layout.addWidget(note_group)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

class CitizenReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Ana layout
        layout = QVBoxLayout()
        
        # Alt sekmeler
        tabs = QTabWidget()
        
        # Sorgulama sekmesi
        query_tab = QWidget()
        query_layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Afet Kaynaklı Vefat Kayıtları")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        query_layout.addWidget(title)
        
        # TC Kimlik Sorgulama Grubu
        query_group = QGroupBox("TC Kimlik No ile Sorgulama")
        query_box_layout = QHBoxLayout()
        
        # TC Kimlik input
        self.tc_input = QLineEdit()
        self.tc_input.setPlaceholderText("11 haneli TC Kimlik No giriniz")
        self.tc_input.setMaxLength(11)
        self.tc_input.setValidator(TCValidator())
        
        # Sorgula butonu
        query_btn = QPushButton("Sorgula")
        query_btn.clicked.connect(self.query_citizen)
        
        query_box_layout.addWidget(self.tc_input)
        query_box_layout.addWidget(query_btn)
        query_group.setLayout(query_box_layout)
        query_layout.addWidget(query_group)
        
        # Sonuç gösterme alanı
        result_group = QGroupBox("Vatandaş Bilgileri")
        self.result_layout = QFormLayout()
        
        # Kişisel Bilgiler
        self.personal_info = QTextEdit()
        self.personal_info.setReadOnly(True)
        self.personal_info.setMinimumHeight(100)
        self.result_layout.addRow("Kişisel Bilgiler:", self.personal_info)
        
        # Nüfus Kayıt Bilgileri
        self.registry_info = QTextEdit()
        self.registry_info.setReadOnly(True)
        self.registry_info.setMinimumHeight(100)
        self.result_layout.addRow("Nüfus Kayıt Bilgileri:", self.registry_info)
        
        # Ölüm Belgesi Bilgileri
        self.death_info = QTextEdit()
        self.death_info.setReadOnly(True)
        self.death_info.setMinimumHeight(100)
        self.result_layout.addRow("Ölüm Belgesi Bilgileri:", self.death_info)
        
        # Doğrulama Durumu
        self.verification_info = QTextEdit()
        self.verification_info.setReadOnly(True)
        self.verification_info.setMinimumHeight(50)
        self.result_layout.addRow("Doğrulama Durumu:", self.verification_info)
        
        # Sosyal Güvenlik Bilgileri
        self.social_info = QTextEdit()
        self.social_info.setReadOnly(True)
        self.social_info.setMinimumHeight(50)
        self.result_layout.addRow("Sosyal Güvenlik Bilgileri:", self.social_info)
        
        # Yerleşim Yeri Bilgileri
        self.address_info = QTextEdit()
        self.address_info.setReadOnly(True)
        self.address_info.setMinimumHeight(50)
        self.result_layout.addRow("Yerleşim Yeri Bilgileri:", self.address_info)
        
        result_group.setLayout(self.result_layout)
        query_layout.addWidget(result_group)
        
        # Kayıt İşlem Butonları
        action_layout = QHBoxLayout()
        
        self.edit_record_btn = QPushButton("Kaydı Düzenle")
        self.edit_record_btn.clicked.connect(self.edit_death_record)
        self.edit_record_btn.setEnabled(False)
        
        self.cancel_record_btn = QPushButton("Kaydı İptal Et")
        self.cancel_record_btn.clicked.connect(self.cancel_death_record)
        self.cancel_record_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_record_btn)
        action_layout.addWidget(self.cancel_record_btn)
        query_layout.addLayout(action_layout)
        
        query_tab.setLayout(query_layout)
        tabs.addTab(query_tab, "Kayıt Sorgulama")
        
        # Yeni Kayıt sekmesi
        new_record_tab = QWidget()
        new_record_layout = QVBoxLayout()
        
        new_record_title = QLabel("Yeni Vefat Kaydı Oluştur")
        new_record_title.setFont(QFont('Arial', 14, QFont.Bold))
        new_record_title.setAlignment(Qt.AlignCenter)
        new_record_layout.addWidget(new_record_title)
        
        # TC Kimlik Grubu
        new_tc_group = QGroupBox("TC Kimlik No")
        new_tc_layout = QHBoxLayout()
        
        self.new_tc_input = QLineEdit()
        self.new_tc_input.setPlaceholderText("11 haneli TC Kimlik No giriniz")
        self.new_tc_input.setMaxLength(11)
        self.new_tc_input.setValidator(TCValidator())
        
        create_btn = QPushButton("Yeni Kayıt Oluştur")
        create_btn.clicked.connect(self.create_death_record)
        
        new_tc_layout.addWidget(self.new_tc_input)
        new_tc_layout.addWidget(create_btn)
        new_tc_group.setLayout(new_tc_layout)
        new_record_layout.addWidget(new_tc_group)
        
        new_record_tab.setLayout(new_record_layout)
        tabs.addTab(new_record_tab, "Yeni Kayıt")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Geçerli TC No
        self.current_tc = None

    def query_citizen(self):
        """TC Kimlik no ile vatandaş sorgulama"""
        tc = self.tc_input.text()
        
        # TC Kimlik no kontrolü
        if len(tc) != 11:
            QMessageBox.warning(self, "Hata", "TC Kimlik No 11 haneli olmalıdır!")
            return
            
        self.current_tc = tc
        # Veritabanında arama
        if tc in CITIZEN_DATA:
            data = CITIZEN_DATA[tc]
            
            # Kişisel bilgileri göster
            personal = data["kisisel_bilgiler"]
            self.personal_info.setText(
                f"Ad: {personal['ad']}\n"
                f"Soyad: {personal['soyad']}\n"
                f"Doğum Tarihi: {personal['dogum_tarihi']}\n"
                f"Cinsiyet: {personal['cinsiyet']}\n"
                f"Uyruk: {personal['uyruk']}\n"
                f"Medeni Hal: {personal['medeni_hal']}"
            )
            
            # Nüfus kayıt bilgilerini göster
            registry = data["nufus_kayit"]
            registry_text = (
                f"Anne Adı: {registry['anne_adi']}\n"
                f"Baba Adı: {registry['baba_adi']}\n"
                f"Doğum Yeri: {registry['dogum_yeri']}\n"
                f"Eş Adı: {registry['es_adi']}\n"
                f"Çocuklar: {', '.join(registry['cocuklar']) if registry['cocuklar'] else 'Yok'}\n"
                f"Ölüm Kaydı: {registry['olum_kaydi']['tarih']} - {registry['olum_kaydi']['yer']}"
            )
            self.registry_info.setText(registry_text)
            
            # Ölüm belgesi bilgilerini göster
            death = data["olum_belgesi"]
            death_text = (
                f"Belge No: {death['belge_no']}\n"
                f"Düzenleyen Kurum: {death['duzenleyen_kurum']}\n"
                f"Ölüm Nedeni: {death['neden']}"
            )
            self.death_info.setText(death_text)
            
            # Sosyal güvenlik bilgilerini göster
            social = data["sosyal_guvenlik"]
            social_text = (
                f"SGK Durumu: {social['sgk_durumu']}\n"
                f"Son Güncelleme: {social['son_guncellenme']}"
            )
            self.social_info.setText(social_text)
            
            # Yerleşim bilgilerini göster
            address = data["yerlesim"]
            address_text = (
                f"İl: {address['il']}\n"
                f"İlçe: {address['ilce']}\n"
                f"Mahalle: {address['mahalle']}\n"
                f"Adres: {address['adres']}"
            )
            self.address_info.setText(address_text)
            
            # Butonları aktif et
            self.edit_record_btn.setEnabled(True)
            self.cancel_record_btn.setEnabled(True)
            
        else:
            QMessageBox.warning(self, "Uyarı", "Bu TC Kimlik No'ya ait kayıt bulunamadı!")
            self.clear_fields()
            
            # Butonları deaktif et
            self.edit_record_btn.setEnabled(False)
            self.cancel_record_btn.setEnabled(False)

    def clear_fields(self):
        """Tüm alanları temizle"""
        self.personal_info.clear()
        self.registry_info.clear()
        self.death_info.clear()
        self.social_info.clear()
        self.address_info.clear()
        self.verification_info.clear()
        self.current_tc = None

    def create_death_record(self):
        """Yeni vefat kaydı oluştur"""
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
                self.edit_death_record(tc)
            return
            
        dialog = DeathRecordDialog(tc, self)
        if dialog.exec_() == QDialog.Accepted:
            # Burada veritabanına kayıt işlemi yapılacak
            QMessageBox.information(self, "Başarılı", "Yeni vefat kaydı oluşturuldu.")
            self.new_tc_input.clear()

    def edit_death_record(self, tc=None):
        """Vefat kaydını düzenle"""
        if tc is None:
            tc = self.current_tc
            
        if tc is None:
            return
            
        dialog = DeathRecordDialog(tc, self)
        if dialog.exec_() == QDialog.Accepted:
            # Burada veritabanında güncelleme işlemi yapılacak
            QMessageBox.information(self, "Başarılı", "Vefat kaydı güncellendi.")

    def cancel_death_record(self):
        """Vefat kaydını iptal et"""
        if self.current_tc is None:
            return
            
        reply = QMessageBox.question(
            self,
            "Kayıt İptali",
            "Bu vefat kaydını iptal etmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Burada veritabanında iptal işlemi yapılacak
            QMessageBox.information(self, "Başarılı", "Vefat kaydı iptal edildi.")
            self.clear_fields() 