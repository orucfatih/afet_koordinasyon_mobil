from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QProgressBar, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from .sms_auth import SMSAuthDialog
from .sms_utils import SMSUtils

class SMSSenderWidget(QWidget):
    sms_sent = pyqtSignal(bool, str)  # Success status and message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.authenticated = False
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Mesaj yazma alanı
        msg_label = QLabel("Mesaj İçeriği:")
        self.message_edit = QTextEdit()
        self.message_edit.textChanged.connect(self.update_message_info)
        layout.addWidget(msg_label)
        layout.addWidget(self.message_edit)
        
        # Mesaj bilgileri
        info_layout = QHBoxLayout()
        self.char_count_label = QLabel("Karakter: 0")
        self.sms_count_label = QLabel("SMS Sayısı: 0")
        info_layout.addWidget(self.char_count_label)
        info_layout.addWidget(self.sms_count_label)
        layout.addLayout(info_layout)
        
        # Alıcı numarası
        recipient_layout = QHBoxLayout()
        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("Alıcı Telefon Numarası")
        recipient_layout.addWidget(self.recipient_edit)
        
        # Tekrar sayısı
        repeat_label = QLabel("Tekrar:")
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 10)
        recipient_layout.addWidget(repeat_label)
        recipient_layout.addWidget(self.repeat_spin)
        layout.addLayout(recipient_layout)
        
        # Maliyet bilgisi
        self.cost_label = QLabel("Tahmini Maliyet: 0.00 TL")
        layout.addWidget(self.cost_label)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Gönder butonu
        self.send_button = QPushButton("Gönder")
        self.send_button.clicked.connect(self.send_sms)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)
        
    def update_message_info(self):
        message = self.message_edit.toPlainText()
        char_count = len(message)
        sms_count = SMSUtils.calculate_sms_count(message)
        
        self.char_count_label.setText(f"Karakter: {char_count}")
        self.sms_count_label.setText(f"SMS Sayısı: {sms_count}")
        
        # Maliyet hesapla
        recipient_count = 1  # Şimdilik tek alıcı
        repeat_count = self.repeat_spin.value()
        cost = SMSUtils.estimate_cost(message, recipient_count * repeat_count)
        self.cost_label.setText(f"Tahmini Maliyet: {cost:.2f} TL")
        
    def send_sms(self):
        if not self.authenticated:
            auth_dialog = SMSAuthDialog(self)
            if auth_dialog.exec_() != SMSAuthDialog.Accepted:
                return
            self.authenticated = True
            
        message = self.message_edit.toPlainText()
        phone = self.recipient_edit.text()
        
        # Mesaj içeriği kontrolü
        valid, error_msg = SMSUtils.validate_message_content(message)
        if not valid:
            QMessageBox.warning(self, "Hata", error_msg)
            return
            
        # Telefon numarası kontrolü
        if not SMSUtils.validate_phone_number(phone):
            QMessageBox.warning(self, "Hata", "Geçersiz telefon numarası formatı.")
            return
            
        # Telefon numarasını formatla
        formatted_phone = SMSUtils.format_phone_number(phone)
        
        # TODO: Implement actual SMS sending logic here
        # For now, just show a success message
        QMessageBox.information(self, "Başarılı", 
                              f"SMS gönderimi başarılı!\nAlıcı: {formatted_phone}\n"
                              f"Mesaj: {message}")
        self.sms_sent.emit(True, "SMS başarıyla gönderildi") 