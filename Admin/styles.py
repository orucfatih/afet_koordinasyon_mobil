# Qt bileşenleri için stil tanımlamaları

# Buton stilleri
BUTTON_STYLE = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #1976D2;
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

# Liste widget stilleri
LIST_WIDGET_STYLE = """
    QListWidget {
        background-color: #262a3c;
        border: 1px solid #3a3f55;
        border-radius: 4px;
        color: white;
    }
    QListWidget::item {
        padding: 5px;
        border-bottom: 1px solid #3a3f55;
    }
    QListWidget::item:selected {
        background-color: #3a3f55;
    }
"""

# Tablo widget stilleri
TABLE_WIDGET_STYLE = """
    QTableWidget {
        background-color: #262a3c;
        color: white;
        gridline-color: #3a3f55;
        border: none;
    }
    QTableWidget::item {
        padding: 5px;
    }
    QHeaderView::section {
        background-color: #1a1d2b;
        color: white;
        padding: 5px;
        border: 1px solid #3a3f55;
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
        background-color: #262a3c;
        color: white;
        padding: 5px;
        border: 1px solid #3a3f55;
        border-radius: 4px;
    }
"""

# TextEdit stilleri
TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: #262a3c;
        color: white;
        padding: 5px;
        border: 1px solid #3a3f55;
        border-radius: 4px;
    }
"""

# Dialog içindeki TextEdit stilleri
DIALOG_TEXT_STYLE = """
    QTextEdit {
        background-color: #282829;
        padding: 10px;
    }
"""

# Label stilleri
TITLE_LABEL_STYLE = "font-size: 14px; font-weight: bold; color: white;"

# Dialog bilgi label stilleri
DIALOG_INFO_LABEL_STYLE = "color: white; background-color: #262a3c; padding: 10px;"