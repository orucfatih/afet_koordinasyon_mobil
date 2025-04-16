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
from config import get_config
from harita.harita import GoogleMapsWindow
from dotenv import load_dotenv
import os
from .task_history import MissionHistoryDialog
from .team_management_panel import TeamManagementPanel
from .task_management import TaskManager
# Firebase veritabanı işlemleri için import
from database import get_database_ref, get_storage_bucket, initialize_firebase
import time
import uuid



class OperationManagementTab(QWidget):
    """Operasyon Yönetim Sekmesi"""
    def __init__(self):
        super().__init__()
        self.config = get_config()
        # Firebase referansları
        self.tasks_ref = get_database_ref('/operations/tasks')
        self.teams_ref = get_database_ref('/operations/teams')
        self.task_history_ref = get_database_ref('/operations/task_history')
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
        self.load_sample_task_data()
        self.load_team_data()

    def load_team_data(self):
        """Firebase'den ekip verilerini yükler"""
        try:
            # Firebase'den takım verilerini al
            teams_data = self.teams_ref.get()
            
            if teams_data:
                # Combobox'ı temizle
                self.team_combo.clear()
                
                # Firebase verilerini işle
                for team_id, team_info in teams_data.items():
                    team_name = team_info.get('team_name', 'İsimsiz Ekip')
                    self.team_combo.addItem(team_name, team_id)
                
                # TeamManagementPanel'a verileri gönder
                self.team_management_panel.update_team_list(teams_data)
            else:
                # Eğer Firebase'de veri yoksa örnek veriyi kullan
                print("Firebase'de takım verisi bulunamadı, örnek veri kullanılıyor.")
                for team in TEAM_DATA:
                    # TEAM_DATA liste içinde liste formatında olduğu için
                    # team_name, doğrudan team[0] indeksinden alınır
                    team_name = team[0]  # Takım ID'si (aynı zamanda adı)
                    team_leader = team[1]  # Takım lideri
                    institution = team[2]  # Kurum
                    self.team_combo.addItem(f"{team_name} - {team_leader} ({institution})")
                
                # TeamManagementPanel'a örnek verileri gönder
                self.team_management_panel.update_team_list(TEAM_DATA)
                
        except Exception as e:
            print(f"Ekip verisi yüklenirken hata: {str(e)}")
            # Hata durumunda örnek veriyi kullan
            for team in TEAM_DATA:
                # TEAM_DATA dizisinden doğru şekilde bilgileri al
                team_name = team[0]  # Takım ID'si (aynı zamanda adı)
                team_leader = team[1]  # Takım lideri
                institution = team[2]  # Kurum
                self.team_combo.addItem(f"{team_name} - {team_leader} ({institution})")
            
            # TeamManagementPanel'a örnek verileri gönder
            self.team_management_panel.update_team_list(TEAM_DATA)

    def show_task_details(self, item):
        """Seçilen görevin detaylarını gösterir"""
        task_id = item.data(Qt.UserRole)
        
        try:
            # Firebase'den görev verilerini al
            task_data = self.tasks_ref.child(task_id).get()
            
            if task_data:
                # Detay penceresini hazırla
                details_dialog = QDialog(self)
                details_dialog.setWindowTitle(f"Görev Detayı: {task_data.get('title', 'İsimsiz Görev')}")
                details_dialog.setMinimumWidth(500)
                details_dialog.setMinimumHeight(400)
                
                layout = QVBoxLayout()
                
                # Görev detayları
                form_layout = QFormLayout()
                form_layout.addRow("Başlık:", QLabel(task_data.get('title', '')))
                form_layout.addRow("Ekip:", QLabel(task_data.get('team', '')))
                form_layout.addRow("Lokasyon:", QLabel(task_data.get('location', '')))
                form_layout.addRow("Öncelik:", QLabel(task_data.get('priority', '')))
                form_layout.addRow("Tahmini Süre:", QLabel(f"{task_data.get('duration', '')} saat"))
                
                # Detaylar için text edit
                details_text = QTextEdit()
                details_text.setReadOnly(True)
                details_text.setText(task_data.get('details', ''))
                details_text.setMinimumHeight(150)
                
                # Butonlar
                buttons = QDialogButtonBox(QDialogButtonBox.Ok)
                buttons.accepted.connect(details_dialog.accept)
                
                layout.addLayout(form_layout)
                layout.addWidget(QLabel("Detaylar:"))
                layout.addWidget(details_text)
                layout.addWidget(buttons)
                
                details_dialog.setLayout(layout)
                details_dialog.exec_()
            else:
                # Firebase'de veri bulunamazsa örnek veriyi kullan
                self._show_legacy_task_details(task_id)
                
        except Exception as e:
            print(f"Görev detayları görüntülenirken hata: {str(e)}")
            # Hata durumunda örnek veriyi kullan
            self._show_legacy_task_details(task_id)
    
    def _show_legacy_task_details(self, task_id):
        """Örnek veri ile görev detaylarını gösterir (eski yöntem)"""
        # Görev bilgilerini bul
        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            if item.data(Qt.UserRole) == task_id:
                task_text = item.text()
                
                # TASK_DETAILS'dan detayları al
                task_detail = TASK_DETAILS.get(task_text)
                
                if not task_detail:
                    QMessageBox.warning(self, "Hata", "Görev detayları bulunamadı.")
                    return
                
                # Detay penceresini hazırla
                details_dialog = QDialog(self)
                details_dialog.setWindowTitle(f"Görev Detayı")
                details_dialog.setMinimumWidth(500)
                details_dialog.setMinimumHeight(400)
                
                layout = QVBoxLayout()
                
                # Detaylar için text edit
                details_text = QTextEdit()
                details_text.setReadOnly(True)
                details_text.setText(task_detail)  # Doğrudan string'i göster
                details_text.setMinimumHeight(150)
                
                # Butonlar
                buttons = QDialogButtonBox(QDialogButtonBox.Ok)
                buttons.accepted.connect(details_dialog.accept)
                
                layout.addWidget(QLabel("Detaylar:"))
                layout.addWidget(details_text)
                layout.addWidget(buttons)
                
                details_dialog.setLayout(layout)
                details_dialog.exec_()
                return
        
        QMessageBox.warning(self, "Hata", "Görev bulunamadı.")
        return

    def delete_selected_task(self):
        """Seçilen görevi siler"""
        selected_items = self.tasks_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bir görev seçin.")
            return
        
        reply = QMessageBox.question(self, 'Görev Silme', 
                                     f"Seçilen {len(selected_items)} görevi silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                for item in selected_items:
                    task_id = item.data(Qt.UserRole)
                    
                    # Firebase'den görevi sil
                    self.tasks_ref.child(task_id).delete()
                    
                    # Listeden kaldır
                    self.tasks_list.takeItem(self.tasks_list.row(item))
                
                QMessageBox.information(self, "Başarılı", 
                                       f"{len(selected_items)} görev başarıyla silindi.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", 
                                    f"Görevler silinirken hata oluştu: {str(e)}")

    def load_sample_task_data(self):
        """Firebase'den görev verilerini yükler veya örnek veri kullanır"""
        try:
            # Firebase'den görev verilerini al
            tasks_data = self.tasks_ref.get()
            
            if tasks_data:
                # Görev listesini temizle
                self.tasks_list.clear()
                
                # Firebase verilerini işle
                for task_id, task_info in tasks_data.items():
                    title = task_info.get('title', 'İsimsiz Görev')
                    priority = task_info.get('priority', 'Orta (2)')
                    location = task_info.get('location', 'Belirtilmemiş')
                    team = task_info.get('team', 'Atanmamış')
                    
                    # Liste öğesini oluştur
                    item = QListWidgetItem(f"{title} - {team} - {location}")
                    item.setData(Qt.UserRole, task_id)  # task_id'yi sakla
                    
                    # Önceliğe göre renk belirle
                    if "Yüksek" in priority:
                        item.setForeground(QBrush(QColor("#FF6B6B")))
                    elif "Orta" in priority:
                        item.setForeground(QBrush(QColor("#FFD93D")))
                    
                    self.tasks_list.addItem(item)
            else:
                # Eğer Firebase'de veri yoksa örnek veriyi kullan
                print("Firebase'de görev verisi bulunamadı, örnek veri kullanılıyor.")
                self._load_legacy_sample_data()
                
        except Exception as e:
            print(f"Görev verisi yüklenirken hata: {str(e)}")
            # Hata durumunda örnek veriyi kullan
            self._load_legacy_sample_data()
    
    def _load_legacy_sample_data(self):
        """Örnek veri ile görev listesini doldurur (eski yöntem)"""
        self.tasks_list.clear()
        for task in TASKS:
            # TASKS listesi string olduğu için string'i parçalara ayırıyoruz
            task_parts = task.split(" - ")
            if len(task_parts) >= 3:
                title = task_parts[0]
                location = task_parts[1]
                priority = task_parts[2]
                
                # Benzersiz ID oluştur
                task_id = str(uuid.uuid4())
                
                # Liste öğesini oluştur
                item = QListWidgetItem(f"{title} - {location} - {priority}")
                item.setData(Qt.UserRole, task_id)  # Benzersiz ID'yi sakla
                
                # Önceliğe göre renk belirle
                if "Yüksek" in priority or "Acil" in priority:
                    item.setForeground(QBrush(QColor("#FF6B6B")))
                elif "Orta" in priority:
                    item.setForeground(QBrush(QColor("#FFD93D")))
                
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
    
    def show_mission_history(self):
        """Görev geçmişi penceresini gösterir"""
        dialog = MissionHistoryDialog(self)
        dialog.exec_()

    def assign_task(self):
        """Yeni görevi oluşturup Firebase'e kaydeder"""
        # Form verilerini al
        title = self.title_input.text().strip()
        location = self.location_input.text().strip()
        details = self.task_input.toPlainText().strip()
        priority = self.priority_combo.currentText()
        team = self.team_combo.currentText()
        team_id = self.team_combo.currentData()  # Firebase team ID
        
        # Süre kontrol
        try:
            duration = float(self.duration_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir süre giriniz.")
            return
            
        # Boş alan kontrolü
        if not title or not location or not details:
            QMessageBox.warning(self, "Eksik Bilgi", 
                                "Lütfen tüm gerekli alanları doldurunuz.")
            return
        
        try:
            # Benzersiz ID oluştur
            task_id = str(uuid.uuid4())
            
            # Firebase'e kaydedilecek görev verisi
            task_data = {
                'id': task_id,
                'title': title,
                'location': location,
                'details': details,
                'priority': priority,
                'team': team,
                'team_id': team_id,  # Firebase team ID
                'duration': duration,
                'status': 'active',
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            # Firebase'e görevi ekle
            self.tasks_ref.child(task_id).set(task_data)
            
            # UI'ı güncelle
            item = QListWidgetItem(f"{title} - {team} - {location}")
            item.setData(Qt.UserRole, task_id)
            
            if "Yüksek" in priority:
                item.setForeground(QBrush(QColor("#FF6B6B")))
            elif "Orta" in priority:
                item.setForeground(QBrush(QColor("#FFD93D")))
            
            self.tasks_list.addItem(item)
            
            # Form alanlarını temizle
            self.title_input.clear()
            self.location_input.clear()
            self.task_input.clear()
            self.duration_input.clear()
            self.priority_combo.setCurrentText("Orta (2)")
            
            QMessageBox.information(self, "Başarılı", "Görev başarıyla oluşturuldu.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Görev oluşturulurken hata oluştu: {str(e)}")

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
        """Seçilen görevi tamamlandı olarak işaretler ve arşive taşır"""
        selected_items = self.tasks_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen tamamlanacak bir görev seçin.")
            return
        
        reply = QMessageBox.question(self, 'Görev Tamamlama', 
                                     f"Seçilen {len(selected_items)} görevi tamamlandı olarak işaretlemek istiyor musunuz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                for item in selected_items:
                    task_id = item.data(Qt.UserRole)
                    
                    # Görev verilerini al
                    task_data = self.tasks_ref.child(task_id).get()
                    
                    if task_data:
                        # Görevi completed olarak güncelle
                        task_data['status'] = 'completed'
                        task_data['completed_at'] = time.time()
                        
                        # Görevi arşive taşı
                        self.task_history_ref.child(task_id).set(task_data)
                        
                        # Aktif görevlerden kaldır
                        self.tasks_ref.child(task_id).delete()
                        
                        # Listeden kaldır
                        self.tasks_list.takeItem(self.tasks_list.row(item))
                
                QMessageBox.information(self, "Başarılı", 
                                       f"{len(selected_items)} görev başarıyla tamamlandı.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", 
                                    f"Görevler tamamlanırken hata oluştu: {str(e)}")
