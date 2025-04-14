# Qt bileşenleri için stil tanımlamaları




# Dark tema renkleri ve stil tanımları
DARK_BACKGROUND = "#191622"
DARK_TEXT_COLOR = "#E1E1E6"
DARK_INPUT_BG = "rgba(33, 32, 44, 0.8)"
DARK_INPUT_FOCUS_BG = "rgba(41, 40, 55, 0.9)"
DARK_BUTTON_BG = "#500073"
DARK_BUTTON_HOVER_BG = "#3f005a"

# Login page stil tanımları
LOGIN_DARK_STYLES = """
    QWidget {
        background-color:rgb(29, 27, 38);
        color: #E1E1E6;
        font-family: 'Segoe UI', sans-serif;
    }
    
    #logoContainer {
        background-color: transparent;
    }
    
    #logoLabel {
        color:rgb(190, 9, 21);
    }
    
    #titleLabel {
        color: #E1E1E6;
    }
    
    #inputContainer {
        background-color: transparent;
    }
    
    QLineEdit {
        background-color: #201c2b;
        border: 2px solid #201c2b;
        border-radius: 8px;
        padding: 5px 15px;
        color: #E1E1E6;
        font-size: 14px;
    }
    
    QLineEdit:focus {
        border: 2px solid #500073;
    }
    
    QLineEdit::placeholder {
        color: #6c6a7c;
    }
    
    #loginButton {
        background-color:rgb(195, 6, 50);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    
    #loginButton:hover {
        background-color:rgb(90, 11, 11);
    }
    
    #loginButton:pressed {
        background-color:rgb(106, 9, 15);
    }
    
    #themeContainer {
        background-color: transparent;
    }

    #ngoSection {
        background-color: #201c2b;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
    }

    QFrame[objectName^="ngoContainer"] {
        background-color: #13111b;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }

    QLabel[objectName^="ngoLabel"] {
        color: #E1E1E6;
        font-size: 12px;
        font-weight: bold;
        margin-top: 10px;
    }

    QChartView {
        background-color: transparent;
        border: none;
    }
"""




DARK_THEME_STYLE = """
    /* Genel arka plan */
    QWidget {
        background-color: #13111b; /* Koyu arkaplan */
        color: #E1E1E6; /* Yazı rengi */
    }
    """



# Buton stilleri (Daha açık siyah ton)
BUTTON_STYLE = """
    QPushButton {
        background-color: #201c2b; /* Daha açık bir koyu ton */
        color: #E1E1E6;
        padding: 8px 16px;
        border-radius: 4px;
        border: 1px solid #2d2b38; /* İnce kenarlık */
    }
    QPushButton:hover {
        background-color: #2d2b38; /* Hover efekti */
    }
    QPushButton:pressed {
        background-color:rgb(97, 11, 134); /* Tıklandığında mor */
    }
"""

GREEN_BUTTON_STYLE = """
    QPushButton {
        background-color:rgb(19, 188, 109);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color:rgb(13, 170, 113);
    }
    QPushButton:pressed {
        background-color: #1ca163;
    }
"""


RED_BUTTON_STYLE = """
    QPushButton {
        background-color: #e95678;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #d44d6e;
    }
    QPushButton:pressed {
        background-color: #c04465;
    }
"""
# Koyu Mavi Buton (Profesyonel)
DARK_BLUE_BUTTON_STYLE = """
    QPushButton {
        background-color: #5e78e6;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #4c66d4;
    }
    QPushButton:pressed {
        background-color: #4055c2;
    }
"""

REFRESH_BUTTON_STYLE = """
    QPushButton {
        background-color: #37da25;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #10c947;
    }
"""

# Liste widget stilleri (Daha açık arka plan)
LIST_WIDGET_STYLE = """
    QListWidget {
        background-color: #201c2b;
        border-radius: 5px;
        border: none;
        color: #E1E1E6;
        padding: 5px;
    }
    QListWidget::item {
        border-radius: 3px;
        padding: 8px;
        margin: 2px;
    }
    QListWidget::item:hover {
        background-color: #2d2b38;
    }
    QListWidget::item:selected {
        background-color: #500073;
    }
"""

# ComboBox stilleri
COMBOBOX_STYLE = """
    QComboBox {
        background-color: #201c2b;
        color: #E1E1E6;
        padding: 5px;
        border: 1px solid #2d2b38;
        border-radius: 4px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: url(down_arrow.png);
        width: 12px;
        height: 12px;
    }
"""

# LineEdit stilleri
LINE_EDIT_STYLE = """
    QLineEdit {
        background-color: #201c2b;
        color: #E1E1E6;
        padding: 5px;
        border: 1px solid #2d2b38;
        border-radius: 4px;
    }
"""

