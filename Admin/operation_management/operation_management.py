"""
Operasyon yönetimi modülü
"""
from PyQt5.QtWidgets import (
    # Layout widgets
    QWidget, QVBoxLayout, QHBoxLayout,
    # Basic widgets
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    # Container widgets
    QGroupBox, QListWidget, QTableWidget, QTableWidgetItem,
    # Dialog related
    QDialog, QMessageBox, QDialogButtonBox,
    # Form widgets
    QFormLayout, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from sample_data import TEAM_DATA, TASKS, TASK_DETAILS
from styles.styles_dark import *
from styles.styles_light import *
from .op_constant import TASK_PRIORITIES
from .op_utils import get_icon_path
from .op_dialogs import create_task_edit_dialog
from .op_config import get_config
from harita import GoogleMapsWindow
from dotenv import load_dotenv
import os
from .task_history import MissionHistoryDialog
from .team_management_panel import TeamManagementPanel

# Görev öncelik renkleri
TASK_PRIORITY_COLORS = {
    "Düşük (1)": "#808080",  # Gri
    "Orta (2)": "#FFA500",   # Turuncu
    "Yüksek (3)": "#FF4500", # Kırmızı-Turuncu
    "Kritik (4)": "#FF0000"  # Kırmızı
}

class OperationManagementTab(QWidget):
    """Operasyon Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        
        load_dotenv()

        self.config = get_config()
        self.api_key = self.config["api_key"]
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Ana panel - Sol ve Sağ bölümler
        main_panel = QHBoxLayout()
        
        # Sol Panel - Harita ve Ekip Listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Harita Bölümü
        self.map_module = GoogleMapsWindow()
        self.map_widget = self.map_module.web_view
        self.map_widget.setMinimumHeight(300)  # Harita için minimum yükseklik
        
        # Ekip Listesi
        team_list_group = QGroupBox("Mevcut Ekipler")
        team_list_layout = QVBoxLayout()
        
        # TeamManagementPanel'i ekle
        self.team_management_panel = TeamManagementPanel(self)
        team_list_layout.addWidget(self.team_management_panel)
        
        team_list_group.setLayout(team_list_layout)
        team_list_group.setMaximumHeight(500)  # Ekip listesi maksimum yükseklik
        
        # Sol panel bileşenlerini ekle
        left_layout.addWidget(self.map_widget, stretch=4)
        left_layout.addWidget(team_list_group, stretch=3)
        
        # Sağ Panel - Aktif Görevler ve Görevlendirme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Aktif Görevler Bölümü
        tasks_group = QGroupBox("Aktif Görevler")
        tasks_layout = QVBoxLayout()
        
        # Görev filtreleme
        filter_layout = QHBoxLayout()
        
        # Öncelik filtresi
        priority_filter_label = QLabel("Öncelik Filtresi:")
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["Tümü"] + TASK_PRIORITIES)
        self.priority_filter.setStyleSheet(COMBOBOX_STYLE)
        self.priority_filter.currentTextChanged.connect(self.filter_tasks)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Görev ara...")
        self.search_input.setStyleSheet(LINE_EDIT_STYLE)
        self.search_input.textChanged.connect(self.filter_tasks)
        
        search_layout.addWidget(QLabel("Ara:"))
        search_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(priority_filter_label)
        filter_layout.addWidget(self.priority_filter)
        filter_layout.addLayout(search_layout)
        
        # Görevler listesi
        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self.show_task_details)
        self.tasks_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.tasks_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Görev yönetim butonları
        task_buttons = QHBoxLayout()
        
        # Düzenleme butonu
        edit_task_btn = QPushButton(" Düzenle")
        edit_task_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        edit_task_btn.setIcon(QIcon(get_icon_path('equalizer.png')))
        edit_task_btn.clicked.connect(self.edit_selected_task)
        
        # Tamamlandı butonu
        complete_task_btn = QPushButton(" Tamamlandı")
        complete_task_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        complete_task_btn.setIcon(QIcon(get_icon_path('check.png')))
        complete_task_btn.clicked.connect(self.complete_selected_task)
        
        # Silme butonu
        delete_task_btn = QPushButton(" Sil")
        delete_task_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_task_btn.setIcon(QIcon(get_icon_path('bin.png')))
        delete_task_btn.clicked.connect(self.delete_selected_task)
        
        # Butonları layout'a ekle
        task_buttons.addWidget(edit_task_btn)
        task_buttons.addWidget(complete_task_btn)
        task_buttons.addWidget(delete_task_btn)
        
        # Widget'ları tasks_layout'a ekle
        tasks_layout.addLayout(filter_layout)
        tasks_layout.addWidget(self.tasks_list)
        tasks_layout.addLayout(task_buttons)
        
        tasks_group.setLayout(tasks_layout)
        
        # Görevlendirme Paneli
        assignment_group = QGroupBox("Ekip Görevlendirme")
        assignment_layout = QVBoxLayout()
        
        # Ekip seçimi
        team_selection_layout = QHBoxLayout()
        team_selection_layout.addWidget(QLabel("Ekip:"))
        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet(COMBOBOX_STYLE)
        team_selection_layout.addWidget(self.team_combo)
        
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
        
        # Öncelik ve süre seçimi için layout
        priority_duration_layout = QHBoxLayout()
        
        # Öncelik seçimi
        priority_layout = QVBoxLayout()
        priority_layout.addWidget(QLabel("Öncelik Seviyesi:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(TASK_PRIORITIES)
        self.priority_combo.setCurrentText("Orta (2)")
        self.priority_combo.setStyleSheet(COMBOBOX_STYLE)
        priority_layout.addWidget(self.priority_combo)
        
        # Tahmini süre
        duration_layout = QVBoxLayout()
        duration_layout.addWidget(QLabel("Tahmini Süre (saat):"))
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Örn: 2.5")
        self.duration_input.setStyleSheet(LINE_EDIT_STYLE)
        duration_layout.addWidget(self.duration_input)
        
        priority_duration_layout.addLayout(priority_layout)
        priority_duration_layout.addLayout(duration_layout)
        
        # Görev detay girişi
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Görev detayları...")
        self.task_input.setMaximumHeight(100)
        self.task_input.setStyleSheet(TEXT_EDIT_STYLE)
        
        # Görev atama ve geçmiş butonları
        button_layout = QHBoxLayout()
        
        # Görev atama butonu
        assign_btn = QPushButton(" Görev Ata")
        assign_btn.setIcon(QIcon(get_icon_path('add1.png')))
        assign_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        assign_btn.clicked.connect(self.assign_task)
        
        # Görev geçmişi butonu
        history_btn = QPushButton(" Görev Geçmişi")
        history_btn.setIcon(QIcon(get_icon_path('history.png')))
        history_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        history_btn.clicked.connect(self.show_mission_history)
        
        button_layout.addWidget(assign_btn)
        button_layout.addWidget(history_btn)
        
        # Widget'ları assignment_layout'a ekle
        assignment_layout.addLayout(team_selection_layout)
        assignment_layout.addLayout(title_location_layout)
        assignment_layout.addLayout(priority_duration_layout)
        assignment_layout.addWidget(QLabel("Görev Detayları:"))
        assignment_layout.addWidget(self.task_input)
        assignment_layout.addLayout(button_layout)
        
        assignment_group.setLayout(assignment_layout)
        
        # Sağ panel bileşenlerini ekle
        right_layout.addWidget(tasks_group, stretch=1)
        right_layout.addWidget(assignment_group, stretch=1)
        
        # Ana panele sol ve sağ bölümleri ekle
        main_panel.addWidget(left_panel, stretch=2)
        main_panel.addWidget(right_panel, stretch=1)
        
        # Ana layout'a paneli ekle
        main_layout.addLayout(main_panel)
        
        self.setLayout(main_layout)
        
        # Örnek verileri yükle
        self.load_sample_data()
        self.load_team_data()

    def load_team_data(self):
        """Örnek ekip verilerini yükler"""
        self.team_management_panel.team_list.setRowCount(0)
        
        # Kurumları topla
        institutions = set()
        
        for team in TEAM_DATA:
            institutions.add(team[2])  # Kurum adlarını topla
            row = self.team_management_panel.team_list.rowCount()
            self.team_management_panel.team_list.insertRow(row)
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
                
                self.team_management_panel.team_list.setItem(row, col, item)
            
            self.team_combo.addItem(f"{team[0]} - {team[1]} ({team[2]})")
        
        # Kurum filtresine kurumları ekle
        self.team_management_panel.institution_filter.addItems(sorted(institutions))
        
        self.team_management_panel.team_list.resizeColumnsToContents()

    def show_task_details(self, item):
        """Görev detaylarını dialog penceresinde gösterir"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Görev Detayları")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        details = QTextEdit()
        details.setPlainText(TASK_DETAILS.get(item.text(), "Detaylı bilgi bulunamadı."))
        details.setReadOnly(True)
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(details)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
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
        # Görevler
        self.tasks_list.clear()
        for task in TASKS:
            item = QListWidgetItem(task)
            # Görev metnini parçala
            task_parts = task.split(" - ")
            if len(task_parts) >= 3:
                priority = task_parts[2]
                item.setData(Qt.UserRole, priority)
            self.tasks_list.addItem(item)

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
                
                # Görevi aktif görevlerden kaldır
                self.tasks_list.takeItem(self.tasks_list.row(current_item))

    def show_mission_history(self):
        """Görev geçmişi penceresini gösterir"""
        dialog = MissionHistoryDialog(self)
        dialog.exec_()

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
            
            # Görevi aktif görevler listesine ekle
            self.tasks_list.addItem(new_task)
            
            # Görev detaylarını TASK_DETAILS sözlüğüne ekle
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

    def filter_tasks(self):
        """Görevleri öncelik ve arama kriterlerine göre filtreler"""
        search_text = self.search_input.text().lower()
        priority_filter = self.priority_filter.currentText()
        
        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            task_text = item.text().lower()
            task_priority = item.data(Qt.UserRole) if item.data(Qt.UserRole) else "Orta (2)"
            
            # Hem arama metni hem de öncelik filtresine göre kontrol et
            should_show = (search_text in task_text) and \
                         (priority_filter == "Tümü" or priority_filter == task_priority)
            
            item.setHidden(not should_show)

    def complete_selected_task(self):
        """Seçili görevi tamamlandı olarak işaretler"""
        current_item = self.tasks_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen tamamlandı olarak işaretlemek için bir görev seçin!")
            return
        
        task_text = current_item.text()
        task_parts = task_text.split(" - ")
        if len(task_parts) >= 2:
            task_type = task_parts[0]
            location = task_parts[1]
            priority = current_item.data(Qt.UserRole) if current_item.data(Qt.UserRole) else "Orta (2)"
            
            # Tamamlanma tarihi
            from datetime import datetime
            completion_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Görev geçmişine ekle
            from sample_data import TASK_HISTORY_DATA
            new_task_history = [
                completion_date,
                task_type,
                location,
                self.duration_input.text() if self.duration_input.text() else "N/A",
                priority,
                "Tamamlandı",
                "Görev başarıyla tamamlandı"
            ]
            TASK_HISTORY_DATA.insert(0, new_task_history)
            
            # Aktif görevlerden kaldır
            self.tasks_list.takeItem(self.tasks_list.row(current_item))
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Görev başarıyla tamamlandı!\n\nGörev: {task_text}"
            )
