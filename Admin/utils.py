import os

def get_icon_path(icon_name):
    """İkon dosyasının tam yolunu döndürür.
    
    Args:
        icon_name (str): İkon dosyasının adı (örn: 'message.png')
        
    Returns:
        str: İkon dosyasının tam yolu
    """
    # Admin klasörünün yolunu al
    admin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(admin_dir, 'Admin', 'icons', icon_name)

def get_project_root():
    """Proje kök dizininin tam yolunu döndürür.
    
    Returns:
        str: Proje kök dizininin tam yolu
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_admin_dir():
    """Admin dizininin tam yolunu döndürür.
    
    Returns:
        str: Admin dizininin tam yolu
    """
    return os.path.join(get_project_root(), 'Admin') 