# TextEdit stilleri
TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: #201c2b;
        border: none;
        border-radius: 5px;
        padding: 8px;
        color: #E1E1E6;
        font-size: 14px;
    }
    QTextEdit:focus {
        background-color: #2d2b38;
    }
"""

# Dialog içindeki TextEdit stilleri
DIALOG_TEXT_STYLE = """
    QTextEdit {
        background-color: #201c2b;
        padding: 10px;
        border: 1px solid #2d2b38;
    }
"""

# Label stilleri
TITLE_LABEL_STYLE = "font-size: 14px; font-weight: bold; color: #E1E1E6;"

#Map stilleri
MAP_STYLE = """
QLabel {
    background-color: #191622;
    color: #E1E1E6;
    font-size: 18px;
    font-weight: bold;
    padding: 10px;
    border: 2px solid #2d2b38;
    border-radius: 10px;
    text-align: center;
}
"""


# Dialog bilgi label stilleri
DIALOG_INFO_LABEL_STYLE = "color: #E1E1E6; background-color: #201c2b; padding: 10px;"

# Tab menü (Daha açık arka plan tonları ve turkuaz seçim rengi)
TAB_WIDGET_STYLE = """
    QTabWidget {
        background-color: #500073;
    }
    QTabWidget::pane {
        border: 1px solid #2d2b38;
        background-color: #13111b;
        top: -1px;
    }
    QTabBar {
        background-color: #13111b;
    }
    QTabBar::tab {
        background-color: #201c2b;
        color: #E1E1E6;
        padding: 8px 0px;
        border: 1px solid #2d2b38;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #500073;
        margin-bottom: -1px;
    }
    QTabBar::tab:hover {
        background-color: #3f005a;
    }
    QTabBar::tab:!selected {
        margin-top: 2px;
    }
    QTabWidget > QWidget > QWidget {
        background: #13111b;
    }
"""


# Mesaj Butonu Stili
MESSAGE_BUTTON_STYLE = """
    QToolButton {
        border: none;
        padding: 5px;
        margin-top: 2px;
        border-radius: 3px;
        background-color: transparent;
    }
    QToolButton:hover {
        background-color: #500073;
    }
"""


# Tablo widget stilleri (Başlık ve hücre renkleri düzenlendi)
TABLE_WIDGET_STYLE = """
    QTableWidget {
        background-color: #13111b;
        color: #E1E1E6;
        border: none;
    }
    QTableWidget::item {
        background-color: #201c2b;
        color: #E1E1E6;
        border: 1px solid #2d2b38;
    }
    QTableWidget::item:selected {
        background-color: #500073;
        color: white;
    }
    QTableWidget::item:hover {
        background-color: #2d2b38;
    }
    QTableWidget::item:focus {
        border: 2px solid #500073;
    }
    QHeaderView::section {
        background-color: #201c2b;
        color: #E1E1E6;
        font-weight: bold;
        padding: 5px;
        border: 1px solid #2d2b38;
    }
    QTableCornerButton::section {
        background-color: #201c2b;
        border: 1px solid #2d2b38;
    }
"""

#Takım Ağacı Stilleri
TEAM_TREE_STYLE = """
    QTreeWidget {
        background-color: #13111b;
        border: 1px solid #2d2b38;
        color: #E1E1E6;
    }
    QTreeWidget::item {
        background-color: #201c2b;
        padding: 5px;
        border-bottom: 1px solid #2d2b38;
        color: #E1E1E6;
    }
    QTreeWidget::item:selected {
        background-color: #500073;
        color: white;
    }
    QTreeWidget::item:hover {
        background-color: #2d2b38;
    }
    QHeaderView::section {
        background-color: #201c2b;
        color: #E1E1E6;
        font-weight: bold;
        padding: 5px;
        border: 1px solid #2d2b38;
    }
"""

# Arama ve filtreleme stilleri
SEARCH_BOX_STYLE = """
    QLineEdit {
        background-color: #201c2b;
        border: none;
        border-radius: 5px;
        padding: 8px;
        color: #E1E1E6;
        font-size: 14px;
    }
    QLineEdit:focus {
        background-color: #2d2b38;
    }
"""

COMBO_BOX_STYLE = """
    QComboBox {
        background-color: #201c2b;
        color: #E1E1E6;
        padding: 5px;
        border: 1px solid #2d2b38;
        border-radius: 3px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: url(icons/down-arrow.png);
        width: 12px;
        height: 12px;
    }
"""

HEADER_STYLE = """
    QHeaderView::section {
        background-color: #201c2b;
        color: #E1E1E6;
        padding: 5px;
        border: 1px solid #2d2b38;
        font-weight: bold;
    }
