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
  StatusBar,
  Image,
  ScrollView,
  TextInput
} from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import auth from '@react-native-firebase/auth';
import storage from '@react-native-firebase/storage';
import firestore from '@react-native-firebase/firestore';
import { savePhoto, initDB } from '../localDB/sqliteHelper';
import { startSyncListener } from '../localDB/syncService';
import Geolocation from 'react-native-geolocation-service';
import DropDownPicker from 'react-native-dropdown-picker';

const CameraScreen = ({ navigation }) => {
  const [uploading, setUploading] = useState(false);
  const [photoUri, setPhotoUri] = useState(null);
  const [location, setLocation] = useState(null);
  const [personCount, setPersonCount] = useState('');
  const [personCountOpen, setPersonCountOpen] = useState(false);
  const [personCountItems, setPersonCountItems] = useState([
    {label: '1 kişi', value: '1'},
    {label: '2 kişi', value: '2'},
    {label: '3 kişi', value: '3'},
    {label: '4 kişi', value: '4'},
    {label: '5 kişi', value: '5'},
    {label: '6-10 kişi', value: '8'},
    {label: '10+ kişi', value: '15'},
    {label: 'Bilinmiyor', value: '0'},
  ]);
  
  const [hoursUnderRubble, setHoursUnderRubble] = useState('');
  const [hoursUnderRubbleOpen, setHoursUnderRubbleOpen] = useState(false);
  const [hoursUnderRubbleItems, setHoursUnderRubbleItems] = useState([
    {label: '0-3 saat', value: '2'},
    {label: '3-6 saat', value: '5'},
    {label: '6-12 saat', value: '9'},
    {label: '12-24 saat', value: '18'},
    {label: '24-48 saat', value: '36'},
    {label: '48+ saat', value: '60'},
    {label: 'Bilinmiyor', value: '0'},
  ]);
  
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [formComplete, setFormComplete] = useState(false);

  useEffect(() => {
    // Form alanlarının dolu olup olmadığını kontrol et
    if (photoUri && personCount !== '' && hoursUnderRubble !== '') {
      setFormComplete(true);
    } else {
      setFormComplete(false);
    }
  }, [photoUri, personCount, hoursUnderRubble]);

  useEffect(() => {
    // Veritabanını başlat
    initDB().catch(error => {
      console.error('Veritabanı başlatma hatası:', error);
    });
    
    // Uygulama başladığında senkronizasyon servisini başlat
    startSyncListener();
  }, []);

  const requestLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Konum İzni',
            message: 'Uygulamanın konumunuza erişmesi gerekiyor.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam'
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    } else {
      return false;
    }
  };
  
  const getCurrentLocation = async () => {
    const hasPermission = await requestLocationPermission();
  
    return new Promise((resolve, reject) => {
      if (!hasPermission) {
        console.log('Konum izni verilmedi');
        return reject({ latitude: null, longitude: null });
      }
  
      Geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => {
          console.log('Konum hatası:', error);
          reject({ latitude: null, longitude: null });
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
      );
    });
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
        
        const locationPermission = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
        );

        if (locationPermission !== PermissionsAndroid.RESULTS.GRANTED) {
          Alert.alert('İzin Gerekli', 'Konum izni olmadan fotoğraf kaydedilemez.');
          return;
        }
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
      saveToPhotos: false,
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

        const { uri } = response.assets[0];
        console.log("Fotoğraf URI:", uri);
        
        // Fotoğraf URI'sini state'e kaydet
        setPhotoUri(uri);
        
        // Konum bilgisini al ve state'e kaydet
        try {
          const locationCoordinates = await getCurrentLocation();
          console.log("Konum alındı:", locationCoordinates);
          setLocation(locationCoordinates);
        } catch (error) {
          console.error("Konum alma hatası:", error);
          setLocation({ latitude: null, longitude: null });
        }
      });
    } catch (error) {
      console.error('Genel hata:', error);
      Alert.alert('Hata', 'Bir hata oluştu.');
    }
  };

  const saveRubbleReport = async () => {
    if (!formComplete) {
      Alert.alert('Eksik Bilgi', 'Lütfen tüm gerekli alanları doldurun.');
      return;
    }

    setUploading(true);
    
    try {
      // Enkaz bilgilerini içeren nesne
      const rubbleInfo = {
        personCount: parseInt(personCount) || 0,
        hoursUnderRubble: parseInt(hoursUnderRubble) || 0,
        additionalInfo: additionalInfo,
      };
      
      // Yerel veritabanına kaydet
      await savePhoto(
        photoUri, 
        location?.latitude, 
        location?.longitude, 
        rubbleInfo
      );
      
      console.log("Kayıt başarılı.");
      Alert.alert(
        'Başarılı',
        'Enkaz bildirimi kaydedildi. İnternet bağlantısı olduğunda otomatik olarak yüklenecek.',
        [{ 
          text: 'Tamam', 
          onPress: () => {
            // Formu sıfırla
            setPhotoUri(null);
            setPersonCount('');
            setHoursUnderRubble('');
            setAdditionalInfo('');
            setLocation(null);
          } 
        }]
      );
    } catch (error) {
      console.error("Kayıt sırasında hata:", error);
      Alert.alert('Hata', 'Enkaz bildirimi kaydedilirken bir hata oluştu.');
    } finally {
      setUploading(false);
    }
  };

  const renderPhotoForm = () => {
    if (!photoUri) return null;
    
    return (
      <ScrollView style={styles.formContainer}>
        <View style={styles.photoPreviewContainer}>
          <Image source={{ uri: photoUri }} style={styles.previewImage} />
          <TouchableOpacity style={styles.retakeButton} onPress={takePicture}>
            <Ionicons name="camera-reverse" size={24} color="#fff" />
            <Text style={styles.retakeButtonText}>Yeniden Çek</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Enkaz Altındaki Tahmini Kişi Sayısı*</Text>
          <DropDownPicker
            open={personCountOpen}
            value={personCount}
            items={personCountItems}
            setOpen={setPersonCountOpen}
            setValue={setPersonCount}
            setItems={setPersonCountItems}
            placeholder="Kişi sayısı seçin"
            style={styles.dropdown}
            dropDownContainerStyle={styles.dropdownContainer}
            listItemLabelStyle={styles.dropdownItemLabel}
            zIndex={3000}
            zIndexInverse={1000}
          />
        </View>
        
        <View style={[styles.formGroup, {marginTop: personCountOpen ? 150 : 20}]}>
          <Text style={styles.label}>Enkazın Üzerinden Geçen Süre*</Text>
          <DropDownPicker
            open={hoursUnderRubbleOpen}
            value={hoursUnderRubble}
            items={hoursUnderRubbleItems}
            setOpen={setHoursUnderRubbleOpen}
            setValue={setHoursUnderRubble}
            setItems={setHoursUnderRubbleItems}
            placeholder="Süre seçin"
            style={styles.dropdown}
            dropDownContainerStyle={styles.dropdownContainer}
            listItemLabelStyle={styles.dropdownItemLabel}
            zIndex={2000}
            zIndexInverse={2000}
          />
        </View>
        
        <View style={[styles.formGroup, {marginTop: hoursUnderRubbleOpen ? 150 : 20}]}>
          <Text style={styles.label}>Ek Bilgiler</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={additionalInfo}
            onChangeText={setAdditionalInfo}
            placeholder="Varsa ek bilgiler (isteğe bağlı)"
            multiline
            numberOfLines={4}
          />
        </View>
        
        <TouchableOpacity 
          style={[
            styles.submitButton, 
            formComplete ? styles.submitButtonActive : styles.submitButtonDisabled
          ]} 
          onPress={saveRubbleReport}
          disabled={!formComplete || uploading}
        >
          {uploading ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <>
              <Ionicons name="send" size={24} color="#fff" />
              <Text style={styles.submitButtonText}>Enkazı Bildir</Text>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.title}>Enkaz Bildirimi</Text>
        </View>
        
        {photoUri ? (
          renderPhotoForm()
        ) : (
          <View style={styles.content}>
            <Text style={styles.description}>Enkaz bölgesini fotoğraflamak için kamerayı kullanın.</Text>
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
        )}
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
  },
  // Form stilleri
  formContainer: {
    flex: 1,
    padding: 16,
  },
  photoPreviewContainer: {
    marginBottom: 20,
    alignItems: 'center',
  },
  previewImage: {
    width: '100%',
    height: 250,
    borderRadius: 10,
    marginBottom: 10,
    resizeMode: 'cover',
  },
  retakeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FF3B30',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  retakeButtonText: {
    color: '#fff',
    marginLeft: 8,
    fontWeight: 'bold',
  },
  formGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  // Dropdown stilleri
  dropdown: {
    backgroundColor: '#f5f5f5',
    borderColor: '#ddd',
    borderRadius: 8,
    height: 50,
  },
  dropdownContainer: {
    backgroundColor: '#fff',
    borderColor: '#ddd',
    borderWidth: 1,
  },
  dropdownItemLabel: {
    color: '#333',
    fontSize: 16,
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 10,
    marginVertical: 20,
    marginBottom: 40,
  },
  submitButtonActive: {
    backgroundColor: '#28CD41',
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  }
});

export default CameraScreen;
