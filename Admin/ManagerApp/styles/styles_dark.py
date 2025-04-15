DARK_THEME_STYLE = """
    QMainWindow {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    QTabWidget::pane {
        border: none;
        background-color: #2d2d2d;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 10px 20px;
        border: none;
        min-width: 120px;
    }
    
    QTabBar::tab:selected {
        background-color: #3d3d3d;
        border-bottom: 2px solid #007acc;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #353535;
    }
    
    QPushButton {
        background-color: #007acc;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #0098ff;
    }
    
    QPushButton:pressed {
        background-color: #005c99;
    }
    
    QLineEdit {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #3d3d3d;
        padding: 5px;
        border-radius: 4px;
    }
    
    QLineEdit:focus {
        border: 1px solid #007acc;
    }
    
    QComboBox {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #3d3d3d;
        padding: 5px;
        border-radius: 4px;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox::down-arrow {
        image: url(resources/icons/down_arrow_white.png);
        width: 12px;
        height: 12px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: white;
        selection-background-color: #007acc;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #2d2d2d;
        width: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4d4d4d;
        min-height: 30px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #5d5d5d;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        border: none;
        background-color: #2d2d2d;
        height: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #4d4d4d;
        min-width: 30px;
        border-radius: 5px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #5d5d5d;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    QMessageBox {
        background-color: #2d2d2d;
        color: white;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
    }
"""

TAB_WIDGET_STYLE = """
    QTabWidget::pane {
        border: none;
        background-color: #2d2d2d;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 12px 24px;
        border: none;
        min-width: 140px;
        font-size: 13px;
    }
    
    QTabBar::tab:selected {
        background-color: #3d3d3d;
        border-bottom: 2px solid #007acc;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #353535;
    }
""" 