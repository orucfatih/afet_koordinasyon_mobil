LIGHT_BACKGROUND = "#f7f3e9"  # Yumuşak krem rengi
LIGHT_TEXT_COLOR = "#4a4a4a"  # Koyu gri
LIGHT_INPUT_BG = "#ffffff"    # Saf beyaz
LIGHT_INPUT_BORDER = "#d1cfc7"  # Hafif gri-krem
LIGHT_BUTTON_BG = "#86c5da"   # Pastel mavi
LIGHT_BUTTON_HOVER_BG = "#6faec8"  # Bir ton daha koyu pastel mavi


# Login page stil tanımları
LOGIN_LIGHT_STYLES = """
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }
    
    #logoContainer {
        background-color: transparent;
    }
    
    #logoLabel {
        color: #4CAF50;
    }
    
    #titleLabel {
        color: #333333;
    }
    
    #inputContainer {
        background-color: transparent;
    }
    
    QLineEdit {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 5px 15px;
        color: #333333;
        font-size: 14px;
    }
    
    QLineEdit:focus {
        border: 2px solid #4CAF50;
    }
    
    QLineEdit::placeholder {
        color: #999999;
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




LIGHT_THEME_STYLE = """
    /* Genel arka plan */
    QWidget {
        background-color: #daf2e0; /* Koyu siyah ton */
        color: #db9ca2; /* Yazı rengi */
    }
"""

# Arama ve filtreleme stilleri
SEARCH_BOX_STYLE = """
    QLineEdit {
        background-color: white;
        color: #4a4a4a;
        padding: 5px;
        border: 1px solid #d1cfc7;
        border-radius: 3px;
    }
"""

COMBO_BOX_STYLE = """
    QComboBox {
        background-color: white;
        color: #4a4a4a;
        padding: 5px;
        border: 1px solid #d1cfc7;
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
        background-color: #f0f0f0;
        color: #4a4a4a;
        padding: 5px;
        border: 1px solid #d1cfc7;
        font-weight: bold;
    }
"""