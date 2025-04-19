import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  TextInput,
  Image,
  Platform,
  Keyboard,
  PermissionsAndroid,
  StatusBar,
  SafeAreaView
} from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { getAuth } from 'firebase/auth';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { getFirestore, doc, setDoc } from 'firebase/firestore';
import app from '../../firebaseConfig';
import DropDownPicker from 'react-native-dropdown-picker';

const Missing = ({ navigation }) => {
  const auth = getAuth(app);
  const storage = getStorage(app);
  const db = getFirestore(app);

  // İlçeler listesi
  const districts = [
    'Aliağa', 'Balçova', 'Bayraklı', 'Bornova', 'Buca', 'Çiğli', 'Gaziemir',
    'Güzelbahçe', 'Karabağlar', 'Karşıyaka', 'Konak', 'Menemen', 'Narlıdere'
  ];

  const [hasPermission, setHasPermission] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [image, setImage] = useState(null);
  
  // Dropdown için state'ler
  const [genderOpen, setGenderOpen] = useState(false);
  const [districtOpen, setDistrictOpen] = useState(false);
  const [genderValue, setGenderValue] = useState('erkek');
  const [districtValue, setDistrictValue] = useState('');

  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    age: '',
    gender: 'erkek',
    district: '',
    clothingDescription: '',
    otherInfo: '',
    lastSeenLocation: null
  });

  const [genderItems] = useState([
    { label: 'Erkek', value: 'erkek' },
    { label: 'Kadın', value: 'kadın' }
  ]);

  const [districtItems] = useState(
    districts.map(district => ({
      label: district,
      value: district
    }))
  );

  useEffect(() => {
    checkCameraPermission();
  }, []);

  const checkCameraPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA,
          {
            title: 'Kamera İzni',
            message: 'Fotoğraf çekmek için kamera iznine ihtiyacımız var.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        setHasPermission(granted === PermissionsAndroid.RESULTS.GRANTED);
      } catch (err) {
        console.warn(err);
        setHasPermission(false);
      }
    } else {
      setHasPermission(true);
    }
  };

  const takePicture = async () => {
    try {
      const options = {
        mediaType: 'photo',
        quality: 1,
        saveToPhotos: false,
      };

      const result = await launchCamera(options);

      if (!result.didCancel && result.assets && result.assets[0]) {
        setImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Fotoğraf çekilirken hata:', error);
      Alert.alert('Hata', 'Fotoğraf çekilirken bir hata oluştu.');
    }
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
          { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
        );
      } else {
        resolve({ latitude: null, longitude: null });
      }
    });
  };

  const selectLocation = async () => {
    try {
      if (Platform.OS === 'android') {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Konum İzni',
            message: 'Son görülme konumunu seçmek için konum iznine ihtiyacımız var.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
          Alert.alert('Konum izni gerekli', 'Son görülme konumunu seçmek için konum iznine ihtiyacımız var.');
          return;
        }
      }

      const location = await getCurrentLocation();
      if (location.latitude && location.longitude) {
        setFormData(prev => ({
          ...prev,
          lastSeenLocation: location
        }));
        Alert.alert('Başarılı', 'Konum başarıyla kaydedildi.');
      } else {
        Alert.alert('Hata', 'Konum alınamadı.');
      }
    } catch (error) {
      console.error('Konum alınırken hata:', error);
      Alert.alert('Hata', 'Konum alınırken bir hata oluştu.');
    }
  };

  const handleSubmit = async () => {
    if (!image) {
      Alert.alert('Uyarı', 'Lütfen bir fotoğraf çekin.');
      return;
    }

    if (!formData.fullName || !formData.phone || !formData.age || !formData.district) {
      Alert.alert('Uyarı', 'Lütfen zorunlu alanları doldurun.');
      return;
    }

    try {
      setUploading(true);

      // Fotoğrafı yükle
      const response = await fetch(image);
      const blob = await response.blob();
      const fileName = `missing_${auth.currentUser.uid}_${Date.now()}.jpg`;
      const storageRef = ref(storage, `missing-reports/${auth.currentUser.uid}/${fileName}`);
      
      await uploadBytes(storageRef, blob);
      const imageUrl = await getDownloadURL(storageRef);

      // Firestore'a kaydet
      const docRef = doc(db, 'missing-reports', `${auth.currentUser.uid}_${Date.now()}`);
      await setDoc(docRef, {
        ...formData,
        imageUrl,
        reporterId: auth.currentUser.uid,
        reporterEmail: auth.currentUser.email,
        timestamp: new Date(),
        status: 'active'
      });

      Alert.alert('Başarılı', 'Kayıp ihbarı başarıyla gönderildi.', [
        { text: 'Tamam', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      console.error('Kayıp ihbarı gönderilirken hata:', error);
      Alert.alert('Hata', 'Kayıp ihbarı gönderilirken bir hata oluştu.');
    } finally {
      setUploading(false);
    }
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>İzin kontrolü yapılıyor...</Text></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.container}><Text>Kamera izni gerekli</Text></View>;
  }

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      <SafeAreaView style={styles.safeArea}>
        <ScrollView 
          style={styles.container}
          keyboardShouldPersistTaps="handled"
        >
          <TouchableOpacity 
            style={styles.dismissKeyboard} 
            activeOpacity={1} 
            onPress={() => Keyboard.dismiss()}
          >
            <View style={styles.header}>
              <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
                <Ionicons name="arrow-back" size={24} color="#333" />
              </TouchableOpacity>
              <Text style={styles.title}>Kayıp İhbarı</Text>
            </View>

            <View style={styles.content}>
              {image ? (
                <View style={styles.imageContainer}>
                  <Image source={{ uri: image }} style={styles.previewImage} />
                  <TouchableOpacity style={styles.retakeButton} onPress={takePicture}>
                    <Text style={styles.retakeButtonText}>Yeniden Çek</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity style={styles.cameraButton} onPress={takePicture}>
                  <Ionicons name="camera" size={40} color="#fff" />
                  <Text style={styles.cameraButtonText}>Fotoğraf Çek</Text>
                </TouchableOpacity>
              )}

              <View style={styles.form}>
                <TextInput
                  style={styles.input}
                  placeholder="Ad Soyad"
                  value={formData.fullName}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, fullName: text }))}
                />

                <TextInput
                  style={styles.input}
                  placeholder="Telefon"
                  value={formData.phone}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, phone: text }))}
                  keyboardType="phone-pad"
                />

                <TextInput
                  style={styles.input}
                  placeholder="Yaş"
                  value={formData.age}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, age: text }))}
                  keyboardType="numeric"
                />

                {/* Cinsiyet Seçimi */}
                <DropDownPicker
                  open={genderOpen}
                  value={genderValue}
                  items={genderItems}
                  setOpen={setGenderOpen}
                  setValue={setGenderValue}
                  onChangeValue={(value) => {
                    setFormData(prev => ({ ...prev, gender: value }))
                  }}
                  style={styles.dropdown}
                  dropDownContainerStyle={styles.dropdownContainer}
                  placeholder="Cinsiyet Seçin"
                  listMode="SCROLLVIEW"
                  zIndex={3000}
                />

                {/* İlçe Seçimi */}
                <DropDownPicker
                  open={districtOpen}
                  value={districtValue}
                  items={districtItems}
                  setOpen={setDistrictOpen}
                  setValue={setDistrictValue}
                  onChangeValue={(value) => {
                    setFormData(prev => ({ ...prev, district: value }))
                  }}
                  style={styles.dropdown}
                  dropDownContainerStyle={styles.dropdownContainer}
                  placeholder="İlçe Seçin"
                  listMode="SCROLLVIEW"
                  searchable={true}
                  searchPlaceholder="İlçe Ara..."
                  zIndex={2000}
                />

                <TextInput
                  style={[styles.input, styles.textArea]}
                  placeholder="Kıyafet Tanımı"
                  value={formData.clothingDescription}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, clothingDescription: text }))}
                  multiline
                  numberOfLines={3}
                />

                <TextInput
                  style={[styles.input, styles.textArea]}
                  placeholder="Diğer Bilgiler"
                  value={formData.otherInfo}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, otherInfo: text }))}
                  multiline
                  numberOfLines={3}
                />

                <TouchableOpacity style={styles.locationButton} onPress={selectLocation}>
                  <Text style={styles.locationButtonText}>
                    {formData.lastSeenLocation ? 'Son Görülme Konumu Seçildi' : 'Son Görülme Konumu Seç'}
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.submitButton}
                  onPress={handleSubmit}
                  disabled={uploading}
                >
                  {uploading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.submitButtonText}>İhbar Gönder</Text>
                  )}
                </TouchableOpacity>
              </View>
            </View>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#2D2D2D',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
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
    padding: 20,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  previewImage: {
    width: 300,
    height: 400,
    borderRadius: 10,
    marginBottom: 10,
  },
  retakeButton: {
    backgroundColor: '#666',
    padding: 10,
    borderRadius: 5,
  },
  retakeButtonText: {
    color: '#fff',
    fontSize: 16,
  },
  cameraButton: {
    backgroundColor: '#007AFF',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 10,
  },
  form: {
    gap: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  locationButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  locationButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#D32F2F',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  dismissKeyboard: {
    flex: 1,
  },
  dropdown: {
    backgroundColor: 'white',
    borderColor: '#ddd',
    borderRadius: 8,
    marginVertical: 8,
  },
  dropdownContainer: {
    borderColor: '#ddd',
    borderRadius: 8,
  },
});

export default Missing;