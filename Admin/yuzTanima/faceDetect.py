import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Sadece kritik hataları göster
import numpy as np
import shutil
import gc
import cv2
from deepface import DeepFace
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread
import sys
import json


work_dir=os.getcwd()
# Veri tabanı klasörleri
YETISKIN_VERI_TABANI = os.path.join(work_dir,"Admin","yuzTanima","yetiskinVeriTabani")
COCUK_VERI_TABANI = os.path.join(work_dir,"Admin","yuzTanima","cocukVeriTabani")


# Yetişkin klasörleri
YETISKIN_KAYBOLANLAR_DIR = os.path.join(YETISKIN_VERI_TABANI, "kaybolanlar")
YETISKIN_BULUNANLAR_DIR = os.path.join(YETISKIN_VERI_TABANI, "bulunanlar")
YETISKIN_ESLESENLER_DIR = os.path.join(YETISKIN_VERI_TABANI, "eslesenler")
YETISKIN_ESLESMELER_DOSYASI = os.path.join(YETISKIN_VERI_TABANI, "eslesenler.json")

# Çocuk klasörleri
COCUK_KAYBOLANLAR_DIR = os.path.join(COCUK_VERI_TABANI, "kaybolanCocuklar")
COCUK_BULUNANLAR_DIR = os.path.join(COCUK_VERI_TABANI, "bulunanCocuklar")
COCUK_ESLESENLER_DIR = os.path.join(COCUK_VERI_TABANI, "eslesenCocuklar")
COCUK_ESLESMELER_DOSYASI = os.path.join(COCUK_VERI_TABANI, "eslesenCocuklar.json")

# NumPy dosyaları
YETISKIN_KAYBOLAN_EMBEDDINGS = os.path.join(YETISKIN_VERI_TABANI, "kaybolan_embeddings.npy")
YETISKIN_KAYBOLAN_PATHS = os.path.join(YETISKIN_VERI_TABANI, "kaybolan_paths.npy")
YETISKIN_BULUNAN_EMBEDDINGS = os.path.join(YETISKIN_VERI_TABANI, "bulunan_embeddings.npy")
YETISKIN_BULUNAN_PATHS = os.path.join(YETISKIN_VERI_TABANI, "bulunan_paths.npy")

COCUK_KAYBOLAN_EMBEDDINGS = os.path.join(COCUK_VERI_TABANI, "kaybolan_embeddings.npy")
COCUK_KAYBOLAN_PATHS = os.path.join(COCUK_VERI_TABANI, "kaybolan_paths.npy")
COCUK_BULUNAN_EMBEDDINGS = os.path.join(COCUK_VERI_TABANI, "bulunan_embeddings.npy")
COCUK_BULUNAN_PATHS = os.path.join(COCUK_VERI_TABANI, "bulunan_paths.npy")

# Klasörleri oluştur
for directory in [YETISKIN_KAYBOLANLAR_DIR, YETISKIN_BULUNANLAR_DIR, YETISKIN_ESLESENLER_DIR,
                  COCUK_KAYBOLANLAR_DIR, COCUK_BULUNANLAR_DIR, COCUK_ESLESENLER_DIR]:
    os.makedirs(directory, exist_ok=True)

# Eşleşmeleri dosyaya kaydetme ve yükleme
def eslesmeleri_kaydet(eslesmeler, dosya):
    with open(dosya, "w") as f:
        json.dump(eslesmeler, f)

def eslesmeleri_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r") as f:
            return json.load(f)
    return []

def mevcut_veriyi_yukle(embeddings_dosyasi, yollar_dosyasi):
    if os.path.exists(embeddings_dosyasi) and os.path.exists(yollar_dosyasi):
        return np.load(embeddings_dosyasi), np.load(yollar_dosyasi, allow_pickle=True).tolist()
    return np.array([], dtype=np.float32).reshape(0, 128), []

