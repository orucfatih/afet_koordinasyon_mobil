from PyQt5.QtWidgets import (QTreeWidget, QTableWidget, QPushButton, QLineEdit, 
                           QComboBox, QMenu, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from .constants import PERSONNEL_TABLE_HEADERS
from styles.styles_dark import *
from styles.styles_light import *
from utils import get_icon_path


class PersonnelUI:
    def __init__(self, parent=None):
        self.parent = parent
        self.setup_search_widgets()
        self.setup_team_tree()
        self.setup_personnel_table()
        self.setup_buttons()
        self.setup_context_menu()
    
    def setup_search_widgets(self):
        """Arama ve filtreleme widget'larını hazırlar"""
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Personel ara...")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setStyleSheet(SEARCH_BOX_STYLE)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tümü", "AFAD", "STK", "DİĞER"])
        self.filter_combo.setCurrentText("Tümü")
        self.filter_combo.setStyleSheet(COMBO_BOX_STYLE)
    
    def setup_team_tree(self):
        """Ekip ağacını hazırlar ve özelleştirir"""
        self.team_tree = QTreeWidget()
        self.customize_team_tree()
    
    def customize_team_tree(self):
        """Ekip ağacını özelleştirir"""
        self.team_tree.setHeaderHidden(False)
        self.team_tree.setHeaderLabel("Ekipler ve Personel")
        self.team_tree.setAlternatingRowColors(True)
        self.team_tree.setAnimated(True)
        self.team_tree.setExpandsOnDoubleClick(True)
        self.team_tree.setDragDropMode(QTreeWidget.InternalMove)
        self.team_tree.setStyleSheet(TEAM_TREE_STYLE)
        
    def setup_personnel_table(self):
        """Personel tablosunu hazırlar"""
        self.personnel_table = QTableWidget()
        self.personnel_table.setColumnCount(len(PERSONNEL_TABLE_HEADERS))
        self.personnel_table.setHorizontalHeaderLabels(PERSONNEL_TABLE_HEADERS)
        self.customize_personnel_table()
    
    def customize_personnel_table(self):
        """Personel tablosunu özelleştirir"""
        self.personnel_table.setAlternatingRowColors(True)
        self.personnel_table.setSortingEnabled(True)
        self.personnel_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.personnel_table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Sütun genişliklerini ayarla
        self.personnel_table.setColumnWidth(0, 150)  # Ad Soyad
        self.personnel_table.setColumnWidth(1, 100)  # Telefon
        self.personnel_table.setColumnWidth(2, 100)  # Ev Telefonu
        self.personnel_table.setColumnWidth(3, 150)  # E-posta
        self.personnel_table.setColumnWidth(4, 200)  # Adres
        self.personnel_table.setColumnWidth(5, 100)  # Ünvan
        self.personnel_table.setColumnWidth(6, 150)  # Uzmanlık
        self.personnel_table.setColumnWidth(7, 120)  # Son Güncelleme
        
        # Yatay başlığı özelleştir
        header = self.personnel_table.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Adres sütunu genişleyebilir
        header.setStyleSheet(HEADER_STYLE)
        
        self.personnel_table.setStyleSheet(TABLE_WIDGET_STYLE)
    
    def setup_buttons(self):
        """Butonları hazırlar ve özelleştirir"""
        # Personel Ekle butonu
        self.add_button = QPushButton("Personel Ekle")
        self.add_button.setIcon(QIcon(get_icon_path('add.png')))
        self.add_button.setToolTip("Yeni personel eklemek için tıklayın")
        self.add_button.setStyleSheet(GREEN_BUTTON_STYLE)
        
        # Düzenle butonu
        self.edit_button = QPushButton("Düzenle")
        self.edit_button.setIcon(QIcon(get_icon_path('edit.png')))
        self.edit_button.setToolTip("Seçili personeli düzenlemek için tıklayın")
        self.edit_button.setStyleSheet(EDIT_BUTTON_STYLE)
        
        # Sil butonu
        self.remove_button = QPushButton("Sil")
        self.remove_button.setIcon(QIcon(get_icon_path('delete.png')))
        self.remove_button.setToolTip("Seçili personeli silmek için tıklayın")
        self.remove_button.setStyleSheet(RED_BUTTON_STYLE)
    
    def setup_context_menu(self):
        """Sağ tık menüsünü hazırlar"""
        self.personnel_table.setContextMenuPolicy(Qt.CustomContextMenu)
        # Bağlantıyı kaldırıyoruz çünkü parent sınıftan gelecek
        # self.personnel_table.customContextMenuRequested.connect(self.show_context_menu)

    def create_context_menu(self, position):
        """Context menu'yü oluşturur ve döndürür"""
        menu = QMenu()
        detay_action = menu.addAction(QIcon(get_icon_path("info.png")), "Detayları Göster")
        duzenle_action = menu.addAction(QIcon(get_icon_path("edit.png")), "Düzenle")
        sil_action = menu.addAction(QIcon(get_icon_path("delete.png")), "Sil")
        menu.addSeparator()
        mesaj_action = menu.addAction(QIcon(get_icon_path("message.png")), "Mesaj Gönder")
        konum_action = menu.addAction(QIcon(get_icon_path("location.png")), "Konum İste")
        
        return menu, {
            'detay': detay_action,
            'duzenle': duzenle_action,
            'sil': sil_action,
            'mesaj': mesaj_action,
            'konum': konum_action
        } 