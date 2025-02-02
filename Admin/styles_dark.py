# Qt bileşenleri için stil tanımlamaları




# Dark tema renkleri ve stil tanımları
DARK_BACKGROUND = "#2c3e50"
DARK_TEXT_COLOR = "#ffffff"
DARK_INPUT_BG = "rgba(255, 255, 255, 0.1)"
DARK_INPUT_FOCUS_BG = "rgba(255, 255, 255, 0.2)"
DARK_BUTTON_BG = "#3498db"
DARK_BUTTON_HOVER_BG = "#2980b9"

# Login page stil tanımları
LOGIN_DARK_STYLES = """
    QWidget {
        background-color: #1a1a1a;
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    
    #logoContainer {
        background-color: transparent;
    }
    
    #logoLabel {
        color: #4CAF50;
    }
    
    #titleLabel {
        color: #ffffff;
    }
    
    #inputContainer {
        background-color: transparent;
    }
    
    QLineEdit {
        background-color: #2d2d2d;
        border: 2px solid #2d2d2d;
        border-radius: 8px;
        padding: 5px 15px;
        color: #ffffff;
        font-size: 14px;
    }
    
    QLineEdit:focus {
        border: 2px solid #4CAF50;
    }
    
    QLineEdit::placeholder {
        color: #808080;
    }
    
    #loginButton {
        background-color: #4CAF50;
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    
    #loginButton:hover {
        background-color: #45a049;
    }
    
    #loginButton:pressed {
        background-color: #3d8b40;
    }
    
    #themeContainer {
        background-color: transparent;
    }
"""




DARK_THEME_STYLE = """
    /* Genel arka plan */
    QWidget {
        background-color: #1e1e1e; /* Koyu siyah ton */
        color: white; /* Yazı rengi */
    }
    """



# Buton stilleri (Daha açık siyah ton)
BUTTON_STYLE = """
    QPushButton {
        background-color: #2a2a2a; /* Daha açık bir siyah */
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        border: 1px solid #444; /* İnce gri kenarlık */
    }
    QPushButton:hover {
        background-color: #444; /* Hover efekti */
    }
    QPushButton:pressed {
        background-color: #009999; /* Tıklandığında turkuaz */
    }
"""

GREEN_BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
"""


RED_BUTTON_STYLE = """
    QPushButton {
        background-color: #cc5a5a;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #a34d4d;
    }
"""
# Koyu Mavi Buton (Profesyonel)
DARK_BLUE_BUTTON_STYLE = """
    QPushButton {
        background-color: #3b5998;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #2d4373;
    }
"""

REFRESH_BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
"""

# Liste widget stilleri (Daha açık arka plan)
LIST_WIDGET_STYLE = """
    QListWidget {
        background-color: #2a2a2a; /* Liste arka plan daha açık siyah */
        border: 1px solid #3a3f55; /* İnce kenarlık */
        border-radius: 4px;
        color: white;
    }
    QListWidget::item {
        background-color: #2e2e2e; /* Liste hücre arka planı */
        padding: 5px;
        border-bottom: 1px solid #444; /* Alt çizgi */
    }
    QListWidget::item:selected {
        background-color: #009999; /* Seçili hücre */
        color: white;
    }
    QListWidget::item:hover {
        background-color: #444; /* Hover efekti */
    }
"""

# ComboBox stilleri
COMBOBOX_STYLE = """
    QComboBox {
        background-color: #262a3c;
        color: white;
        padding: 5px;
        border: 1px solid #3a3f55;
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
        background-color: #2e2e2e;
        color: white;
        padding: 5px;
        border: 1px solid #555;
        border-radius: 4px;
    }
"""

# TextEdit stilleri
TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: #2e2e2e;
        color: white;
        padding: 5px;
        border: 1px solid #555;
        border-radius: 4px;
    }
"""

# Dialog içindeki TextEdit stilleri
DIALOG_TEXT_STYLE = """
    QTextEdit {
        background-color: #282829;
        padding: 10px;
        border: 1px solid #3a3f55;
    }
"""

# Label stilleri
TITLE_LABEL_STYLE = "font-size: 14px; font-weight: bold; color: white;"

#Map stilleri
MAP_STYLE = """
QLabel {
    background-color: #2b2b2b;  /* Koyu arka plan */
    color: #f0f0f0;            /* Açık yazı rengi */
    font-size: 18px;           /* Orta boy yazı */
    font-weight: bold;         /* Kalın yazı */
    padding: 10px;             /* İçerik boşluğu */
    border: 2px solid #444;    /* İnce çerçeve */
    border-radius: 10px;       /* Yumuşak köşeler */
    text-align: center;        /* Metin ortalama */
}
"""


# Dialog bilgi label stilleri
DIALOG_INFO_LABEL_STYLE = "color: white; background-color: #262a3c; padding: 10px;"

# Tab menü (Daha açık arka plan tonları)
TAB_WIDGET_STYLE = """
    QTabWidget::pane {
        background-color: #2a2a2a; /* Genel arka plan rengi */
        border: 1px solid #3a3f55;
    }
    QTabBar::tab {
        background-color: #2e2e2e; /* Sekme arka planı */
        color: white;
        padding: 12px 20px;
        border: 1px solid #444; /* Daha belirgin kenarlık */
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 150px;
        max-width: 250px;
        text-align: center;
    }
    QTabBar::tab:selected {
        background-color: #009999;
        color: white;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background-color: #444; /* Hover efekti */
        color: #00ccff;
    }
