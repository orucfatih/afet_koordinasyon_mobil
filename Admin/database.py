import firebase_admin
from firebase_admin import credentials, db, storage
import os

# Dosya yolunu düzelt
current_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(current_dir, "afad-proje-firebase-adminsdk-asriu-04ee794487.json")

# Firebase bağlantısını başlat
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://afad-proje-default-rtdb.europe-west1.firebasedatabase.app/',
    'storageBucket': 'afad-proje.appspot.com'  # Storage bucket adını ekleyin
})
