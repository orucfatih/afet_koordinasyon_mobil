import React, { useState, useEffect } from 'react';
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
import Geolocation from 'react-native-geolocation-service';

const CameraScreen = ({ navigation }) => {
  const [uploading, setUploading] = useState(false);
  const auth = getAuth(app);
  const storage = getStorage(app);
  const db = getFirestore(app);

  const requestCameraPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA,
          {
            title: "Kamera İzni",
            message: "Afet bildirimi yapabilmek için kamera izni gerekli.",
            buttonNeutral: "Daha Sonra Sor",
            buttonNegative: "İptal",
            buttonPositive: "Tamam"
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  const requestLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: "Konum İzni",
            message: "Afet bildiriminin konumunu kaydetmek için konum izni gerekli.",
            buttonNeutral: "Daha Sonra Sor",
            buttonNegative: "İptal",
            buttonPositive: "Tamam"
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  const uploadImageToFirebase = async (uri, coordinates) => {
    try {
      await auth.currentUser.reload();
  
      const response = await fetch(uri);
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
        location: coordinates,
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
    try {
      const hasCameraPermission = await requestCameraPermission();
      if (!hasCameraPermission) {
        Alert.alert('İzin Gerekli', 'Fotoğraf çekmek için kamera izni gerekli.');
        return;
      }

      const hasLocationPermission = await requestLocationPermission();
      if (!hasLocationPermission) {
        Alert.alert('Uyarı', 'Konum izni olmadan devam edilecek.');
      }

      const options = {
        mediaType: 'photo',
        includeBase64: false,
        maxHeight: 1280,
        maxWidth: 1280,
        quality: 0.7,
        saveToPhotos: false,
        presentationStyle: 'fullScreen',
        cameraType: 'back',
        includeExtra: true,
        formatAsMp4: false,
        rotation: 0,
        durationLimit: 0,
        videoQuality: 'high'
      };

      const result = await launchCamera(options);
      console.log('Kamera sonucu:', JSON.stringify(result, null, 2));

      if (!result || result.didCancel || !result.assets) {
        console.log('Kamera iptal edildi veya sonuç yok');
        return;
      }

      if (result.errorCode) {
        console.error('Kamera hatası:', result.errorMessage);
        Alert.alert('Hata', `Kamera hatası: ${result.errorMessage}`);
        return;
      }

      const asset = result.assets[0];
      if (!asset || !asset.uri) {
        console.error('Fotoğraf alınamadı');
        Alert.alert('Hata', 'Fotoğraf alınamadı');
        return;
      }

      setUploading(true);

      try {
        let coordinates = { latitude: null, longitude: null };
        if (hasLocationPermission) {
          try {
            const location = await new Promise((resolve, reject) => {
              Geolocation.getCurrentPosition(
                position => resolve(position),
                error => reject(error),
                { 
                  enableHighAccuracy: true, 
                  timeout: 15000, 
                  maximumAge: 10000,
                  distanceFilter: 0,
                  forceRequestLocation: true
                }
              );
            });

            if (location?.coords) {
              coordinates = {
                latitude: location.coords.latitude,
                longitude: location.coords.longitude
              };
            }
          } catch (locationError) {
            console.warn('Konum alınamadı:', locationError);
          }
        }

        const fileUri = Platform.OS === 'ios' ? asset.uri.replace('file://', '') : asset.uri;
        
        await uploadImageToFirebase(fileUri, coordinates);

        Alert.alert(
          'Başarılı', 
          'Fotoğraf başarıyla yüklendi.', 
          [{ text: 'Tamam', onPress: () => navigation.goBack() }]
        );
      } catch (error) {
        console.error('Yükleme hatası:', error);
        Alert.alert(
          'Hata',
          'Fotoğraf yüklenemedi. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.'
        );
      } finally {
        setUploading(false);
      }
    } catch (error) {
      console.error('Genel hata:', error);
      Alert.alert(
        'Hata',
        'Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.'
      );
      setUploading(false);
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
