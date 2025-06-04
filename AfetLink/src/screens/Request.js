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
import Ionicons from 'react-native-vector-icons/Ionicons';
import auth from '@react-native-firebase/auth';
import firestore from '@react-native-firebase/firestore';
import DropDownPicker from 'react-native-dropdown-picker';
import Geolocation from 'react-native-geolocation-service';
import MapView, { Marker } from 'react-native-maps';

const Request = ({ navigation }) => {
  // İlçeler listesi
  const districts = [
    'Aliağa', 'Balçova', 'Bayraklı', 'Bornova', 'Buca', 'Çiğli', 'Gaziemir',
    'Güzelbahçe', 'Karabağlar', 'Karşıyaka', 'Konak', 'Menemen', 'Narlıdere'
  ];

  // İhtiyaç kategorileri
  const needCategories = [
    'Su', 'Gıda', 'Giyim', 'Isınma', 'Barınma', 'Hijyen',
    'İlaç', 'Bebek Malzemeleri', 'Diğer'
  ];

  const [hasLocationPermission, setHasLocationPermission] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  
  // Dropdown için state'ler
  const [categoryOpen, setCategoryOpen] = useState(false);
  const [urgencyOpen, setUrgencyOpen] = useState(false);
  const [districtOpen, setDistrictOpen] = useState(false);
  const [categoryValue, setCategoryValue] = useState('');
  const [urgencyValue, setUrgencyValue] = useState('');
  const [districtValue, setDistrictValue] = useState('');

  const [formData, setFormData] = useState({
    contactName: '',
    phone: '',
    needCategory: '',
    urgencyLevel: '',
    district: '',
    peopleCount: '',
    description: '',
    location: null
  });

  const [categoryItems] = useState(
    needCategories.map(category => ({
      label: category,
      value: category
    }))
  );

  const [urgencyItems] = useState([
    { label: 'Kritik - Acil', value: 'kritik' },
    { label: 'Yüksek', value: 'yuksek' },
    { label: 'Orta', value: 'orta' },
    { label: 'Düşük', value: 'dusuk' }
  ]);

  const [districtItems] = useState(
    districts.map(district => ({
      label: district,
      value: district
    }))
  );

  useEffect(() => {
    checkLocationPermission();
  }, []);

  const checkLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Konum İzni',
            message: 'İhtiyaç konumunu belirlemek için konum iznine ihtiyacımız var.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        setHasLocationPermission(granted === PermissionsAndroid.RESULTS.GRANTED);
        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          await fetchCurrentLocation();
        }
      } catch (err) {
        console.warn(err);
        setHasLocationPermission(false);
      }
    } else {
      setHasLocationPermission(true);
      await fetchCurrentLocation();
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
      // İlk açılışta mevcut konumu seçili konum olarak ayarla
      setSelectedLocation({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      });
    } catch (error) {
      console.error('Mevcut konum alınırken hata:', error);
      Alert.alert('Hata', 'Mevcut konum alınamadı, harita varsayılan konumda açılacak.');
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

    setFormData(prev => ({
      ...prev,
      location: selectedLocation
    }));
    Alert.alert('Başarılı', 'İhtiyaç konumu kaydedildi.');
  };

  const handleSubmit = async () => {
    if (!formData.contactName || !formData.phone || !formData.needCategory || !formData.urgencyLevel || !formData.district) {
      Alert.alert('Uyarı', 'Lütfen zorunlu alanları doldurun (İrtibat Kişisi, Telefon, İhtiyaç Kategorisi, Aciliyet, İlçe).');
      return;
    }

    if (!formData.location) {
      Alert.alert('Uyarı', 'Lütfen ihtiyaç konumunu seçin.');
      return;
    }

    try {
      setUploading(true);

      await firestore()
        .collection('need-requests')
        .doc(`${auth().currentUser.uid}_${Date.now()}`)
        .set({
          ...formData,
          requesterId: auth().currentUser.uid,
          requesterEmail: auth().currentUser.email,
          timestamp: new Date(),
          status: 'pending'
        });

      Alert.alert('Başarılı', 'İhtiyaç bildirimi başarıyla gönderildi.', [
        { text: 'Tamam', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      console.error('İhtiyaç bildirimi gönderilirken hata:', error);
      Alert.alert('Hata', 'İhtiyaç bildirimi gönderilirken bir hata oluştu.');
    } finally {
      setUploading(false);
    }
  };

  if (hasLocationPermission === null) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>İzin kontrolü yapılıyor...</Text>
      </View>
    );
  }

  if (hasLocationPermission === false) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionTitle}>Konum İzni Gerekli</Text>
        <Text style={styles.permissionText}>
          İhtiyaç konumunu belirlemek için konum iznine ihtiyacımız var.
        </Text>
        <TouchableOpacity style={styles.permissionButton} onPress={checkLocationPermission}>
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
              <Text style={styles.title}>İhtiyaç Bildirimi</Text>
            </View>

            <View style={styles.content}>
              <View style={styles.mapContainer}>
                <Text style={styles.mapTitle}>İhtiyaç Konumunu Seçin</Text>
                <MapView
                  style={styles.map}
                  initialRegion={{
                    latitude: currentLocation ? currentLocation.latitude : 38.4237, // İzmir merkezi
                    longitude: currentLocation ? currentLocation.longitude : 27.1428,
                    latitudeDelta: 0.01,
                    longitudeDelta: 0.01,
                  }}
                  onPress={handleMapPress}
                  showsUserLocation={!!currentLocation}
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
                    {formData.location ? 'Konumu Güncelle' : 'Konumu Kaydet'}
                  </Text>
                </TouchableOpacity>
              </View>

              <View style={styles.form}>
                <TextInput
                  style={styles.input}
                  placeholder="İrtibat Kişisi"
                  placeholderTextColor="lightgray"
                  value={formData.contactName}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, contactName: text }))}
                  autoCorrect={false}
                  spellCheck={false}
                  autoCapitalize="none"
                  keyboardType="default"
                  returnKeyType="next"
                  {...(Platform.OS === 'ios' && {
                    clearButtonMode: 'while-editing',
                  })}
                />

                <TextInput
                  style={styles.input}
                  placeholder="Telefon"
                  placeholderTextColor="lightgray"
                  value={formData.phone}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, phone: text }))}
                  keyboardType="phone-pad"
                  returnKeyType="next"
                  {...(Platform.OS === 'ios' && {
                    clearButtonMode: 'while-editing',
                  })}
                />

                <DropDownPicker
                  open={categoryOpen}
                  value={categoryValue}
                  items={categoryItems}
                  setOpen={setCategoryOpen}
                  setValue={setCategoryValue}
                  onChangeValue={(value) => {
                    setFormData(prev => ({ ...prev, needCategory: value }))
                  }}
                  style={styles.dropdown}
                  dropDownContainerStyle={styles.dropdownContainer}
                  placeholder="İhtiyaç Kategorisi Seçin"
                  listMode="SCROLLVIEW"
                  zIndex={4000}
                  searchable={true}
                  searchPlaceholder="Kategori Ara..."
                />

                <DropDownPicker
                  open={urgencyOpen}
                  value={urgencyValue}
                  items={urgencyItems}
                  setOpen={setUrgencyOpen}
                  setValue={setUrgencyValue}
                  onChangeValue={(value) => {
                    setFormData(prev => ({ ...prev, urgencyLevel: value }))
                  }}
                  style={styles.dropdown}
                  dropDownContainerStyle={styles.dropdownContainer}
                  placeholder="Aciliyet Düzeyi Seçin"
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
                  style={styles.input}
                  placeholder="Etkilenen Kişi Sayısı"
                  placeholderTextColor="lightgray"
                  value={formData.peopleCount}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, peopleCount: text }))}
                  keyboardType="numeric"
                  returnKeyType="next"
                />

                <TextInput
                  style={[styles.input, styles.textArea]}
                  placeholder="İhtiyaç Detayı"
                  placeholderTextColor="lightgray"
                  value={formData.description}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, description: text }))}
                  multiline
                  numberOfLines={4}
                  autoCorrect={false}
                  spellCheck={false}
                  autoCapitalize="none"
                  keyboardType="default"
                  returnKeyType="default"
                  blurOnSubmit={false}
                  {...(Platform.OS === 'ios' && {
                    clearButtonMode: 'while-editing',
                  })}
                />

                <TouchableOpacity
                  style={styles.submitButton}
                  onPress={handleSubmit}
                  disabled={uploading}
                >
                  {uploading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.submitButtonText}>İhtiyaç Bildir</Text>
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
  form: {
    gap: 15,
    marginTop: 20,
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
  submitButton: {
    backgroundColor: '#4CAF50',
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
    marginBottom: 20,
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

export default Request; 