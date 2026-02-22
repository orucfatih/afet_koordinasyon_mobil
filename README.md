# 🌐 Afet-Link

---

## 📖 Abstract
Afet-Link projesi, afet öncesi, sırası ve sonrasında etkin koordinasyon sağlamak amacıyla geliştirilmiş bir afet yönetim sistemidir. **AFAD** ile iş birliği içerisinde geliştirilen bu platform, **ekip koordinasyonu**, **kaynak yönetimi** ve **rapor takibi** gibi afet öncesi kritik süreçleri kolaylaştırmayı hedeflemektedir.

Afet-Link; sadece olay anına müdahale etmekle kalmaz, afet öncesi hazırlık, risk azaltımı, kaynak yönetimi, ekip koordinasyonu ve simülasyon tabanlı eğitimler gibi kritik önleyici adımları da destekler. Afet anında ise vatandaşların aktif katılımını sağlayarak **enkaz tespiti**, **hasarlı yol bildirimi** ve **toplanma alanları** gibi önemli verilerin hızla paylaşılmasını mümkün kılar. Afet sonrası süreçte **kayıp kişi takibi**, **yardım koordinasyonu** ve **güvenli iletişim ağlarını** destekleyen sistemimiz, kriz anlarında etkin karar alma süreçlerini hızlandırmayı amaçlamaktadır.

---

## 🚀 Özellikler

### 📅 Afet Öncesi
- 📊 **Kaynak Yönetimi**  
- 👥 **Ekip Koordinasyonu**  
- 📁 **Raporlama ve Veri Takibi**  
- 🗺️ **Risk Haritaları ve Tahmin Analizleri**  

### ⚡ Afet Sırası
- 🏚️ **Enkaz Tespiti**  
- 📍 **Toplanma Alanları Haritası**  
- 🛣️ **Hasarlı Yol Bildirimi**  
- 🆘 **Vatandaşlar için "Hayattayım" Butonu**  

### 📦 Afet Sonrası
- 🗃️ **Kayıp Kişi Arama ve Eşleşme Sistemi**  
- 🏕️ **Yardım ve İhtiyaç Koordinasyonu** *(Gıda, İlaç, Barınma)*  
- 🔔 **Gelişmeler ve Acil Duyurular**  
- 🌉 **Gönüllü Katılım Sistemi**  

---

## 💻 Teknolojiler

| Katman          | Kullanılan Teknolojiler                     |
|-----------------|----------------------------------------------|
| 🖥️ **Frontend**   | React Native, PyQt                         |
| 🔙 **Backend**    | Django, FastAPI                             |
| 🗄️ **Veritabanı** | NoSql                                        |
| 🗺️ **Harita API**  | GoogleMaps API                           |
| 🤖 **Makine Öğrenimi** | TensorFlow, OpenCV                    |
| ☁️ **Bulut**      | Google Cloud, Firebase                      |

---

## 📥 Kurulum Rehberi

Projeyi yerel ortamınızda sorunsuz bir şekilde derleyip çalıştırmak için aşağıdaki adımları sırasıyla izleyin.

### 1. Ön Koşullar (Prerequisites)
Projeyi çalıştırmadan önce sisteminizde aşağıdaki yazılımların kurulu olduğundan emin olun:
- **Node.js** (Güncel LTS sürümü)
- **Java Development Kit (JDK) 17 LTS** (React Native için en stabil sürümdür, farklı sürümler derleme hatalarına yol açabilir)
- **Android Studio** (Android SDK ve sanal cihaz kurulumları için gereklidir)

### 2. Depoyu Klonlama ve Paket Kurulumu
Öncelikle projeyi bilgisayarınıza çekin ve gerekli Node.js paketlerini yükleyin:
```bash
git clone [https://github.com/KULLANICI_ADINIZ/afet_koordinasyon_mobil.git](https://github.com/KULLANICI_ADINIZ/afet_koordinasyon_mobil.git)
cd afet_koordinasyon_mobil/AfetLink
npm install

### 3. Çevresel Değişkenler ve Gizli Dosyalar (ÖNEMLİ!)
Güvenlik sebebiyle Github'da (`.gitignore` içinde) bulunmayan **3 kritik dosyayı** manuel olarak oluşturmalısınız. Bu dosyalar olmadan proje derlenmeyecektir:

- **`android/local.properties`:** Android SDK yolunuzu belirtmek içindir. Projeyi Android Studio ile bir kez açtığınızda otomatik oluşur. Manuel oluşturmak isterseniz `android` klasörü içine `local.properties` adında bir dosya açıp aşağıdaki gibi kendi bilgisayarınızdaki SDK yolunu yazın:
  ```properties
  sdk.dir=C\:\\Users\\KullaniciAdiniz\\AppData\\Local\\Android\\Sdk
  ```

- **`android/app/google-services.json`:** Firebase servislerinin çalışması için zorunludur. Firebase Console üzerinden projeye ait `google-services.json` dosyasını indirin ve tam olarak `android/app/` dizininin içine yapıştırın.

- **`.env` Dosyası:** Projenin ana dizininde (`AfetLink` klasörü içinde) bir `.env` dosyası oluşturun ve projeye ait API anahtarlarını (Google Maps, Backend URL vb.) içine ekleyin.

### 4. Windows Kullanıcıları İçin Ekstra Ayar (Uzun Yol Hatası)
Windows üzerinde derleme alırken React Native'in derin C++ dosyaları `Filename longer than 260 characters` hatasına sebep olabilir. Bunu önlemek için PowerShell'i **Yönetici olarak** çalıştırıp şu komutu girin ve bilgisayarınızı yeniden başlatın:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### 5. Uygulamayı Başlatma
Tüm ayarları tamamladıktan sonra Android emülatörünüzü başlatın (veya fiziksel cihazınızı bağlayın) ve uygulamayı derleyin:
```bash
npx react-native run-android
```
*(Not: İlk derleme işlemi bilgisayarınızın performansına bağlı olarak 5-10 dakika arası sürebilir.)*

## 🤝 Katkıda Bulunma
Katkıda bulunmak isterseniz, lütfen bir **fork** oluşturun, değişikliklerinizi yapın ve bir **pull request** gönderin. Her türlü geri bildirime açığız! 🚀  

---

## 📬 İletişim
Herhangi bir sorunuz veya öneriniz varsa bizimle iletişime geçebilirsiniz:  
**✉️ Email:** orucfatiih@gmail.com  
