from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QListWidget, 
                           QTextEdit, QComboBox, QTabWidget, 
                           QGroupBox, QLineEdit,
                           QFormLayout, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QDialog, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from stk_yonetim import STKYonetimTab
from kaynak_yonetimi import KaynakYonetimTab
from rapor import RaporYonetimTab
from afad_personel import PersonelYonetimTab
from harita import HaritaYonetimi


class NotificationDetailDialog(QDialog):
    """Bildirim Detayları Dialog Penceresi"""
    def __init__(self, title, details, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Detay metni
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setText(details)
        self.detail_text.setStyleSheet("background-color: #282829; padding: 10px;")
        
        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        layout.addWidget(self.detail_text)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class MessageItem(QListWidgetItem):
    """Özel Mesaj Item Sınıfı"""
    def __init__(self, sender, message, timestamp):
        super().__init__()
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        self.setText(f"{sender} - {timestamp}\n{message}")
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Unchecked)

class OperationManagementTab(QWidget):
    """Operasyon Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.harita = HaritaYonetimi()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Üst Panel - Harita ve Durum Bilgisi
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)


        self.messages_list = QListWidget()  # home sayfasında ekip mesajlaşma kısmı oluşturuluyor

        
        # Harita Bölümü
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        
        # Harita başlığı ve kontroller
        map_header = QWidget()
        map_header_layout = QHBoxLayout(map_header)
        
        map_title = QLabel("Afet Bölgesi Haritası")
        map_title.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        
        refresh_map_btn = QPushButton("Haritayı Yenile")
        refresh_map_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        map_header_layout.addWidget(map_title)
        map_header_layout.addWidget(refresh_map_btn)
        map_header_layout.addStretch()
        
        # Harita görünümü
        self.map_view = self.harita.initialize_map(height=470)
        
        map_layout.addWidget(map_header)
        map_layout.addWidget(self.map_view)
        
        # Sağ Panel - Bildirimler ve Görevler
        right_info_panel = QWidget()
        right_info_layout = QVBoxLayout(right_info_panel)
        
        # Bildirimler Listesi
        notifications_group = QGroupBox("Gelen Bildirimler")
        notifications_layout = QVBoxLayout()
        self.notification_list = QListWidget()
        self.notification_list.itemDoubleClicked.connect(self.show_notification_details)
        self.notification_list.setStyleSheet("""
            QListWidget {
                background-color: #262a3c;
                border: 1px solid #3a3f55;
                border-radius: 4px;
                color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3a3f55;
            }
            QListWidget::item:selected {
                background-color: #3a3f55;
            }
        """)
        notifications_layout.addWidget(self.notification_list)
        notifications_group.setLayout(notifications_layout)
        
        # Görevler Listesi
        tasks_group = QGroupBox("Aktif Görevler")
        tasks_layout = QVBoxLayout()
        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self.show_task_details)
        self.tasks_list.setStyleSheet("""
            QListWidget {
                background-color: #262a3c;
                border: 1px solid #3a3f55;
                border-radius: 4px;
                color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3a3f55;
            }
            QListWidget::item:selected {
                background-color: #3a3f55;
            }
        """)
        tasks_layout.addWidget(self.tasks_list)
        tasks_group.setLayout(tasks_layout)
        
        right_info_layout.addWidget(notifications_group)
        right_info_layout.addWidget(tasks_group)
        
        # Üst panel layout düzenleme
        top_layout.addWidget(map_widget, stretch=2)
        top_layout.addWidget(right_info_panel, stretch=1)
        
        # Alt Panel - Ekip Yönetimi
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Ekip Listesi
        team_list_group = QGroupBox("Mevcut Ekipler")
        team_list_layout = QVBoxLayout()
        
        self.team_list = QTableWidget()
        self.team_list.setColumnCount(5)
        self.team_list.setHorizontalHeaderLabels(["Ekip ID", "Ekip Lideri", "Kurum", "Durum", "İletişim"])
        self.team_list.setStyleSheet("""
            QTableWidget {
                background-color: #262a3c;
                color: white;
                gridline-color: #3a3f55;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1a1d2b;
                color: white;
                padding: 5px;
                border: 1px solid #3a3f55;
            }
        """)
        
        team_list_layout.addWidget(self.team_list)
        team_list_group.setLayout(team_list_layout)
        
        # Görevlendirme Paneli
        assignment_group = QGroupBox("Ekip Görevlendirme")
        assignment_layout = QFormLayout()
        
        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet("""
            QComboBox {
                background-color: #262a3c;
                color: white;
                padding: 5px;
                border: 1px solid #3a3f55;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Görev lokasyonu")
        self.location_input.setStyleSheet("""
            QLineEdit {
                background-color: #262a3c;
                color: white;
                padding: 5px;
                border: 1px solid #3a3f55;
                border-radius: 4px;
            }
        """)
        
        self.task_description = QTextEdit()
        self.task_description.setPlaceholderText("Görev detayları...")
        self.task_description.setStyleSheet("""
            QTextEdit {
                background-color: #262a3c;
                color: white;
                padding: 5px;
                border: 1px solid #3a3f55;
                border-radius: 4px;
            }
        """)
        
        assign_button = QPushButton("Görevi Ata")
        assign_button.clicked.connect(self.assign_task)
        assign_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        contact_button = QPushButton("Ekip ile İletişime Geç")
        contact_button.clicked.connect(self.contact_team)
        contact_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        assignment_layout.addRow("Ekip Seçimi:", self.team_combo)
        assignment_layout.addRow("Lokasyon:", self.location_input)
        assignment_layout.addRow("Görev Detayları:", self.task_description)
        assignment_layout.addRow("", assign_button)
        assignment_layout.addRow("", contact_button)
        
        assignment_group.setLayout(assignment_layout)
        
        # Alt panel layout düzenleme
        bottom_layout.addWidget(team_list_group, stretch=2)
        bottom_layout.addWidget(assignment_group, stretch=1)
        
        # Ana layout'a panelleri ekleme
        main_layout.addWidget(top_panel, stretch=2)
        main_layout.addWidget(bottom_panel, stretch=1)
        
        self.setLayout(main_layout)
        
        # Örnek verileri yükle
        self.load_sample_data()
        self.load_team_data()

    def load_team_data(self):
        """Örnek ekip verilerini yükler"""
        self.team_list.setRowCount(0)  # Mevcut satırları temizle
        
        teams = [
            ("T001", "Ahmet Yılmaz", "AFAD", "Müsait", "0555-111-2233"),
            ("T002", "Mehmet Demir", "STK-A", "Görevde", "0555-222-3344"),
            ("T003", "Ayşe Kaya", "AFAD", "Müsait", "0555-333-4455"),
            ("T004", "Ali Öztürk", "STK-B", "Görevde", "0555-444-5566"),
            ("T005", "Fatma Şahin", "AFAD", "Müsait", "0555-555-6677")
        ]
        
        for team in teams:
            row = self.team_list.rowCount()
            self.team_list.insertRow(row)
            for col, data in enumerate(team):
                item = QTableWidgetItem(str(data))
                if col == 3:  # Durum sütunu
                    if data == "Müsait":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    else:
                        item.setBackground(QBrush(QColor("#4CAF50")))
                item.setTextAlignment(Qt.AlignCenter)
                self.team_list.setItem(row, col, item)
            
            self.team_combo.addItem(f"{team[0]} - {team[1]} ({team[2]})")
        
        self.team_list.resizeColumnsToContents()

    def assign_task(self):
        """Seçili ekibe görev atar"""
        if not self.team_combo.currentText() or not self.location_input.text() or not self.task_description.toPlainText():
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return
            
        reply = QMessageBox.question(self, 'Görev Atama Onayı',
                                   f'Seçili ekibe görevi atamak istediğinize emin misiniz?\n\n'
                                   f'Ekip: {self.team_combo.currentText()}\n'
                                   f'Lokasyon: {self.location_input.text()}\n'
                                   f'Görev: {self.task_description.toPlainText()[:50]}...',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Başarılı", "Görev başarıyla atandı!")
            
            # Formu temizle
            self.location_input.clear()
            self.task_description.clear()

    def contact_team(self):
        """Seçili ekip ile iletişim penceresini açar"""
        selected_items = self.team_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçin!")
            return
            
        row = selected_items[0].row()
        team_id = self.team_list.item(row, 0).text()
        team_leader = self.team_list.item(row, 1).text()
        contact = self.team_list.item(row, 4).text()
        
        contact_dialog = QDialog(self)
        contact_dialog.setWindowTitle("Ekip İletişim")
        contact_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Ekip: {team_id}\nLider: {team_leader}\nİletişim: {contact}")
        info_label.setStyleSheet("color: white; background-color: #262a3c; padding: 10px;")
        
        message_input = QTextEdit()
        message_input.setPlaceholderText("Mesajınızı yazın...")
        message_input.setStyleSheet("""
            QTextEdit {
                background-color: #262a3c;
                color: white;
                border: 1px solid #3a3f55;
                border-radius: 4px;
            }
        """)
        
        send_button = QPushButton("Mesaj Gönder")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        layout.addWidget(info_label)
        layout.addWidget(message_input)
        layout.addWidget(send_button)
        
        contact_dialog.setLayout(layout)
        contact_dialog.exec_()

    def show_notification_details(self, item):
        """Bildirim detaylarını dialog penceresinde gösterir"""
        details = {
            "Acil: Su Baskını - Mahmutlar Mah.": 
                "Konum: Mahmutlar Mahallesi, Ana Cadde No:15\n"
                "Durum: Zemin katta su baskını\n"
                "Etkilenen Alan: Yaklaşık 500m²\n"
                "İhtiyaçlar: Su tahliye pompası, kum torbaları\n"
                "İletişim: Mahalle Muhtarı (555-123-4567)",
            "Yangın İhbarı - Atatürk Cad.": 
                "Konum: Atatürk Caddesi No:78\n"
                "Durum: 3 katlı binada yangın\n"
                "Risk: Yüksek\n"
                "Müdahale Eden Ekip: İtfaiye 3 araç\n"
                "Destek İhtiyacı: Ambulans, Güvenlik",
            "Bina Hasarı - Cumhuriyet Mah.":
                "Konum: Cumhuriyet Mahallesi, Okul Sokak\n"
                "Yapı Türü: 5 katlı apartman\n"
                "Hasar Durumu: Orta seviye çatlaklar\n"
                "Risk Değerlendirmesi: Yapısal analiz gerekli\n"
                "Tahliye Durumu: Kısmi tahliye önerisi"
        }
        
        dialog = NotificationDetailDialog(
            "Bildirim Detayları",
            details.get(item.text(), "Detaylı bilgi bulunamadı."),
            self
        )
        dialog.exec_()

    def show_task_details(self, item):
        """Görev detaylarını dialog penceresinde gösterir"""
        details = {
            "Arama Kurtarma - Merkez": 
                "Görev Tipi: Arama Kurtarma\n"
                "Lokasyon: Şehir Merkezi, Park Caddesi\n"
                "Ekip Sayısı: 3 ekip (12 personel)\n"
                "Ekipman: Termal kamera, Arama köpeği\n"
                "Durum: Devam ediyor\n"
                "Başlangıç: 10:30\n"
                "Tahmini Bitiş: 18:00",
            "Gıda Dağıtımı - Doğu Bölgesi":
                "Görev: Gıda ve Su Dağıtımı\n"
                "Bölge: Doğu Mahalleler\n"
                "Dağıtım Noktası Sayısı: 5\n"
                "Görevli Personel: 15\n"
                "Araç Sayısı: 3 kamyonet\n"
                "Dağıtılacak: 1000 gıda kolisi, 2000L su",
            "Sağlık Taraması - Batı Bölgesi":
                "Görev: Mobil Sağlık Taraması\n"
                "Kapsam: 5 mahalle\n"
                "Sağlık Personeli: 8 doktor, 12 hemşire\n"
                "Mobil Ünite: 2 araç\n"
                "Hedef Kitle: Yaşlılar ve çocuklar öncelikli\n"
                "İlerleme: 2/5 mahalle tamamlandı"
        }
        
        dialog = NotificationDetailDialog(
            "Görev Detayları",
            details.get(item.text(), "Detaylı bilgi bulunamadı."),
            self
        )
        dialog.exec_()

    def delete_selected_messages(self):
        """Seçili mesajları siler"""
        items_to_remove = []
        for i in range(self.messages_list.count()):
            item = self.messages_list.item(i)
            if item.checkState() == Qt.Checked:
                items_to_remove.append(item)
        
        for item in items_to_remove:
            self.messages_list.takeItem(self.messages_list.row(item))

    def load_sample_data(self):
        """Örnek verileri yükler"""
        # Bildirimler
        notifications = [
            "Acil: Su Baskını - Mahmutlar Mah.",
            "Yangın İhbarı - Atatürk Cad.",
            "Bina Hasarı - Cumhuriyet Mah."
        ]
        self.notification_list.addItems(notifications)
        
        # Görevler
        tasks = [
            "Arama Kurtarma - Merkez",
            "Gıda Dağıtımı - Doğu Bölgesi",
            "Sağlık Taraması - Batı Bölgesi"
        ]
        self.tasks_list.addItems(tasks)
        
        # Mesajlar
        messages = [
            MessageItem("Saha Ekibi 1", "Bölgede elektrik kesintisi devam ediyor.", "14:30"),
            MessageItem("112 Acil", "2 ambulans bölgeye yönlendirildi.", "14:45"),
            MessageItem("İtfaiye", "Yangın kontrol altına alındı.", "15:00")
        ]
        for message in messages:
            self.messages_list.addItem(message)


class AfetYonetimAdmin(QMainWindow):
    """Ana Uygulama Penceresi"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Admin Paneli")
        self.setGeometry(100, 100, 1400, 800)
        

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Tab widget oluşturma
        tabs = QTabWidget()
        tabs.addTab(OperationManagementTab(), "Operasyon Yönetimi")
        tabs.addTab(STKYonetimTab(), "STK Yönetimi")
        tabs.addTab(KaynakYonetimTab(), "Kaynak Yönetimi")
        tabs.addTab(RaporYonetimTab(), "Rapor")
        tabs.addTab(PersonelYonetimTab(), "Personel Yönetim")

        layout.addWidget(tabs)