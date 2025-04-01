from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
 QGroupBox, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit,
QComboBox, QMessageBox, QDialog, QFormLayout, QListWidgetItem, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from dialogs import NotificationDetailDialog
from sample_data import TEAM_DATA, NOTIFICATIONS, TASKS, MESSAGES, NOTIFICATION_DETAILS, TASK_DETAILS
from styles_dark import *
from styles_light import *
from .op_man_ui import MessageItem, create_team_dialog, create_contact_dialog, create_task_edit_dialog, TeamManagementDialog, get_icon_path
from .constants_op_man import TEAM_TABLE_HEADERS, STATUS_COLORS, TASK_PRIORITY_COLORS, TASK_PRIORITIES
from .table_utils import create_status_item, sync_tables
from .dialogs_op_man import TeamDialog
from dotenv import load_dotenv
import os

class OperationManagementTab(QWidget):
    """Operasyon Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        
        load_dotenv()

        API_KEY = os.getenv("API_KEY")
        self.api_key = API_KEY
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Üst Panel - Harita ve Durum Bilgisi
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)

        self.messages_list = QListWidget()  # Ekip mesajlaşma kısmı
        
        # Harita Bölümü
        self.map_widget = QWebEngineView()
        self.load_default_map()

        # Sağ Panel - Bildirimler ve Görevler
        right_info_panel = QWidget()
        right_info_layout = QVBoxLayout(right_info_panel)
        
        # Bildirimler Listesi
        notifications_group = QGroupBox("Gelen Bildirimler")
        notifications_layout = QVBoxLayout()
        
        # Bildirimler listesi
        self.notification_list = QListWidget()
        self.notification_list.itemDoubleClicked.connect(self.show_notification_details)
        self.notification_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.notification_list.setSelectionMode(QListWidget.MultiSelection)  # Çoklu seçim özelliği
        
        # Butonlar için container
        notification_buttons = QHBoxLayout()
        
        # Cevapla butonu
        reply_notification_btn = QPushButton(" Cevapla")
        reply_notification_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        reply_notification_btn.setIcon(QIcon(get_icon_path('customer-service.png')))
        reply_notification_btn.clicked.connect(self.reply_to_notification)
        
        # Silme butonu
        delete_notification_btn = QPushButton(" Sil")
        delete_notification_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_notification_btn.setIcon(QIcon(get_icon_path('bin.png')))
        delete_notification_btn.clicked.connect(self.delete_selected_notifications)
        
        # Butonları layout'a ekle
        notification_buttons.addWidget(reply_notification_btn)
        notification_buttons.addWidget(delete_notification_btn)
        
        # Widget'ları layout'a ekle
        notifications_layout.addWidget(self.notification_list)
        notifications_layout.addLayout(notification_buttons)
        
        notifications_group.setLayout(notifications_layout)
        
        # Görevler Listesi
        tasks_group = QGroupBox("Aktif Görevler")
        tasks_layout = QVBoxLayout()
        
        # Görevler listesi
        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self.show_task_details)
        self.tasks_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.tasks_list.setSelectionMode(QListWidget.MultiSelection)  # Çoklu seçim özelliği
        
        # Butonlar için container
        task_buttons = QHBoxLayout()
        
        # Düzenleme butonu
        edit_task_btn = QPushButton(" Düzenle")
        edit_task_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_task_btn.setIcon(QIcon(get_icon_path('equalizer.png')))
        edit_task_btn.clicked.connect(self.edit_selected_task)
        
        # Silme butonu
        delete_task_btn = QPushButton(" Sil")
        delete_task_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_task_btn.setIcon(QIcon(get_icon_path('bin.png')))
        delete_task_btn.clicked.connect(self.delete_selected_task)
        
        # Butonları layout'a ekle
        task_buttons.addWidget(edit_task_btn)
        task_buttons.addWidget(delete_task_btn)
        
        # Widget'ları layout'a ekle
        tasks_layout.addWidget(self.tasks_list)
        tasks_layout.addLayout(task_buttons)
        
        tasks_group.setLayout(tasks_layout)
        
        # Bildirimler ve görevler için minimum yükseklik ayarla
        notifications_group.setMinimumHeight(250)  
        tasks_group.setMinimumHeight(250)
        
        # Bildirimler ve görevler için stretch değerleri
        right_info_layout.addWidget(notifications_group, stretch=3)  
        right_info_layout.addWidget(tasks_group, stretch=3)  
        
        # Üst panel düzenleme
        top_layout.addWidget(self.map_widget, stretch=2)
        top_layout.addWidget(right_info_panel, stretch=1)
        
        # Alt Panel - Ekip Yönetimi ve Görevlendirme
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Ekip Listesi
        team_list_group = QGroupBox("Mevcut Ekipler")
        team_list_layout = QVBoxLayout()
        
        # Tablo widget'ını oluştur
        self.team_list = QTableWidget()
        self.team_list.setColumnCount(8)
        self.team_list.setHorizontalHeaderLabels(TEAM_TABLE_HEADERS)
        self.team_list.setStyleSheet(TABLE_WIDGET_STYLE)
        self.team_list.itemClicked.connect(self.toggle_team_status)  # Tıklama olayını bağla
        
        # Filtre Paneli
        filter_panel = QWidget()
        filter_layout = QHBoxLayout(filter_panel)
        
        # Kurum Filtresi
        institution_filter = QComboBox()
        institution_filter.addItem("Tüm Kurumlar")
        institution_filter.setStyleSheet(COMBOBOX_STYLE)
        institution_filter.currentTextChanged.connect(self.apply_filters)
        
        # Durum Filtresi
        status_filter = QComboBox()
        status_filter.addItems(["Tüm Durumlar", "Müsait", "Meşgul"])
        status_filter.setStyleSheet(COMBOBOX_STYLE)
        status_filter.currentTextChanged.connect(self.apply_filters)
        
        # Uzmanlık Filtresi
        expertise_filter = QComboBox()
        expertise_filter.addItem("Tüm Uzmanlıklar")
        expertise_filter.addItems([
            "USAR (Arama-Kurtarma)",
            "Sağlık Ekibi",
            "Enkaz Kaldırma",
            "İlk Yardım",
            "Yangın Söndürme",
            "Altyapı Onarım",
            "Lojistik Destek",
            "Güvenlik",
            "Barınma-İaşe",
            "Teknik Destek",
            "Haberleşme",
            "Koordinasyon"
        ])
        expertise_filter.setStyleSheet(COMBOBOX_STYLE)
        expertise_filter.currentTextChanged.connect(self.apply_filters)
        
        # Filtreleri layout'a ekle
        filter_layout.addWidget(QLabel("Kurum:"))
        filter_layout.addWidget(institution_filter)
        filter_layout.addWidget(QLabel("Durum:"))
        filter_layout.addWidget(status_filter)
        filter_layout.addWidget(QLabel("Uzmanlık:"))
        filter_layout.addWidget(expertise_filter)
        
        # Sınıf değişkenlerini kaydet
        self.institution_filter = institution_filter
        self.status_filter = status_filter
        self.expertise_filter = expertise_filter
        
        # Alt butonlar için container
        bottom_buttons = QHBoxLayout()
        
        # Ekip Yönetim Butonu
        team_management_btn = QPushButton(" Ekip Yönetimi")
        team_management_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        team_management_btn.setIcon(QIcon(get_icon_path('add-group.png')))
        team_management_btn.clicked.connect(self.show_team_management)
        
        # İletişim Butonu
        contact_button = QPushButton(" Ekip ile İletişime Geç")
        contact_button.clicked.connect(self.contact_team)
        contact_button.setStyleSheet(GREEN_BUTTON_STYLE)
        contact_button.setIcon(QIcon(get_icon_path('customer-service.png')))
        
        # Butonları yatay düzende ekle
        bottom_buttons.addWidget(team_management_btn)
        bottom_buttons.addWidget(contact_button)
        
        team_list_layout.addWidget(filter_panel)
        team_list_layout.addWidget(self.team_list)
        team_list_layout.addLayout(bottom_buttons)
        
        team_list_group.setLayout(team_list_layout)
        
        # Görevlendirme Paneli
        assignment_group = QGroupBox("Ekip Görevlendirme")
        assignment_layout = QVBoxLayout()
        
        # Ekip seçimi
        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet(COMBOBOX_STYLE)
        
        # Başlık ve Lokasyon için yatay layout
        title_location_layout = QHBoxLayout()
        
        # Başlık için dikey layout
        title_layout = QVBoxLayout()
        title_layout.addWidget(QLabel("Görev Başlığı:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Görev başlığı...")
        self.title_input.setStyleSheet(LINE_EDIT_STYLE)
        title_layout.addWidget(self.title_input)
        
        # Lokasyon için dikey layout
        location_layout = QVBoxLayout()
        location_layout.addWidget(QLabel("Lokasyon:"))
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Görev lokasyonu...")
        self.location_input.setStyleSheet(LINE_EDIT_STYLE)
        location_layout.addWidget(self.location_input)
        
        # Başlık ve lokasyonu yatay layout'a ekle
        title_location_layout.addLayout(title_layout)
        title_location_layout.addLayout(location_layout)
        
        # Öncelik seçimi için combobox
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(TASK_PRIORITIES)
        self.priority_combo.setCurrentText("Orta (2)")
        self.priority_combo.setStyleSheet(COMBOBOX_STYLE)
        
        # Görev detay girişi
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Görev detayları...")
        self.task_input.setMaximumHeight(100)
        self.task_input.setStyleSheet(TEXT_EDIT_STYLE)
        
        # Widget'ları layout'a ekle
        assignment_layout.addWidget(QLabel("Ekip Seç:"))
        assignment_layout.addWidget(self.team_combo)
        assignment_layout.addLayout(title_location_layout)  # Başlık ve lokasyonu yan yana ekle
        assignment_layout.addWidget(QLabel("Öncelik Seviyesi:"))
        assignment_layout.addWidget(self.priority_combo)
        assignment_layout.addWidget(QLabel("Görev Detayları:"))
        assignment_layout.addWidget(self.task_input)
        
        # Görev atama butonu
        assign_btn = QPushButton(" Görev Ata")
        assign_btn.setIcon(QIcon(get_icon_path('add1.png')))
        assign_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        assign_btn.clicked.connect(self.assign_task)
        
        assignment_layout.addWidget(assign_btn)
        assignment_group.setLayout(assignment_layout)
        
        # Ekip listesi ve görevlendirme için yükseklik ayarları
        team_list_group.setMinimumHeight(400)     # Ekip listesi minimum yükseklik
        assignment_group.setMinimumHeight(350)     # Görevlendirme minimum yükseklik
        assignment_group.setMaximumHeight(400)     # Görevlendirme maksimum yükseklik
        
        # Alt panel layout oranları
        bottom_layout.addWidget(team_list_group, stretch=2)
        bottom_layout.addWidget(assignment_group, stretch=1)
        
        # Ana layout oranları
        main_layout.addWidget(top_panel, stretch=2)    # Üst panel için daha fazla alan
        main_layout.addWidget(bottom_panel, stretch=3)  # Alt panel için daha fazla alan
        
        self.setLayout(main_layout)
        
        # Örnek verileri yükle
        self.load_sample_data()
        self.load_team_data()



    def load_default_map(self):
        """Türkiye merkezli bir harita yükler"""
        # Türkiye için merkez koordinatları (yaklaşık olarak Ankara)
        turkey_lat = 39.9334
        turkey_lng = 32.8597
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <title>Operasyon Haritası - Türkiye</title>
            <style>
                html, body, #map {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
            </style>
            <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key}&callback=initMap&libraries=places" async defer></script>
            <script>
                var map;
                var markers = [];
                
                function initMap() {{
                    map = new google.maps.Map(document.getElementById('map'), {{
                        center: {{lat: {turkey_lat}, lng: {turkey_lng}}},
                        zoom: 6,
                        mapTypeControl: true,
                        mapTypeControlOptions: {{
                            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                            position: google.maps.ControlPosition.TOP_RIGHT
                        }}
                    }});
                    
                    // Ekip üyeleri için işaretleyiciler ekle (gerçek uygulamada dinamik olacaktır)
                    addTeamMarkers();
                }}
                
                function addTeamMarkers() {{
                    // Örnek ekip lokasyonları - gerçek uygulamada bu veriler veri kaynağınızdan gelecektir
                    var teamLocations = [
                        {{lat: 39.9334, lng: 32.8597, name: 'Takım 1', status: 'Aktif'}},
                        {{lat: 41.0082, lng: 28.9784, name: 'Takım 2', status: 'Görevde'}},
                        {{lat: 38.4237, lng: 27.1428, name: 'Takım 3', status: 'Hazır'}}
                    ];
                    
                    for (var i = 0; i < teamLocations.length; i++) {{
                        var marker = new google.maps.Marker({{
                            position: {{lat: teamLocations[i].lat, lng: teamLocations[i].lng}},
                            map: map,
                            title: teamLocations[i].name + ' - ' + teamLocations[i].status
                        }});
                        
                        markers.push(marker);
                        
                        // Her işaretleyici için bilgi penceresi ekle
                        (function(marker, data) {{
                            var infoWindow = new google.maps.InfoWindow({{
                                content: '<div><strong>' + data.name + '</strong><br>' + 
                                         'Durum: ' + data.status + '</div>'
                            }});
                            
                            marker.addListener('click', function() {{
                                infoWindow.open(map, marker);
                            }});
                        }})(marker, teamLocations[i]);
                    }}
                }}
            </script>
        </head>
        <body>
            <div id="map"></div>
        </body>
        </html>
        """
        self.map_widget.setHtml(html)




    def refresh_map(self):
        self.harita.clear_map()  # Haritayı temizle
        self.map_view = self.harita.initialize_map(height=470)  # Yeniden başlat


    def add_team(self):
        """Yeni ekip eklemek için bir dialog açar."""
        dialog = create_team_dialog(self, self.save_new_team)
        dialog.exec_()


    def toggle_team_status(self, item):
        """Durum sütununa tıklandığında durumu değiştirir"""
        if self.team_list.column(item) == 3:  # Durum sütunu
            current_status = item.text()
            new_status = "Meşgul" if current_status == "Müsait" else "Müsait"
            
            # Yeni durum item'ı oluştur
            new_item = QTableWidgetItem(new_status)
            new_item.setTextAlignment(Qt.AlignCenter)
            
            # Duruma göre renk ayarla
            if new_status == "Müsait":
                new_item.setBackground(QBrush(QColor("#4CAF50")))
            else:
                new_item.setBackground(QBrush(QColor("#f44336")))
            
            # Hücreyi salt okunur yap
            new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
            
            # Değişikliği uygula
            self.team_list.setItem(item.row(), 3, new_item)


    def save_new_team(self, dialog, team_id_input, leader_input, institution_input, status_combo, contact_input):
        """Yeni ekibi kaydeder."""
        team_id = team_id_input.text()
        leader = leader_input.text()
        institution = institution_input.text()
        status = status_combo.currentText()
        contact = contact_input.text()
        
        row = self.team_list.rowCount()
        self.team_list.insertRow(row)
        self.team_list.setItem(row, 0, QTableWidgetItem(team_id))
        self.team_list.setItem(row, 1, QTableWidgetItem(leader))
        self.team_list.setItem(row, 2, QTableWidgetItem(institution))
        
        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)
        if status == "Müsait":
            status_item.setBackground(QBrush(QColor("#4CAF50")))
        else:
            status_item.setBackground(QBrush(QColor("#f44336")))
        self.team_list.setItem(row, 3, status_item)
        
        self.team_list.setItem(row, 4, QTableWidgetItem(contact))
        self.team_combo.addItem(f"{team_id} - {leader} ({institution})")
        self.team_list.resizeColumnsToContents()
        dialog.accept()

    def remove_selected_team(self):
        """Seçili ekibi kaldırır."""
        selected_items = self.team_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçin!")
            return
        
        selected_row = selected_items[0].row()
        self.team_list.removeRow(selected_row)


    def load_team_data(self):
        """Örnek ekip verilerini yükler"""
        self.team_list.setRowCount(0)
        
        # Kurumları topla
        institutions = set()
        
        for team in TEAM_DATA:
            institutions.add(team[2])  # Kurum adlarını topla
            row = self.team_list.rowCount()
            self.team_list.insertRow(row)
            for col, data in enumerate(team):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Durum sütunu için özel ayarlar
                if col == 3:  # Durum sütunu
                    if data == "Müsait":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    else:
                        item.setBackground(QBrush(QColor("#f44336")))
                    # Sadece durum sütununu salt okunur yap
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                self.team_list.setItem(row, col, item)
            
            self.team_combo.addItem(f"{team[0]} - {team[1]} ({team[2]})")
        
        # Kurum filtresine kurumları ekle
        self.institution_filter.addItems(sorted(institutions))
        
        self.team_list.resizeColumnsToContents()

    def apply_filters(self):
        """Seçili filtrelere göre ekip listesini filtreler"""
        selected_institution = self.institution_filter.currentText()
        selected_status = self.status_filter.currentText()
        selected_expertise = self.expertise_filter.currentText()
        
        for row in range(self.team_list.rowCount()):
            show_row = True
            institution = self.team_list.item(row, 2).text()
            status = self.team_list.item(row, 3).text()
            expertise = self.team_list.item(row, 5).text() if self.team_list.item(row, 5) else ""
            
            if selected_institution != "Tüm Kurumlar" and institution != selected_institution:
                show_row = False
            if selected_status != "Tüm Durumlar" and status != selected_status:
                show_row = False
            if selected_expertise != "Tüm Uzmanlıklar" and expertise != selected_expertise:
                show_row = False
                
            self.team_list.setRowHidden(row, not show_row)

    def assign_task(self):
        """Seçili ekibe görev atar"""
        # Seçili ekibi kontrol et
        selected_team = self.team_combo.currentText()
        if not selected_team:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ekip seçin!")
            return

        # Görev başlığı kontrolü
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Uyarı", "Lütfen görev başlığını girin!")
            return

        # Lokasyon kontrolü
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.warning(self, "Uyarı", "Lütfen görev lokasyonunu girin!")
            return

        # Görev detaylarını kontrol et
        task_details = self.task_input.toPlainText().strip()
        if not task_details:
            QMessageBox.warning(self, "Uyarı", "Lütfen görev detaylarını girin!")
            return

        # Öncelik seviyesini al
        priority = self.priority_combo.currentText()

        # Onay mesajı oluştur
        confirmation_text = (
            f"Aşağıdaki görev atamasını onaylıyor musunuz?\n\n"
            f"Ekip: {selected_team}\n"
            f"Başlık: {title}\n"
            f"Lokasyon: {location}\n"
            f"Öncelik: {priority}\n"
            f"Detaylar: {task_details}"
        )

        # Onay dialogu göster
        reply = QMessageBox.question(
            self,
            'Görev Atama Onayı',
            confirmation_text,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Görev metnini oluştur
            task_text = f"{title} - {location} - {priority}"

            # Yeni görev item'ı oluştur
            new_task = QListWidgetItem(task_text)
            new_task.setData(Qt.UserRole, priority)
            
            # Öncelik seviyesine göre arka plan rengini ayarla
            color = TASK_PRIORITY_COLORS.get(priority, "#000000")
            new_task.setBackground(QBrush(QColor(color)))
            
            # Görevi aktif görevler listesine ekle
            self.tasks_list.addItem(new_task)
            
            # Görev detaylarını TASK_DETAILS sözlüğüne ekle
            from sample_data import TASK_DETAILS
            TASK_DETAILS[task_text] = (
                f"Ekip: {selected_team}\n"
                f"Başlık: {title}\n"
                f"Lokasyon: {location}\n"
                f"Öncelik: {priority}\n"
                f"Detaylar: {task_details}"
            )
            
            # Input alanlarını temizle
            self.title_input.clear()
            self.location_input.clear()
            self.task_input.clear()
            self.priority_combo.setCurrentText("Orta (2)")
            
            # Başarılı mesajı göster
            QMessageBox.information(
                self,
                "Başarılı",
                f"Görev başarıyla atandı!\n\nEkip: {selected_team}"
            )


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
        
        dialog = create_contact_dialog(self, team_id, team_leader, contact)
        dialog.exec_()


    def show_notification_details(self, item):
        """Bildirim detaylarını dialog penceresinde gösterir"""
        dialog = NotificationDetailDialog(
            "Bildirim Detayları",
            NOTIFICATION_DETAILS.get(item.text(), "Detaylı bilgi bulunamadı."),
            self
        )
        dialog.exec_()


    def show_task_details(self, item):
        """Görev detaylarını dialog penceresinde gösterir"""
        dialog = NotificationDetailDialog(
            "Görev Detayları",
            TASK_DETAILS.get(item.text(), "Detaylı bilgi bulunamadı."),
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
        self.notification_list.addItems(NOTIFICATIONS)
        
        # Görevler
        self.tasks_list.addItems(TASKS)
        
        # Mesajlar
        for message_data in MESSAGES:
            message = MessageItem(
                message_data["sender"],
                message_data["message"],
                message_data["timestamp"]
            )
            self.messages_list.addItem(message)


    def edit_selected_task(self):
        """Seçili görevi düzenlemek için dialog açar"""
        current_item = self.tasks_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir görev seçin!")
            return
        
        dialog = create_task_edit_dialog(self, current_item, self.save_edited_task)
        dialog.exec_()
    
    def save_edited_task(self, item, new_text, dialog, priority):
        """Düzenlenen görevi kaydeder"""
        if item:
            # Görev metnini parçala ve yeni öncelik ile güncelle
            task_parts = item.text().split(" - ")
            if len(task_parts) >= 2:
                title = task_parts[0]
                location = task_parts[1]
                # Yeni metni oluştur
                updated_text = f"{title} - {location} - {priority}"
                item.setText(updated_text)
                item.setData(Qt.UserRole, priority)  # Öncelik seviyesini kaydet
                
                # Öncelik seviyesine göre arka plan rengini ayarla
                color = TASK_PRIORITY_COLORS.get(priority, "#000000")
                item.setBackground(QBrush(QColor(color)))
                
                # Görev detaylarını güncelle
                if updated_text in TASK_DETAILS:
                    details = TASK_DETAILS[updated_text].split("\n")
                    updated_details = []
                    for line in details:
                        if line.startswith("Öncelik:"):
                            updated_details.append(f"Öncelik: {priority}")
                        else:
                            updated_details.append(line)
                    TASK_DETAILS[updated_text] = "\n".join(updated_details)
            
            dialog.accept()
    
    def delete_selected_task(self):
        """Seçili görevi siler ve görev geçmişine ekler"""
        current_item = self.tasks_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir görev seçin!")
            return
        
        # Onay dialogu göster
        reply = QMessageBox.question(
            self,
            'Görev Silme Onayı',
            'Bu görevi tamamlandı olarak işaretleyip görev geçmişine eklemek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            task_text = current_item.text()
            # Görev metnini parçala
            task_parts = task_text.split(" - ")
            if len(task_parts) >= 2:
                task_type = task_parts[0]
                location = task_parts[1]
                priority = current_item.data(Qt.UserRole) if current_item.data(Qt.UserRole) else "Orta (2)"
                
                # Şu anki tarihi al
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Yeni görev geçmişi verisi oluştur
                new_task_history = [
                    current_date,
                    task_type,
                    location,
                    "N/A",  # Süre
                    priority,  # Öncelik seviyesi
                    "Tamamlandı",
                    "Görev tamamlandı"
                ]
                
                # Görev geçmişi verilerine ekle
                from sample_data import TASK_HISTORY_DATA
                TASK_HISTORY_DATA.insert(0, new_task_history)  # En başa ekle
                
                # Eğer ekip yönetimi penceresi açıksa, görev geçmişini güncelle
                if hasattr(self, 'team_management_dialog') and self.team_management_dialog.isVisible():
                    self.team_management_dialog.load_history_data()
                
                # Görevi aktif görevlerden kaldır
                self.tasks_list.takeItem(self.tasks_list.row(current_item))

    def delete_selected_notifications(self):
        """Seçili bildirimleri siler"""
        selected_items = self.notification_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bildirim seçin!")
            return
        
        reply = QMessageBox.question(
            self,
            'Bildirim Silme Onayı',
            f'{len(selected_items)} adet bildirimi silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in selected_items:
                self.notification_list.takeItem(self.notification_list.row(item))

    def reply_to_notification(self):
        """Seçili bildirime cevap verir"""
        selected_items = self.notification_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen cevaplamak için bildirim seçin!")
            return
        
        if len(selected_items) > 1:
            QMessageBox.warning(self, "Uyarı", "Lütfen tek bir bildirim seçin!")
            return
        
        notification = selected_items[0].text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Bildirim Cevapla")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # Seçili bildirimin detayları
        notification_details = QTextEdit()
        notification_details.setPlainText(NOTIFICATION_DETAILS.get(notification, "Detay bulunamadı."))
        notification_details.setReadOnly(True)
        notification_details.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        # Cevap yazma alanı
        reply_label = QLabel("Cevabınız:")
        reply_text = QTextEdit()
        reply_text.setPlaceholderText("Cevabınızı buraya yazın...")
        reply_text.setMinimumHeight(100)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(lambda: self.send_notification_reply(dialog, notification, reply_text.toPlainText()))
        buttons.rejected.connect(dialog.reject)
        
        # Layout'a widget'ları ekle
        layout.addWidget(QLabel("Bildirim Detayları:"))
        layout.addWidget(notification_details)
        layout.addWidget(reply_label)
        layout.addWidget(reply_text)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def send_notification_reply(self, dialog, notification, reply):
        """Bildirime verilen cevabı gönderir"""
        if not reply.strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cevap yazın!")
            return
        
        QMessageBox.information(
            self,
            "Başarılı",
            f"Cevabınız gönderildi!\n\nBildirim: {notification}\n\nCevap: {reply[:50]}..."
        )
        dialog.accept()

    def show_team_management(self):
        """Ekip yönetim penceresini gösterir"""
        self.team_management_dialog = TeamManagementDialog(self)  # Referansı sakla
        self.team_management_dialog.exec_()
