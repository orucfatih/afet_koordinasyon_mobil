"""
Firebase veritabanı ve depolama işlemleri için yardımcı fonksiyonlar.
Bu modül, config.py'den Firebase yapılandırmasını alır ve bağlantıları yönetir.
"""
import os
from pathlib import Path
import firebase_admin
from firebase_admin import db as firebase_db

# Proje kökünü içeren klasörü sys.path'e ekle
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Config modülünden Firebase fonksiyonlarını içe aktar
from config import (
    initialize_firebase, 
    get_database_ref, 
    get_storage_bucket,
    get_firestore_client,
    init_config
)

# Konfigürasyon ayarlarını başlat
init_config()

# Firebase'i başlat
app = initialize_firebase()

# Geriye dönük uyumluluk için doğrudan değişkenler
database = get_database_ref('/')
bucket = get_storage_bucket()
db = firebase_db

def get_firebase_app():
    """
    Firebase uygulama örneğini döndürür.
    """
    return app

# Geriye dönük uyumluluk için eski fonksiyonları koruyoruz
def get_database_reference(path='/'):
    """
    Belirtilen yoldaki veritabanı referansını döndürür.
    """
    return get_database_ref(path)

def get_storage():
    """
    Firebase Storage bucket'ını döndürür.
    """
    return get_storage_bucket()

def get_firestore():
    """
    Firestore veritabanı istemcisini döndürür.
    """
    return get_firestore_client()