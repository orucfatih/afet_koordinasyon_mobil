import sys
from ui import AfetYonetimAdmin
from PyQt5.QtWidgets import QApplication
import os
import platform
from auth.login import LoginPage
from resources_management.kaynak_yonetimi import KaynakYonetimTab
from operation_management.operation_management import OperationManagementTab

if platform.system() == "Linux":
    session_type = os.environ.get("XDG_SESSION_TYPE")

    if session_type == "wayland":
        os.environ["QT_QPA_PLATFORM"] = "wayland"
        os.environ["QT_QUICK_BACKEND"] = "software"
        os.environ["QT_XCB_GL_INTEGRATION"] = "none"
    elif session_type == "x11":
        os.environ["QT_QPA_PLATFORM"] = "xcb"

elif platform.system() == "Windows":
    os.environ["QT_QPA_PLATFORM"] = "windows"
elif platform.system() == "Darwin":  # macOS için fakat test edilmedi
    os.environ["QT_QPA_PLATFORM"] = "cocoa"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginPage()
    login_window.show()
    sys.exit(app.exec_())