def embedding_al(resim_yolu):
    try:
        embedding = DeepFace.represent(
            img_path=resim_yolu,
            model_name="Facenet",
            enforce_detection=True
        )[0]["embedding"]
        print(f"✅ Embedding alındı: {os.path.basename(resim_yolu)}")
        return embedding,False
    except Exception as e:
        print(f"⚠️ Yüz algılanamadı: {os.path.basename(resim_yolu)} | {str(e)}")
        img = cv2.imread(resim_yolu, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"❌ Resim okunamadı: {resim_yolu}")
            return None
        if img.shape[-1] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        elif img.shape[-1] == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        h, w = img.shape[:2]
        target_size = 640
        scale = target_size / max(h, w)
        yeni_boyut = (int(w * scale), int(h * scale))
        img = cv2.resize(img, yeni_boyut)
        yeni_resim_yolu = f"temp_{os.path.basename(resim_yolu)}"
        cv2.imwrite(yeni_resim_yolu, img)
        print(f"📏 Yeniden boyutlandırıldı ve kaydedildi: {yeni_resim_yolu}")
        try:
            embedding = DeepFace.represent(
                img_path=yeni_resim_yolu,
                model_name="Facenet",
                detector_backend="mtcnn",
                enforce_detection=True
            )[0]["embedding"]
            print(f"✅ Embedding (2. deneme): {os.path.basename(resim_yolu)}")
            return embedding,True
        except Exception as e2:
            print(f"❌ Başarısız (2. deneme): {os.path.basename(resim_yolu)} | {str(e2)}")
            return None,False
        finally:
            if os.path.exists(yeni_resim_yolu):
                os.remove(yeni_resim_yolu)
                print(f"🧹 Geçici dosya silindi: {yeni_resim_yolu}")

def embeddingleri_cikar(resim_yollari, batch_size=20):
    embeddings = []
    valid_paths = []
    is_second_try_flags = []
    for i in range(0, len(resim_yollari), batch_size):
        batch = resim_yollari[i:i + batch_size]
        for resim_yolu in batch:
            embedding, is_second_try = embedding_al(resim_yolu)
            if embedding is not None:
                embeddings.append(embedding)
                valid_paths.append(resim_yolu)
                is_second_try_flags.append(is_second_try)
        gc.collect()
    embeddings = np.array(embeddings, dtype=np.float32) if embeddings else np.array([], dtype=np.float32).reshape(0, 128)
    return embeddings, valid_paths, is_second_try_flags

def yeni_resimleri_bul(klasor, mevcut_yollar):
    mevcut_set = set(mevcut_yollar)
    return [os.path.join(klasor, img) for img in os.listdir(klasor) if os.path.join(klasor, img) not in mevcut_set and img.lower().endswith(('.png', '.jpg', '.jpeg'))]

def embeddingleri_guncelle(resim_yollari, embeddings_dosyasi, yollar_dosyasi, mevcut_embeddings, mevcut_yollar, batch_size=20):
    if not resim_yollari:
        return mevcut_embeddings, mevcut_yollar, []
    yeni_embeddings, valid_yeni_yollar, is_second_try_flags = embeddingleri_cikar(resim_yollari, batch_size)
    if len(mevcut_embeddings) > 0 and len(yeni_embeddings) > 0:
        mevcut_embeddings = np.vstack([mevcut_embeddings, yeni_embeddings])
    elif len(yeni_embeddings) > 0:
        mevcut_embeddings = yeni_embeddings
    mevcut_yollar.extend(valid_yeni_yollar)
    np.save(embeddings_dosyasi, mevcut_embeddings)
    np.save(yollar_dosyasi, np.array(mevcut_yollar))
    return mevcut_embeddings, mevcut_yollar, is_second_try_flags

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)

