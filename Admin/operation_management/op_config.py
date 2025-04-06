"""
Operation Management modülü için konfigürasyon yönetimi
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def get_env_file_path():
    """
    .env dosyasının yolunu döndürür.
    Dosya yoksa oluşturur.
    """
    # Proje kök dizinini bul (Afet-Link klasörü)
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    
    # .env dosyası yoksa oluştur
    if not env_path.exists():
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Google Maps API Key\nAPI_KEY=your_api_key_here\n")
    
    return env_path

def load_api_key():
    """
    Google Maps API anahtarını yükler ve döndürür.
    API anahtarı .env dosyasında saklanır.
    
    API anahtarını almak için:
    1. https://console.cloud.google.com/ adresine gidin
    2. Yeni bir proje oluşturun veya mevcut projeyi seçin
    3. Maps JavaScript API'yi etkinleştirin
    4. Credentials (Kimlik Bilgileri) bölümünden API anahtarı oluşturun
    5. Oluşturulan API anahtarını .env dosyasındaki API_KEY= satırına yapıştırın
    """
    env_path = get_env_file_path()
    load_dotenv(env_path)
    
    api_key = os.getenv("API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Uyarı: API anahtarı bulunamadı veya varsayılan değerde!")
        print(f"Lütfen {env_path} dosyasına geçerli bir API anahtarı ekleyin.")
    
    return api_key

def get_config():
    """
    Tüm konfigürasyon ayarlarını döndürür
    """
    return {
        "api_key": load_api_key(),
        "map_default_center": {"lat": 39.925533, "lng": 32.866287},  # Ankara
        "map_default_zoom": 6,
        "debug_mode": os.getenv("DEBUG", "False").lower() == "true"
    } 