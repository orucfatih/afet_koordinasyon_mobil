from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QFormLayout, 
                             QMessageBox, QTextEdit, QTabWidget, QComboBox,
                             QDateEdit, QCheckBox, QDialog, QDialogButtonBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QValidator, QIcon
from sample_data import CITIZEN_DATA
import datetime
import os

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

# Koyu tema tablo stili
TABLE_WIDGET_STYLE = """
    QTableWidget {
        background-color: #1e222f;
        alternate-background-color: #2c3e50;
        color: white;
        gridline-color: #3a3f55;
        border: 1px solid #3a3f55;
        border-radius: 4px;
    }
    QTableWidget::item {
        padding: 4px;
        border: none;
    }
    QTableWidget::item:selected {
        background-color: #3498db;
        color: white;
    }
    QHeaderView::section {
        background-color: #34495e;
        color: white;
        padding: 6px;
        border: 1px solid #3a3f55;
        font-weight: bold;
    }
    QTableWidget QTableCornerButton::section {
        background-color: #34495e;
        border: 1px solid #3a3f55;
    }
    QScrollBar:vertical {
        background-color: #2c3e50;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #3a3f55;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

# Buton Stilleri
GREEN_BUTTON_STYLE = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #2ecc71;
    }
    QPushButton:pressed {
        background-color: #219653;
    }
"""

DARK_BLUE_BUTTON_STYLE = """
    QPushButton {
        background-color: #2980b9;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3498db;
    }
    QPushButton:pressed {
        background-color: #1c587f;
    }
"""

RED_BUTTON_STYLE = """
    QPushButton {
        background-color: #c0392b;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e74c3c;
    }
    QPushButton:pressed {
        background-color: #922b21;
    }
"""

