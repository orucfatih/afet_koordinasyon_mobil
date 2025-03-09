import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import app from '../../firebaseConfig';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { db } from '../../firebaseConfig';
import { collection, addDoc, doc, setDoc } from 'firebase/firestore';

const CameraScreen = ({ navigation }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [uploading, setUploading] = useState(false);
  const storage = getStorage(app);

  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const uploadImageToFirebase = async (uri) => {
    try {
      // URI'den blob oluştur
      const response = await fetch(uri);
      const blob = await response.blob();

      // Tarih bilgisi ile dosya adı oluştur
      const currentDate = new Date();
      const fileName = `afet_${currentDate.getFullYear()}_${currentDate.getMonth() + 1}_${currentDate.getDate()}_${currentDate.getHours()}_${currentDate.getMinutes()}_${currentDate.getSeconds()}.jpg`;

      // Storage referansı oluştur
      const storageRef = ref(storage, `afet-bildirimleri/${fileName}`);

      // Dosyayı yükle
      await uploadBytes(storageRef, blob);

      // Yüklenen dosyanın URL'sini al
      const downloadURL = await getDownloadURL(storageRef);
      console.log('Fotoğraf URL:', downloadURL);

      // Firestore'a bilgileri kaydet
      const docRef = doc(db, "afet-bildirimleri", fileName);
      await setDoc(docRef, {
        imageUrl: downloadURL,
        timestamp: currentDate,
        fileName: fileName,
        status: "yeni", // Bildirim durumu
        location: {
          latitude: null, // Konum bilgisi eklenebilir
          longitude: null
        },
        description: "", // Açıklama eklenebilir
        severity: "normal", // Önem derecesi eklenebilir
        type: "genel" // Afet tipi eklenebilir
      });

      return downloadURL;
    } catch (error) {
      console.error('Fotoğraf yüklenirken hata oluştu:', error);
      throw error;
    }
  };

  const takePicture = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled) {
        setUploading(true);
        try {
          const downloadURL = await uploadImageToFirebase(result.assets[0].uri);
          Alert.alert(
            'Başarılı', 
            'Fotoğraf çekildi ve başarıyla yüklendi.',
            [{ text: 'Tamam', onPress: () => navigation.goBack() }]
          );
        } catch (error) {
          Alert.alert('Hata', 'Fotoğraf yüklenirken bir hata oluştu.');
        } finally {
          setUploading(false);
        }
      }
    } catch (error) {
      console.error('Fotoğraf çekilirken hata oluştu:', error);
      Alert.alert('Hata', 'Fotoğraf çekilirken bir hata oluştu.');
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>İzin kontrolü yapılıyor...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Kamera izni gerekli</Text>
        <TouchableOpacity 
          style={styles.button} 
          onPress={() => ImagePicker.requestCameraPermissionsAsync()}
        >
          <Text style={styles.buttonText}>İzin Ver</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Afet Bildirimi</Text>
      </View>

      <View style={styles.content}>
        <Text style={styles.description}>
          Afet bölgesindeki durumu fotoğraflamak için kamerayı kullanın.
        </Text>

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
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backButton: {
    marginRight: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  description: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  cameraButton: {
    backgroundColor: '#007AFF',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 10,
  },
  text: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  uploadingContainer: {
    alignItems: 'center',
  },
  uploadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
});

export default CameraScreen; 