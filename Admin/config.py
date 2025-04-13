"""
Uygulama için konfigürasyon yönetimi
- Google Maps API key
- Firebase yapılandırması
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

def get_env_file_path():
    """
    .env dosyasının yolunu döndürür.
    Dosya yoksa oluşturur.
    """
    # Proje kök dizinini bul
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    
    # .env dosyası yoksa oluştur
    if not env_path.exists():
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Configuration file\n\n# Google Maps API Key\nGOOGLE_MAPS_API_KEY=your_api_key_here\n")
    
    return env_path

def extract_firebase_credentials():
    """
    Firebase kimlik bilgilerini JSON dosyasından çıkarır ve .env dosyasına kaydeder
    """
    # Firebase kimlik dosyasının yolunu belirle
    credentials_file = Path(__file__).parent / "afad-proje-firebase-adminsdk-asriu-04ee794487.json"
    
    if not credentials_file.exists():
        print(f"Uyarı: Firebase kimlik dosyası bulunamadı: {credentials_file}")
        return False
    
    try:
        # JSON dosyasını oku
        with open(credentials_file, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        
        # .env dosyasının yolunu al
        env_path = get_env_file_path()
        
        # Mevcut .env içeriğini oku
        env_content = ""
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()
        
        # Firebase alanlarını ekle veya güncelle
        firebase_vars = {
            # Europe-West1 bölgesi için doğru URL formatını kullan
            "FIREBASE_DATABASE_URL": f"https://{creds['project_id']}-default-rtdb.europe-west1.firebasedatabase.app",
            "FIREBASE_STORAGE_BUCKET": f"{creds['project_id']}.appspot.com",
            "FIREBASE_ADMIN_TYPE": creds['type'],
            "FIREBASE_ADMIN_PROJECT_ID": creds['project_id'],
            "FIREBASE_ADMIN_PRIVATE_KEY_ID": creds['private_key_id'],
            "FIREBASE_ADMIN_PRIVATE_KEY": creds['private_key'].replace('\n', '\\n'),
            "FIREBASE_ADMIN_CLIENT_EMAIL": creds['client_email'],
            "FIREBASE_ADMIN_CLIENT_ID": creds['client_id'],
            "FIREBASE_ADMIN_AUTH_URI": creds['auth_uri'],
            "FIREBASE_ADMIN_TOKEN_URI": creds['token_uri'],
            "FIREBASE_ADMIN_AUTH_PROVIDER_CERT_URL": creds['auth_provider_x509_cert_url'],
            "FIREBASE_ADMIN_CLIENT_CERT_URL": creds['client_x509_cert_url'],
            "FIREBASE_ADMIN_UNIVERSE_DOMAIN": creds['universe_domain']
        }
        
        # Eğer .env dosyası yoksa veya içeriği boşsa, yeni bir dosya oluştur
        if not env_content:
            env_content = "# Configuration file\n\n# Google Maps API Key\nGOOGLE_MAPS_API_KEY=your_api_key_here\n\n# Firebase Configuration\n"
        
        # Her bir Firebase değişkenini .env içeriğine ekle
        for key, value in firebase_vars.items():
            # Eğer değişken zaten varsa, değerini güncelle
            if f"{key}=" in env_content:
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = f"{key}={value}"
                env_content = '\n'.join(lines)
            # Yoksa, yeni değişkeni ekle
            else:
                env_content += f"{key}={value}\n"
        
        # .env dosyasına yaz
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        return True
    
    except Exception as e:
        print(f"Firebase kimlik bilgilerini çıkarırken hata oluştu: {e}")
        return False

def load_google_maps_api_key():
    """
    Google Maps API anahtarını yükler ve döndürür.
    API anahtarı .env dosyasında saklanır.
    
    API anahtarını almak için:
    1. https://console.cloud.google.com/ adresine gidin
    2. Yeni bir proje oluşturun veya mevcut projeyi seçin
    3. Maps JavaScript API'yi etkinleştirin
    4. Credentials (Kimlik Bilgileri) bölümünden API anahtarı oluşturun
    5. Oluşturulan API anahtarını .env dosyasındaki GOOGLE_MAPS_API_KEY= satırına yapıştırın
    """
    env_path = get_env_file_path()
    load_dotenv(env_path)
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Uyarı: Google Maps API anahtarı bulunamadı veya varsayılan değerde!")
        print(f"Lütfen {env_path} dosyasına geçerli bir API anahtarı ekleyin.")
    
    return api_key

def init_config():
    """
    Konfigürasyon ayarlarını başlatır
    """
    # Firebase kimlik bilgilerini çıkar ve .env dosyasına kaydet
    extract_firebase_credentials()
    
    # .env dosyasını yükle
    env_path = get_env_file_path()
    load_dotenv(env_path)

def get_config():
    """
    Tüm konfigürasyon ayarlarını döndürür
    """
    # Konfigürasyon ayarlarını başlat
    init_config()
    
    return {
        "google_maps_api_key": load_google_maps_api_key(),
        "map_default_center": {"lat": 39.925533, "lng": 32.866287},  # Ankara
        "map_default_zoom": 6,
        "debug_mode": os.getenv("DEBUG", "False").lower() == "true"
    } 