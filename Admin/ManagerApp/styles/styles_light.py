LIGHT_THEME_STYLE = """
    QMainWindow {
        background-color: #f5f5f5;
        color: #333333;
    }
    
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
    }
    
    QTabWidget::pane {
        border: none;
        background-color: #ffffff;
    }
    
    QTabBar::tab {
        background-color: #f0f0f0;
        color: #333333;
        padding: 10px 20px;
        border: none;
        min-width: 120px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: 2px solid #0078d4;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #e5e5e5;
    }
    
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #0086e8;
    }
    
    QPushButton:pressed {
        background-color: #005a9e;
    }
    
    QLineEdit {
        background-color: white;
        color: #333333;
        border: 1px solid #cccccc;
        padding: 5px;
        border-radius: 4px;
    }
    
    QLineEdit:focus {
        border: 1px solid #0078d4;
    }
    
    QComboBox {
        background-color: white;
        color: #333333;
        border: 1px solid #cccccc;
        padding: 5px;
        border-radius: 4px;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox::down-arrow {
        image: url(resources/icons/down_arrow_dark.png);
        width: 12px;
        height: 12px;
    }
    
    QComboBox QAbstractItemView {
        background-color: white;
        color: #333333;
        selection-background-color: #0078d4;
        selection-color: white;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #f0f0f0;
        width: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        min-height: 30px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        border: none;
        background-color: #f0f0f0;
        height: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        min-width: 30px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    QMessageBox {
        background-color: white;
        color: #333333;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
    }
"""

TAB_WIDGET_STYLE = """
    QTabWidget::pane {
        border: none;
        background-color: #ffffff;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #f0f0f0;
        color: #333333;
        padding: 12px 24px;
        border: none;
        min-width: 140px;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: 2px solid #0078d4;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #e5e5e5;
    }
""" 