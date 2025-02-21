import face_recognition
import cv2

def preprocess_image(image_path):
    """
    Görüntüyü yükler, boyutunu düzenler ve bulanıklığı azaltır.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Görüntü yüklenemedi: {image_path}")

    image = cv2.resize(image, (500, 500))  # Sabit boyut
    image = cv2.GaussianBlur(image, (3, 3), 0)  # Gürültü azaltma
    return image

def load_and_encode_image(image_path):
    """
    Görüntüyü yükler ve yüz kodlamasını çıkarır.
    """
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image, model="large")  # Daha hassas model

    if len(face_encodings) > 0:
        return face_encodings[0]  # İlk yüz kodlamasını döndür
    else:
        return None  # Yüz bulunamazsa None döndür

def compare_faces(known_encoding, unknown_encoding):
    """
    İki yüz kodlamasını karşılaştırır ve mesafe skorunu döndürür.
    """
    if known_encoding is None or unknown_encoding is None:
        return False, None  # Yüz bulunamazsa eşleşme yok ve skor None
    
    distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]  # Mesafe skoru
    match = distance < 0.6  # Eşik değere göre eşleşme kontrolü

    return match, distance

# Kayıp kişinin fotoğrafı
missing_person_image_path = "polat.jpg"
preprocess_image(missing_person_image_path)  # Görüntüyü işle
missing_person_encoding = load_and_encode_image(missing_person_image_path)

# Bulunan kişinin fotoğrafı
found_person_image_path = "trump1.jpg"
preprocess_image(found_person_image_path)  # Görüntüyü işle
found_person_encoding = load_and_encode_image(found_person_image_path)

# Yüzleri karşılaştır ve skoru al
face_match, face_distance = compare_faces(missing_person_encoding, found_person_encoding)

# Sonucu yazdır
if face_distance is not None:
    print(f"Karşılaştırma Skoru (Mesafe): {face_distance}")  # Skoru yazdır
else:
    print("Yüzlerden biri tespit edilemedi!")

# Eşik değer belirleme
low_suspicion_threshold = 0.55  # Güçlü eşleşme
high_suspicion_threshold = 0.63  # Şüpheli eşleşme

if face_distance is not None:
    if face_distance < low_suspicion_threshold:
        print(" Eşleşme bulundu! Bu kişi kayıp kişi olabilir. (Şüphe düşük)")
        print("kayip kisinin fotografinin adresi",missing_person_image_path)
        print(f"bulan kisinin yukledigi fotografin adresi {found_person_image_path}")
    elif face_distance < high_suspicion_threshold:
        print(" Eşleşme bulundu ancak şüpheli! Kontrol edin, benzer kişiler olabilir.")
        print("kayip kisinin fotografinin adresi",missing_person_image_path)
        print(f"bulan kisinin yukledigi fotografin adresi {found_person_image_path}")
    else:
        print(" Eşleşme bulunamadı.")
        