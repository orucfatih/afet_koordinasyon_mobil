import NetInfo from '@react-native-community/netinfo';
import { getUnsentPhotos, markPhotoAsSent, initDB } from './sqliteHelper';
import auth from '@react-native-firebase/auth';
import storage from '@react-native-firebase/storage';
import firestore from '@react-native-firebase/firestore';
import { Platform } from 'react-native';

export const startSyncListener = () => {
  // Veritabanını başlat
  initDB().catch(error => {
    console.error('Senkronizasyon veritabanı başlatma hatası:', error);
  });
  
  // Her 5 dakikada bir senkronizasyonu kontrol et
  const intervalId = setInterval(() => {
    NetInfo.fetch().then(state => {
      if (state.isConnected && auth().currentUser) {
        syncPhotos();
      }
    });
  }, 300000); // 5 dakika

  // İnternet bağlantısı değişikliklerini dinle
  const unsubscribe = NetInfo.addEventListener(state => {
    if (state.isConnected && auth().currentUser) {
      syncPhotos();
    }
  });

  // Cleanup fonksiyonu döndür
  return () => {
    clearInterval(intervalId);
    unsubscribe();
  };
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
  // Kullanıcı giriş yapmamışsa senkronizasyonu durdur
  if (!auth().currentUser) {
    console.log('Kullanıcı giriş yapmamış, senkronizasyon yapılamıyor');
    return;
  }

  try {
    const photos = await getUnsentPhotos();
    console.log('Senkronize edilecek fotoğraf sayısı:', photos.length);

    for (const photo of photos) {
      try {
        // Firebase'e yükle
        const fileName = `${auth().currentUser.uid}_${Date.now()}.jpg`;
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
            description: "",
            severity: "normal",
            type: "genel"
          });

        // Başarıyla yüklenen fotoğrafı yerel veritabanında işaretle
        await markPhotoAsSent(photo.id);
        console.log(`Fotoğraf başarıyla senkronize edildi. ID: ${photo.id}`);
      } catch (error) {
        console.error('Fotoğraf senkronizasyon hatası:', error);
      }
    }
  } catch (error) {
    console.error('Senkronizasyon hatası:', error);
  }
};

const uploadPhoto = async (localUri) => {
  try {
    const fileName = localUri.split('/').pop();
    const ref = storage().ref(`uploads/${fileName}`);
    await ref.putFile(localUri);
    return true;
  } catch (e) {
    console.log('Yükleme hatası:', e);
    return false;
  }
};


//------------------------------------------

const uploadImageToFirebase = async (uri, coordinates) => {
  try {
    // URL formatını kontrol et
    const correctUri = Platform.OS === 'android' ? uri : uri.replace('file://', '');
    
    const response = await fetch(correctUri);
    const blob = await response.blob();

    const fileName = `${auth().currentUser.uid}_${Date.now()}.jpg`;
    const storageRef = storage().ref(`afet-bildirimleri/${auth().currentUser.uid}/${fileName}`);

    await storageRef.put(blob);
    const downloadURL = await storageRef.getDownloadURL();

    await firestore()
      .collection('afet-bildirimleri')
      .doc(auth().currentUser.uid)
      .collection('images')
      .doc(fileName)
      .set({
        imageUrl: downloadURL,
        timestamp: new Date(),
        fileName: fileName,
        status: "yeni",
        location: coordinates || { latitude: null, longitude: null },
        description: "",
        severity: "normal",
        type: "genel"
      });

    return downloadURL;
  } catch (error) {
    console.error('Fotoğraf yüklenirken hata oluştu:', error);
    throw error;
  }
};
