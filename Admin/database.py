import firebase_admin
from firebase_admin import credentials, db, storage
import os

import json
from dotenv import load_dotenv
from pathlib import Path

# .env dosyasını yükle
# .env dosyasını projenin kök dizininde ara
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = root_dir / '.env'

from config import init_config, get_env_file_path
from dotenv import load_dotenv

# Konfigurasyon ayarlarını başlat
init_config()

# .env dosyasını yükle
dotenv_path = get_env_file_path()

load_dotenv(dotenv_path)

def initialize_firebase():
    """Firebase bağlantısını başlatır."""
    
    # .env dosyasından değerleri oku
    database_url = os.getenv('FIREBASE_DATABASE_URL')
    storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
    
    # Admin SDK yapılandırma bilgilerini .env'den al
    admin_config = {
        'type': os.getenv('FIREBASE_ADMIN_TYPE'),
        'project_id': os.getenv('FIREBASE_ADMIN_PROJECT_ID'),
        'private_key_id': os.getenv('FIREBASE_ADMIN_PRIVATE_KEY_ID'),
        'private_key': os.getenv('FIREBASE_ADMIN_PRIVATE_KEY').replace('\\n', '\n'),
        'client_email': os.getenv('FIREBASE_ADMIN_CLIENT_EMAIL'),
        'client_id': os.getenv('FIREBASE_ADMIN_CLIENT_ID'),
        'auth_uri': os.getenv('FIREBASE_ADMIN_AUTH_URI'),
        'token_uri': os.getenv('FIREBASE_ADMIN_TOKEN_URI'),
        'auth_provider_x509_cert_url': os.getenv('FIREBASE_ADMIN_AUTH_PROVIDER_CERT_URL'),
        'client_x509_cert_url': os.getenv('FIREBASE_ADMIN_CLIENT_CERT_URL'),
        'universe_domain': os.getenv('FIREBASE_ADMIN_UNIVERSE_DOMAIN', 'googleapis.com')
    }
    
    # Firebase Admin SDK kimlik bilgilerini oluştur
    cred = credentials.Certificate(admin_config)
    
    # Uygulama zaten başlatılmışsa, yeni bir uygulama oluşturma
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url,
            'storageBucket': storage_bucket
        })
    
    return firebase_admin.get_app()

# Firebase bağlantısını başlat
app = initialize_firebase()

# Veritabanı ve depolama referansları
database = db.reference('/')
bucket = storage.bucket()

def get_database_ref(path=''):
    """Belirtilen yoldaki veritabanı referansını döndürür."""
    return db.reference(path)

def get_storage_bucket():
    """Firebase Storage bucket referansını döndürür."""
    return bucket