import sys
from PyQt5.QtWidgets import QApplication
import os
import platform
from login import LoginPage
from ui import AfetYonetimAdmin

# İşletim sistemine göre QT_QPA_PLATFORM ayarı
if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
elif platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"

def main():
    app = QApplication(sys.argv)
    login_window = LoginPage()
    login_window.show()
    sys.exit(app.exec_())
