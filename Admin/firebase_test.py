"""
Firebase bağlantısını test etmek için basit bir betik.
"""
import sys
import os
import time
import traceback

# Ana klasörü sys.path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("Çalışma dizini:", current_dir)
print(".env dosya yolu:", os.path.join(os.path.dirname(current_dir), '.env'))

try:
    # Database modülünü içe aktar
    print("Database modülünü içe aktarma...")
    from database import get_database_ref, get_storage_bucket, initialize_firebase
    print("Database modülü başarıyla içe aktarıldı.")
except Exception as e:
    print("Database modülü içe aktarılırken hata:", str(e))
    traceback.print_exc()
    sys.exit(1)

def test_firebase_connection():
    """Firebase bağlantısını test eder ve bazı temel işlemleri gerçekleştirir."""
    print("Firebase bağlantısı test ediliyor...")
    
    try:
        # Firebase'i başlat
        app = initialize_firebase()
        print("Firebase uygulaması başarıyla başlatıldı:", app.name)
        
        # Veritabanı referansı alınıyor
        print("Veritabanı referansı alınıyor...")
        ref = get_database_ref('/test')
        print("Veritabanı referansı başarıyla alındı.")
        
        # Örnek veri yazma
        test_data = {
            'test_id': 'test_' + str(int(time.time())),
            'message': 'Firebase bağlantısı başarılı!',
            'timestamp': time.time()
        }
        
        # Veriyi Firebase'e yaz
        print("Veri yazılıyor:", test_data)
        ref.set(test_data)
        print("Veri yazma başarılı!")
        
        # Yazılan veriyi oku
        print("Veri okunuyor...")
        result = ref.get()
        print("Okunan veri:", result)
        
        # Storage bucket'ı test et
        print("Storage bucket'a bağlanılıyor...")
        bucket = get_storage_bucket()
        print("Storage bucket'a bağlantı:", bucket.name)
        
        print("Firebase bağlantı testi başarılı!")
        return True
        
    except Exception as e:
        print("Firebase bağlantı hatası:", str(e))
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_firebase_connection() 