"""
# Tablo widget stilleri (Başlık ve hücre renkleri düzenlendi)
TABLE_WIDGET_STYLE = """
    QTableWidget {
        background-color: #1e1e1e; /* Genel arka plan */
        color: white; /* Yazı rengi */
        border: none;
    }
    QTableWidget::item {
        background-color: #2e2e2e; /* Hücre arka planı */
        color: white;
        border: 1px solid #555; /* Hücre kenarlıkları */
    }
    QTableWidget::item:selected {
        background-color: #009999; /* Seçili hücre arka planı */
        color: white;
    }
    QTableWidget::item:hover {
        background-color: #444; /* Hover efekti */
    }
    QTableWidget::item:focus {
        border: 2px solid #009999; /* Seçili hücre kenarlığı */
    }
    QHeaderView::section {
        background-color: #2e2e2e; /* Başlık arka planı */
        color: white; /* Başlık yazı rengi */
        font-weight: bold;
        padding: 5px;
        border: 1px solid #3a3f55; /* Başlık kenarlığı */
    }
    QTableCornerButton::section {
        background-color: #2e2e2e; /* Sol üst köşe hücresinin rengi */
        border: 1px solid #3a3f55;
    }
"""

#Takım Ağacı Stilleri
TEAM_TREE_STYLE = """
    QTreeWidget {
        background-color: #1e1e1e; /* Genel arka plan (daha koyu siyah) */
        border: 1px solid #3a3f55; /* Kenarlık */
        color: white; /* Yazı rengi */
    }
    QTreeWidget::item {
        background-color: #2a2a2a; /* Hücre arka planı (daha açık siyah) */
        padding: 5px; /* Hücre içi boşluk */
        border-bottom: 1px solid #3a3f55; /* Alt çizgi */
        color: white;
    }
    QTreeWidget::item:selected {
        background-color: #009999; /* Seçili hücre arka planı (turkuaz ton) */
        color: white;
    }
    QTreeWidget::item:hover {
        background-color: #444; /* Hover efekti (gri ton) */
    }
    QHeaderView::section {
        background-color: #2e2e2e; /* Başlık arka planı */
        color: white; /* Başlık yazı rengi */
        font-weight: bold;
        padding: 5px;
        border: 1px solid #3a3f55; /* Başlık kenarlığı */
    }
"""

# Arama ve filtreleme stilleri
SEARCH_BOX_STYLE = """
    QLineEdit {
        background-color: #2e2e2e;
        color: white;
        padding: 5px;
        border: 1px solid #555;
        border-radius: 3px;
    }
"""

COMBO_BOX_STYLE = """
    QComboBox {
        background-color: #2e2e2e;
        color: white;
        padding: 5px;
        border: 1px solid #555;
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
        background-color: #2e2e2e;
        color: white;
        padding: 5px;
        border: 1px solid #3a3f55;
        font-weight: bold;
    }
"""

# Düzenle butonu için özel mavi stil
EDIT_BUTTON_STYLE = """
QPushButton {
    background-color: #2980b9;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3498db;
}
QPushButton:pressed {
    background-color: #2475a8;
}
"""

# İletişim butonları için özel turuncu stil
COMMUNICATION_BUTTON_STYLE = """
QPushButton {
    background-color: #d35400;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #e67e22;
}
QPushButton:pressed {
    background-color: #c44e00;
}
"""

# Kaynak Yönetimi Arama Widget Stili
SEARCH_WIDGET_STYLE = """
    QWidget {
        background-color: #2a2a2a;
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
        background: #333;
        color: white;
        border: 1px solid #555;
    }
    QLineEdit:focus {
        border: 1px solid #009688;
    }
"""

# Kaynak Yönetimi Buton Stili
RESOURCE_BUTTON_STYLE = """
    QPushButton {
        padding: 10px;
        border-radius: 5px;
        background: #2a2a2a;
        color: white;
        border: 1px solid #009688;
    }
    QPushButton:hover {
        background: #009688;
    }
"""

# Kaynak Yönetimi Tablo Stili
RESOURCE_TABLE_STYLE = """
    QTableWidget {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 5px;
        gridline-color: #444;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #444;
    }
    QHeaderView::section {
        background-color: #009688;
        padding: 8px;
        border: none;
        font-weight: bold;
    }
"""

# Kaynak Yönetimi GroupBox Stili
RESOURCE_GROUP_STYLE = """
    QGroupBox {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
    }
    QGroupBox::title {
        color: #009688;
        subcontrol-position: top center;
        padding: 5px;
    }
"""

# Kaynak Yönetimi Ekle Buton Stili
RESOURCE_ADD_BUTTON_STYLE = """
    QPushButton {
        padding: 10px;
        border-radius: 5px;
        background: #009688;
        color: white;
        border: none;
        font-weight: bold;
    }
    QPushButton:hover {
        background: #00796b;
    }
"""

# Kaynak Yönetimi TextEdit Stili
RESOURCE_TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: #333;
        border-radius: 4px;
        padding: 10px;
        color: white;
        border: 1px solid #555;
    }
"""