"""

# Düzenle butonu için özel mavi stil
EDIT_BUTTON_STYLE = """
QPushButton {
    background-color: #5e78e6;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4c66d4;
}
QPushButton:pressed {
    background-color: #4055c2;
}
"""

# İletişim butonları için özel turuncu stil
COMMUNICATION_BUTTON_STYLE = """
QPushButton {
    background-color: #f7b267;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #f8a250;
}
QPushButton:pressed {
    background-color: #f69133;
}
"""

# Kaynak Yönetimi Arama Widget Stili
SEARCH_WIDGET_STYLE = """
    QWidget {
        background-color: #201c2b;
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
    }
"""

# Kaynak Yönetimi Input Stili
RESOURCE_INPUT_STYLE = """
    QLineEdit {
        padding: 8px;
        border-radius: 4px;
        background: #191622;
        color: #E1E1E6;
        border: 1px solid #2d2b38;
    }
    QLineEdit:focus {
        border: 1px solid #500073;
    }
"""

# Kaynak Yönetimi Buton Stili
RESOURCE_BUTTON_STYLE = """
    QPushButton {
        padding: 10px;
        border-radius: 5px;
        background: #201c2b;
        color: #E1E1E6;
        border: 1px solid #de2525;
    }
    QPushButton:hover {
        background: #bc2131;
    }
"""

# Kaynak Yönetimi Tablo Stili
RESOURCE_TABLE_STYLE = """
    QTableWidget {
        background-color: #13111b;
        border-radius: 8px;
        padding: 5px;
        gridline-color: #2d2b38;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #2d2b38;
        color: #E1E1E6;
        background-color: #201c2b;
    }
    QTableWidget::item:alternate {
        background-color: #191622;
    }
    QHeaderView::section {
        background-color: #0d00a6;
        padding: 8px;
        border: none;
        font-weight: bold;
        color: white;
    }
"""

# Kaynak Yönetimi GroupBox Stili
RESOURCE_GROUP_STYLE = """
    QGroupBox {
        background-color: #201c2b;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
    }
    QGroupBox::title {
        color: white;
        background-color: #0d00a6;
        padding: 5px 10px;
        border-radius: 4px;
        subcontrol-position: top center;
        margin-top: -10px;
    }
"""

# Kaynak Yönetimi Ekle Buton Stili
RESOURCE_ADD_BUTTON_STYLE = """
    QPushButton {
        padding: 10px;
        border-radius: 5px;
        background: #1dc925;
        color: white;
        border: none;
        font-weight: bold;
    }
    QPushButton:hover {
        background: #5260da;
    }
"""

# Kaynak Yönetimi TextEdit Stili
RESOURCE_TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: #191622;
        border-radius: 4px;
        padding: 10px;
        color: #E1E1E6;
        border: 1px solid #2d2b38;
    }
"""

# Ana pencere stili
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #1a1e1e;
        color: #E1E1E6;
    }
"""

# Scroll bar stili
SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        border: none;
        background-color: #201c2b;
        width: 10px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #2d2b38;
        min-height: 30px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #3a3846;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background-color: #201c2b;
        height: 10px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: #2d2b38;
        min-width: 30px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #3a3846;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""

# Citizen Report modülüne ait stil tanımlamaları
CITIZEN_TABLE_STYLE = """
    QTableWidget {
        background-color: #1e222f;
        alternate-background-color: #2c3e50;
        color: white;
        gridline-color: #3a3f55;
        border: 1px solid #3a3f55;
        border-radius: 4px;
    }
    QTableWidget::item {
        padding: 4px;
        border: none;
    }
    QTableWidget::item:selected {
        background-color: #3498db;
        color: white;
    }
    QHeaderView::section {
        background-color: #34495e;
        color: white;
        padding: 6px;
        border: 1px solid #3a3f55;
        font-weight: bold;
    }
    QTableWidget QTableCornerButton::section {
        background-color: #34495e;
        border: 1px solid #3a3f55;
    }
    QScrollBar:vertical {
        background-color: #2c3e50;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #3a3f55;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

CITIZEN_GREEN_BUTTON_STYLE = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #2ecc71;
    }
    QPushButton:pressed {
        background-color: #219653;
    }
"""

CITIZEN_DARK_BLUE_BUTTON_STYLE = """
    QPushButton {
        background-color: #2980b9;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3498db;
    }
    QPushButton:pressed {
        background-color: #1c587f;
    }
"""

CITIZEN_RED_BUTTON_STYLE = """
    QPushButton {
        background-color: #c0392b;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e74c3c;
    }
    QPushButton:pressed {
        background-color: #922b21;
    }
"""

CITIZEN_ORANGE_BUTTON_STYLE = """
    QPushButton {
        background-color: #d35400;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e67e22;
    }
    QPushButton:pressed {
        background-color: #b64100;
    }
"""


