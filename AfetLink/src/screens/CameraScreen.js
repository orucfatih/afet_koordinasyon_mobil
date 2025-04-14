import React, { useState } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  Alert, 
  ActivityIndicator, 
  Platform,
  PermissionsAndroid,
  SafeAreaView,
  StatusBar
} from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { getAuth } from 'firebase/auth';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { getFirestore, doc, setDoc } from 'firebase/firestore';
import app from '../../firebaseConfig';

const CameraScreen = ({ navigation }) => {
  const [uploading, setUploading] = useState(false);
  const auth = getAuth(app);
  const storage = getStorage(app);
  const db = getFirestore(app);

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
  
  const takePicture = async () => {
    // İzinleri kontrol et
    if (Platform.OS === 'android') {
      try {
        const cameraPermission = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA
        );
        
        if (cameraPermission !== PermissionsAndroid.RESULTS.GRANTED) {
          Alert.alert('İzin Gerekli', 'Kamera izni olmadan fotoğraf çekilemez.');
          return;
        }
        
        // Konum izni iste
        await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
        );
      } catch (err) {
        console.error("İzin hatası:", err);
        return;
      }
    }

    // Kamerayı başlat - çok basit seçeneklerle
    const options = {
      mediaType: 'photo',
      includeBase64: false,
      quality: 0.7,
      maxWidth: 1000,
      maxHeight: 1000,
      saveToPhotos: false
    };

    try {
      launchCamera(options, async (response) => {
        if (response.didCancel) {
          console.log('Kullanıcı kamerayı iptal etti');
          return;
        }
        
        if (response.errorCode) {
          console.log('Kamera hatası: ', response.errorMessage);
          Alert.alert('Hata', 'Kamera açılırken bir hata oluştu.');
          return;
        }
        
        if (!response.assets || !response.assets[0] || !response.assets[0].uri) {
          console.log('Fotoğraf alınamadı');
          Alert.alert('Hata', 'Fotoğraf alınamadı.');
          return;
        }

        // Fotoğraf alındı, yüklemeye başla
        setUploading(true);
        
        try {
          const { uri } = response.assets[0];
          console.log("Fotoğraf URI:", uri);
          
          // Konum almaya çalış
          let locationCoordinates;
          try {
            locationCoordinates = await getCurrentLocation();
            console.log("Konum alındı:", locationCoordinates);
          } catch (locationError) {
            console.log("Konum alınamadı:", locationError);
            locationCoordinates = { latitude: null, longitude: null };
          }
          
          // Firebase'e yükle (konumla birlikte)
          await uploadImageToFirebase(uri, locationCoordinates);
          
          // Başarılı mesajı göster
          Alert.alert(
            'Başarılı',
            'Fotoğraf başarıyla yüklendi.',
            [{ text: 'Tamam', onPress: () => navigation.goBack() }]
          );
        } catch (error) {
          console.error('Yükleme hatası:', error);
          Alert.alert('Hata', 'Fotoğraf yüklenirken bir hata oluştu.');
        } finally {
          setUploading(false);
        }
      });
    } catch (error) {
      console.error('Genel hata:', error);
      Alert.alert('Hata', 'Bir hata oluştu.');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.title}>Afet Bildirimi</Text>
        </View>
        <View style={styles.content}>
          <Text style={styles.description}>Afet bölgesindeki durumu fotoğraflamak için kamerayı kullanın.</Text>
          {uploading ? (
            <View style={styles.uploadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.uploadingText}>Fotoğraf yükleniyor...</Text>
            </View>
          ) : (
            <TouchableOpacity style={styles.cameraButton} onPress={takePicture}>
              <Ionicons name="camera" size={40} color="#fff" />
              <Text style={styles.cameraButtonText}>Fotoğraf Çek</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0
  },
  container: { 
    flex: 1, 
    backgroundColor: '#fff' 
  },
  header: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  backButton: { 
    padding: 8,
  },
  title: { 
    fontSize: 20, 
    fontWeight: 'bold', 
    color: '#333',
    marginLeft: 16,
  },
  content: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center', 
    padding: 20 
  },
  description: { 
    fontSize: 16, 
    color: '#666', 
    textAlign: 'center', 
    marginBottom: 30 
  },
  cameraButton: { 
    backgroundColor: '#007AFF', 
    padding: 20, 
    borderRadius: 15, 
    alignItems: 'center',
    width: '80%',
  },
  cameraButtonText: { 
    color: '#fff', 
    fontSize: 18, 
    fontWeight: 'bold', 
    marginTop: 10 
  },
  uploadingContainer: { 
    alignItems: 'center' 
  },
  uploadingText: { 
    marginTop: 10, 
    fontSize: 16, 
    color: '#666' 
  }
});

export default CameraScreen;
