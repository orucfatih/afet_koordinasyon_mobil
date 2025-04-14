from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QGroupBox, QTextEdit, QTreeWidget, QTreeWidgetItem,
                           QLineEdit, QPushButton, QMessageBox, QDialog,
                           QDialogButtonBox, QFormLayout, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from utils import get_icon_path
from .sms_auth import SMSAuthDialog
from styles.styles_dark import (CITIZEN_TABLE_STYLE, CITIZEN_GREEN_BUTTON_STYLE,
                              CITIZEN_DARK_BLUE_BUTTON_STYLE)
from simulations.sehirler_ve_ilceler import sehirler, bolgelere_gore_iller
import os

class MassSMSTab(QWidget):
    def __init__(self):
        super().__init__()
        self.city_tree = None
        self.selected_areas_text = None
        self.total_population_label = None
        self.message_text = None
        self.city_tree_manager = None
        self.is_authenticated = False
        self.send_button = None  # Gönder butonu referansı
        self.message_templates = {
            "Deprem Öncesi Bilgilendirme": "Deprem öncesi hazırlık için önemli bilgilendirme: Acil durum çantanızı hazırlayın, toplanma alanlarını öğrenin. Detaylı bilgi: afad.gov.tr",
            "Deprem Sonrası Bilgilendirme": "Bölgenizde deprem meydana geldi. Lütfen paniğe kapılmayın. En yakın toplanma alanına gidin. Yardım ekipleri yolda.",
            "Sel Uyarısı": "DİKKAT: Bölgenizde sel riski var. Lütfen güvenli bölgelere geçin ve resmi duyuruları takip edin.",
            "Tahliye Bildirimi": "ACİL: Bölgeniz tahliye edilecektir. Lütfen en yakın güvenli bölgeye geçin. Detaylar için: [LINK]",
            "Yardım Noktaları": "Size en yakın yardım noktaları: [ADRESLER]. İhtiyaçlarınız için bu noktalara başvurabilirsiniz."
        }
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Mesaj şablonları
        template_group = QGroupBox("Hazır SMS Şablonları")
        template_layout = QVBoxLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(list(self.message_templates.keys()))
        self.template_combo.currentTextChanged.connect(self.load_template)
        
        template_layout.addWidget(self.template_combo)
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Mesaj yazma alanı
        message_group = QGroupBox("SMS Mesajı")
        message_layout = QVBoxLayout()
        
        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText("SMS mesajınızı buraya yazın veya yukarıdan şablon seçin...")
        self.message_text.textChanged.connect(self.update_character_count)
        
        self.char_count_label = QLabel("Karakter sayısı: 0/160")
        self.char_count_label.setAlignment(Qt.AlignRight)
        
        message_layout.addWidget(self.message_text)
        message_layout.addWidget(self.char_count_label)
        
        # Öncelik seçenekleri
        priority_layout = QHBoxLayout()
        self.priority_check = QCheckBox("Acil Öncelikli Mesaj")
        self.priority_check.setToolTip("Acil durumlarda öncelikli gönderim için işaretleyin")
        priority_layout.addWidget(self.priority_check)
        
        self.confirmation_check = QCheckBox("Okundu Onayı İste")
        self.confirmation_check.setToolTip("Mesajın alıcılar tarafından okunduğunu takip edin")
        priority_layout.addWidget(self.confirmation_check)
        
        message_layout.addLayout(priority_layout)
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Bölge seçimi arayüzü
        region_layout = self.create_region_selection_ui()
        layout.addLayout(region_layout)
        
        # Gönderim seçenekleri
        options_group = QGroupBox("Gönderim Seçenekleri")
        options_layout = QVBoxLayout()
        
        # Hedef kitle seçimi
        target_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Tüm Nüfus",
            "Yalnızca Yetişkinler (18+)",
            "Acil Durum Ekipleri",
            "Sağlık Personeli",
            "Güvenlik Güçleri"
        ])
        target_layout.addWidget(QLabel("Hedef Kitle:"))
        target_layout.addWidget(self.target_combo)
        options_layout.addLayout(target_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Gönder butonu
        self.send_button = QPushButton(" SMS Gönder")
        self.send_button.setIcon(QIcon(get_icon_path('send.png')))
        self.send_button.setIconSize(QSize(16, 16))
        self.send_button.clicked.connect(self.send_sms)
        self.send_button.setStyleSheet(CITIZEN_GREEN_BUTTON_STYLE)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)

    def create_region_selection_ui(self):
        """Bölge seçimi arayüzünü oluştur"""
        top_layout = QHBoxLayout()
        
        # Sol taraf - Şehir ağacı
        city_group = QGroupBox("SMS Gönderilecek Bölgeler")
        city_layout = QVBoxLayout()
        
        self.city_tree = QTreeWidget()
        self.city_tree.setHeaderLabel("Şehirler ve İlçeler")
        self.city_tree.setMinimumHeight(300)
        
        city_layout.addWidget(self.city_tree)
        city_group.setLayout(city_layout)
        top_layout.addWidget(city_group)
        
        # Sağ taraf - Seçim özeti
        summary_group = QGroupBox("Seçim Özeti")
        summary_layout = QVBoxLayout()
        
        self.selected_areas_text = QTextEdit()
        self.selected_areas_text.setReadOnly(True)
        self.selected_areas_text.setMinimumHeight(100)
        
        self.total_population_label = QLabel("Toplam Alıcı: 0")
        self.total_population_label.setFont(QFont('Arial', 10, QFont.Bold))
        
        summary_layout.addWidget(self.selected_areas_text)
        summary_layout.addWidget(self.total_population_label)
        
        summary_group.setLayout(summary_layout)
        top_layout.addWidget(summary_group)
        
        # Şehir ağacı yöneticisini oluştur
        self.city_tree_manager = CityTreeManager(
            self.city_tree,
            self.selected_areas_text,
            self.total_population_label
        )
        
        return top_layout

    def load_template(self, template_name):
        """Seçilen şablonu mesaj alanına yükle"""
        if template_name in self.message_templates:
            self.message_text.setText(self.message_templates[template_name])

    def authenticate(self):
        """Kimlik doğrulama işlemi"""
        try:
            # Kimlik bilgilerini dosyadan oku
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'auth_config.txt')
            with open(config_path, 'r') as f:
                config = dict(line.strip().split('=') for line in f if '=' in line)
            
            dialog = SMSAuthDialog(self)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                username = dialog.username.text().strip()
                password = dialog.password.text().strip()
                
                if username == config.get('username') and password == config.get('password'):
                    self.is_authenticated = True
                    QMessageBox.information(self, "Başarılı", "Kimlik doğrulama başarılı!")
                    self.send_button.setText(" SMS Gönder")
                    return True
                else:
                    self.is_authenticated = False
                    QMessageBox.warning(self, "Hata", "Geçersiz kullanıcı adı veya şifre!")
                    dialog.username.clear()
                    dialog.password.clear()
                    return False
            return False
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kimlik doğrulama hatası: {str(e)}")
            return False

    def update_character_count(self):
        """SMS karakter sayısını güncelle"""
        count = len(self.message_text.toPlainText())
        self.char_count_label.setText(f"Karakter sayısı: {count}/160")
        
        # 160 karakteri aşarsa kırmızı yap
        if count > 160:
            self.char_count_label.setStyleSheet("color: red;")
        else:
            self.char_count_label.setStyleSheet("")

    def send_sms(self):
        """SMS gönderme işlemi"""
        if not self.is_authenticated:
            if not self.authenticate():
                return
            
        message = self.message_text.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Hata", "Lütfen bir mesaj yazın!")
            return
            
        if len(message) > 160:
            QMessageBox.warning(self, "Hata", "SMS mesajı 160 karakteri aşamaz!")
            return
            
        selected_districts = self.city_tree_manager.get_selected_districts()
        if not selected_districts:
            QMessageBox.warning(self, "Hata", "Lütfen en az bir bölge seçin!")
            return
            
        total_recipients = self.city_tree_manager.get_total_population()
        
        # Gönderim özeti oluştur
        summary = f"SMS Gönderim Özeti:\n\n"
        summary += f"- Hedef Kitle: {self.target_combo.currentText()}\n"
        summary += f"- Toplam Alıcı: {total_recipients:,} kişi\n"
        summary += f"- Öncelik: {'Acil' if self.priority_check.isChecked() else 'Normal'}\n"
        summary += f"- Okundu Onayı: {'Evet' if self.confirmation_check.isChecked() else 'Hayır'}\n"
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{summary}\n\nGönderimi onaylıyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Burada gerçek SMS gönderme API'si entegre edilecek
            QMessageBox.information(
                self,
                "Başarılı",
                f"SMS gönderimi başlatıldı!\n\n{summary}"
            )
            self.message_text.clear()

