import sys
from ui import AfetYonetimAdmin
from PyQt5.QtWidgets import QApplication
import os
import platform
from auth.login import LoginPage
from resources_management.kaynak_yonetimi import KaynakYonetimTab
from operation_management.operation_management import OperationManagementTab

# Set QT_QPA_PLATFORM based on OS
if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
elif platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginPage()
    login_window.show()
    sys.exit(app.exec_())