ORANGE_BUTTON_STYLE = """
    QPushButton {
        background-color: #d35400;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e67e22;
    }
    QPushButton:pressed {
        background-color: #b64100;
    }
"""

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
        self.witness_tc.setValidator(TCValidator())
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

    def load_existing_data(self):
        """Mevcut vatandaş bilgilerini form alanlarına doldur"""
        try:
            data = CITIZEN_DATA[self.tc_no]
            
            # Nüfus kaydından bilgileri al
            registry = data.get("nufus_kayit", {})
            olum_kaydi = registry.get("olum_kaydi", {})
            
            # Ölüm belgesi bilgilerini al
            death_data = data.get("olum_belgesi", {})
            
            # Temel bilgiler
            if "tarih" in olum_kaydi:
                # Tarih formatı: YYYY-MM-DD 
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
            
            # Belge bilgileri
            if "belge_no" in death_data:
                self.doc_number.setText(death_data["belge_no"])
            
            if "duzenleyen_kurum" in death_data:
                # ComboBox'ta kurumu seç
                kurum = death_data["duzenleyen_kurum"]
                index = self.issuing_inst.findText(kurum)
                if index >= 0:
                    self.issuing_inst.setCurrentIndex(index)
            
            # Örnek veri olduğu için gerçek defin bilgileri olmayabilir
            # Burada örnek olarak vefat tarihini defin tarihi olarak kullanıyoruz
            if "tarih" in olum_kaydi:
                date_str = olum_kaydi["tarih"]
                try:
                    date_parts = date_str.split("-")
                    if len(date_parts) == 3:
                        year, month, day = map(int, date_parts)
                        self.burial_date.setDate(QDate(year, month, day))
                except:
                    pass
            
            # Diğer örnek defin bilgileri
            yerlesim = data.get("yerlesim", {})
            if "il" in yerlesim and "ilce" in yerlesim:
                self.burial_location.setText(f"{yerlesim['il']} {yerlesim['ilce']} Mezarlığı")
                
            # Adres detayları
            if "adres" in yerlesim:
                self.address_details.setText(yerlesim['adres'])
                
            # Diğer alanlar için örnek verilerle doldurabiliriz
            # Burada gerçek veri olmadığı için, örnek veri ile oluşturmayacağız
            # Gerçek uygulamada, diğer tüm alanlar da veritabanından alınan değerlerle doldurulmalıdır
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veri yüklenirken bir hata oluştu: {str(e)}")

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
        query_btn = QPushButton(" Sorgula")
        query_btn.setIcon(QIcon(get_icon_path('search.png')))
        query_btn.setIconSize(QSize(16, 16))
        query_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        query_btn.clicked.connect(self.query_citizen)
        
        query_box_layout.addWidget(self.tc_input)
        query_box_layout.addWidget(query_btn)
        query_group.setLayout(query_box_layout)
        query_layout.addWidget(query_group)
        
        # Gelişmiş Arama Grubu
        advanced_query_group = QGroupBox("Gelişmiş Arama")
        advanced_query_layout = QFormLayout()
        
        # Ad
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Vatandaş adı")
        advanced_query_layout.addRow("Ad:", self.name_input)
        
        # Soyad
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Vatandaş soyadı")
        advanced_query_layout.addRow("Soyad:", self.surname_input)
        
        # Vefat Tarihi
        date_layout = QHBoxLayout()
        date_layout.setSpacing(2)  # Öğeler arasındaki boşluğu azalt
        
        self.death_date_start = QDateEdit()
        self.death_date_start.setCalendarPopup(True)
        self.death_date_start.setDate(QDate.currentDate().addMonths(-1))
        
        # Daha kompakt bir ayraç etiketi
        date_separator = QLabel("-")
        date_separator.setFixedWidth(8)
        date_separator.setAlignment(Qt.AlignCenter)
        
        self.death_date_end = QDateEdit()
        self.death_date_end.setCalendarPopup(True)
        self.death_date_end.setDate(QDate.currentDate())
        
        date_layout.addWidget(self.death_date_start)
        date_layout.addWidget(date_separator)
        date_layout.addWidget(self.death_date_end)
        
        # Araya küçük bir boşluk ekleyin
        date_layout.addSpacing(10)
        
        # Tam tarih arama seçeneği
        self.exact_date_checkbox = QCheckBox("Tam tarih ara")
        self.exact_date_checkbox.toggled.connect(self.toggle_exact_date)
        date_layout.addWidget(self.exact_date_checkbox)
        
        # Kalan boşlukları sağa doğru it
        date_layout.addStretch(1)
        
        advanced_query_layout.addRow("Vefat Tarihi:", date_layout)
        
        # Vefat Yeri
        self.death_location_input = QLineEdit()
        self.death_location_input.setPlaceholderText("Şehir, ilçe veya tam adres")
        advanced_query_layout.addRow("Vefat Yeri:", self.death_location_input)
        
        # Ölüm Nedeni
        self.death_cause_combo = QComboBox()
        self.death_cause_combo.addItem("Tümü")
        self.death_cause_combo.addItems([
            "Deprem - Göçük Altında Kalma",
            "Deprem - Bina Çökmesi",
            "Deprem - İkincil Nedenler",
            "Sel Felaketi",
            "Yangın",
            "Diğer Doğal Afetler"
        ])
        advanced_query_layout.addRow("Ölüm Nedeni:", self.death_cause_combo)
        
        # Gelişmiş Arama butonu
        advanced_query_btn = QPushButton(" Gelişmiş Arama Yap")
        advanced_query_btn.setIcon(QIcon(get_icon_path('search-advanced.png')))
        advanced_query_btn.setIconSize(QSize(16, 16))
        advanced_query_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        advanced_query_btn.clicked.connect(self.advanced_query)
        advanced_query_layout.addRow("", advanced_query_btn)
        
        advanced_query_group.setLayout(advanced_query_layout)
        query_layout.addWidget(advanced_query_group)
        
        # Sonuçları Tablo Formatında Gösterme
        result_group = QGroupBox("Arama Sonuçları")
        result_layout = QVBoxLayout()
        
        # Tablo buton kontrolü için yatay düzen
        table_control_layout = QHBoxLayout()
        
        # Sonuçları temizleme butonu
        clear_results_btn = QPushButton(" Sonuçları Temizle")
        clear_results_btn.setIcon(QIcon(get_icon_path('clear.png')))
        clear_results_btn.setIconSize(QSize(16, 16))
        clear_results_btn.clicked.connect(self.clear_results_table)
        clear_results_btn.setStyleSheet(ORANGE_BUTTON_STYLE)
        table_control_layout.addWidget(clear_results_btn)
        
        # Sağa boşluk ekleme
        table_control_layout.addStretch(1)
        
        result_layout.addLayout(table_control_layout)
        
        # Ayırıcı çizgi ekle
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3a3f55;")
        result_layout.addWidget(line)
        
        # Tablo oluştur
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "TC No", "Ad", "Soyad", "Doğum Tarihi", "Vefat Tarihi", "Vefat Yeri", "Vefat Nedeni"
        ])
        
        # Tablo ayarları - Ekipman listesi stilini uygula
        self.results_table.setStyleSheet(TABLE_WIDGET_STYLE)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)  # Satır numaralarını gizle
        self.results_table.itemSelectionChanged.connect(self.display_selected_record)
        # Çift tıklama ile düzenleme
        self.results_table.itemDoubleClicked.connect(self.on_table_double_click)
        
        result_layout.addWidget(self.results_table)
        
        # Seçili Kayıt Detayları
        details_layout = QFormLayout()
        
        # Kişisel Bilgiler
        self.personal_info = QTextEdit()
        self.personal_info.setReadOnly(True)
        self.personal_info.setMinimumHeight(70)
        self.personal_info.setMaximumHeight(100)
        details_layout.addRow("Kişisel Bilgiler:", self.personal_info)
        
        # Ölüm Belgesi Bilgileri
        self.death_info = QTextEdit()
        self.death_info.setReadOnly(True)
        self.death_info.setMinimumHeight(70)
        self.death_info.setMaximumHeight(100)
        details_layout.addRow("Ölüm Belgesi Bilgileri:", self.death_info)
        
        # Yerleşim Yeri Bilgileri
        self.address_info = QTextEdit()
        self.address_info.setReadOnly(True)
        self.address_info.setMinimumHeight(70)
        self.address_info.setMaximumHeight(100)
        details_layout.addRow("Yerleşim Yeri Bilgileri:", self.address_info)
        
        result_layout.addLayout(details_layout)
        result_group.setLayout(result_layout)
        query_layout.addWidget(result_group)
        
        # Kayıt İşlem Butonları
        action_layout = QHBoxLayout()
        
        self.edit_record_btn = QPushButton(" Kaydı Düzenle")
        self.edit_record_btn.setIcon(QIcon(get_icon_path('edit.png')))
        self.edit_record_btn.setIconSize(QSize(16, 16))
        self.edit_record_btn.clicked.connect(self.edit_death_record)
        self.edit_record_btn.setEnabled(False)
        self.edit_record_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        
        self.cancel_record_btn = QPushButton(" Kaydı İptal Et")
        self.cancel_record_btn.setIcon(QIcon(get_icon_path('delete.png')))
        self.cancel_record_btn.setIconSize(QSize(16, 16))
        self.cancel_record_btn.clicked.connect(self.cancel_death_record)
        self.cancel_record_btn.setEnabled(False)
        self.cancel_record_btn.setStyleSheet(RED_BUTTON_STYLE)
        
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
        
        new_tc_layout.addWidget(self.new_tc_input)
        new_tc_group.setLayout(new_tc_layout)
        new_record_layout.addWidget(new_tc_group)
        
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
        self.new_witness_tc.setValidator(TCValidator())
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
        
        # Doğrulama Notları
        note_group = QGroupBox("Doğrulama Notları")
        note_layout = QVBoxLayout()
        self.new_verification_notes = QTextEdit()
        self.new_verification_notes.setPlaceholderText("Doğrulama süreciyle ilgili notlar...")
        note_layout.addWidget(self.new_verification_notes)
        note_group.setLayout(note_layout)
        form_layout.addWidget(note_group)
        
        new_record_layout.addWidget(form_scroll)
        
        # Kaydet Butonu
        save_btn = QPushButton(" Vefat Kaydını Oluştur")
        save_btn.setIcon(QIcon(get_icon_path('add.png')))
        save_btn.setIconSize(QSize(16, 16))
        save_btn.clicked.connect(self.save_new_death_record)
        save_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        new_record_layout.addWidget(save_btn)
        
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
        
        # Tabloda bu TC no zaten var mı kontrol et
        tc_already_exists = False
        for row in range(self.results_table.rowCount()):
            if self.results_table.item(row, 0).text() == tc:
                tc_already_exists = True
                # Önceden varsa, o satırı seç
                self.results_table.selectRow(row)
                break
        
        # Eğer TC no tabloda yoksa, yeni sonuç olarak ekle
        if not tc_already_exists:
            # Veritabanında arama
            if tc in CITIZEN_DATA:
                data = CITIZEN_DATA[tc]
                
                # Yeni satır için mevcut satır sayısını al
                current_row = self.results_table.rowCount()
                self.results_table.setRowCount(current_row + 1)
                
                # TC No
                self.results_table.setItem(current_row, 0, QTableWidgetItem(tc))
                
                # Ad
                personal = data["kisisel_bilgiler"]
                self.results_table.setItem(current_row, 1, QTableWidgetItem(personal['ad']))
                
                # Soyad
                self.results_table.setItem(current_row, 2, QTableWidgetItem(personal['soyad']))
                
                # Doğum Tarihi
                self.results_table.setItem(current_row, 3, QTableWidgetItem(personal['dogum_tarihi']))
                
                # Vefat Tarihi ve Yeri
                registry = data["nufus_kayit"]
                self.results_table.setItem(current_row, 4, QTableWidgetItem(registry['olum_kaydi']['tarih']))
                self.results_table.setItem(current_row, 5, QTableWidgetItem(registry['olum_kaydi']['yer']))
                
                # Vefat Nedeni
                death = data["olum_belgesi"]
                self.results_table.setItem(current_row, 6, QTableWidgetItem(death['neden']))
                
                # Yeni eklenen satırı seç
                self.results_table.selectRow(current_row)
                
                # Butonları aktif et
                self.edit_record_btn.setEnabled(True)
                self.cancel_record_btn.setEnabled(True)
                
            else:
                QMessageBox.warning(self, "Uyarı", "Bu TC Kimlik No'ya ait kayıt bulunamadı!")
                # Butonları deaktif et (ancak önceki sonuçları silme)
                if self.results_table.selectedItems():
                    self.edit_record_btn.setEnabled(True)
                    self.cancel_record_btn.setEnabled(True)
                else:
                    self.edit_record_btn.setEnabled(False)
                    self.cancel_record_btn.setEnabled(False)
        
        # Giriş alanını temizle
        self.tc_input.clear()
    
    def toggle_exact_date(self, checked):
        """Tam tarih arama durumunda bitiş tarihini devre dışı bırak"""
        if checked:
            # Tam tarih araması seçildiğinde, bitiş tarihini başlangıç tarihi ile aynı yap ve devre dışı bırak
            self.death_date_end.setDate(self.death_date_start.date())
            self.death_date_end.setEnabled(False)
        else:
            # Tarih aralığı araması için bitiş tarihini tekrar etkinleştir
            self.death_date_end.setEnabled(True)

    def advanced_query(self):
        """Gelişmiş arama kriterleri ile sorgulama"""
        # Arama kriterlerini al
        name = self.name_input.text().lower() if self.name_input.text() else ""
        surname = self.surname_input.text().lower() if self.surname_input.text() else ""
        death_location = self.death_location_input.text().lower() if self.death_location_input.text() else ""
        death_cause = self.death_cause_combo.currentText() if self.death_cause_combo.currentIndex() > 0 else ""
        
        # Tarih aralığı
        date_start = self.death_date_start.date().toString("yyyy-MM-dd")
        date_end = self.death_date_end.date().toString("yyyy-MM-dd")
        exact_date_search = self.exact_date_checkbox.isChecked()
        
        # Tüm verilerde arama yap (örnek veri kullanarak simüle ediyoruz)
        matched_records = []
        for tc, data in CITIZEN_DATA.items():
            personal = data["kisisel_bilgiler"]
            registry = data["nufus_kayit"]
            death_data = data["olum_belgesi"]
            
            # Kriterleri kontrol et
            name_match = not name or name in personal['ad'].lower()
            surname_match = not surname or surname in personal['soyad'].lower()
            location_match = not death_location or death_location in registry['olum_kaydi']['yer'].lower()
            cause_match = not death_cause or death_cause == death_data['neden']
            
            # Tarih kontrolü - tam tarih veya aralık kontrolü
            death_date = registry['olum_kaydi']['tarih']
            if exact_date_search:
                # Tam tarih eşleşmesi kontrol et
                date_match = death_date == date_start
            else:
                # Tarih aralığında kontrolü yap
                date_match = date_start <= death_date <= date_end
            
            # Tüm kriterler eşleşirse kayıtları ekle
            if name_match and surname_match and location_match and cause_match and date_match:
                matched_records.append((tc, data))
        
        # Mevcut tabloda olan TC numaralarını tut
        existing_tc_list = []
        for row in range(self.results_table.rowCount()):
            existing_tc_list.append(self.results_table.item(row, 0).text())
        
        # Sonuçları tabloya yerleştir
        if matched_records:
            # Yeni başlangıç satırı mevcut satır sayısı
            start_row = self.results_table.rowCount()
            new_matches = 0
            
            for tc, data in matched_records:
                # Eğer TC numarası zaten tabloda varsa ekleme
                if tc in existing_tc_list:
                    continue
                
                # Yeni satır ekle
                current_row = start_row + new_matches
                self.results_table.setRowCount(current_row + 1)
                new_matches += 1
                
                personal = data["kisisel_bilgiler"]
                registry = data["nufus_kayit"]
                death_data = data["olum_belgesi"]
                
                # TC No
                self.results_table.setItem(current_row, 0, QTableWidgetItem(tc))
                
                # Ad
                self.results_table.setItem(current_row, 1, QTableWidgetItem(personal['ad']))
                
                # Soyad
                self.results_table.setItem(current_row, 2, QTableWidgetItem(personal['soyad']))
                
                # Doğum Tarihi
                self.results_table.setItem(current_row, 3, QTableWidgetItem(personal['dogum_tarihi']))
                
                # Vefat Tarihi ve Yeri
                self.results_table.setItem(current_row, 4, QTableWidgetItem(registry['olum_kaydi']['tarih']))
                self.results_table.setItem(current_row, 5, QTableWidgetItem(registry['olum_kaydi']['yer']))
                
                # Vefat Nedeni
                self.results_table.setItem(current_row, 6, QTableWidgetItem(death_data['neden']))
            
            # Yeni eklenen sonuç var mı kontrol et
            if new_matches > 0:
                # Son eklenen satırı seç
                self.results_table.selectRow(start_row)
                
                # Butonları aktif et
                self.edit_record_btn.setEnabled(True)
                self.cancel_record_btn.setEnabled(True)
            else:
                QMessageBox.information(self, "Bilgi", "Arama kriterlerine uygun yeni kayıt bulunamadı!")
        else:
            # Eğer tabloda hiç sonuç yoksa uyarı göster
            if self.results_table.rowCount() == 0:
                QMessageBox.information(self, "Bilgi", "Arama kriterlerine uygun kayıt bulunamadı!")
                self.edit_record_btn.setEnabled(False)
                self.cancel_record_btn.setEnabled(False)
            else:
                QMessageBox.information(self, "Bilgi", "Arama kriterlerine uygun yeni kayıt bulunamadı!")
        
        # Arama sonrası giriş alanlarını temizle
        self.name_input.clear()
        self.surname_input.clear()
        self.death_location_input.clear()
        self.death_cause_combo.setCurrentIndex(0)  # "Tümü" seçeneğine dön

    def display_selected_record(self):
        """Tabloda seçilen kaydın detaylarını göster"""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            return
        
        # Seçilen satırdan TC numarasını al
        row = self.results_table.currentRow()
        tc = self.results_table.item(row, 0).text()
        self.current_tc = tc
        
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
            
            # Ölüm belgesi bilgilerini göster
            death = data["olum_belgesi"]
            registry = data["nufus_kayit"]
            death_text = (
                f"Belge No: {death['belge_no']}\n"
                f"Düzenleyen Kurum: {death['duzenleyen_kurum']}\n"
                f"Ölüm Nedeni: {death['neden']}\n"
                f"Ölüm Kaydı: {registry['olum_kaydi']['tarih']} - {registry['olum_kaydi']['yer']}"
            )
            self.death_info.setText(death_text)
            
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

    def clear_results_table(self):
        """Arama sonuçları tablosunu temizle"""
        self.results_table.setRowCount(0)
        self.personal_info.clear()
        self.death_info.clear()
        self.address_info.clear()
        self.edit_record_btn.setEnabled(False)
        self.cancel_record_btn.setEnabled(False)

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
            self.clear_results_table()

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
                self.edit_death_record(tc)
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
        self.new_verification_notes.clear()
        
        # CheckBox'u temizle
        self.new_verification.setChecked(False)
        
        # ComboBox'ların ilk öğelerini seç
        self.new_death_cause.setCurrentIndex(0)
        self.new_issuing_inst.setCurrentIndex(0)
        self.new_burial_authority.setCurrentIndex(0)
        self.new_witness_relation.setCurrentIndex(0)

    def on_table_double_click(self, item):
        """Tablodaki bir satıra çift tıklandığında düzenleme penceresini aç"""
        # Seçilen satırın TC numarasını al
        row = item.row()
        tc = self.results_table.item(row, 0).text()
        
        # TC numarası ile düzenleme işlemini başlat
        self.edit_death_record(tc) 