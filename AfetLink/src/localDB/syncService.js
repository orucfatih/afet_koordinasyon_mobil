import NetInfo from '@react-native-community/netinfo';
import { getUnsentPhotos, markPhotoAsSent } from './sqliteHelper';
import { getAuth } from 'firebase/auth';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { getFirestore, doc, setDoc } from 'firebase/firestore';
import app from '../../firebaseConfig';

export const startSyncListener = () => {
  const auth = getAuth(app);

  // Her 5 dakikada bir senkronizasyonu kontrol et
  const intervalId = setInterval(() => {
    NetInfo.fetch().then(state => {
      if (state.isConnected && auth.currentUser) {
        syncPhotos();
      }
    });
  }, 300000); // 5 dakika

  // İnternet bağlantısı değişikliklerini dinle
  const unsubscribe = NetInfo.addEventListener(state => {
    if (state.isConnected && auth.currentUser) {
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
  const auth = getAuth(app);
  
  // Kullanıcı giriş yapmamışsa senkronizasyonu durdur
  if (!auth.currentUser) {
    console.log('Kullanıcı giriş yapmamış, senkronizasyon yapılamıyor');
    return;
  }

  const photos = await getUnsentPhotos();
  const storage = getStorage(app);
  const db = getFirestore(app);

  for (const photo of photos) {
    try {
      // Firebase'e yükle
      const fileName = `${auth.currentUser.uid}_${Date.now()}.jpg`;
      const storageRef = ref(storage, `afet-bildirimleri/${auth.currentUser.uid}/${fileName}`);
      
      const response = await fetch(photo.uri);
      const blob = await response.blob();
      
      await uploadBytes(storageRef, blob);
      const downloadURL = await getDownloadURL(storageRef);

      // Firestore'a metadata kaydet
      const imageDocRef = doc(db, 'afet-bildirimleri', auth.currentUser.uid, 'images', fileName);
      await setDoc(imageDocRef, {
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
    } catch (error) {
      console.error('Fotoğraf senkronizasyon hatası:', error);
    }
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

    const fileName = `${auth.currentUser.uid}_${Date.now()}.jpg`;
    const storageRef = ref(storage, `afet-bildirimleri/${auth.currentUser.uid}/${fileName}`);

    await uploadBytes(storageRef, blob);
    const downloadURL = await getDownloadURL(storageRef);

    await setDoc(doc(db, `afet-bildirimleri/${auth.currentUser.uid}/images`, fileName), {
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
