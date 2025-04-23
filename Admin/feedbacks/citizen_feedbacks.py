import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                           QTableWidgetItem, QPushButton, QSplitter, QTextEdit, 
                           QLineEdit, QHeaderView, QFrame, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

# Ana dizini sys.path'e ekleyerek modülleri bulmasını sağlıyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_icon_path

from sample_data import CITIZEN_FEEDBACK_DATA, FEEDBACK_REPLIES, FEEDBACK_STATISTICS

class CitizenFeedbackTab(QWidget):
    """Vatandaş Feedback Sistemi için sekme"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
        # Örnek verileri yükleme (gerçek uygulamada veritabanından gelecek)
        self.load_sample_data()
        
    def initUI(self):
        """UI bileşenlerini oluştur"""
        main_layout = QVBoxLayout(self)
        
        # Başlık
        header_label = QLabel("Vatandaş Geri Bildirim Sistemi")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Info text
        info_label = QLabel("Bu modül, mobil uygulama üzerinden vatandaşların gönderdiği geri bildirimleri görüntüler ve yönetir.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("margin-bottom: 15px;")
        main_layout.addWidget(info_label)
        
        # Ana içerik splitter'ı (tablo ve detay görünümü için)
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sol paneli oluştur (filtreleme ve feedback listesi)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filtre araçları
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Durum filtresi
        filter_layout.addWidget(QLabel("Durum:"))
        self.status_combo = QComboBox()
        # Sadece Tümü, Yeni ve Okundu seçenekleri
        self.status_combo.addItems(["Tümü", "Yeni", "Okundu"])
        self.status_combo.currentTextChanged.connect(self.filter_feedbacks)
        filter_layout.addWidget(self.status_combo)
        
        # Arama alanı
        filter_layout.addWidget(QLabel("Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Feedback içinde ara...")
        self.search_input.textChanged.connect(self.filter_feedbacks)
        filter_layout.addWidget(self.search_input)
        
        # Yenile butonu
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon(get_icon_path('refresh.png')))
        refresh_button.setToolTip("Listeyi Yenile")
        refresh_button.setFixedSize(QSize(30, 30))
        refresh_button.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_button)
        
        left_layout.addWidget(filter_frame)
        
        # Feedback tablosu
        self.feedback_table = QTableWidget()
        self.feedback_table.setColumnCount(4)
        self.feedback_table.setHorizontalHeaderLabels(["ID", "Başlık", "Tarih", "Durum"])
        self.feedback_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.feedback_table.horizontalHeader().setStretchLastSection(False)
        self.feedback_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.feedback_table.setSelectionMode(QTableWidget.SingleSelection)
        self.feedback_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.feedback_table.setAlternatingRowColors(True)
        self.feedback_table.verticalHeader().setVisible(False)
        self.feedback_table.itemSelectionChanged.connect(self.show_feedback_details)
        
        left_layout.addWidget(self.feedback_table)
        
        # Sağ panel (feedback detayları)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Detay görünümü için frame
        detail_frame = QFrame()
        detail_frame.setFrameShape(QFrame.StyledPanel)
        detail_layout = QVBoxLayout(detail_frame)
        
        # Başlık
        detail_layout.addWidget(QLabel("Feedback Detayları"))
        
        # Feedback bilgileri
        info_layout = QHBoxLayout()
        self.detail_id_label = QLabel("ID: -")
        self.detail_date_label = QLabel("Tarih: -")
        self.detail_email_label = QLabel("E-posta: -")
        info_layout.addWidget(self.detail_id_label)
        info_layout.addWidget(self.detail_date_label)
        info_layout.addWidget(self.detail_email_label)
        detail_layout.addLayout(info_layout)
        
        # Feedback başlığı
        detail_layout.addWidget(QLabel("Başlık:"))
        self.detail_title = QLineEdit()
        self.detail_title.setReadOnly(True)
        detail_layout.addWidget(self.detail_title)
        
        # Feedback içeriği
        detail_layout.addWidget(QLabel("İçerik:"))
        self.detail_content = QTextEdit()
        self.detail_content.setReadOnly(True)
        detail_layout.addWidget(self.detail_content)
        
        # Durum değiştirme
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Durum:"))
        self.detail_status = QComboBox()
        # Sadece Yeni ve Okundu seçenekleri
        self.detail_status.addItems(["Yeni", "Okundu"])
        status_layout.addWidget(self.detail_status)
        
        save_button = QPushButton("Kaydet")
        save_button.clicked.connect(self.save_status_change)
        status_layout.addWidget(save_button)
        detail_layout.addLayout(status_layout)
        
        # Yanıt yazma alanı
        detail_layout.addWidget(QLabel("Yanıt:"))
        self.reply_text = QTextEdit()
        detail_layout.addWidget(self.reply_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        send_reply_btn = QPushButton("Yanıt Gönder")
        send_reply_btn.clicked.connect(self.send_reply)
        button_layout.addWidget(send_reply_btn)
        
        mark_read_btn = QPushButton("Okundu Olarak İşaretle")
        mark_read_btn.clicked.connect(self.mark_as_read)
        button_layout.addWidget(mark_read_btn)
        detail_layout.addLayout(button_layout)
        
        right_layout.addWidget(detail_frame)
        
        # Splitter'a panelleri ekle
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([300, 400])  # Başlangıç boyutları
        
        main_layout.addWidget(content_splitter)
        
        # İstatistik bilgisi
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Toplam: 0")
        self.new_label = QLabel("Yeni: 0")
        self.read_label = QLabel("Okundu: 0")
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.new_label)
        stats_layout.addWidget(self.read_label)
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)
    
    def load_sample_data(self):
        """Örnek verileri yükle - Bu fonksiyon daha sonra veritabanı bağlantısıyla değiştirilecek"""
        # CITIZEN_FEEDBACK_DATA'dan örnek verileri al
        self.feedbacks = CITIZEN_FEEDBACK_DATA
        
        # Durum değerlerini güncelle - "İnceleniyor" ve "Çözümlendi" durumlarını "Okundu" olarak değiştir
        for feedback in self.feedbacks:
            if feedback.get("status") in ["İnceleniyor", "Çözümlendi", "Kapatıldı"]:
                feedback["status"] = "Okundu"
        
        # Örnek yanıtları da yükle
        self.feedback_replies = FEEDBACK_REPLIES
        
        # Tabloyu güncelle
        self.update_table()
        
        # İstatistikleri güncelle
        self.update_statistics()
        
    def update_table(self):
        """Tablo verilerini güncelle"""
        self.feedback_table.setRowCount(0)  # Tabloyu temizle
        
        # Filtrelenmiş verileri tabloya ekle
        row = 0
        for feedback in self.feedbacks:
            # Filtre uygula
            status_filter = self.status_combo.currentText()
            search_text = self.search_input.text().lower()
            
            # Duruma göre filtrele
            if status_filter != "Tümü" and feedback.get("status") != status_filter:
                continue
                
            # Arama metnine göre filtrele
            if search_text and search_text not in feedback.get("title").lower() and search_text not in feedback.get("content").lower():
                continue
                
            # Filtreyi geçen satırları ekle
            self.feedback_table.insertRow(row)
            self.feedback_table.setItem(row, 0, QTableWidgetItem(str(feedback.get("id"))))
            self.feedback_table.setItem(row, 1, QTableWidgetItem(feedback.get("title")))
            self.feedback_table.setItem(row, 2, QTableWidgetItem(feedback.get("date")))
            
            status_item = QTableWidgetItem(feedback.get("status"))
            # Duruma göre hücre stilini değiştir - Açık kırmızı ve yeşil
            if feedback.get("status") == "Yeni":
                status_item.setBackground(Qt.red)  # Kırmızı
                status_item.setForeground(Qt.white)
            elif feedback.get("status") == "Okundu":
                status_item.setBackground(Qt.green)  # Yeşil
                status_item.setForeground(Qt.white)
            
            self.feedback_table.setItem(row, 3, status_item)
            row += 1
    
    def show_feedback_details(self):
        """Seçilen feedback'in detaylarını göster"""
        selected_items = self.feedback_table.selectedItems()
        if not selected_items:
            return
            
        selected_row = selected_items[0].row()
        feedback_id = int(self.feedback_table.item(selected_row, 0).text())
        
        # Seçilen feedback'i bul
        selected_feedback = None
        for feedback in self.feedbacks:
            if feedback.get("id") == feedback_id:
                selected_feedback = feedback
                break
                
        if selected_feedback:
            # Detay alanlarını doldur
            self.detail_id_label.setText(f"ID: {selected_feedback.get('id')}")
            self.detail_date_label.setText(f"Tarih: {selected_feedback.get('date')}")
            self.detail_email_label.setText(f"E-posta: {selected_feedback.get('email')}")
            self.detail_title.setText(selected_feedback.get("title"))
            self.detail_content.setText(selected_feedback.get("content"))
            
            # Lokasyon bilgisini göster (sample_data dan alınan sonra silinecek kodlar)
            if hasattr(self, 'detail_location'):
                self.detail_location.setText(selected_feedback.get("location", "Belirtilmemiş"))
            
            # Durumu seç
            index = self.detail_status.findText(selected_feedback.get("status"))
            if index >= 0:
                self.detail_status.setCurrentIndex(index)
                
            # Mevcut yanıtları göster (sample_data dan alınan sonra silinecek kodlar)
            if hasattr(self, 'replies_text'):
                self.replies_text.clear()
                feedback_id = selected_feedback.get("id")
                if feedback_id in self.feedback_replies:
                    replies_text = ""
                    for reply in self.feedback_replies[feedback_id]:
                        replies_text += f"[{reply['date']}] {reply['sender']}:\n{reply['content']}\n\n"
                    self.replies_text.setText(replies_text)
    
    def filter_feedbacks(self):
        """Feedback'leri filtrele"""
        self.update_table()
    
    def refresh_data(self):
        """Verileri yeniden yükle"""
        # Gerçek uygulamada veritabanından yeniden çekilecek
        QMessageBox.information(self, "Bilgi", "Veriler henüz veritabanına bağlı değil. İleride bu fonksiyon veritabanından verileri yenileyecek.")
        self.load_sample_data()
        self.update_table()
    
    def save_status_change(self):
        """Durum değişikliğini kaydet"""
        selected_items = self.feedback_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir feedback seçin.")
            return
            
        selected_row = selected_items[0].row()
        feedback_id = int(self.feedback_table.item(selected_row, 0).text())
        new_status = self.detail_status.currentText()
        
        # Seçilen feedback'i güncelle
        for feedback in self.feedbacks:
            if feedback.get("id") == feedback_id:
                feedback["status"] = new_status
                break
        
        # Tabloyu güncelle
        self.update_table()
        self.update_statistics()
        
        QMessageBox.information(self, "Bilgi", "Durum değişikliği kaydedildi.")
    
    def send_reply(self):
        """Yanıt gönder"""
        reply_text = self.reply_text.toPlainText().strip()
        if not reply_text:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir yanıt yazın.")
            return
            
        selected_items = self.feedback_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir feedback seçin.")
            return
        
        # Otomatik olarak okundu olarak işaretle
        selected_row = selected_items[0].row()
        feedback_id = int(self.feedback_table.item(selected_row, 0).text())
        
        # Seçilen feedback'i güncelle
        for feedback in self.feedbacks:
            if feedback.get("id") == feedback_id:
                feedback["status"] = "Okundu"
                break
                
        # Durumu güncelle
        index = self.detail_status.findText("Okundu")
        if index >= 0:
            self.detail_status.setCurrentIndex(index)
        
        # Gerçek uygulamada e-posta gönderme işlemi olacak
        QMessageBox.information(self, "Bilgi", "Yanıt gönderme fonksiyonu henüz uygulanmadı. İleride bu fonksiyon e-posta gönderecek.")
        self.reply_text.clear()
        
        # Tabloyu ve istatistikleri güncelle
        self.update_table()
        self.update_statistics()
    
    def mark_as_read(self):
        """Seçili feedback'i okundu olarak işaretle"""
        selected_items = self.feedback_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir feedback seçin.")
            return
            
        selected_row = selected_items[0].row()
        feedback_id = int(self.feedback_table.item(selected_row, 0).text())
        
        # Seçilen feedback'i güncelle
        for feedback in self.feedbacks:
            if feedback.get("id") == feedback_id:
                feedback["status"] = "Okundu"
                break
        
        # Tabloyu güncelle
        index = self.detail_status.findText("Okundu")
        if index >= 0:
            self.detail_status.setCurrentIndex(index)
            
        self.update_table()
        self.update_statistics()
        
        QMessageBox.information(self, "Bilgi", "Feedback okundu olarak işaretlendi.")
    
    def update_statistics(self):
        """İstatistik bilgilerini güncelle"""
        total = len(self.feedbacks)
        new_count = sum(1 for f in self.feedbacks if f.get("status") == "Yeni")
        read_count = sum(1 for f in self.feedbacks if f.get("status") == "Okundu")
        
        self.total_label.setText(f"Toplam: {total}")
        self.new_label.setText(f"Yeni: {new_count}")
        self.read_label.setText(f"Okundu: {read_count}")

        