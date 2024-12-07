# Qt bileşenleri için stil tanımlamaları




# Dark tema renkleri ve stil tanımları
DARK_BACKGROUND = "#2c3e50"
DARK_TEXT_COLOR = "#ffffff"
DARK_INPUT_BG = "rgba(255, 255, 255, 0.1)"
DARK_INPUT_FOCUS_BG = "rgba(255, 255, 255, 0.2)"
DARK_BUTTON_BG = "#3498db"
DARK_BUTTON_HOVER_BG = "#2980b9"

# Login page stil tanımları
LOGIN_DARK_STYLES = f"""
    QWidget {{
        background-color: {DARK_BACKGROUND};
        color: {DARK_TEXT_COLOR};
        font-family: Arial, sans-serif;
    }}
    QLineEdit {{
        background-color: {DARK_INPUT_BG};
        border: none;
        color: {DARK_TEXT_COLOR};
        padding: 10px;
        border-radius: 5px;
    }}
    QLineEdit:focus {{
        background-color: {DARK_INPUT_FOCUS_BG};
    }}
    QPushButton {{
        background-color: {DARK_BUTTON_BG};
        color: {DARK_TEXT_COLOR};
        border: none;
        padding: 12px;
        border-radius: 5px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {DARK_BUTTON_HOVER_BG};
    }}
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