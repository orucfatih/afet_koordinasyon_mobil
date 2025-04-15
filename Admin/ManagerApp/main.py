"""
bu uygulama şifre işlemleri 
kullanıcı atama 
verilen karar kontrolleri ve onaylama
gibi bir üst seviye işlemleri yapabilir


"""


import sys
import os
import platform
from ui import YonetimPaneli
from PyQt5.QtWidgets import QApplication

if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_QUICK_BACKEND"] = "software"
    os.environ["QT_XCB_GL_INTEGRATION"] = "none"
elif platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"
elif platform.system() == "Darwin":
    os.environ["QT_QPA_PLATFORM"] = "cocoa"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YonetimPaneli()
    window.show()
    sys.exit(app.exec_()) 