from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget
from message.message_ui import MessageDialog

class MessageManager:
    """Mesajlaşma yönetimi için ana sınıf"""
    def __init__(self, parent=None):
        self.parent = parent
        
    def show_message_dialog(self):
        """Mesajlaşma penceresini gösterir"""
        dialog = MessageDialog(self.parent)
        dialog.exec_() 