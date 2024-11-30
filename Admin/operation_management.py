from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
                             QGroupBox, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                             QComboBox, QMessageBox, QDialog, QFormLayout, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from harita import HaritaYonetimi
from dialogs import NotificationDetailDialog  
from styles_dark import *
from styles_light import *

from sample_data import TEAM_DATA, NOTIFICATIONS, TASKS, MESSAGES, NOTIFICATION_DETAILS, TASK_DETAILS
from harita import MapWidget


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
        self.notification_list = QListWidget()
        self.notification_list.itemDoubleClicked.connect(self.show_notification_details)
        self.notification_list.setStyleSheet(LIST_WIDGET_STYLE)

        notifications_layout.addWidget(self.notification_list)
        notifications_group.setLayout(notifications_layout)
        
        # Görevler Listesi
        tasks_group = QGroupBox("Aktif Görevler")
        tasks_layout = QVBoxLayout()
        
        tasks_container = QWidget()
        tasks_container_layout = QHBoxLayout(tasks_container)
        
        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self.show_task_details)
        self.tasks_list.setStyleSheet(LIST_WIDGET_STYLE)
        
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        
        edit_task_btn = QPushButton(" Düzenle")
        edit_task_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_task_btn.setIcon(QIcon('icons/equalizer.png'))
        edit_task_btn.clicked.connect(self.edit_selected_task)
        
        delete_task_btn = QPushButton(" Sil")
        delete_task_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_task_btn.setIcon(QIcon('icons/bin.png'))
        delete_task_btn.clicked.connect(self.delete_selected_task)
        
        buttons_layout.addWidget(edit_task_btn)
        buttons_layout.addWidget(delete_task_btn)
        buttons_layout.addStretch()
        
        tasks_container_layout.addWidget(self.tasks_list)
        tasks_container_layout.addWidget(buttons_container)
        
        tasks_layout.addWidget(tasks_container)
        tasks_group.setLayout(tasks_layout)
        
        right_info_layout.addWidget(notifications_group)
        right_info_layout.addWidget(tasks_group)
        
        # Üst panel düzenleme
        top_layout.addWidget(self.map_widget, stretch=2)  # Harita widget'ı burada
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
        self.team_list.setStyleSheet(TABLE_WIDGET_STYLE)
        
        button_layout = QHBoxLayout()

        add_team_button = QPushButton(" Ekip Ekle")
        add_team_button.setStyleSheet(GREEN_BUTTON_STYLE)
        add_team_button.setIcon(QIcon('icons/add-group.png'))
        add_team_button.clicked.connect(self.add_team)

        remove_team_button = QPushButton(" Ekip Çıkar")
        remove_team_button.setStyleSheet(RED_BUTTON_STYLE)
        remove_team_button.setIcon(QIcon('icons/delete-group.png'))
        remove_team_button.clicked.connect(self.remove_selected_team)

        button_layout.addWidget(add_team_button)
        button_layout.addWidget(remove_team_button)

        team_list_layout.addWidget(self.team_list)
        team_list_layout.addLayout(button_layout)

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
        self.priority_combo.addItems(["Düşük", "Orta", "Yüksek", "Acil"])
        self.priority_combo.setCurrentIndex(1)
        self.priority_combo.setStyleSheet(COMBOBOX_STYLE)

        assign_button = QPushButton("Görevi Ata")
        assign_button.clicked.connect(self.assign_task)
        assign_button.setStyleSheet(BUTTON_STYLE)

        contact_button = QPushButton(" Ekip ile İletişime Geç")
        contact_button.clicked.connect(self.contact_team)
        contact_button.setStyleSheet(GREEN_BUTTON_STYLE)
        contact_button.setIcon(QIcon('icons/customer-service.png'))

        assignment_layout.addRow("Ekip Seçimi:", self.team_combo)
        assignment_layout.addRow("Lokasyon:", self.location_input)
        assignment_layout.addRow("Görev Detayları:", self.task_description)
        assignment_layout.addRow("Öncelik Seviyesi:", self.priority_combo)
        assignment_layout.addRow("", assign_button)
        assignment_layout.addRow("", contact_button)

        assignment_group.setLayout(assignment_layout)
        
        bottom_layout.addWidget(team_list_group, stretch=2)
        bottom_layout.addWidget(assignment_group, stretch=1)
        
        # Ana layout
        main_layout.addWidget(top_panel, stretch=2)
        main_layout.addWidget(bottom_panel, stretch=1)
        
        self.setLayout(main_layout)
        
        # Örnek verileri yükle
        self.load_sample_data()
        self.load_team_data()


    def refresh_map(self):
        self.harita.clear_map()  # Haritayı temizle
        self.map_view = self.harita.initialize_map(height=470)  # Yeniden başlat


    def add_team(self):
        """Yeni ekip eklemek için bir dialog açar."""
        # Yeni bir dialog oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("Ekip Ekle")
        dialog.setFixedSize(400, 300)

        # Dialog için bir form düzeni oluştur
        layout = QFormLayout()

        # Giriş alanlarını tanımla
        team_id_input = QLineEdit()
        leader_input = QLineEdit()
        institution_input = QLineEdit()
        status_combo = QComboBox()
        status_combo.addItems(["Müsait", "Meşgul"])
        contact_input = QLineEdit()

        # Kaydet butonunu tanımla
        save_button = QPushButton(" Kaydet")
        save_button.setIcon(QIcon('icons/save.png'))
        save_button.clicked.connect(lambda: self.save_new_team(dialog, team_id_input, leader_input, institution_input, status_combo, contact_input))
        save_button.setStyleSheet(BUTTON_STYLE)

        # Alanları ve butonu düzenlemeye ekle
        layout.addRow("Ekip ID:", team_id_input)
        layout.addRow("Ekip Lideri:", leader_input)
        layout.addRow("Kurum:", institution_input)
        layout.addRow("Durum:", status_combo)
        layout.addRow("İletişim:", contact_input)
        layout.addRow(save_button)

        # Dialog düzenini ayarla
        dialog.setLayout(layout)
        dialog.exec_()



    def handle_cell_click(self, row, column):
        """Tablo hücresine tıklandığında çalışacak fonksiyon"""
        if column == 3:  # Durum sütunu
            current_item = self.team_list.item(row, column)
            current_status = current_item.text()
            
            # Durumu değiştir
            new_status = "Meşgul" if current_status == "Müsait" else "Müsait"
            current_item.setText(new_status)
            
            # Arka plan rengini güncelle
            if new_status == "Müsait":
                current_item.setBackground(QBrush(QColor("#4CAF50")))  # Yeşil
            else:
                current_item.setBackground(QBrush(QColor("#f44336")))  # Kırmızı)


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
        self.team_list.setRowCount(0)  # Mevcut satırları temizle
        
        # Tablo üzerine tıklama sinyalini bağla
        self.team_list.cellClicked.connect(self.handle_cell_click)
        
        for team in TEAM_DATA:
            row = self.team_list.rowCount()
            self.team_list.insertRow(row)
            for col, data in enumerate(team):
                item = QTableWidgetItem(str(data))
                if col == 3:  # Durum sütunu
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    if data == "Müsait":
                        item.setBackground(QBrush(QColor("#4CAF50")))
                    else:
                        item.setBackground(QBrush(QColor("#f44336")))
                item.setTextAlignment(Qt.AlignCenter)
                self.team_list.setItem(row, col, item)
            
            self.team_combo.addItem(f"{team[0]} - {team[1]} ({team[2]})")
        
        self.team_list.resizeColumnsToContents()

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
        
        contact_dialog = QDialog(self)
        contact_dialog.setWindowTitle("Ekip İletişim")
        contact_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Ekip: {team_id}\nLider: {team_leader}\nİletişim: {contact}")
        info_label.setStyleSheet(DIALOG_INFO_LABEL_STYLE)        

        message_input = QTextEdit()
        message_input.setPlaceholderText("Mesajınızı yazın...")
        message_input.setStyleSheet(TEXT_EDIT_STYLE)
        
        send_button = QPushButton(" Mesaj Gönder")
        send_button.setStyleSheet(GREEN_BUTTON_STYLE)
        send_button.setIcon(QIcon('icons/paper-plane.png'))
        
        layout.addWidget(info_label)
        layout.addWidget(message_input)
        layout.addWidget(send_button)
        
        contact_dialog.setLayout(layout)
        contact_dialog.exec_()


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
        
        # Düzenleme dialogu oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("Görev Düzenle")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Metin düzenleme alanı
        task_edit = QTextEdit()
        task_edit.setText(current_item.text())
        task_edit.setStyleSheet(TEXT_EDIT_STYLE)
        
        # Kaydet butonu
        save_btn = QPushButton(" Kaydet")
        save_btn.setIcon(QIcon('icons/save.png'))
        save_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        save_btn.clicked.connect(lambda: self.save_edited_task(current_item, task_edit.toPlainText(), dialog))
        
        layout.addWidget(task_edit)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
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