class CityTreeManager:
    """Şehir ağacı yönetimi için yardımcı sınıf"""
    def __init__(self, tree_widget, selected_areas_text, total_population_label):
        self.city_tree = tree_widget
        self.selected_areas_text = selected_areas_text
        self.total_population_label = total_population_label
        self.selected_districts = {}
        self.total_population = 0
        
        # Ağacı doldur ve sinyali bağla
        self.populate_city_tree()
        self.city_tree.itemChanged.connect(self.on_district_selection_changed)
    
    def populate_city_tree(self):
        """Şehir ağacını bölgelere göre doldur"""
        self.city_tree.clear()
        
        for bolge, bolge_sehirleri in bolgelere_gore_iller.items():
            bolge_item = QTreeWidgetItem(self.city_tree)
            bolge_item.setText(0, bolge)
            bolge_item.setFlags(bolge_item.flags() | Qt.ItemIsUserCheckable)
            bolge_item.setCheckState(0, Qt.Unchecked)
            
            for sehir in sorted(bolge_sehirleri):
                if sehir in sehirler:
                    sehir_item = QTreeWidgetItem(bolge_item)
                    sehir_item.setText(0, sehir)
                    sehir_item.setFlags(sehir_item.flags() | Qt.ItemIsUserCheckable)
                    sehir_item.setCheckState(0, Qt.Unchecked)
                    
                    for ilce, nufus in sorted(sehirler[sehir].items()):
                        ilce_item = QTreeWidgetItem(sehir_item)
                        ilce_item.setText(0, f"{ilce} ({nufus:,} kişi)")
                        ilce_item.setFlags(ilce_item.flags() | Qt.ItemIsUserCheckable)
                        ilce_item.setCheckState(0, Qt.Unchecked)
                        ilce_item.setData(0, Qt.UserRole, nufus)
    
    def on_district_selection_changed(self, item, column):
        """Bölge, şehir veya ilçe seçimi değiştiğinde"""
        self.city_tree.blockSignals(True)
        
        if item.parent() is None:  # Bölge seçimi
            self._handle_region_selection(item)
        elif item.parent().parent() is None:  # Şehir seçimi
            self._handle_city_selection(item)
        else:  # İlçe seçimi
            self._handle_district_selection(item)
        
        self.city_tree.blockSignals(False)
        self.update_selected_areas()
    
    def _handle_region_selection(self, item):
        """Bölge seçimini işle"""
        check_state = item.checkState(0)
        for i in range(item.childCount()):
            sehir_item = item.child(i)
            sehir_item.setCheckState(0, check_state)
            for j in range(sehir_item.childCount()):
                ilce_item = sehir_item.child(j)
                ilce_item.setCheckState(0, check_state)
    
    def _handle_city_selection(self, item):
        """Şehir seçimini işle"""
        check_state = item.checkState(0)
        # İlçeleri güncelle
        for i in range(item.childCount()):
            ilce_item = item.child(i)
            ilce_item.setCheckState(0, check_state)
        
        # Bölge durumunu güncelle
        self._update_parent_state(item.parent())
    
    def _handle_district_selection(self, item):
        """İlçe seçimini işle"""
        sehir_item = item.parent()
        self._update_parent_state(sehir_item)
        self._update_parent_state(sehir_item.parent())
    
    def _update_parent_state(self, parent_item):
        """Üst öğenin durumunu alt öğelere göre güncelle"""
        all_checked = True
        for i in range(parent_item.childCount()):
            if parent_item.child(i).checkState(0) != Qt.Checked:
                all_checked = False
                break
        parent_item.setCheckState(0, Qt.Checked if all_checked else Qt.Unchecked)
    
    def update_selected_areas(self):
        """Seçili bölgeleri ve toplam nüfusu güncelle"""
        self.selected_districts.clear()
        self.total_population = 0
        text = ""
        
        for i in range(self.city_tree.topLevelItemCount()):
            bolge_item = self.city_tree.topLevelItem(i)
            bolge = bolge_item.text(0)
            
            selected_cities = []
            for j in range(bolge_item.childCount()):
                sehir_item = bolge_item.child(j)
                sehir = sehir_item.text(0)
                
                selected_districts = []
                for k in range(sehir_item.childCount()):
                    ilce_item = sehir_item.child(k)
                    if ilce_item.checkState(0) == Qt.Checked:
                        ilce_name = ilce_item.text(0).split(" (")[0]
                        population = ilce_item.data(0, Qt.UserRole)
                        self.selected_districts[(sehir, ilce_name)] = population
                        self.total_population += population
                        selected_districts.append(f"{ilce_name} ({population:,} kişi)")
                
                if selected_districts:
                    if not selected_cities:
                        text += f"{bolge}:\n"
                    selected_cities.append(sehir)
                    text += f"  {sehir}:\n"
                    text += "\n".join(f"    - {d}" for d in selected_districts)
                    text += "\n\n"
        
        self.selected_areas_text.setText(text)
        self.total_population_label.setText(f"Toplam Alıcı: {self.total_population:,} kişi")
    
    def get_selected_districts(self):
        """Seçili ilçeleri döndür"""
        return self.selected_districts
    
    def get_total_population(self):
        """Toplam nüfusu döndür"""
        return self.total_population 