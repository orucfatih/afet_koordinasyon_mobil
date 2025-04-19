"""
Uygulama için konfigürasyon yönetimi
- Google Maps API key
- Firebase yapılandırması
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db, firestore, storage

# Firebase uygulama örnekleri
_firebase_app = None
_firestore_client = None
_storage_bucket = None
_database_ref = None

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
    Firebase kimlik bilgilerini JSON dosyasından çıkarır ve .env dosyasına kaydeder.
    Başarıyla kaydedilirse True, aksi halde False döner.
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
        
        # Private key'i JSON'dan düzgün şekilde alıp, .env formatında \n karakterleriyle kaçış işlemi yapmalıyız
        private_key = creds['private_key']
        # Private key'i herhangi bir değişiklik yapmadan aynen al
                
        # Firebase alanlarını ekle veya güncelle
        firebase_vars = {
            # Europe-West1 bölgesi için doğru URL formatını kullan
            "FIREBASE_DATABASE_URL": f"https://{creds['project_id']}-default-rtdb.europe-west1.firebasedatabase.app",
            "FIREBASE_STORAGE_BUCKET": f"{creds['project_id']}.appspot.com",
            "FIREBASE_ADMIN_TYPE": creds['type'],
            "FIREBASE_ADMIN_PROJECT_ID": creds['project_id'],
            "FIREBASE_ADMIN_PRIVATE_KEY_ID": creds['private_key_id'],
            "FIREBASE_ADMIN_PRIVATE_KEY": private_key,
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
            value_str = str(value)
            # Özel işlem: Private key için özel kaçış karakterleri gerekiyor
            if key == "FIREBASE_ADMIN_PRIVATE_KEY":
                # Satır sonu karakterlerini düzgün şekilde korumak için escape ediyoruz
                value_str = value_str.replace('\n', '\\n')
            
            # Eğer değişken zaten varsa, değerini güncelle
            if f"{key}=" in env_content:
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = f"{key}={value_str}"
                env_content = '\n'.join(lines)
            # Yoksa, yeni değişkeni ekle
            else:
                env_content += f"{key}={value_str}\n"
        
        # .env dosyasına yaz
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # Ayrıca JSON formatında tek bir string olarak FIREBASE_CREDENTIALS değişkenini ekleyelim
        # Bu, doğrudan tüm credentials'a ihtiyaç duyan eski kodlar için geriye dönük uyumluluk sağlar
        firebase_credentials_json = json.dumps(creds)
        
        # Eğer FIREBASE_CREDENTIALS zaten varsa, güncelle
        if "FIREBASE_CREDENTIALS=" in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("FIREBASE_CREDENTIALS="):
                    lines[i] = f"FIREBASE_CREDENTIALS={firebase_credentials_json}"
            env_content = '\n'.join(lines)
        # Yoksa, yeni değişkeni ekle
        else:
            env_content += f"FIREBASE_CREDENTIALS={firebase_credentials_json}\n"
            
        # Güncellenmiş içeriği .env dosyasına yaz
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

def get_firebase_config():
    """
    .env'den Firebase yapılandırma bilgilerini okur ve bir sözlük olarak döndürür
    """
    # Private key'in doğru formatlanması için özel işlem yapılmalı
    private_key = os.getenv('FIREBASE_ADMIN_PRIVATE_KEY', '')
    if private_key:
        # Eğer private_key \\n içeriyorsa, gerçek yeni satır karakterlerine dönüştür
        private_key = private_key.replace('\\n', '\n')
    
    return {
        'type': os.getenv('FIREBASE_ADMIN_TYPE'),
        'project_id': os.getenv('FIREBASE_ADMIN_PROJECT_ID'),
        'private_key_id': os.getenv('FIREBASE_ADMIN_PRIVATE_KEY_ID'),
        'private_key': private_key,
        'client_email': os.getenv('FIREBASE_ADMIN_CLIENT_EMAIL'),
        'client_id': os.getenv('FIREBASE_ADMIN_CLIENT_ID'),
        'auth_uri': os.getenv('FIREBASE_ADMIN_AUTH_URI'),
        'token_uri': os.getenv('FIREBASE_ADMIN_TOKEN_URI'),
        'auth_provider_x509_cert_url': os.getenv('FIREBASE_ADMIN_AUTH_PROVIDER_CERT_URL'),
        'client_x509_cert_url': os.getenv('FIREBASE_ADMIN_CLIENT_CERT_URL'),
        'universe_domain': os.getenv('FIREBASE_ADMIN_UNIVERSE_DOMAIN', 'googleapis.com')
    }

def initialize_firebase():
    """
    Firebase uygulamasını başlatır ve uygulama örneğini döndürür.
    Uygulama zaten başlatılmışsa, mevcut örneği döndürür.
    """
    global _firebase_app
    
    if _firebase_app:
        return _firebase_app
    
    try:
        # Firebase kimlik dosyasının yolunu belirle
        credentials_file = Path(__file__).parent / "afad-proje-firebase-adminsdk-asriu-04ee794487.json"
        
        if not credentials_file.exists():
            # Dosya yoksa, .env dosyasındaki değişkenleri kullanmayı dene
            print(f"Uyarı: Firebase kimlik dosyası bulunamadı: {credentials_file}")
            # Ortam değişkenlerinden değerleri oku
            admin_config = get_firebase_config()
            cred = credentials.Certificate(admin_config)
        else:
            # Dosya varsa, doğrudan dosyadan oku
            cred = credentials.Certificate(str(credentials_file))
        
        # Firebase yapılandırma değerlerini oku
        database_url = os.getenv('FIREBASE_DATABASE_URL')
        storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
        
        # Uygulama zaten başlatılmışsa, mevcut örneği kullan
        if not firebase_admin._apps:
            _firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url,
                'storageBucket': storage_bucket
            })
        else:
            _firebase_app = firebase_admin.get_app()
        
        return _firebase_app
        
    except Exception as e:
        print(f"Firebase başlatılırken hata oluştu: {e}")
        raise

def get_firestore_client():
    """
    Firestore istemcisini döndürür.
    """
    global _firestore_client
    
    if _firestore_client:
        return _firestore_client
    
    # Firebase'i başlat
    initialize_firebase()
    
    # Firestore istemcisini oluştur
    _firestore_client = firestore.client()
    return _firestore_client

def get_storage_bucket():
    """
    Firebase Storage bucket'ını döndürür.
    """
    global _storage_bucket
    
    if _storage_bucket:
        return _storage_bucket
    
    # Firebase'i başlat
    initialize_firebase()
    
    # Storage bucket'ını oluştur
    _storage_bucket = storage.bucket()
    return _storage_bucket

def get_database_ref(path='/'):
    """
    Belirtilen yoldaki veritabanı referansını döndürür.
    """
    global _database_ref
    
    # Firebase'i başlat
    initialize_firebase()
    
    # Veritabanı referansını oluştur
    _database_ref = db.reference(path)
    return _database_ref

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