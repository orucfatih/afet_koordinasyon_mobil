from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QListWidget,
                            QPushButton, QTextEdit, QLabel, QComboBox, QSplitter, QTabWidget,
                            QListWidgetItem, QLineEdit, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor
from styles.styles_dark import *
from styles.styles_light import *
from sample_data import MESSAGE_CONTACTS, MESSAGE_HISTORY
import os
from message.contact_item import ContactItem


def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)



class NewMessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Yeni Mesaj")
        self.setMinimumSize(800, 600)
        self.selected_contact = None  # Seçilen kişiyi sakla
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()  # Ana layout'u dikey yap
        
        # Arama kutusu
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Ara...")
        self.search_box.setStyleSheet(SEARCH_BOX_STYLE)
        self.search_box.textChanged.connect(self.filter_contacts)
        
        # Kategori seçimi için tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.West)  # Tabları sola al
        self.tab_widget.setStyleSheet(TAB_WIDGET_STYLE)
        
        # Ekip Liderleri Tab'ı
        team_leaders_widget = QWidget()
        team_leaders_layout = QVBoxLayout()
        self.team_leaders_list = QListWidget()
        self.team_leaders_list.setStyleSheet(LIST_WIDGET_STYLE)
        team_leaders_layout.addWidget(self.team_leaders_list)
        team_leaders_widget.setLayout(team_leaders_layout)
        
        # Kurumlar Tab'ı
        institutions_widget = QWidget()
        institutions_layout = QVBoxLayout()
        self.institutions_list = QListWidget()
        self.institutions_list.setStyleSheet(LIST_WIDGET_STYLE)
        institutions_layout.addWidget(self.institutions_list)
        institutions_widget.setLayout(institutions_layout)
        
        # Kriz Masaları Tab'ı
        crisis_widget = QWidget()
        crisis_layout = QVBoxLayout()
        self.crisis_list = QListWidget()
        self.crisis_list.setStyleSheet(LIST_WIDGET_STYLE)
        crisis_layout.addWidget(self.crisis_list)
        crisis_widget.setLayout(crisis_layout)
        
        # Tab'ları ekle
        self.tab_widget.addTab(team_leaders_widget, "Ekip Liderleri")
        self.tab_widget.addTab(institutions_widget, "Kurumlar")
        self.tab_widget.addTab(crisis_widget, "Kriz Masaları")
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        start_chat_btn = QPushButton(" Mesajlaşma Başlat")
        start_chat_btn.setIcon(QIcon(get_icon_path('paper-plane.png')))
        start_chat_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        start_chat_btn.clicked.connect(self.start_chat)
        
        cancel_btn = QPushButton(" İptal")
        cancel_btn.setIcon(QIcon(get_icon_path('close.png')))
        cancel_btn.setStyleSheet(RED_BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(start_chat_btn)
        
        # Ana layout'a widget'ları ekle
        layout.addWidget(self.search_box)
        layout.addWidget(self.tab_widget)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Örnek verileri yükle
        self.load_contacts()
        
        # Liste seçim olaylarını bağla
        self.team_leaders_list.itemClicked.connect(self.contact_selected)
        self.institutions_list.itemClicked.connect(self.contact_selected)
        self.crisis_list.itemClicked.connect(self.contact_selected)
    
    def load_contacts(self):
        """Örnek kişi ve kurumları yükler"""
        # Ekip liderleri
        for leader in MESSAGE_CONTACTS["Ekip Liderleri"]:
            self.team_leaders_list.addItem(ContactItem(leader))
        
        # Kurumlar
        for institution in MESSAGE_CONTACTS["Kurumlar"]:
            self.institutions_list.addItem(ContactItem(institution))
        
        # Kriz masaları
        for crisis in MESSAGE_CONTACTS["Kriz Masaları"]:
            self.crisis_list.addItem(ContactItem(crisis))
    
    def filter_contacts(self, text):
        """Arama kutusuna göre kişileri filtreler"""
        text = text.lower()
        
        # Tüm listeleri kontrol et
        for list_widget in [self.team_leaders_list, self.institutions_list, self.crisis_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if text in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
    
    def contact_selected(self, item):
        """Bir kişi veya kurum seçildiğinde"""
        self.selected_contact = item.contact_data
    
    def start_chat(self):
        """Mesajlaşmayı başlatır"""
        if not self.selected_contact:
            return
        self.accept()

class MessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Mesajlaşma")
        self.setMinimumSize(1000, 600)
        self.current_chat = None  # Aktif sohbet
        self.chat_messages = {}  # Tüm mesajları saklamak için sözlük
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        
        # Sol Panel - Konuşma Listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Üst kısım - Butonlar
        top_buttons = QHBoxLayout()
        
        # Yeni mesaj butonu
        new_message_btn = QPushButton(" Yeni Mesaj")
        new_message_btn.setIcon(QIcon(get_icon_path('new-message.png')))
        new_message_btn.setStyleSheet(GREEN_BUTTON_STYLE)
        new_message_btn.clicked.connect(self.new_message)
        
        # Konuşma sil butonu - İsim değiştirildi
        delete_conversation_btn = QPushButton(" Konuşma Sil")
        delete_conversation_btn.setIcon(QIcon(get_icon_path('delete.png')))
        delete_conversation_btn.setStyleSheet(RED_BUTTON_STYLE)
        delete_conversation_btn.clicked.connect(self.delete_conversation)
        
        top_buttons.addWidget(new_message_btn)
        top_buttons.addWidget(delete_conversation_btn)
        
        # Konuşma listesi
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet(LIST_WIDGET_STYLE)
        self.chat_list.itemClicked.connect(self.load_chat)
        
        left_layout.addLayout(top_buttons)
        left_layout.addWidget(self.chat_list)
        left_panel.setLayout(left_layout)
        
        # Sağ Panel - Mesajlaşma Alanı
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Mesaj geçmişi
        self.message_history = QListWidget()
        self.message_history.setStyleSheet(LIST_WIDGET_STYLE)
        
        # Mesaj yazma alanı - dikey düzen
        message_input_container = QWidget()
        message_input_layout = QVBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Mesajınızı yazın...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet(TEXT_EDIT_STYLE)
        
        send_btn = QPushButton(" Gönder")
        send_btn.setIcon(QIcon(get_icon_path('paper-plane.png')))
        send_btn.setStyleSheet(DARK_BLUE_BUTTON_STYLE)
        send_btn.clicked.connect(self.send_message)
        send_btn.setFixedWidth(200)
        
        # Gönder butonunu sağa hizala
        send_btn_container = QHBoxLayout()
        send_btn_container.addStretch()
        send_btn_container.addWidget(send_btn)
        
        message_input_layout.addWidget(self.message_input)
        message_input_layout.addLayout(send_btn_container)
        message_input_container.setLayout(message_input_layout)
        
        right_layout.addWidget(self.message_history)
        right_layout.addWidget(message_input_container)
        right_panel.setLayout(right_layout)
        
        # Splitter ile panelleri ayır
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Örnek verileri yükle
        self.load_sample_data()
    
    def delete_conversation(self):
        """Seçili konuşmayı tamamen siler"""
        if not self.current_chat:
            return
        
        # Şu anda seçilen konuşmayı bul ve sil
        current_row = self.chat_list.currentRow()
        if current_row >= 0:
            # Sohbet listesinden öğeyi kaldır
            self.chat_list.takeItem(current_row)
            
            # Mesaj verilerini temizle
            if self.current_chat in self.chat_messages:
                del self.chat_messages[self.current_chat]
            
            # Mesaj geçmişini temizle
            self.message_history.clear()
            
            # Aktif sohbeti sıfırla
            self.current_chat = None
    
    def new_message(self):
        """Yeni mesaj başlatır"""
        dialog = NewMessageDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_contact:
            contact_data = dialog.selected_contact
            contact_id = contact_data['id']
            
            # Eğer bu kişiyle daha önce sohbet başlatılmamışsa
            if contact_id not in self.chat_messages:
                # Yeni sohbet oluştur
                item = QListWidgetItem(f"{contact_data['name']}")
                item.setIcon(QIcon(get_icon_path('user.png')))
                item.contact_data = contact_data
                self.chat_list.addItem(item)
                
                # Sohbet mesajlarını başlat
                self.chat_messages[contact_id] = [
                    {
                        'sender': 'Sistem',
                        'message': f"{contact_data['name']} ile sohbet başlatıldı",
                        'type': 'system'
                    }
                ]
                
                # Yeni sohbeti yükle
                self.chat_list.setCurrentItem(item)
                self.load_chat(item)
    
    def load_sample_data(self):
        """Örnek konuşmaları yükler"""
        # Mevcut konuşmaları yükle
        for contact_type in MESSAGE_CONTACTS.values():
            for contact in contact_type:
                if contact['id'] in MESSAGE_HISTORY:
                    item = QListWidgetItem(f"{contact['name']}")
                    item.setIcon(QIcon(get_icon_path('user.png')))
                    item.contact_data = contact
                    self.chat_list.addItem(item)
                    
                    # Mesajları hafızaya yükle
                    self.chat_messages[contact['id']] = [
                        {
                            'sender': 'Sistem',
                            'message': f"{contact['name']} ile sohbet başlatıldı",
                            'type': 'system'
                        }
                    ]
                    
                    # Varolan mesajları ekle
                    for message in MESSAGE_HISTORY[contact['id']]:
                        if message['type'] != 'system':
                            self.chat_messages[contact['id']].append({
                                'sender': message['sender'],
                                'message': message['message'],
                                'type': message['type']
                            })
    
    def load_chat(self, item):
        """Seçili konuşmayı yükler"""
        contact_data = item.contact_data
        contact_id = contact_data['id']
        self.current_chat = contact_id  # Aktif sohbeti güncelle
        
        self.message_history.clear()
        
        # Hafızadaki mesajları yükle
        if contact_id in self.chat_messages:
            for message in self.chat_messages[contact_id]:
                msg_item = QListWidgetItem(f"{message['sender']}: {message['message']}")
                if message['type'] == 'system':
                    msg_item.setForeground(QColor('#888888'))  # Gri
                elif message['type'] == 'received':
                    msg_item.setForeground(QColor('#4CAF50'))  # Yeşil
                elif message['type'] == 'sent':
                    msg_item.setForeground(QColor('#4CAF50'))  # Yeşil
                self.message_history.addItem(msg_item)
        
        # Başlık güncelleme
        if hasattr(self, 'title_label'):
            contact_title = contact_data.get('title', '')
            self.setWindowTitle(f"Mesajlaşma - {contact_data['name']} {contact_title}")
    
    def send_message(self):
        """Mesajı gönderir"""
        if not self.current_chat:
            return
            
        message = self.message_input.toPlainText().strip()
        if message:
            # Yeni mesajı oluştur
            new_message = {
                'sender': 'Siz',
                'message': message,
                'type': 'sent'
            }
            
            # Mesajı hafızaya ve görünüme ekle
            self.chat_messages[self.current_chat].append(new_message)
            msg_item = QListWidgetItem(f"{new_message['sender']}: {new_message['message']}")
            msg_item.setForeground(QColor('#4CAF50'))  # Yeşil
            self.message_history.addItem(msg_item)
            
            self.message_input.clear()

class ContactItem(QListWidgetItem):
    def __init__(self, contact_data):
        super().__init__()
        self.contact_data = contact_data
        self.id = contact_data.get('id')
        
        # Görünüm ayarları
        display_text = contact_data['name']
        if 'title' in contact_data and contact_data['title']:
            display_text += f"\n{contact_data['title']}"
        
        self.setText(display_text)
        self.setIcon(QIcon(get_icon_path('user.png')))
        self.setForeground(QColor('#4CAF50'))  # Yeşil