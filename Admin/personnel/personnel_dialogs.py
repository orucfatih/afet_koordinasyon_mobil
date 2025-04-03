from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton, QDialogButtonBox,
                           QLabel, QFormLayout, QHBoxLayout, QGroupBox, QTextBrowser,
                           QComboBox, QMessageBox, QListWidget, QLineEdit)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDateTime
from .constants import PERSONNEL_TABLE_HEADERS
from styles.styles_dark import *
from styles.styles_light import *
from database import db
from firebase_admin import db as firebase_db
from .state_manager import PersonnelStateManager


DIALOG_TITLES = {
    'add': "Personel Ekle",
    'edit': "Personel Bilgilerini Düzenle",
    'detail': "Personel Detayları",
    'message': "Mesaj Gönder"
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
        ara_btn.setIcon(QIcon("icons/call.png"))
        ara_btn.clicked.connect(lambda: self.ara(self.personel_data["phone"]))
        
        mesaj_btn = QPushButton(" Mesaj Gönder")
        mesaj_btn.setStyleSheet(BUTTON_STYLE)
        mesaj_btn.setIcon(QIcon("icons/message.png"))
        mesaj_btn.clicked.connect(lambda: self.mesaj_gonder(self.personel_data["phone"]))
        
        konum_iste_btn = QPushButton(" Konum İste")
        konum_iste_btn.setStyleSheet(BUTTON_STYLE)
        konum_iste_btn.setIcon(QIcon("icons/location.png"))
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


class BasePersonnelDialog(QDialog):
    def __init__(self, title, personnel=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.personnel = personnel
        self.input_fields = PersonnelFormFields.create_input_fields(personnel)
        self.initialize_dialog_ui()
    
    def initialize_dialog_ui(self):
        layout = QFormLayout()
        PersonnelFormFields.add_form_rows(layout, self.input_fields)
        
        self.add_status_combo(layout)
        self.add_action_buttons(layout)
        self.setLayout(layout)
    
    def add_status_combo(self, layout):
        """Kurum seçimi combo box'ını ekler"""
        self.status_combo = QComboBox()
        status_options = ["AFAD", "STK", "DİĞER"]
        self.status_combo.addItems(status_options)
        if self.personnel:
            current_status = self.personnel.get('status', 'AFAD')
            self.status_combo.setCurrentText(current_status)
        layout.addRow("Kurum:", self.status_combo)
    
    def add_action_buttons(self, layout):
        """Kaydet/İptal butonlarını ekler"""
        btn_layout = QHBoxLayout()
        kaydet_btn = create_styled_button(
            "Kaydet", 
            'icons/save.png', 
            BUTTON_STYLE, 
            self.save_personnel_data
        )
        iptal_btn = create_styled_button(
            "İptal", 
            style=RED_BUTTON_STYLE, 
            on_click=self.reject
        )
        
        btn_layout.addWidget(kaydet_btn)
        btn_layout.addWidget(iptal_btn)
        layout.addRow(btn_layout)
    
    def save_personnel_data(self):
        try:
            self.personnel_data = PersonnelFormFields.collect_personnel_info(self.input_fields)
            self.personnel_data["status"] = self.status_combo.currentText()
            self.personnel_data["last_update"] = QDateTime.currentDateTime().toString("dd.MM.yyyy HH:mm")

            if not self.personnel_data.get('name') or not self.personnel_data.get('phone'):
                QMessageBox.warning(self, "Uyarı", "İsim ve telefon alanları zorunludur!")
                return False

            current_team = PersonnelStateManager.get_current_team()
            print(f"Saving personnel for team: {current_team}") 
            if not current_team:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçin!")
                return False

            ref = firebase_db.reference(f'teams/{current_team}/members')

            new_personnel = {
                'name': self.personnel_data['name'],
                'phone': self.personnel_data['phone'],
                'status': self.personnel_data['status'],
                'last_update': self.personnel_data['last_update']
            }

            ref.push(new_personnel)
            QMessageBox.information(self, "Başarılı", "Personel başarıyla kaydedildi!")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt sırasında hata oluştu: {str(e)}")
            return False
    
    def get_personnel_data(self):
        return self.personnel_data


class PersonnelFormFields:
    """Personel form alanlarını yöneten yardımcı sınıf"""
    INPUT_KEYS = [
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
            fields[f"{key}_input"] = QLineEdit(defaults.get(key, ""))
        return fields

    @staticmethod
    def add_form_rows(layout, input_fields):
        """Form düzenine giriş alanlarını ekler."""
        for key, label_text in PersonnelFormFields.INPUT_KEYS:
            layout.addRow(label_text, input_fields[f"{key}_input"])

    @staticmethod
    def collect_personnel_info(input_fields):
        """Personel bilgilerini toplar."""
        return {
            key: input_fields[f"{key}_input"].text()
            for key, _ in PersonnelFormFields.INPUT_KEYS
        }


class PersonelEkleDialog(BasePersonnelDialog):
    def __init__(self, parent=None):
        super().__init__("Personel Ekle", parent=parent)


class PersonelDuzenleDialog(BasePersonnelDialog):
    def __init__(self, personnel, parent=None):
        super().__init__("Personel Bilgilerini Düzenle", personnel=personnel, parent=parent)


class PersonelSecDialog(QDialog):
    """Personel seçim dialog penceresi"""
    def __init__(self, personnel_list, parent=None, edit_mode=False):
        super().__init__(parent)
        self.personnel_list = personnel_list
        self.edit_mode = edit_mode
        self.setWindowTitle(DIALOG_TITLES['edit'] if edit_mode else "Personel Seç")
        self.initialize_selection_ui()
    
    def initialize_selection_ui(self):
        layout = QVBoxLayout()
        self.setup_personnel_list(layout)
        self.setup_selection_buttons(layout)
        self.setLayout(layout)
    
    def setup_personnel_list(self, layout):
        """Personel listesini hazırlar"""
        self.personel_listesi = QListWidget()
        for person in self.personnel_list:
            self.personel_listesi.addItem(f"{person['name']} - {person['title']}")
        layout.addWidget(self.personel_listesi)
    
    def setup_selection_buttons(self, layout):
        """Seçim butonlarını hazırlar"""
        btn_layout = QHBoxLayout()
        sec_btn = create_styled_button(
            "Düzenle" if self.edit_mode else "Seç",
            style=GREEN_BUTTON_STYLE,
            on_click=self.accept
        )
        iptal_btn = create_styled_button(
            "İptal",
            style=RED_BUTTON_STYLE,
            on_click=self.reject
        )
        
        btn_layout.addWidget(sec_btn)
        btn_layout.addWidget(iptal_btn)
        layout.addLayout(btn_layout)
    
    def get_selected_personnel(self):
        """Seçilen personeli döner"""
        secili_index = self.personel_listesi.currentRow()
        return self.personnel_list[secili_index]


def create_styled_button(text, icon_path=None, style=BUTTON_STYLE, on_click=None):
    """Stil uygulanmış buton oluşturur"""
    btn = QPushButton(text)
    btn.setStyleSheet(style)
    if icon_path:
        btn.setIcon(QIcon(icon_path))
    if on_click:
        btn.clicked.connect(on_click)
    return btn


def create_form_field(label, value="", readonly=False):
    """Form alanı oluşturur"""
    field = QLabel(str(value)) if readonly else QLineEdit(str(value))
    if readonly:
        field.setTextInteractionFlags(Qt.TextSelectableByMouse)
    return label, field
