from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
                             QGroupBox, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                             QComboBox, QMessageBox, QDialog, QFormLayout, QListWidgetItem, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from harita import HaritaYonetimi
from dialogs import NotificationDetailDialog
from styles_dark import *
from styles_light import *

from sample_data import TEAM_DATA, NOTIFICATIONS, TASKS, MESSAGES, NOTIFICATION_DETAILS, TASK_DETAILS
from harita import MapWidget
from operation_management.op_man_ui import MessageItem, create_team_dialog, create_contact_dialog, create_task_edit_dialog, TeamManagementDialog


class OperationManagementTab(QWidget):
    """Operasyon Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.harita = HaritaYonetimi()  # Harita yönetimi örneği
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Üst Panel - Harita ve Durum Bilgisi
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)

        self.messages_list = QListWidget()  # Ekip mesajlaşma kısmı
        
        # Harita Bölümü
        self.map_widget = MapWidget(self.harita)  # Harita widget'ını kullanıyoruz
        
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
        reply_notification_btn.setIcon(QIcon('icons/reply.png'))
        reply_notification_btn.clicked.connect(self.reply_to_notification)
        
        # Silme butonu
        delete_notification_btn = QPushButton(" Sil")
        delete_notification_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_notification_btn.setIcon(QIcon('icons/bin.png'))
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
        edit_task_btn.setIcon(QIcon('icons/equalizer.png'))
        edit_task_btn.clicked.connect(self.edit_selected_task)
        
        # Silme butonu
        delete_task_btn = QPushButton(" Sil")
        delete_task_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_task_btn.setIcon(QIcon('icons/bin.png'))
        delete_task_btn.clicked.connect(self.delete_selected_task)
        
        # Butonları layout'a ekle
        task_buttons.addWidget(edit_task_btn)
        task_buttons.addWidget(delete_task_btn)
        
        # Widget'ları layout'a ekle
        tasks_layout.addWidget(self.tasks_list)
        tasks_layout.addLayout(task_buttons)
        
        tasks_group.setLayout(tasks_layout)
        
        # Bildirimler ve görevler için minimum yükseklik ayarla
        notifications_group.setMinimumHeight(250)  # Bildirimlere daha fazla alan
        tasks_group.setMinimumHeight(250)         # Görevlere daha fazla alan
        
        # Bildirimler ve görevler için stretch değerleri
        right_info_layout.addWidget(notifications_group, stretch=3)  # Daha fazla alan
        right_info_layout.addWidget(tasks_group, stretch=3)  # Daha fazla alan
        
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
        self.team_list.setHorizontalHeaderLabels([
            "Ekip ID", "Ekip Lideri", "Kurum", "Durum", "İletişim",
            "Uzmanlık", "Personel Sayısı", "Ekipman Durumu"
        ])
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
        team_management_btn.setIcon(QIcon('icons/team-management.png'))
        team_management_btn.clicked.connect(self.show_team_management)
        
        # İletişim Butonu
        contact_button = QPushButton(" Ekip ile İletişime Geç")
        contact_button.clicked.connect(self.contact_team)
        contact_button.setStyleSheet(GREEN_BUTTON_STYLE)
        contact_button.setIcon(QIcon('icons/customer-service.png'))
        
        # Butonları yatay düzende ekle
        bottom_buttons.addWidget(team_management_btn)
        bottom_buttons.addWidget(contact_button)
        
        team_list_layout.addWidget(filter_panel)
        team_list_layout.addWidget(self.team_list)
        team_list_layout.addLayout(bottom_buttons)
        
        team_list_group.setLayout(team_list_layout)
        
        # Görevlendirme Paneli
        assignment_group = QGroupBox("Ekip Görevlendirme")
        assignment_layout = QFormLayout()

        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet(COMBOBOX_STYLE)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Görev lokasyonu")
        self.location_input.setStyleSheet(LINE_EDIT_STYLE)

        self.task_description = QTextEdit()
        self.task_description.setPlaceholderText("Görev detayları...")
        self.task_description.setStyleSheet(TEXT_EDIT_STYLE)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems([
            "Seviye 1 - Düşük",
            "Seviye 2 - Orta",
            "Seviye 3 - Yüksek",
            "Seviye 4 - Acil"
        ])
        self.priority_combo.setCurrentIndex(1)  # Varsayılan olarak "Seviye 2 - Orta" seçili
        self.priority_combo.setStyleSheet(COMBOBOX_STYLE)

        assign_button = QPushButton("Görevi Ata")
        assign_button.clicked.connect(self.assign_task)
        assign_button.setStyleSheet(BUTTON_STYLE)

        assignment_layout.addRow("Ekip Seçimi:", self.team_combo)
        assignment_layout.addRow("Lokasyon:", self.location_input)
        assignment_layout.addRow("Görev Detayları:", self.task_description)
        assignment_layout.addRow("Öncelik Seviyesi:", self.priority_combo)
        assignment_layout.addRow("", assign_button)

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
        """Seçili ekibe görev atar ve aktif görevler listesine ekler"""
        if not self.team_combo.currentText() or not self.location_input.text() or not self.task_description.toPlainText():
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return

        selected_priority = self.priority_combo.currentText()  # Seçili öncelik seviyesini al

        reply = QMessageBox.question(
            self, 'Görev Atama Onayı',
            f'Seçili ekibe görevi atamak istediğinize emin misiniz?\n\n'
            f'Ekip: {self.team_combo.currentText()}\n'
            f'Lokasyon: {self.location_input.text()}\n'
            f'Öncelik: {selected_priority}\n'
            f'Görev: {self.task_description.toPlainText()[:50]}...',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Görev metnini oluştur
            task_text = (f"Ekip: {self.team_combo.currentText()}\n"
                        f"Lokasyon: {self.location_input.text()}\n"
                        f"Öncelik: {selected_priority}\n"
                        f"Görev: {self.task_description.toPlainText()}")

            # Aktif görevler listesine ekle
            self.tasks_list.addItem(task_text)

            QMessageBox.information(self, "Başarılı", "Görev başarıyla atandı ve aktif görevlere eklendi!")

            # Formu temizle
            self.location_input.clear()
            self.task_description.clear()
            self.priority_combo.setCurrentIndex(1)  # Öncelik seviyesini varsayılana sıfırla


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
    
    def save_edited_task(self, item, new_text, dialog):
        """Düzenlenen görevi kaydeder"""
        item.setText(new_text)
        dialog.accept()
    
    def delete_selected_task(self):
        """Seçili görevi siler"""
        current_item = self.tasks_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir görev seçin!")
            return
        
        # Onay dialogu göster
        reply = QMessageBox.question(
            self,
            'Görev Silme Onayı',
            'Bu görevi silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
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
        dialog = TeamManagementDialog(self)
        dialog.exec_()
