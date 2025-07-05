import NetInfo from '@react-native-community/netinfo';
import { getUnsentPhotos, markPhotoAsSent, initDB, deletePhoto } from './sqliteHelper';
import auth from '@react-native-firebase/auth';
import storage from '@react-native-firebase/storage';
import firestore from '@react-native-firebase/firestore';
import { Platform, Alert } from 'react-native';

// Singleton pattern - tek bir listener instance'ı
let syncListenerInstance = null;
let isSyncing = false;
let intervalId = null;
let unsubscribe = null;

// Severity seviyesini kişi sayısına göre belirle
const getSeverityLevel = (personCount) => {
  if (!personCount) return "bilinmiyor";
  
  switch (personCount) {
    case '1 kişi':
    case '2 kişi':
    case '3 kişi':
    case '4 kişi':
    case '5 kişi':
      return "normal";
    case '6-10 kişi':
    case '11-20 kişi':
      return "yüksek";
    case '21-50 kişi':
    case '50+ kişi':
      return "kritik";
    case 'Bilinmiyor':
    default:
      return "bilinmiyor";
  }
};

export const startSyncListener = () => {
  // Eğer zaten çalışıyorsa, yeni instance oluşturma
  if (syncListenerInstance) {
    console.log('Senkronizasyon listener zaten çalışıyor');
    return syncListenerInstance;
  }

  console.log('Senkronizasyon listener başlatılıyor...');

  // Veritabanını başlat
  initDB().catch(error => {
    console.error('Senkronizasyon veritabanı başlatma hatası:', error);
  });
  
  // Önceki listener'ları temizle
  if (intervalId) {
    clearInterval(intervalId);
  }
  if (unsubscribe) {
    unsubscribe();
  }
  
  // Her 5 dakikada bir senkronizasyonu kontrol et
  intervalId = setInterval(() => {
    NetInfo.fetch().then(state => {
      if (state.isConnected && auth().currentUser && !isSyncing) {
        console.log('Interval tetiklendi - senkronizasyon başlatılıyor');
        syncPhotos();
      }
    });
  }, 300000); // 5 dakika

  // İnternet bağlantısı değişikliklerini dinle
  unsubscribe = NetInfo.addEventListener(state => {
    if (state.isConnected && auth().currentUser && !isSyncing) {
      console.log('İnternet bağlantısı değişikliği - senkronizasyon başlatılıyor');
      syncPhotos();
    }
  });

  // Singleton instance'ı oluştur
  syncListenerInstance = {
    stop: () => {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
      if (unsubscribe) {
        unsubscribe();
        unsubscribe = null;
      }
      syncListenerInstance = null;
      console.log('Senkronizasyon listener durduruldu');
    }
  };

  return syncListenerInstance;
};

const getCurrentLocation = () => {
  return new Promise((resolve) => {
    if (navigator && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => {
          console.log('Konum hatası:', error);
          resolve({ latitude: null, longitude: null });
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 10000 }
      );
    } else {
      resolve({ latitude: null, longitude: null });
    }
  });
};

const syncPhotos = async () => {
  // Senkronizasyon kilidi kontrolü
  if (isSyncing) {
    console.log('Senkronizasyon zaten çalışıyor, bekleniyor...');
    return;
  }

  // Kullanıcı giriş yapmamışsa senkronizasyonu durdur
  if (!auth().currentUser) {
    console.log('Kullanıcı giriş yapmamış, senkronizasyon yapılamıyor');
    return;
  }

  console.log('Senkronizasyon başlatılıyor...');
  isSyncing = true;

  try {
    const photos = await getUnsentPhotos();
    console.log('Senkronize edilecek fotoğraf sayısı:', photos.length);

    if (photos.length === 0) {
      console.log('Senkronize edilecek fotoğraf yok');
      return; // Senkronize edilecek fotoğraf yoksa çık
    }

    let successCount = 0;
    let errorCount = 0;

    for (const photo of photos) {
      try {
        console.log(`Fotoğraf yükleniyor: ID ${photo.id}`);
        
        // Benzersiz dosya adı oluştur (timestamp + random + photo.id)
        const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}_${photo.id}`;
        const fileName = `${auth().currentUser.uid}_${uniqueId}.jpg`;
        const storageRef = storage().ref(`afet-bildirimleri/${auth().currentUser.uid}/${fileName}`);
        
        const response = await fetch(photo.uri);
        const blob = await response.blob();
        
        await storageRef.put(blob);
        const downloadURL = await storageRef.getDownloadURL();

        // Firestore'a metadata kaydet
        await firestore()
          .collection('afet-bildirimleri')
          .doc(auth().currentUser.uid)
          .collection('images')
          .doc(fileName)
          .set({
            imageUrl: downloadURL,
            timestamp: photo.timestamp,
            fileName: fileName,
            status: "yeni",
            location: {
              latitude: photo.latitude,
              longitude: photo.longitude
            },
            disasterInfo: {
              disasterType: photo.disaster_type || null,
              personCount: photo.person_count || null,
              timeSinceDisaster: photo.time_since_disaster || null,
              additionalInfo: photo.additional_info || ""
            },
            description: "",
            severity: getSeverityLevel(photo.person_count),
          });

        // Başarıyla yüklenen fotoğrafı yerel veritabanından sil
        await deletePhoto(photo.id);
        successCount++;
        console.log(`Afet bildirimi başarıyla senkronize edildi ve silindi. ID: ${photo.id}`);
      } catch (error) {
        console.error('Fotoğraf senkronizasyon hatası:', error);
        errorCount++;
        
        // Hata durumunda fotoğrafı silmeyi dene (muhtemelen zaten yüklenmiş)
        try {
          await deletePhoto(photo.id);
          console.log(`Hata sonrası fotoğraf silindi. ID: ${photo.id}`);
        } catch (deleteError) {
          console.error('Fotoğraf silme hatası:', deleteError);
        }
      }
    }

    console.log(`Senkronizasyon tamamlandı. Başarılı: ${successCount}, Hata: ${errorCount}`);

    // Kullanıcıya sonuç bildirimi göster
    if (successCount > 0) {
      Alert.alert(
        'Senkronizasyon Tamamlandı',
        `${successCount} afet bildirimi başarıyla yüklendi.`,
        [{ text: 'Tamam' }]
      );
    }

    if (errorCount > 0) {
      Alert.alert(
        'Senkronizasyon Hatası',
        `${errorCount} bildirim yüklenirken hata oluştu. İnternet bağlantınızı kontrol edin.`,
        [{ text: 'Tamam' }]
      );
    }

  } catch (error) {
    console.error('Senkronizasyon hatası:', error);
    Alert.alert(
      'Senkronizasyon Hatası',
      'Bildirimler yüklenirken bir hata oluştu. Lütfen internet bağlantınızı kontrol edin.',
      [{ text: 'Tamam' }]
    );
  } finally {
    console.log('Senkronizasyon kilidi kaldırılıyor');
    isSyncing = false;
  }
};



