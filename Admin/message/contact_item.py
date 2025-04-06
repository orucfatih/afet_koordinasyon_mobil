from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon, QColor
import os

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'icons', icon_name)

class ContactItem(QListWidgetItem):
    def __init__(self, contact_data):
        super().__init__()
        self.contact_data = contact_data
        self.id = contact_data.get('id')
        
        # Görünüm ayarları
        display_text = f"{contact_data['name']}\n"
        if 'title' in contact_data:
            display_text += f"{contact_data['title']} - "
        elif 'type' in contact_data:
            display_text += f"{contact_data['type']} - "
        elif 'location' in contact_data:
            display_text += f"{contact_data['location']} - "
        display_text += contact_data['status']
        
        self.setText(display_text)
        self.setIcon(QIcon(get_icon_path('user.png')))
        
        # Durum rengini ayarla
        if contact_data['status'] == 'Çevrimiçi' or contact_data['status'] == 'Aktif':
            self.setForeground(QColor('#4CAF50'))
        elif contact_data['status'] == 'Meşgul':
            self.setForeground(QColor('#FFA500'))
        else:
            self.setForeground(QColor('#f44336')) 