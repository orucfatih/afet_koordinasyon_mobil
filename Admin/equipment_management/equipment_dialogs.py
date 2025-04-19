from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox,
                         QDialogButtonBox, QLabel, QMessageBox)
from PyQt5.QtGui import QIntValidator

class EquipmentDialog(QDialog):
    """Ekipman ekleme/düzenleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Ekipman Bilgileri")
        self.setFixedSize(400, 500)
        
        layout = QFormLayout()
        
        # Form alanları
        self.equipment_id = QLineEdit()
        self.equipment_name = QLineEdit()
        self.equipment_type = QComboBox()
        self.equipment_type.addItems([
            "Kurtarma Ekipmanı", "Arama Ekipmanı", "Güç Ekipmanı",
            "Güç Ekipmanı - Jeneratörler", "Sağlık Ekipmanı", "Yangın Ekipmanı", 
            "İletişim Ekipmanı", "Su Tahliye", "Diğer"
        ])
        
        self.status = QComboBox()
        self.status.addItems(["Aktif", "Bakımda", "Onarımda"])
        
        self.last_check = QLineEdit()
        self.next_check = QLineEdit()
        self.responsible = QLineEdit()
        self.location = QComboBox()
        self.location.addItems(["Ana Depo", "Mobil Depo 1", "Mobil Depo 2", "Saha"])
        self.location.setEditable(True)
        self.status_detail = QLineEdit()
        self.team_id = QLineEdit()
        
        # Form alanlarını ekle
        layout.addRow("Ekipman ID:", self.equipment_id)
        layout.addRow("Ekipman Adı:", self.equipment_name)
        layout.addRow("Tür:", self.equipment_type)
        layout.addRow("Durum:", self.status)
        layout.addRow("Son Kontrol:", self.last_check)
        layout.addRow("Sonraki Kontrol:", self.next_check)
        layout.addRow("Sorumlu Personel:", self.responsible)
        layout.addRow("Konum/Depo:", self.location)
        layout.addRow("Durum Detayı:", self.status_detail)
        layout.addRow("Ekip ID:", self.team_id)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        """Form verilerini doğrula ve kaydet"""
        if not all([
            self.equipment_id.text(),
            self.equipment_name.text(),
            self.last_check.text(),
            self.next_check.text(),
            self.responsible.text(),
            self.team_id.text()
        ]):
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
            return
        
        self.accept()

    def get_values(self):
        """Dialog form değerlerini liste olarak döndür"""
        return [
            self.equipment_id.text(),
            self.equipment_name.text(),
            self.equipment_type.currentText(),
            self.status.currentText(),
            self.last_check.text(),
            self.next_check.text(),
            self.responsible.text(),
            self.location.currentText(),
            self.status_detail.text(),
            self.team_id.text()
        ]

    def set_values(self, values):
        """Dialog form alanlarını verilen değerlerle doldur"""
        self.equipment_id.setText(values[0])
        self.equipment_name.setText(values[1])
        self.equipment_type.setCurrentText(values[2])
        self.status.setCurrentText(values[3])
        self.last_check.setText(values[4])
        
        # Eğer sonraki kontrol tarihini içeren bir array ise
        if len(values) > 5:
            self.next_check.setText(values[5])
            if len(values) > 6:
                self.responsible.setText(values[6])
                if len(values) > 7:
                    self.location.setCurrentText(values[7])
                    if len(values) > 8:
                        self.status_detail.setText(values[8])
                        if len(values) > 9:
                            self.team_id.setText(values[9])
                        else:
                            self.team_id.setText("")
                    else:
                        self.status_detail.setText("")
                else:
                    self.location.setCurrentText("Ana Depo")
            else:
                self.responsible.setText("")
        else:
            self.next_check.setText("")

class InventoryDialog(QDialog):
    """Envanter ekleme/düzenleme dialog'u"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Envanter Bilgileri")
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        # Form alanları
        self.location = QComboBox()
        self.location.addItems(["Ana Depo", "Mobil Depo 1", "Mobil Depo 2", "Saha", "Yeni Depo"])
        self.location.setEditable(True)  # Kullanıcı yeni lokasyon girebilir
        
        self.total_equipment = QLineEdit()
        self.active = QLineEdit()
        self.in_maintenance = QLineEdit()
        self.critical_level = QLineEdit()
        
        # Sayısal alanlar için validasyon
        self.total_equipment.setValidator(QIntValidator(0, 9999))
        self.active.setValidator(QIntValidator(0, 9999))
        self.in_maintenance.setValidator(QIntValidator(0, 9999))
        self.critical_level.setValidator(QIntValidator(0, 9999))
        
        # Form alanlarını ekle
        layout.addRow("Lokasyon/Depo:", self.location)
        layout.addRow("Toplam Ekipman:", self.total_equipment)
        layout.addRow("Aktif Ekipman:", self.active)
        layout.addRow("Bakımda Olan:", self.in_maintenance)
        layout.addRow("Kritik Seviye:", self.critical_level)
        
        # Yardım metni
        help_label = QLabel("* Kritik seviye, stok miktarının altına düştüğünde uyarı verilecek eşik değeridir.")
        help_label.setStyleSheet("color: #FFA500; font-size: 11px;")
        layout.addRow("", help_label)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        """Form verilerini doğrula ve kaydet"""
        if not all([
            self.location.currentText(),
            self.total_equipment.text(),
            self.active.text(),
            self.in_maintenance.text(),
            self.critical_level.text()
        ]):
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        # Aktif + Bakımda sayısının toplam sayıdan fazla olmadığını kontrol et
        total = int(self.total_equipment.text())
        active = int(self.active.text())
        in_maintenance = int(self.in_maintenance.text())
        
        if active + in_maintenance > total:
            QMessageBox.warning(self, "Uyarı", "Aktif ve bakımdaki ekipman sayısı toplamı, toplam ekipman sayısından fazla olamaz!")
            return
        
        self.accept()

    def get_values(self):
        """Dialog form değerlerini liste olarak döndür"""
        return [
            self.location.currentText(),
            self.total_equipment.text(),
            self.active.text(),
            self.in_maintenance.text(),
            self.critical_level.text()
        ]

    def set_values(self, values):
        """Dialog form alanlarını verilen değerlerle doldur"""
        self.location.setCurrentText(values[0])
        self.total_equipment.setText(values[1])
        self.active.setText(values[2])
        self.in_maintenance.setText(values[3])
        self.critical_level.setText(values[4]) 