def eslestir_ve_tasi(kaybolan_embeddings, kaybolan_yollar, bulunan_embeddings, bulunan_yollar, 
                     eslesmeler_dosyasi, eslesenler_dir,esik ,batch_size=20, is_second_try_flags=None,
                     embeddings_kaybolan=None, paths_kaybolan=None, embeddings_bulunan=None, paths_bulunan=None):
    eslesmeler = eslesmeleri_yukle(eslesmeler_dosyasi)
    matched_kaybolan = set([e[0] for e in eslesmeler])
    
    if len(kaybolan_embeddings) == 0 or len(bulunan_embeddings) == 0:
        print("Eşleştirme yapılamadı: Kaybolan veya bulunan embedding'ler boş.")
        return
    
    kaybolan_yollar = list(dict.fromkeys(kaybolan_yollar))
    bulunan_yollar = list(dict.fromkeys(bulunan_yollar))
    kaybolan_embeddings = kaybolan_embeddings[:len(kaybolan_yollar)]
    bulunan_embeddings = bulunan_embeddings[:len(bulunan_yollar)]
    
    if is_second_try_flags is None:
        is_second_try_flags = [False] * len(kaybolan_embeddings)

    for i in range(0, len(kaybolan_embeddings), batch_size):
        batch_embeddings = kaybolan_embeddings[i:i + batch_size]
        batch_yollar = kaybolan_yollar[i:i + batch_size]
        batch_flags = is_second_try_flags[i:i + batch_size]
        
        j = 0
        while j < len(batch_embeddings):
            kaybolan_embedding = batch_embeddings[j]
            kaybolan_resim = batch_yollar[j]
            if kaybolan_resim in matched_kaybolan:
                j += 1
                continue
            
            # Eşik değerini esik parametresine göre dinamik ayarla
            if batch_flags[j]:  # İkinci deneme
                current_esik = 0.7 if esik == 0.75 else 0.4  # Çocuklar için 0.7, yetişkinler için 0.4
            else:  # İlk deneme
                current_esik = esik  # Yetişkinler 0.45, çocuklar 0.75
            
            max_similarity = -1
            best_match_idx = -1
            
            for k, bulunan_embedding in enumerate(bulunan_embeddings):
                similarity = cosine_similarity(kaybolan_embedding, bulunan_embedding)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_idx = k
            
            if max_similarity > current_esik:
                bulunan_resim = bulunan_yollar[best_match_idx]
                
                # Eşleşen resimleri eslesenler klasörüne kopyala (hem kaybolan hem bulunan)
                kaybolan_dosya_adi = os.path.basename(kaybolan_resim)
                bulunan_dosya_adi = os.path.basename(bulunan_resim)
                kaybolan_hedef = os.path.join(eslesenler_dir, f"k{kaybolan_dosya_adi}")
                bulunan_hedef = os.path.join(eslesenler_dir, f"b{bulunan_dosya_adi}")
                
                shutil.copy2(kaybolan_resim, kaybolan_hedef)
                shutil.copy2(bulunan_resim, bulunan_hedef)
                
                # JSON için eslesenler klasöründeki yollarla eşleşme kaydı
                eslesme = (kaybolan_hedef, bulunan_hedef, float(max_similarity))
                if eslesme not in eslesmeler:
                    eslesmeler.append(eslesme)
                    matched_kaybolan.add(kaybolan_resim)
                    print(f"Eşleşme bulundu: {os.path.basename(kaybolan_resim)} -> {os.path.basename(bulunan_resim)}, Skor: {max_similarity:.4f}, Eşik: {current_esik}")
                    print(f"📂 Kaybolan kopyalandı: {kaybolan_hedef}")
                    print(f"📂 Bulunan kopyalandı: {bulunan_hedef}")
                
                # Orijinal dosyaları sil
                try:
                    os.remove(kaybolan_resim)
                    print(f"🗑️ Kaybolan silindi: {os.path.basename(kaybolan_resim)}")
                except OSError as e:
                    print(f"⚠️ Kaybolan silinemedi: {os.path.basename(kaybolan_resim)} | {str(e)}")
                
                try:
                    os.remove(bulunan_resim)
                    print(f"🗑️ Bulunan silindi: {os.path.basename(bulunan_resim)}")
                except OSError as e:
                    print(f"⚠️ Bulunan silinemedi: {os.path.basename(bulunan_resim)} | {str(e)}")
                
                # Embedding ve yolları sil
                kaybolan_idx = kaybolan_yollar.index(kaybolan_resim)
                bulunan_idx = bulunan_yollar.index(bulunan_resim)
                
                kaybolan_embeddings = np.delete(kaybolan_embeddings, kaybolan_idx, axis=0)
                kaybolan_yollar.pop(kaybolan_idx)
                batch_embeddings = np.delete(batch_embeddings, j, axis=0)
                batch_yollar.pop(j)
                batch_flags.pop(j)
                
                bulunan_embeddings = np.delete(bulunan_embeddings, bulunan_idx, axis=0)
                bulunan_yollar.pop(bulunan_idx)
                
                # SSD'deki embedding ve yol dosyalarını güncelle
                if embeddings_kaybolan and paths_kaybolan:
                    np.save(embeddings_kaybolan, kaybolan_embeddings)
                    np.save(paths_kaybolan, np.array(kaybolan_yollar))
                    print(f"📥 Kaybolan embedding'ler güncellendi: {len(kaybolan_yollar)} kaldı")
                if embeddings_bulunan and paths_bulunan:
                    np.save(embeddings_bulunan, bulunan_embeddings)
                    np.save(paths_bulunan, np.array(bulunan_yollar))
                    print(f"📥 Bulunan embedding'ler güncellendi: {len(bulunan_yollar)} kaldı")
            else:
                print(f"Eşleşme bulunamadı: {os.path.basename(kaybolan_resim)}, En yüksek skor: {max_similarity:.4f}, Eşik: {current_esik}")
                j += 1
        
        gc.collect()
    
    eslesmeleri_kaydet(eslesmeler, eslesmeler_dosyasi)

