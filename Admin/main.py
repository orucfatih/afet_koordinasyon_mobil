import sys
from ui import AfetYonetimAdmin
from PyQt5.QtWidgets import QApplication
import os
import platform

# İşletim sistemine göre QT_QPA_PLATFORM ayarı
if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
elif platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AfetYonetimAdmin()
    window.show()
    sys.exit(app.exec_())