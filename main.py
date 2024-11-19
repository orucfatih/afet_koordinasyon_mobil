import sys
from ui import AfetYonetimAdmin
from PyQt5.QtWidgets import QApplication
import os

os.environ["QT_QPA_PLATFORM"] = "wayland"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AfetYonetimAdmin()
    window.show()
    sys.exit(app.exec_())