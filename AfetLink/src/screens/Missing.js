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
import { launchImageLibrary } from 'react-native-image-picker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import auth from '@react-native-firebase/auth';
import storage from '@react-native-firebase/storage';
import firestore from '@react-native-firebase/firestore';
import DropDownPicker from 'react-native-dropdown-picker';
import Geolocation from 'react-native-geolocation-service';
import MapView, { Marker } from 'react-native-maps';

const Missing = ({ navigation }) => {
  // İlçeler listesi
  const districts = [
    'Aliağa', 'Balçova', 'Bayraklı', 'Bornova', 'Buca', 'Çiğli', 'Gaziemir',
    'Güzelbahçe', 'Karabağlar', 'Karşıyaka', 'Konak', 'Menemen', 'Narlıdere'
  ];

  const [hasStoragePermission, setHasStoragePermission] = useState(null);
  const [hasLocationPermission, setHasLocationPermission] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [image, setImage] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  
  // Dropdown için state'ler
  const [genderOpen, setGenderOpen] = useState(false);
  const [districtOpen, setDistrictOpen] = useState(false);
  const [genderValue, setGenderValue] = useState('');
  const [districtValue, setDistrictValue] = useState('');

  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    age: '',
    gender: '',
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
    checkPermissions();
  }, []);

  const checkPermissions = async () => {
    await checkStoragePermission();
    await checkLocationPermission();
    if (hasLocationPermission) {
      await fetchCurrentLocation();
    }
  };

  const checkStoragePermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          Platform.Version >= 33
            ? PermissionsAndroid.PERMISSIONS.READ_MEDIA_IMAGES
            : PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
          {
            title: 'Galeri İzni',
            message: 'Galeriden fotoğraf seçmek için depolama iznine ihtiyacımız var.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        setHasStoragePermission(granted === PermissionsAndroid.RESULTS.GRANTED);
      } catch (err) {
        console.warn(err);
        setHasStoragePermission(false);
      }
    } else {
      setHasStoragePermission(true);
    }
  };

  const checkLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
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
        setHasLocationPermission(granted === PermissionsAndroid.RESULTS.GRANTED);
      } catch (err) {
        console.warn(err);
        setHasLocationPermission(false);
      }
    } else {
      setHasLocationPermission(true);
    }
  };

  const fetchCurrentLocation = async () => {
    try {
      const position = await new Promise((resolve, reject) => {
        Geolocation.getCurrentPosition(
          resolve,
          reject,
          { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
        );
      });
      setCurrentLocation({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      });
    } catch (error) {
      console.error('Mevcut konum alınırken hata:', error);
      Alert.alert('Hata', 'Mevcut konum alınamadı, harita varsayılan konumda açılacak.');
    }
  };

  const pickImage = async () => {
    try {
      const options = {
        mediaType: 'photo',
        quality: 1,
        saveToPhotos: false,
      };

      const result = await launchImageLibrary(options);

      if (!result.didCancel && result.assets && result.assets[0]) {
        setImage(result.assets[0].uri);
      } else {
        Alert.alert('Uyarı', 'Fotoğraf seçimi iptal edildi.');
      }
    } catch (error) {
      console.error('Fotoğraf seçilirken hata:', error);
      Alert.alert('Hata', 'Fotoğraf seçilirken bir hata oluştu.');
    }
  };

  const handleMapPress = (event) => {
    const { coordinate } = event.nativeEvent;
    setSelectedLocation(coordinate);
  };

  const saveSelectedLocation = () => {
    if (!selectedLocation) {
      Alert.alert('Uyarı', 'Lütfen haritadan bir konum seçin.');
      return;
    }

    if (
      formData.lastSeenLocation &&
      formData.lastSeenLocation.latitude === selectedLocation.latitude &&
      formData.lastSeenLocation.longitude === selectedLocation.longitude
    ) {
      Alert.alert(
        'Konum Aynı',
        'Seçilen konum, zaten kaydedilmiş olan son görülme konumuyla aynı. Yine de güncellemek ister misiniz?',
        [
          { text: 'Hayır', style: 'cancel' },
          {
            text: 'Evet',
            onPress: () => {
              setFormData(prev => ({
                ...prev,
                lastSeenLocation: selectedLocation
              }));
              Alert.alert('Başarılı', 'Konum güncellendi.');
            }
          }
        ]
      );
    } else {
      setFormData(prev => ({
        ...prev,
        lastSeenLocation: selectedLocation
      }));
      Alert.alert('Başarılı', 'Son görülme konumu kaydedildi.');
    }
  };

  const handleSubmit = async () => {
    if (!formData.fullName || !formData.phone || !formData.age || !formData.district) {
      Alert.alert('Uyarı', 'Lütfen zorunlu alanları doldurun (Ad Soyad, Telefon, Yaş, İlçe).');
      return;
    }

    if (!image) {
      Alert.alert(
        'Fotoğraf Önemli',
        'Fotoğraf yüklemek kayıp ihbarının bulunma şansını artırır. Fotoğraf olmadan devam etmek istiyor musunuz?',
        [
          { text: 'Hayır', style: 'cancel' },
          {
            text: 'Evet',
            onPress: async () => {
              await submitReport(null);
            }
          }
        ]
      );
    } else {
      await submitReport(image);
    }
  };

  const submitReport = async (imageUri) => {
    try {
      setUploading(true);

      let imageUrl = null;
      if (imageUri) {
        const response = await fetch(imageUri);
        const blob = await response.blob();
        const fileName = `missing_${auth().currentUser.uid}_${Date.now()}.jpg`;
        const storageRef = storage().ref(`missing-reports/${auth().currentUser.uid}/${fileName}`);
        
        await storageRef.put(blob);
        imageUrl = await storageRef.getDownloadURL();
      }

      await firestore()
        .collection('missing-reports')
        .doc(`${auth().currentUser.uid}_${Date.now()}`)
        .set({
          ...formData,
          imageUrl,
          reporterId: auth().currentUser.uid,
          reporterEmail: auth().currentUser.email,
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

  if (hasStoragePermission === null || hasLocationPermission === null) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>İzin kontrolü yapılıyor...</Text>
      </View>
    );
  }

  if (hasStoragePermission === false || hasLocationPermission === false) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionTitle}>İzin Gerekli</Text>
        <Text style={styles.permissionText}>
          {hasStoragePermission === false && hasLocationPermission === false
            ? 'Galeriden fotoğraf seçmek ve konum bilgisi için depolama ve konum izinlerine ihtiyacımız var.'
            : hasStoragePermission === false
            ? 'Galeriden fotoğraf seçmek için depolama iznine ihtiyacımız var.'
            : 'Son görülme konumunu seçmek için konum iznine ihtiyacımız var.'}
        </Text>
        <TouchableOpacity style={styles.permissionButton} onPress={checkPermissions}>
          <Text style={styles.permissionButtonText}>İzin Ver</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}/>

      <SafeAreaView style={styles.safeArea}>
        <ScrollView 
          style={styles.container}
          keyboardShouldPersistTaps="handled">

          <TouchableOpacity 
            style={styles.dismissKeyboard} 
            activeOpacity={1} 
            onPress={() => Keyboard.dismiss()}>
              
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
                  <TouchableOpacity style={styles.retakeButton} onPress={pickImage}>
                    <Text style={styles.retakeButtonText}>Yeniden Seç</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity style={styles.cameraButton} onPress={pickImage}>
                  <Ionicons name="image" size={40} color="#fff" />
                  <Text style={styles.cameraButtonText}>Fotoğraf Seç</Text>
                </TouchableOpacity>
              )}

              <View style={styles.form}>
                <TextInput
                  style={styles.input}
                  placeholder="Ad Soyad"
                  placeholderTextColor="lightgray"
                  value={formData.fullName}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, fullName: text }))}
                />

                <TextInput
                  style={styles.input}
                  placeholder="Telefon"
                  placeholderTextColor="lightgray"
                  value={formData.phone}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, phone: text }))}
                  keyboardType="phone-pad"
                />

                <TextInput
                  style={styles.input}
                  placeholder="Yaş"
                  placeholderTextColor="lightgray"
                  value={formData.age}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, age: text }))}
                  keyboardType="numeric"
                />

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
                  placeholderTextColor="lightgray"
                  value={formData.clothingDescription}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, clothingDescription: text }))}
                  multiline
                  numberOfLines={3}
                />

                <TextInput
                  style={[styles.input, styles.textArea]}
                  placeholder="Diğer Bilgiler"
                  placeholderTextColor="lightgray"
                  value={formData.otherInfo}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, otherInfo: text }))}
                  multiline
                  numberOfLines={3}
                />

                <View style={styles.mapContainer}>
                  <Text style={styles.mapTitle}>Son Görülme Konumu Seçin</Text>
                  <MapView
                    style={styles.map}
                    initialRegion={{
                      latitude: currentLocation ? currentLocation.latitude : 38.4237, // İzmir merkezi
                      longitude: currentLocation ? currentLocation.longitude : 27.1428,
                      latitudeDelta: 0.01,
                      longitudeDelta: 0.01,
                    }}
                    onPress={handleMapPress}
                    showsUserLocation={!!currentLocation} // Mevcut konum varsa kullanıcı konumu göster
                    zoomEnabled={true}
                    zoomControlEnabled={true}
                  >
                    {selectedLocation && (
                      <Marker
                        coordinate={selectedLocation}
                        title="Seçilen Konum"
                        pinColor="red"
                      />
                    )}
                    {currentLocation && (
                      <Marker
                        coordinate={currentLocation}
                        title="Mevcut Konum"
                        pinColor="blue"
                      />
                    )}
                  </MapView>
                  <TouchableOpacity style={styles.saveLocationButton} onPress={saveSelectedLocation}>
                    <Text style={styles.saveLocationButtonText}>
                      {formData.lastSeenLocation ? 'Konumu Güncelle' : 'Konumu Kaydet'}
                    </Text>
                  </TouchableOpacity>
                </View>

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
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  permissionText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24,
  },
  permissionButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  mapContainer: {
    marginTop: 20,
    gap: 10,
  },
  mapTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  map: {
    height: 300,
    borderRadius: 8,
  },
  mapLoadingText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  saveLocationButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveLocationButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default Missing;