def yeni_veriyi_isle(kaybolan_dir, bulunan_dir, eslesenler_dir, embeddings_kaybolan, paths_kaybolan, 
                     embeddings_bulunan, paths_bulunan, eslesmeler_dosyasi, esik):
    kaybolan_embeddings, kaybolan_yollar = mevcut_veriyi_yukle(embeddings_kaybolan, paths_kaybolan)
    bulunan_embeddings, bulunan_yollar = mevcut_veriyi_yukle(embeddings_bulunan, paths_bulunan)

    yeni_kaybolanlar = yeni_resimleri_bul(kaybolan_dir, kaybolan_yollar)
    is_second_try_flags = []
    if len(kaybolan_embeddings) > 0:
        is_second_try_flags = [False] * len(kaybolan_embeddings)
    if yeni_kaybolanlar:
        print(f"Yeni kaybolanlar bulundu: {len(yeni_kaybolanlar)}")
        yeni_embeddings, yeni_yollar, yeni_flags = embeddingleri_guncelle(
            yeni_kaybolanlar, embeddings_kaybolan, paths_kaybolan, kaybolan_embeddings, kaybolan_yollar
        )
        kaybolan_embeddings, kaybolan_yollar = yeni_embeddings, yeni_yollar
        is_second_try_flags.extend(yeni_flags)
    
    yeni_bulunanlar = yeni_resimleri_bul(bulunan_dir, bulunan_yollar)
    if yeni_bulunanlar:
        print(f"Yeni bulunanlar bulundu: {len(yeni_bulunanlar)}")
        bulunan_embeddings, bulunan_yollar, _ = embeddingleri_guncelle(
            yeni_bulunanlar, embeddings_bulunan, paths_bulunan, bulunan_embeddings, bulunan_yollar
        )
    if len(kaybolan_embeddings) > 0 and len(bulunan_embeddings) > 0:
        eslestir_ve_tasi(kaybolan_embeddings, kaybolan_yollar, bulunan_embeddings, bulunan_yollar, 
                         eslesmeler_dosyasi, eslesenler_dir, esik, is_second_try_flags=is_second_try_flags,
                         embeddings_kaybolan=embeddings_kaybolan, paths_kaybolan=paths_kaybolan,
                         embeddings_bulunan=embeddings_bulunan, paths_bulunan=paths_bulunan)
    else:
        print("Eşleştirme yapılmadı: Yeterli veri yok.")

class IslemThread(QThread):
    def __init__(self, tip):
        super().__init__()
        self.tip = tip

    def run(self):
        if self.tip == "yetiskin":
            yeni_veriyi_isle(YETISKIN_KAYBOLANLAR_DIR, YETISKIN_BULUNANLAR_DIR, YETISKIN_ESLESENLER_DIR,
                             YETISKIN_KAYBOLAN_EMBEDDINGS, YETISKIN_KAYBOLAN_PATHS, YETISKIN_BULUNAN_EMBEDDINGS, YETISKIN_BULUNAN_PATHS,
                             YETISKIN_ESLESMELER_DOSYASI, esik=0.45)
        elif self.tip == "cocuk":
            yeni_veriyi_isle(COCUK_KAYBOLANLAR_DIR, COCUK_BULUNANLAR_DIR, COCUK_ESLESENLER_DIR,
                             COCUK_KAYBOLAN_EMBEDDINGS, COCUK_KAYBOLAN_PATHS, COCUK_BULUNAN_EMBEDDINGS, COCUK_BULUNAN_PATHS,
                             COCUK_ESLESMELER_DOSYASI, esik=0.75)

