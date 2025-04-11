from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QCheckBox, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QIcon, QPixmap
from styles.styles_dark import LOGIN_DARK_STYLES
from styles.styles_light import LOGIN_LIGHT_STYLES
from utils import get_icon_path

class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.setFont(QFont('Segoe UI', 10))

class StyledToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.setCursor(Qt.PointingHandCursor)
        self._slide_pos = 0
        self._animation = QPropertyAnimation(self, b"slide_pos")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)

    @pyqtProperty(float)
    def slide_pos(self):
        return self._slide_pos

    @slide_pos.setter
    def slide_pos(self, pos):
        self._slide_pos = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg_rect = self.rect()
        bg_color = QColor('#4a4a4a') if not self.isChecked() else QColor('#4CAF50')
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, 15, 15)

        slider_width = 26
        slider_height = 26
        margin = 2
        x = margin + self._slide_pos * (self.width() - slider_width - 2 * margin)
        slider_rect = QRect(int(x), margin, slider_width, slider_height)
        
        painter.setBrush(QBrush(QColor('white')))
        painter.drawEllipse(slider_rect)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.toggle()
        
        start_value = 0 if not self.isChecked() else 1
        end_value = 1 if not self.isChecked() else 0
        
        self._animation.setStartValue(start_value)
        self._animation.setEndValue(end_value)
        self._animation.start()

class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.theme = 'dark'
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Afet Yönetim Sistemi - Giriş")
        self.setMinimumSize(800, 800)  # Minimum size for the window
        
        self.setStyleSheet(LOGIN_DARK_STYLES)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Top section (existing login components)
        top_section = QVBoxLayout()
        
        # Logo Container
        logo_container = QFrame()
        logo_container.setFixedHeight(120)
        logo_container.setObjectName("logoContainer")
        
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Logo Label
        logo_label = QLabel("AFET-LINK")
        logo_label.setFont(QFont('Segoe UI', 36, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setObjectName("logoLabel")
        
        # Title Label
        title_label = QLabel("Afet Yönetim Sistemi")
        title_label.setFont(QFont('Segoe UI', 14))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_container.setLayout(logo_layout)
        
        # Input Container
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)
        
        # Username Input
        self.username_input = StyledLineEdit("Kullanıcı Adı")
        self.username_input.setObjectName("usernameInput")
        
        # Password Input
        self.password_input = StyledLineEdit("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")
        
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(self.password_input)
        input_container.setLayout(input_layout)
        
        # Theme Toggle Container
        theme_container = QFrame()
        theme_container.setObjectName("themeContainer")
        theme_layout = QHBoxLayout()
        
        theme_label = QLabel("Tema:")
        theme_label.setFont(QFont('Segoe UI', 10))
        
        self.theme_toggle = StyledToggle()
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_toggle)
        theme_layout.addStretch()
        theme_container.setLayout(theme_layout)
        
        # Login Button
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setFixedHeight(45)
        self.login_button.setFont(QFont('Segoe UI', 11))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setObjectName("loginButton")
        
        # Add login components to top section
        top_section.addWidget(logo_container)
        top_section.addSpacing(20)
        top_section.addWidget(input_container)
        top_section.addWidget(theme_container)
        top_section.addWidget(self.login_button)
        
        # NGO Section
        ngo_section = QFrame()
        ngo_section.setObjectName("ngoSection")
        ngo_layout = QGridLayout()
        
        # NGO Logos and Labels
        ngos = [
            {"name": "AKUT", "logo": "akut.png", "color": "#e74c3c"},
            {"name": "Kızılay", "logo": "kizilay.png", "color": "#c0392b"},
            {"name": "UMKE", "logo": "umke.png", "color": "#2ecc71"},
            {"name": "İHH", "logo": "ihh.png", "color": "#3498db"},
            {"name": "Beşir Derneği", "logo": "besir.png", "color": "#9b59b6"},
            {"name": "Ahbap", "logo": "ahbap.png", "color": "#f1c40f"}
        ]
        
        for i, ngo in enumerate(ngos):
            row = i // 3
            col = i % 3
            
            # Create container for each NGO
            ngo_container = QFrame()
            ngo_container.setObjectName(f"ngoContainer_{i}")
            ngo_container_layout = QVBoxLayout()
            
            # Logo
            logo_label = QLabel()
            logo_label.setFixedSize(80, 80)
            logo_label.setScaledContents(True)
            logo_label.setObjectName(f"ngoLogo_{i}")
            
            # Try to load the logo using get_icon_path
            logo_path = get_icon_path(ngo["logo"])
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                logo_label.setPixmap(logo_pixmap)
            else:
                # If logo can't be loaded, show colored background with first letter
                logo_label.setStyleSheet(f"background-color: {ngo['color']}; border-radius: 10px;")
                letter_label = QLabel(ngo["name"][0])
                letter_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
                letter_label.setAlignment(Qt.AlignCenter)
                letter_label.setStyleSheet("color: white;")
                logo_label.setLayout(QVBoxLayout())
                logo_label.layout().addWidget(letter_label)
            
            # Label
            name_label = QLabel(ngo["name"])
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
            name_label.setObjectName(f"ngoLabel_{i}")
            
            ngo_container_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
            ngo_container_layout.addWidget(name_label, alignment=Qt.AlignCenter)
            ngo_container.setLayout(ngo_container_layout)
            
            ngo_layout.addWidget(ngo_container, row, col)
        
        ngo_section.setLayout(ngo_layout)
        
        # Add all sections to main layout
        main_layout.addLayout(top_section)
        main_layout.addWidget(ngo_section)
        
        self.setLayout(main_layout)

    def toggle_theme(self):
        self.theme = 'light' if self.theme_toggle.isChecked() else 'dark'
        
        if self.theme == 'dark':
            self.setStyleSheet(LOGIN_DARK_STYLES)
        else:
            self.setStyleSheet(LOGIN_LIGHT_STYLES) 