from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QComboBox, QFormLayout,
                            QDialogButtonBox)
from PyQt5.QtGui import QIcon
from styles_dark import *

class BaseDialog(QDialog):
    """Temel dialog sınıfı"""
    def __init__(self, parent=None, title="", width=400, height=300):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

class TeamDialog(BaseDialog):
    """Ekip işlemleri için dialog sınıfı"""
    def __init__(self, parent=None, team_data=None, is_edit=False):
        super().__init__(parent, 
                        title="Ekip Düzenle" if is_edit else "Ekip Ekle",
                        width=400, height=300)
        self.setup_ui(team_data)
    
    def setup_ui(self, team_data=None):
        form_layout = QFormLayout()
        
        self.team_id = QLineEdit(team_data[0] if team_data else "")
        self.leader = QLineEdit(team_data[1] if team_data else "")
        self.institution = QLineEdit(team_data[2] if team_data else "")
        self.status = QComboBox()
        self.status.addItems(["Müsait", "Meşgul"])
        if team_data:
            self.status.setCurrentText(team_data[3])
        self.contact = QLineEdit(team_data[4] if team_data else "")
        
        form_layout.addRow("Ekip ID:", self.team_id)
        form_layout.addRow("Ekip Lideri:", self.leader)
        form_layout.addRow("Kurum:", self.institution)
        form_layout.addRow("Durum:", self.status)
        form_layout.addRow("İletişim:", self.contact)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        
        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.buttons) 