class EslesmePenceresi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eşleşen Kişiler")
        self.setGeometry(100, 100, 800, 600)

        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        ana_layout = QVBoxLayout()
        ana_widget.setLayout(ana_layout)

        yetiskin_layout = QHBoxLayout()
        self.yetiskin_islem_buton = QPushButton("Yetişkinler için İşlem Yap")
        self.yetiskin_kaybolan_ekle = QPushButton("Yetişkin Kaybolanlara Ekle")
        self.yetiskin_bulunan_ekle = QPushButton("Yetişkin Bulunanlara Ekle")
        yetiskin_layout.addWidget(self.yetiskin_islem_buton)
        yetiskin_layout.addWidget(self.yetiskin_kaybolan_ekle)
        yetiskin_layout.addWidget(self.yetiskin_bulunan_ekle)
        ana_layout.addLayout(yetiskin_layout)

        cocuk_layout = QHBoxLayout()
        self.cocuk_islem_buton = QPushButton("Çocuklar için İşlem Yap")
        self.cocuk_kaybolan_ekle = QPushButton("Çocuk Kaybolanlara Ekle")
        self.cocuk_bulunan_ekle = QPushButton("Çocuk Bulunanlara Ekle")
        cocuk_layout.addWidget(self.cocuk_islem_buton)
        cocuk_layout.addWidget(self.cocuk_kaybolan_ekle)
        cocuk_layout.addWidget(self.cocuk_bulunan_ekle)
        ana_layout.addLayout(cocuk_layout)

        self.liste = QListWidget()
        ana_layout.addWidget(QLabel("Eşleşmeler:"))
        ana_layout.addWidget(self.liste)

        self.statusBar().showMessage("Program başlatılıyor...")

        self.yetiskin_islem_buton.clicked.connect(lambda: self.baslat("yetiskin"))
        self.cocuk_islem_buton.clicked.connect(lambda: self.baslat("cocuk"))
        self.yetiskin_kaybolan_ekle.clicked.connect(lambda: self.resim_ekle(YETISKIN_KAYBOLANLAR_DIR))
        self.yetiskin_bulunan_ekle.clicked.connect(lambda: self.resim_ekle(YETISKIN_BULUNANLAR_DIR))
        self.cocuk_kaybolan_ekle.clicked.connect(lambda: self.resim_ekle(COCUK_KAYBOLANLAR_DIR))
        self.cocuk_bulunan_ekle.clicked.connect(lambda: self.resim_ekle(COCUK_BULUNANLAR_DIR))

    def baslat(self, tip):
        self.thread = IslemThread(tip)
        self.thread.finished.connect(self.islem_tamamlandi)
        self.thread.start()

    def resim_ekle(self, hedef_klasor):
        dosyalar, _ = QFileDialog.getOpenFileNames(self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if dosyalar:
            for dosya in dosyalar:
                hedef_yol = os.path.join(hedef_klasor, os.path.basename(dosya))
                shutil.copy2(dosya, hedef_yol)
            self.statusBar().showMessage(f"{len(dosyalar)} resim eklendi.")

    def islem_tamamlandi(self):
        self.statusBar().showMessage("Eşleşmeler gösteriliyor...")
        self.eslesmeleri_goster()

    def eslesmeleri_goster(self):
        self.liste.clear()
        if "cocuk" in self.thread.tip:
            eslesmeler = eslesmeleri_yukle(COCUK_ESLESMELER_DOSYASI)
        else:
            eslesmeler = eslesmeleri_yukle(YETISKIN_ESLESMELER_DOSYASI)
        
        if not eslesmeler:
            self.liste.addItem("Hiç eşleşme bulunamadı.")
        else:
            for kaybolan, bulunan, mesafe in eslesmeler:
                eslesme_widget = QWidget()
                eslesme_layout = QHBoxLayout()

                kaybolan_pixmap = QPixmap(kaybolan).scaled(150, 150, Qt.KeepAspectRatio)
                kaybolan_label = QLabel()
                kaybolan_label.setPixmap(kaybolan_pixmap)
                eslesme_layout.addWidget(kaybolan_label)

                bulunan_pixmap = QPixmap(bulunan).scaled(150, 150, Qt.KeepAspectRatio)
                bulunan_label = QLabel()
                bulunan_label.setPixmap(bulunan_pixmap)
                eslesme_layout.addWidget(bulunan_label)

                bilgi_label = QLabel(f"Kaybolan: {os.path.basename(kaybolan)}\nBulunan: {os.path.basename(bulunan)}\nBenzerlik: {mesafe:.4f}")
                eslesme_layout.addWidget(bilgi_label)

                eslesme_widget.setLayout(eslesme_layout)
                item = QListWidgetItem(self.liste)
                item.setSizeHint(eslesme_widget.sizeHint())
                self.liste.setItemWidget(item, eslesme_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = EslesmePenceresi()
    pencere.show()
    sys.exit(app.exec_())