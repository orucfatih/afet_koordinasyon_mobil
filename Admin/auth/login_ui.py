from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QCheckBox, QFrame, QGridLayout,
                           QStackedWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty, QSize
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QIcon, QPixmap, QCursor
from styles.styles_dark import LOGIN_DARK_STYLES
from styles.styles_light import LOGIN_LIGHT_STYLES
from utils import get_icon_path

class LoginCard(QFrame):
    def __init__(self, title, icon_path, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(550, 200)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("loginCard")

        
        # Use grid layout for better alignment control
        layout = QGridLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Icon Container - centered in left half
        icon_container = QFrame()
        icon_container.setFixedSize(120, 120)  # Make slightly larger
        icon_container.setStyleSheet("""
            background-color: rgba(30, 0, 0, 0.1);
            border-radius: 20px;
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(10, 10, 10, 10)
        icon_layout.setAlignment(Qt.AlignCenter)  # Center the icon in container
        
        # Icon - larger and centered
        icon_label = QLabel()
        icon_label.setFixedSize(90, 90)  # Make icon larger
        icon_label.setScaledContents(True)
        icon_label.setAlignment(Qt.AlignCenter)  # Center the icon
        icon_pixmap = QPixmap(get_icon_path(icon_path))
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap)
        
        icon_layout.addWidget(icon_label)
        
        # Text Container
        text_container = QFrame()
        text_layout = QVBoxLayout(text_container)
        text_layout.setAlignment(Qt.AlignVCenter)  # Vertically center
        text_layout.setSpacing(15)  # Increased spacing
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("color: #ffffff;")
        
        subtitle_label = QLabel("Giriş yapmak için tıklayın")
        subtitle_label.setFont(QFont('Segoe UI', 11))
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        
        # Add to grid layout
        layout.addWidget(icon_container, 0, 0, Qt.AlignCenter)
        layout.addWidget(text_container, 0, 1, Qt.AlignVCenter)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.main_window:
            self.main_window.show_login_form(self.objectName())

            
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
        self.setMinimumSize(1920, 1080)
        self.setStyleSheet(LOGIN_DARK_STYLES)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
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
        main_layout.addWidget(logo_container)
        
        # Stacked Widget for switching between cards and login form
        self.stacked_widget = QStackedWidget()
        
        # Cards Page
        cards_page = QWidget()
        cards_layout = QVBoxLayout()
        
        # Login Cards Container Frame
        login_cards_frame = QFrame()
        login_cards_frame.setObjectName("loginCardsFrame")
        login_cards_frame.setStyleSheet("""
            #loginCardsFrame {
                background-color: #13111b;
                border-radius: 25px;
                padding: 20px;
                margin: 20px;
            }
        """)
        
        # Login Cards Layout
        login_cards = QHBoxLayout(login_cards_frame)
        login_cards.setSpacing(30)  # Kartlar arası boşluk arttı
        login_cards.setContentsMargins(30, 30, 30, 30)  # Kenar boşlukları arttı
        login_cards.setAlignment(Qt.AlignCenter)
        
        # Create cards
        self.personel_card = LoginCard("Personel Girişi", "afad.png", main_window=self)
        self.personel_card.setObjectName("personel")
        self.admin_card = LoginCard("Yönetici Girişi", "bakanlik.png", main_window=self)
        self.admin_card.setObjectName("admin")
        
        login_cards.addWidget(self.personel_card)
        login_cards.addWidget(self.admin_card)
        
        cards_layout.addWidget(login_cards_frame)
        
        # Add NGO section to cards page
        cards_layout.addWidget(self.create_ngo_section())
        
        cards_page.setLayout(cards_layout)
        
        # Login Form Page
        login_page = QWidget()
        login_layout = QVBoxLayout()
        
        # Header Container (Back Button + Title)
        header_container = QFrame()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        # Back button with text
        back_btn_container = QFrame()
        back_btn_layout = QHBoxLayout()
        back_btn_layout.setContentsMargins(0, 0, 0, 0)
        back_btn_layout.setSpacing(5)
        
        back_btn = QPushButton()
        back_btn.setIcon(QIcon(get_icon_path('back.png')))
        back_btn.setIconSize(QSize(24, 24))
        back_btn.setFixedSize(40, 40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        back_btn.clicked.connect(self.show_cards)
        
        back_label = QLabel("Geri Dön")
        back_label.setFont(QFont('Segoe UI', 12))
        back_label.setCursor(Qt.PointingHandCursor)
        back_label.setStyleSheet("color: #3498db;")
        back_label.mousePressEvent = lambda e: self.show_cards()
        
        back_btn_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
            }
        """)
        
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.addWidget(back_label)
        back_btn_container.setLayout(back_btn_layout)
        
        # Title Container
        title_container = QFrame()
        title_container.setFixedWidth(400)  # Sabit genişlik
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignCenter)
        
        self.login_type_label = QLabel()
        self.login_type_label.setFont(QFont('Segoe UI', 22, QFont.Bold))  # Biraz daha küçük
        self.login_type_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.login_type_label)
        
        # Header layout düzenleme
        header_layout.addWidget(back_btn_container, 1)  # Stretch factor 1
        header_layout.addWidget(title_container, 2)     # Stretch factor 2
        header_layout.addStretch(1)                     # Sağ tarafı dengele
        
        header_container.setLayout(header_layout)
        
        # Input Container
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)
        
        self.username_input = StyledLineEdit("Kullanıcı Adı")
        self.username_input.setObjectName("usernameInput")
        
        self.password_input = StyledLineEdit("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")
        
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(self.password_input)
        input_container.setLayout(input_layout)
        
        # Theme Toggle
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
        
        # Add components to login layout
        login_layout.addWidget(header_container)
        login_layout.addWidget(input_container)
        login_layout.addWidget(theme_container)
        login_layout.addWidget(self.login_button)
        login_layout.addStretch()
        
        # Add NGO section to login page
        login_layout.addWidget(self.create_ngo_section())
        
        login_page.setLayout(login_layout)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(cards_page)
        self.stacked_widget.addWidget(login_page)
        
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
        # Show cards initially
        self.show_cards()

    def show_cards(self):
        """Kart seçim ekranını göster"""
        self.stacked_widget.setCurrentIndex(0)
        # Formu temizle
        self.username_input.clear()
        self.password_input.clear()
        
    def show_login_form(self, login_type):
        """Giriş formunu göster"""
        if login_type == "personel":
            self.login_type_label.setText("Personel Girişi")
        else:
            self.login_type_label.setText("Yönetici Girişi")
        self.stacked_widget.setCurrentIndex(1)
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()

    def create_ngo_section(self):
        """STK bölümünü oluştur"""
        ngo_section = QFrame()
        ngo_section.setObjectName("ngoSection")
        ngo_layout = QGridLayout()
        
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
            
            ngo_container = QFrame()
            ngo_container.setObjectName(f"ngoContainer_{i}")
            ngo_container_layout = QVBoxLayout()
            
            logo_label = QLabel()
            logo_label.setFixedSize(80, 80)
            logo_label.setScaledContents(True)
            logo_label.setObjectName(f"ngoLogo_{i}")
            
            logo_path = get_icon_path(ngo["logo"])
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                logo_label.setPixmap(logo_pixmap)
            else:
                logo_label.setStyleSheet(f"background-color: {ngo['color']}; border-radius: 10px;")
                letter_label = QLabel(ngo["name"][0])
                letter_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
                letter_label.setAlignment(Qt.AlignCenter)
                letter_label.setStyleSheet("color: white;")
                logo_label.setLayout(QVBoxLayout())
                logo_label.layout().addWidget(letter_label)
            
            name_label = QLabel(ngo["name"])
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
            name_label.setObjectName(f"ngoLabel_{i}")
            
            ngo_container_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
            ngo_container_layout.addWidget(name_label, alignment=Qt.AlignCenter)
            ngo_container.setLayout(ngo_container_layout)
            
            ngo_layout.addWidget(ngo_container, row, col)
        
        ngo_section.setLayout(ngo_layout)
        return ngo_section

    def toggle_theme(self):
        self.theme = 'light' if self.theme_toggle.isChecked() else 'dark'
        if self.theme == 'dark':
            self.setStyleSheet(LOGIN_DARK_STYLES)
        else:
            self.setStyleSheet(LOGIN_LIGHT_STYLES) 