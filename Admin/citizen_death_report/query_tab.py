from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QFormLayout, 
                             QMessageBox, QTextEdit, QComboBox, QDateEdit, 
                             QCheckBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QDialog)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon
from utils import get_icon_path
from sample_data import CITIZEN_DATA
from .death_record_dialog import DeathRecordDialog
from styles.styles_dark import (CITIZEN_TABLE_STYLE, CITIZEN_DARK_BLUE_BUTTON_STYLE,
                              CITIZEN_RED_BUTTON_STYLE, CITIZEN_ORANGE_BUTTON_STYLE)

class QueryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_tc = None
        self.initUI()

    def initUI(self):
        # Ana layout
        layout = QVBoxLayout()
        
        # TC Kimlik Sorgulama Grubu
        query_group = QGroupBox("TC Kimlik No ile Sorgulama")
        query_box_layout = QHBoxLayout()
        
        # TC Kimlik input
        self.tc_input = QLineEdit()
        self.tc_input.setPlaceholderText("11 haneli TC Kimlik No giriniz")
        self.tc_input.setMaxLength(11)
        
        # Sorgula butonu
        query_btn = QPushButton(" Sorgula")
        query_btn.setIcon(QIcon(get_icon_path('search.png')))
        query_btn.setIconSize(QSize(16, 16))
        query_btn.setStyleSheet(CITIZEN_DARK_BLUE_BUTTON_STYLE)
        query_btn.clicked.connect(self.query_citizen)
        
        query_box_layout.addWidget(self.tc_input)
        query_box_layout.addWidget(query_btn)
        query_group.setLayout(query_box_layout)
        layout.addWidget(query_group)
        
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
        date_layout.setSpacing(2)
        
        self.death_date_start = QDateEdit()
        self.death_date_start.setCalendarPopup(True)
        self.death_date_start.setDate(QDate.currentDate().addMonths(-1))
        
        date_separator = QLabel("-")
        date_separator.setFixedWidth(8)
        date_separator.setAlignment(Qt.AlignCenter)
        
        self.death_date_end = QDateEdit()
        self.death_date_end.setCalendarPopup(True)
        self.death_date_end.setDate(QDate.currentDate())
        
        date_layout.addWidget(self.death_date_start)
        date_layout.addWidget(date_separator)
        date_layout.addWidget(self.death_date_end)
        date_layout.addSpacing(10)
        
        self.exact_date_checkbox = QCheckBox("Tam tarih ara")
        self.exact_date_checkbox.toggled.connect(self.toggle_exact_date)
        date_layout.addWidget(self.exact_date_checkbox)
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
        advanced_query_btn.setStyleSheet(CITIZEN_DARK_BLUE_BUTTON_STYLE)
        advanced_query_btn.clicked.connect(self.advanced_query)
        advanced_query_layout.addRow("", advanced_query_btn)
        
        advanced_query_group.setLayout(advanced_query_layout)
        layout.addWidget(advanced_query_group)
        
        # Sonuçlar Tablosu
        result_group = QGroupBox("Arama Sonuçları")
        result_layout = QVBoxLayout()
        
        table_control_layout = QHBoxLayout()
        
        clear_results_btn = QPushButton(" Sonuçları Temizle")
        clear_results_btn.setIcon(QIcon(get_icon_path('clear.png')))
        clear_results_btn.setIconSize(QSize(16, 16))
        clear_results_btn.clicked.connect(self.clear_results_table)
        clear_results_btn.setStyleSheet(CITIZEN_ORANGE_BUTTON_STYLE)
        table_control_layout.addWidget(clear_results_btn)
        table_control_layout.addStretch(1)
        
        result_layout.addLayout(table_control_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3a3f55;")
        result_layout.addWidget(line)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "TC No", "Ad", "Soyad", "Doğum Tarihi", "Vefat Tarihi", "Vefat Yeri", "Vefat Nedeni"
        ])
        
        self.results_table.setStyleSheet(CITIZEN_TABLE_STYLE)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.itemSelectionChanged.connect(self.display_selected_record)
        self.results_table.itemDoubleClicked.connect(self.on_table_double_click)
        
        result_layout.addWidget(self.results_table)
        
        # Seçili Kayıt Detayları
        details_layout = QFormLayout()
        
        self.personal_info = QTextEdit()
        self.personal_info.setReadOnly(True)
        self.personal_info.setMinimumHeight(70)
        self.personal_info.setMaximumHeight(100)
        details_layout.addRow("Kişisel Bilgiler:", self.personal_info)
        
        self.death_info = QTextEdit()
        self.death_info.setReadOnly(True)
        self.death_info.setMinimumHeight(70)
        self.death_info.setMaximumHeight(100)
        details_layout.addRow("Ölüm Belgesi Bilgileri:", self.death_info)
        
        self.address_info = QTextEdit()
        self.address_info.setReadOnly(True)
        self.address_info.setMinimumHeight(70)
        self.address_info.setMaximumHeight(100)
        details_layout.addRow("Yerleşim Yeri Bilgileri:", self.address_info)
        
        result_layout.addLayout(details_layout)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Kayıt İşlem Butonları
        action_layout = QHBoxLayout()
        
        self.edit_record_btn = QPushButton(" Kaydı Düzenle")
        self.edit_record_btn.setIcon(QIcon(get_icon_path('edit.png')))
        self.edit_record_btn.setIconSize(QSize(16, 16))
        self.edit_record_btn.clicked.connect(self.edit_death_record)
        self.edit_record_btn.setEnabled(False)
        self.edit_record_btn.setStyleSheet(CITIZEN_DARK_BLUE_BUTTON_STYLE)
        
        self.cancel_record_btn = QPushButton(" Kaydı İptal Et")
        self.cancel_record_btn.setIcon(QIcon(get_icon_path('delete.png')))
        self.cancel_record_btn.setIconSize(QSize(16, 16))
        self.cancel_record_btn.clicked.connect(self.cancel_death_record)
        self.cancel_record_btn.setEnabled(False)
        self.cancel_record_btn.setStyleSheet(CITIZEN_RED_BUTTON_STYLE)
        
        action_layout.addWidget(self.edit_record_btn)
        action_layout.addWidget(self.cancel_record_btn)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)

    def query_citizen(self):
        """TC Kimlik no ile vatandaş sorgulama"""
        tc = self.tc_input.text()
        
        if len(tc) != 11:
            QMessageBox.warning(self, "Hata", "TC Kimlik No 11 haneli olmalıdır!")
            return
            
        self.current_tc = tc
        
        tc_already_exists = False
        for row in range(self.results_table.rowCount()):
            if self.results_table.item(row, 0).text() == tc:
                tc_already_exists = True
                self.results_table.selectRow(row)
                break
        
        if not tc_already_exists:
            if tc in CITIZEN_DATA:
                data = CITIZEN_DATA[tc]
                current_row = self.results_table.rowCount()
                self.results_table.setRowCount(current_row + 1)
                
                self.results_table.setItem(current_row, 0, QTableWidgetItem(tc))
                
                personal = data["kisisel_bilgiler"]
                self.results_table.setItem(current_row, 1, QTableWidgetItem(personal['ad']))
                self.results_table.setItem(current_row, 2, QTableWidgetItem(personal['soyad']))
                self.results_table.setItem(current_row, 3, QTableWidgetItem(personal['dogum_tarihi']))
                
                registry = data["nufus_kayit"]
                self.results_table.setItem(current_row, 4, QTableWidgetItem(registry['olum_kaydi']['tarih']))
                self.results_table.setItem(current_row, 5, QTableWidgetItem(registry['olum_kaydi']['yer']))
                
                death = data["olum_belgesi"]
                self.results_table.setItem(current_row, 6, QTableWidgetItem(death['neden']))
                
                self.results_table.selectRow(current_row)
                self.edit_record_btn.setEnabled(True)
                self.cancel_record_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Uyarı", "Bu TC Kimlik No'ya ait kayıt bulunamadı!")
                if self.results_table.selectedItems():
                    self.edit_record_btn.setEnabled(True)
                    self.cancel_record_btn.setEnabled(True)
                else:
                    self.edit_record_btn.setEnabled(False)
                    self.cancel_record_btn.setEnabled(False)
        
        self.tc_input.clear()

    def toggle_exact_date(self, checked):
        if checked:
            self.death_date_end.setDate(self.death_date_start.date())
            self.death_date_end.setEnabled(False)
        else:
            self.death_date_end.setEnabled(True)

    def advanced_query(self):
        name = self.name_input.text().lower() if self.name_input.text() else ""
        surname = self.surname_input.text().lower() if self.surname_input.text() else ""
        death_location = self.death_location_input.text().lower() if self.death_location_input.text() else ""
        death_cause = self.death_cause_combo.currentText() if self.death_cause_combo.currentIndex() > 0 else ""
        
        date_start = self.death_date_start.date().toString("yyyy-MM-dd")
        date_end = self.death_date_end.date().toString("yyyy-MM-dd")
        exact_date_search = self.exact_date_checkbox.isChecked()
        
        matched_records = []
        for tc, data in CITIZEN_DATA.items():
            personal = data["kisisel_bilgiler"]
            registry = data["nufus_kayit"]
            death_data = data["olum_belgesi"]
            
            name_match = not name or name in personal['ad'].lower()
            surname_match = not surname or surname in personal['soyad'].lower()
            location_match = not death_location or death_location in registry['olum_kaydi']['yer'].lower()
            cause_match = not death_cause or death_cause == death_data['neden']
            
            death_date = registry['olum_kaydi']['tarih']
            if exact_date_search:
                date_match = death_date == date_start
            else:
                date_match = date_start <= death_date <= date_end
            
            if name_match and surname_match and location_match and cause_match and date_match:
                matched_records.append((tc, data))
        
        existing_tc_list = []
        for row in range(self.results_table.rowCount()):
            existing_tc_list.append(self.results_table.item(row, 0).text())
        
        if matched_records:
            start_row = self.results_table.rowCount()
            new_matches = 0
            
            for tc, data in matched_records:
                if tc in existing_tc_list:
                    continue
                
                current_row = start_row + new_matches
                self.results_table.setRowCount(current_row + 1)
                new_matches += 1
                
                personal = data["kisisel_bilgiler"]
                registry = data["nufus_kayit"]
                death_data = data["olum_belgesi"]
                
                self.results_table.setItem(current_row, 0, QTableWidgetItem(tc))
                self.results_table.setItem(current_row, 1, QTableWidgetItem(personal['ad']))
                self.results_table.setItem(current_row, 2, QTableWidgetItem(personal['soyad']))
                self.results_table.setItem(current_row, 3, QTableWidgetItem(personal['dogum_tarihi']))
                self.results_table.setItem(current_row, 4, QTableWidgetItem(registry['olum_kaydi']['tarih']))
                self.results_table.setItem(current_row, 5, QTableWidgetItem(registry['olum_kaydi']['yer']))
                self.results_table.setItem(current_row, 6, QTableWidgetItem(death_data['neden']))
            
            if new_matches > 0:
                self.results_table.selectRow(start_row)
                self.edit_record_btn.setEnabled(True)
                self.cancel_record_btn.setEnabled(True)
            else:
                QMessageBox.information(self, "Bilgi", "Arama kriterlerine uygun yeni kayıt bulunamadı!")
        else:
            if self.results_table.rowCount() == 0:
                QMessageBox.information(self, "Bilgi", "Arama kriterlerine uygun kayıt bulunamadı!")
                self.edit_record_btn.setEnabled(False)
                self.cancel_record_btn.setEnabled(False)
            else:
                QMessageBox.information(self, "Bilgi", "Arama kriterlerine uygun yeni kayıt bulunamadı!")
        
        self.name_input.clear()
        self.surname_input.clear()
        self.death_location_input.clear()
        self.death_cause_combo.setCurrentIndex(0)

    def display_selected_record(self):
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            return
        
        row = self.results_table.currentRow()
        tc = self.results_table.item(row, 0).text()
        self.current_tc = tc
        
        if tc in CITIZEN_DATA:
            data = CITIZEN_DATA[tc]
            
            personal = data["kisisel_bilgiler"]
            self.personal_info.setText(
                f"Ad: {personal['ad']}\n"
                f"Soyad: {personal['soyad']}\n"
                f"Doğum Tarihi: {personal['dogum_tarihi']}\n"
                f"Cinsiyet: {personal['cinsiyet']}\n"
                f"Uyruk: {personal['uyruk']}\n"
                f"Medeni Hal: {personal['medeni_hal']}"
            )
            
            death = data["olum_belgesi"]
            registry = data["nufus_kayit"]
            death_text = (
                f"Belge No: {death['belge_no']}\n"
                f"Düzenleyen Kurum: {death['duzenleyen_kurum']}\n"
                f"Ölüm Nedeni: {death['neden']}\n"
                f"Ölüm Kaydı: {registry['olum_kaydi']['tarih']} - {registry['olum_kaydi']['yer']}"
            )
            self.death_info.setText(death_text)
            
            address = data["yerlesim"]
            address_text = (
                f"İl: {address['il']}\n"
                f"İlçe: {address['ilce']}\n"
                f"Mahalle: {address['mahalle']}\n"
                f"Adres: {address['adres']}"
            )
            self.address_info.setText(address_text)
            
            self.edit_record_btn.setEnabled(True)
            self.cancel_record_btn.setEnabled(True)

    def clear_results_table(self):
        self.results_table.setRowCount(0)
        self.personal_info.clear()
        self.death_info.clear()
        self.address_info.clear()
        self.edit_record_btn.setEnabled(False)
        self.cancel_record_btn.setEnabled(False)

    def edit_death_record(self, tc=None):
        if tc is None:
            tc = self.current_tc
            
        if tc is None:
            return
            
        dialog = DeathRecordDialog(tc, self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Başarılı", "Vefat kaydı güncellendi.")

    def cancel_death_record(self):
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
            QMessageBox.information(self, "Başarılı", "Vefat kaydı iptal edildi.")
            self.clear_results_table()

    def on_table_double_click(self, item):
        row = item.row()
        tc = self.results_table.item(row, 0).text()
        self.edit_death_record(tc) 