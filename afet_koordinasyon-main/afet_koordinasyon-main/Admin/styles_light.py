LIGHT_BACKGROUND = "#f7f3e9"  # Yumuşak krem rengi
LIGHT_TEXT_COLOR = "#4a4a4a"  # Koyu gri
LIGHT_INPUT_BG = "#ffffff"    # Saf beyaz
LIGHT_INPUT_BORDER = "#d1cfc7"  # Hafif gri-krem
LIGHT_BUTTON_BG = "#86c5da"   # Pastel mavi
LIGHT_BUTTON_HOVER_BG = "#6faec8"  # Bir ton daha koyu pastel mavi


# Login page stil tanımları
LOGIN_LIGHT_STYLES = f"""
    QWidget {{
        background-color: {LIGHT_BACKGROUND};
        color: {LIGHT_TEXT_COLOR};
        font-family: Arial, sans-serif;
    }}
    QLineEdit {{
        background-color: {LIGHT_INPUT_BG};
        color: {LIGHT_TEXT_COLOR};
        border: 1px solid {LIGHT_INPUT_BORDER};
        padding: 10px;
        border-radius: 5px;
    }}
    QLabel {{
        color: {LIGHT_TEXT_COLOR};
    }}
"""




LIGHT_THEME_STYLE = """
    /* Genel arka plan */
    QWidget {
        background-color: #daf2e0; /* Koyu siyah ton */
        color: #db9ca2; /* Yazı rengi */
    }
"""