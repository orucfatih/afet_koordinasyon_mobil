import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Dimensions,
  FlatList,
  Linking,
  StatusBar,
  Platform,
  SafeAreaView,
  Alert,
  PermissionsAndroid,
  AppState,
} from 'react-native';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import MapView, { Marker } from 'react-native-maps';
import Ionicons from 'react-native-vector-icons/Ionicons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ProfileScreen, SettingsScreen, Info, CustomButton, ChatScreen } from '../components/index';
import * as Animatable from 'react-native-animatable';
import Geolocation from 'react-native-geolocation-service';
import toplanmaAlanlari from '../../afet_toplanma_alanlari.json';
import LocationTrackingService from '../services/LocationTrackingService';
import database from '@react-native-firebase/database';
import auth from '@react-native-firebase/auth';
import {GOOGLE_CLOUD_API_KEY, KOERI_SCRAPER_URL} from '@env';

const { width } = Dimensions.get('window');

// Animation definitions
Animatable.initializeRegistryWithDefinitions({
  pulseBorder: {
    0: { scale: 1, borderWidth: 2, borderColor: '#fff', shadowOpacity: 0.2 },
    0.5: { scale: 1.05, borderWidth: 4, borderColor: '#ff4444', shadowOpacity: 0.4 },
    1: { scale: 1, borderWidth: 2, borderColor: '#fff', shadowOpacity: 0.2 },
  },
  modernPulse: {
    0: { scale: 1, opacity: 1 },
    0.5: { scale: 1.1, opacity: 0.9 },
    1: { scale: 1, opacity: 1 },
  },
  fadeInUpModern: {
    0: { translateY: 50, opacity: 0 },
    1: { translateY: 0, opacity: 1 },
  }
});

const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Dünya'nın yarıçapı (km)
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Kilometre cinsinden mesafe
};

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

const GOOGLE_PLACES_API_KEY = GOOGLE_CLOUD_API_KEY;

const EarthquakeScreen = ({ setCameraVisible, navigation }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [earthquakeData, setEarthquakeData] = useState([]);
  const [info, setInfo] = useState(false);
  const [assemblyAreas, setAssemblyAreas] = useState([]);
  const [nearbyHospitals, setNearbyHospitals] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('assembly'); // 'assembly' or 'hospitals'
 
   const [region, setRegion] = useState({
     latitude: 38.4192, // İzmir merkez
     longitude: 27.1287,
     latitudeDelta: 0.5,
     longitudeDelta: 0.5,
   });

  const TURKEY_BOUNDS = {
    minLatitude: 32.0,
    maxLatitude: 44.0,
    minLongitude: 22.0,
    maxLongitude: 48.0,
  };

  const handleRegionChange = (newRegion) => {
    const limitedRegion = {
      latitude: Math.max(Math.min(newRegion.latitude, TURKEY_BOUNDS.maxLatitude), TURKEY_BOUNDS.minLatitude),
      longitude: Math.max(Math.min(newRegion.longitude, TURKEY_BOUNDS.maxLongitude), TURKEY_BOUNDS.minLongitude),
      latitudeDelta: Math.max(Math.min(newRegion.latitudeDelta, 15), 0.001),
      longitudeDelta: Math.max(Math.min(newRegion.longitudeDelta, 15), 0.001),
    };
    setRegion(limitedRegion);
  };

  const fetchNearbyHospitals = async (latitude, longitude) => {
    try {
      const response = await axios.get(
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${latitude},${longitude}&radius=10000&type=hospital&key=${GOOGLE_PLACES_API_KEY}`
      );

      if (response.data.results) {
        const hospitals = response.data.results.map(hospital => ({
          id: hospital.place_id,
          name: hospital.name,
          address: hospital.vicinity,
          rating: hospital.rating || 'N/A',
          latitude: hospital.geometry.location.lat,
          longitude: hospital.geometry.location.lng,
          distance: calculateDistance(
            latitude,
            longitude,
            hospital.geometry.location.lat,
            hospital.geometry.location.lng
          ),
          isOpen: hospital.opening_hours ? hospital.opening_hours.open_now : null,
          photoReference: hospital.photos ? hospital.photos[0].photo_reference : null
        }))
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 4);

        setNearbyHospitals(hospitals);
      }
    } catch (error) {
      console.error('Hastane verisi alınırken hata:', error);
    }
  };

  useEffect(() => {
    const getUserLocationAndSortAreas = async () => {
      try {
        setIsLoading(true);
        
        // Android için konum izni kontrolü
        if (Platform.OS === 'android') {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
          );
          if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
            throw new Error('Konum izni reddedildi');
          }
        }

        // Konum alma
        const userLoc = await getCurrentLocation();
        if (userLoc.latitude && userLoc.longitude) {
          setUserLocation(userLoc);
          console.log('Kullanıcı konumu alındı:', userLoc);

          // JSON dosyasından toplanma alanlarını al ve mesafeye göre sırala
          const areasWithDistance = toplanmaAlanlari
            .filter(area => {
              const hasValidCoords = area.ENLEM && area.BOYLAM && 
                !isNaN(parseFloat(area.ENLEM)) && !isNaN(parseFloat(area.BOYLAM));
              if (!hasValidCoords) {
                console.log('Geçersiz koordinat:', area);
              }
              return hasValidCoords;
            })
            .map(area => ({
              id: area.ACIKLAMA || Math.random().toString(),
              name: area.ADI || 'İsimsiz Toplanma Alanı',
              district: area.ILCE || '',
              neighborhood: area.MAHALLE || '',
              street: area.YOL || '',
              latitude: parseFloat(area.ENLEM),
              longitude: parseFloat(area.BOYLAM),
              distance: calculateDistance(
                userLoc.latitude,
                userLoc.longitude,
                parseFloat(area.ENLEM),
                parseFloat(area.BOYLAM)
              )
            }))
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 4);

          console.log('En yakın 4 toplanma alanı:', areasWithDistance);
          setAssemblyAreas(areasWithDistance);

          // Hastaneleri de al
          await fetchNearbyHospitals(userLoc.latitude, userLoc.longitude);
          
          setRegion({
            latitude: userLoc.latitude,
            longitude: userLoc.longitude,
            latitudeDelta: 0.05,
            longitudeDelta: 0.05,
          });
        } else {
          console.log('Konum alınamadı');
          Alert.alert('Hata', 'Konum alınamadı');
          // Varsayılan toplanma alanlarını göster
          const defaultAreas = toplanmaAlanlari
            .filter(area => area.ENLEM && area.BOYLAM)
            .slice(0, 4)
            .map(area => ({
              id: area.ACIKLAMA || Math.random().toString(),
              name: area.ADI || 'İsimsiz Toplanma Alanı',
              district: area.ILCE || '',
              neighborhood: area.MAHALLE || '',
              street: area.YOL || '',
              latitude: parseFloat(area.ENLEM),
              longitude: parseFloat(area.BOYLAM),
              distance: null
            }));
          setAssemblyAreas(defaultAreas);
        }
      } catch (error) {
        console.log('Toplanma alanları yüklenirken hata:', error);
        Alert.alert('Hata', 'Toplanma alanları yüklenirken bir hata oluştu.');
      } finally {
        setIsLoading(false);
      }
    };

    getUserLocationAndSortAreas();
  }, []);

  useEffect(() => {
    const fetchEarthquakeData = async () => {
      try {
        console.log('Veri çekme başladı...');
        const response = await axios.get(KOERI_SCRAPER_URL);
        console.log('Tam yanıt:', JSON.stringify(response.data, null, 2));

        if (!response.data || !Array.isArray(response.data.data)) {
          console.error('Beklenen veri formatı alınamadı:', response.data);
          setEarthquakeData([]);
          return;
        }

        const data = response.data.data
          .map(item => {
            if (!item.Date || !item.Magnitude || !item.Place) {
              console.warn('Eksik veri:', item);
              return null;
            }
            const dateParts = item.Date.split(' ');
            return {
              id: `${item.Date}-${item.Magnitude}`,
              magnitude: parseFloat(item.Magnitude) || 0,
              location: item.Place || 'Bilinmeyen Yer',
              time: dateParts[1] || 'Bilinmeyen Saat',
              date: dateParts[0] || 'Bilinmeyen Tarih',
              lat: parseFloat(item.Lat) || null,
              lon: parseFloat(item.Lon) || null,
            };
          })
          .filter(item => item !== null && item.magnitude >= 3.0)
          .slice(0, 10);

        console.log('İşlenmiş veri:', data);
        setEarthquakeData(data);
      } catch (error) {
        console.error('Hata:', error.message);
        console.error('Hata detayları:', error);
        setEarthquakeData([]);
      }
    };

    fetchEarthquakeData();
  }, []);

  const handleNavigateToAssemblyArea = (latitude, longitude) => {
    setRegion({
      latitude,
      longitude,
      latitudeDelta: 0.01,
      longitudeDelta: 0.01,
    });
  };

  const handleScroll = (event) => {
    const scrollX = event.nativeEvent.contentOffset.x;
    const activeIndex = Math.round(scrollX / width);
    setCurrentIndex(activeIndex);
  };

  const renderEarthquakeCard = ({ item }) => {
    const getMagnitudeColor = (magnitude) => {
      if (magnitude < 4) return '#4CAF50';
      if (magnitude < 6) return '#FFC107';
      return '#D32F2F';
    };

    const getFontSizeByLocation = (location) => {
      const length = location.length;
      if (length > 30) return 14;
      if (length > 20) return 16;
      if (length > 10) return 18;
      return 20;
    };

    const getFontSize = (circleSize) => Math.floor(circleSize * 0.2);

    const circleSize = 120;

    return (
      <View style={styles.earthquakeCard}>
        <View style={styles.magnitudeWrapper}>
          <View style={[styles.circle, { backgroundColor: getMagnitudeColor(item.magnitude), width: circleSize, height: circleSize }]}>
            <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.3)', width: circleSize - 20, height: circleSize - 20 }]}>
              <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.5)', width: circleSize - 40, height: circleSize - 40 }]}>
                <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.7)', width: circleSize - 60, height: circleSize - 60 }]}>
                  <Text style={[styles.magnitudeText, { fontSize: getFontSize(circleSize) }]}>{item.magnitude}</Text>
                </View>
              </View>
            </View>
          </View>
          <View style={styles.seismicWaves}>
            <View style={styles.seismicGraph}>
              {/* Modern sismik dalga */}
              <View style={styles.waveContainer}>
                <View style={[styles.modernWave, { height: 8, marginLeft: 0 }]} />
                <View style={[styles.modernWave, { height: 16, marginLeft: 4 }]} />
                <View style={[styles.modernWave, { height: 24, marginLeft: 4 }]} />
                <View style={[styles.modernWave, { height: 32, marginLeft: 4 }]} />
                <View style={[styles.modernWave, { height: 20, marginLeft: 4 }]} />
                <View style={[styles.modernWave, { height: 12, marginLeft: 4 }]} />
                <View style={[styles.modernWave, { height: 18, marginLeft: 4 }]} />
                <View style={[styles.modernWave, { height: 10, marginLeft: 4 }]} />
              </View>
            </View>
          </View>
        </View>
        <View style={styles.earthquakeInfo}>
          <Text style={[styles.earthquakeLocation, { fontSize: getFontSizeByLocation(item.location) }]}>{item.location}</Text>
          <Text style={styles.earthquakeTime}>{item.time}</Text>
          <Text style={styles.earthquakeDate}>{item.date}</Text>
        </View>
      </View>
    );
  };

  const handleFamilyNotification = async () => {
    try {
      const familyMessage = await AsyncStorage.getItem('familyMessage');
      const selectedContacts = JSON.parse(await AsyncStorage.getItem('selectedContacts') || '[]');
      
      if (!familyMessage || selectedContacts.length === 0) {
        Alert.alert(
          'Uyarı',
          'Lütfen önce ayarlar kısmından bildirim mesajınızı ve kişilerinizi ekleyin.'
        );
        navigation.navigate('Settings');
        return;
      }

      // Her bir kişi için SMS gönderme
      selectedContacts.forEach(contact => {
        const phoneNumber = contact.phoneNumber.replace(/\D/g, ''); // Sadece rakamları al
        const encodedMessage = encodeURIComponent(familyMessage);
        const url = Platform.select({
          ios: `sms:${phoneNumber}&body=${encodedMessage}`,
          android: `sms:${phoneNumber}?body=${encodedMessage}`
        });

        Linking.openURL(url).catch(err => {
          console.error('SMS gönderme hatası:', err);
          Alert.alert('Hata', 'SMS gönderilemedi. Lütfen tekrar deneyin.');
        });
      });

      Alert.alert('Başarılı', 'SMS gönderme işlemi başlatıldı');
    } catch (error) {
      console.error('SMS gönderme hatası:', error);
      Alert.alert(
        'Hata',
        'SMS gönderilemedi. Lütfen tekrar deneyin.'
      );
    }
  };

  if (info) {
    return <Info setInfo={setInfo} />;
  }

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}/>

      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <TouchableOpacity onPress={() => navigation.navigate('HomePage2')}>
            <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.whistleButton} onPress={() => navigation.navigate('Horn')}>
            <Ionicons name="megaphone" size={25} color="white" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.info} onPress={() => setInfo(true)}>
            <Ionicons name="information-circle" size={25} color="white" />
          </TouchableOpacity>
        </View>

        <ScrollView 
         style={styles.container}
         contentContainerStyle={styles.scrollContent}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Son Depremler</Text>
            <TouchableOpacity onPress={() => navigation.navigate('ViewAll')}>
              <Text style={styles.viewAll}>Tümünü Gör</Text>
            </TouchableOpacity>
          </View>

          <FlatList
            data={earthquakeData.slice(0, 10)}
            renderItem={renderEarthquakeCard}
            keyExtractor={(item) => item.id}
            horizontal
            pagingEnabled
            showsHorizontalScrollIndicator={false}
            onScroll={handleScroll}
            style={styles.slider}
          />

          <View style={styles.pagination}>
            {earthquakeData.map((_, index) => (
              <View key={index} style={[styles.dot, currentIndex === index && styles.activeDot]} />
            ))}
          </View>

          
          <View style={styles.warning}>
            <Animatable.View
              animation="pulseBorder"
              iterationCount="infinite"
              duration={2000}
              style={styles.bigButtonWrapper}>

              <TouchableOpacity 
                style={styles.bigButton} 
                onPress={() => navigation.navigate('Camera')}>

                <Text style={styles.bigButtonText}>AFET BİLDİR</Text>
                <Ionicons name="warning" size={30} color="white" style={styles.camera} />
              </TouchableOpacity>
            </Animatable.View>

            {/* Modern Enkaz Altındayım Butonu */}
            <TouchableOpacity 
              style={styles.modernEnkazButton}
              onPress={() => navigation.navigate('UnderDebris')}
            >
              <View style={styles.modernButtonContent}>
                <View style={styles.modernButtonIcon}>
                  <Ionicons name="alert-circle" size={28} color="white" />
                </View>
                <View style={styles.modernButtonTextContainer}>
                  <Text style={styles.modernButtonTitle}>ENKAZ ALTINDAYIM</Text>
                  <Text style={styles.modernButtonSubtitle}>Acil yardım çağır</Text>
                </View>
              </View>
              <View style={styles.modernButtonGlow} />
            </TouchableOpacity>
          </View>


          <View style={styles.buttonContainer}>
            <TouchableOpacity 
              style={styles.modernSmallButton}
              onPress={handleFamilyNotification}
            >
              <View style={styles.smallButtonGradient}>
                <View style={styles.smallButtonIconWrapper}>
                  <Ionicons name="notifications" size={22} color="#fff" />
                </View>
                <Text style={styles.modernSmallButtonText}>Ailene Bildir</Text>
              </View>
            </TouchableOpacity>

            <TouchableOpacity
             style={styles.modernSmallButton}
             onPress={() => navigation.navigate('Missing')}>
              <View style={styles.smallButtonGradient}>
                <View style={styles.smallButtonIconWrapper}>
                  <Ionicons name="person" size={22} color="#fff" />
                </View>
                <Text style={styles.modernSmallButtonText}>Kayıp İhbar</Text>
              </View>
           </TouchableOpacity>

            <TouchableOpacity 
              style={styles.modernSmallButton} 
              onPress={() => navigation.navigate('İnformation')}>
              <View style={styles.smallButtonGradient}>
                <View style={styles.smallButtonIconWrapper}>
                  <Ionicons name="information-circle" size={22} color="#fff" />
                </View>
                <Text style={styles.modernSmallButtonText}>Deprem Bilgilendirme</Text>
              </View>
            </TouchableOpacity>
          </View>

          <TouchableOpacity 
            style={styles.modernSmallButton} 
            onPress={() => navigation.navigate('Report')}>
            <View style={styles.smallButtonGradient}>
              <View style={styles.smallButtonIconWrapper}>
                <Ionicons name="document-text" size={22} color="#fff" />
              </View>
              <Text style={styles.modernSmallButtonText}>Rapor İşlemleri</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.modernSmallButton} 
            onPress={() => navigation.navigate('Tasks')}>
            <View style={styles.smallButtonGradient}>
              <View style={styles.smallButtonIconWrapper}>
                <Ionicons name="list" size={22} color="#fff" />
              </View>
              <Text style={styles.modernSmallButtonText}>Görevler</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.modernSmallButton} 
            onPress={() => navigation.navigate('Request')}>
            <View style={styles.smallButtonGradient}>
              <View style={styles.smallButtonIconWrapper}>
                <Ionicons name="alert-circle" size={22} color="#fff" />
              </View>
              <Text style={styles.modernSmallButtonText}>İhtiyaç Bildir</Text>
            </View>
          </TouchableOpacity>

          <MapView
            style={styles.map}
            region={region}
            onRegionChangeComplete={handleRegionChange}
            zoomEnabled={true}
            zoomControlEnabled={true}
            showsUserLocation={true}>

            {assemblyAreas.map((area, index) => (
              <Marker
                key={index}
                coordinate={{
                  latitude: parseFloat(area.latitude),
                  longitude: parseFloat(area.longitude),
                }}
                title={area.name}
                description={`${area.district} - ${area.neighborhood}\nUzaklık: ${area.distance.toFixed(2)} km`}
                onPress={() => {
                  const scheme = Platform.select({ ios: 'maps:0,0?q=', android: 'geo:0,0?q=' });
                  const latLng = `${area.latitude},${area.longitude}`;
                  const label = area.name;
                  const url = Platform.select({
                    ios: `${scheme}${label}@${latLng}`,
                    android: `${scheme}${latLng}(${label})`
                  });
                  //Linking.openURL(url);
                }}
              />
            ))}
            {nearbyHospitals.map((hospital, index) => (
              <Marker
                key={`hospital-${index}`}
                coordinate={{
                  latitude: hospital.latitude,
                  longitude: hospital.longitude,
                }}
                title={hospital.name}
                description={`${hospital.address}\nUzaklık: ${hospital.distance.toFixed(2)} km`}
                pinColor="green"
              />
            ))}
            {userLocation && (
              <Marker
                coordinate={userLocation}
                title="Konumunuz"
                pinColor="blue"
              />
            )}
          </MapView>

          {/* Tab Navigation */}
          <View style={styles.tabContainer}>
            <TouchableOpacity 
              style={[styles.tabButton, activeTab === 'assembly' && styles.activeTabButton]}
              onPress={() => setActiveTab('assembly')}
            >
              <Ionicons 
                name="people" 
                size={20} 
                color={activeTab === 'assembly' ? '#fff' : '#666'} 
                style={styles.tabIcon}
              />
              <Text style={[styles.tabText, activeTab === 'assembly' && styles.activeTabText]}>
                Toplanma Alanları
              </Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.tabButton, activeTab === 'hospitals' && styles.activeTabButton]}
              onPress={() => setActiveTab('hospitals')}
            >
              <Ionicons 
                name="medical" 
                size={20} 
                color={activeTab === 'hospitals' ? '#fff' : '#666'} 
                style={styles.tabIcon}
              />
              <Text style={[styles.tabText, activeTab === 'hospitals' && styles.activeTabText]}>
                En Yakın Hastaneler
              </Text>
            </TouchableOpacity>
          </View>

          {/* Content based on active tab */}
          {activeTab === 'assembly' && (
            <View style={styles.assemblyButtonsContainer}>
              {isLoading ? (
                <Text style={styles.loadingText}>Toplanma alanları yükleniyor...</Text>
              ) : (
               assemblyAreas.map((area) => (
                <TouchableOpacity
                  key={area.id}
                  style={styles.assemblyButton}
                  onPress={() => handleNavigateToAssemblyArea(area.latitude, area.longitude)}
                >
                  <View style={styles.assemblyButtonContent}>
                    <View style={styles.assemblyIconWrapper}>
                      <Ionicons name="people" size={30} color="white" />
                    </View>
                    <View style={styles.assemblyInfo}>
                      <Text style={styles.assemblyButtonText}>{area.name}</Text>
                      <Text style={styles.assemblyDetails}>{area.district} - {area.neighborhood}</Text>
                      <Text style={styles.assemblyDetails}>{area.street}</Text>
                        {area.distance && (
                          <Text style={styles.assemblyDetails}>
                            Mesafe: {area.distance.toFixed(2)} km
                          </Text>
                        )}
                    </View>
                  </View>
                </TouchableOpacity>
              ))
            )}
            </View>
          )}

          {activeTab === 'hospitals' && (
            <View style={styles.assemblyButtonsContainer}>
              {isLoading ? (
                <Text style={styles.loadingText}>Hastaneler yükleniyor...</Text>
              ) : nearbyHospitals.length > 0 ? (
                nearbyHospitals.map((hospital) => (
                  <TouchableOpacity
                    key={hospital.id}
                    style={styles.assemblyButton}
                    onPress={() => handleNavigateToAssemblyArea(hospital.latitude, hospital.longitude)}
                  >
                    <View style={styles.assemblyButtonContent}>
                      <View style={[styles.assemblyIconWrapper, { backgroundColor: '#D32F2F' }]}>
                        <Ionicons name="medical" size={30} color="white" />
                      </View>
                      <View style={styles.assemblyInfo}>
                        <Text style={styles.assemblyButtonText}>{hospital.name}</Text>
                        <Text style={styles.assemblyDetails}>{hospital.address}</Text>
                        <View style={styles.hospitalDetailsRow}>
                          {hospital.rating !== 'N/A' && (
                            <Text style={styles.hospitalRating}>
                              ⭐ {hospital.rating}
                            </Text>
                          )}
                          {hospital.isOpen !== null && (
                            <Text style={[styles.hospitalStatus, { color: hospital.isOpen ? '#4CAF50' : '#F44336' }]}>
                              {hospital.isOpen ? '🟢 Açık' : '🔴 Kapalı'}
                            </Text>
                          )}
                        </View>
                        <Text style={styles.assemblyDetails}>
                          Mesafe: {hospital.distance.toFixed(2)} km
                        </Text>
                      </View>
                    </View>
                  </TouchableOpacity>
                ))
              ) : (
                <Text style={styles.loadingText}>Yakında hastane bulunamadı</Text>
              )}
            </View>
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
};

const HomePage2 = ({ navigation }) => {
  const [currentTab, setCurrentTab] = useState('Earthquake');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [cameraVisible, setCameraVisible] = useState(false);

  const insets = useSafeAreaInsets();

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const userToken = await AsyncStorage.getItem('staffToken');
        setIsAuthenticated(!!userToken);
        
        // Eğer kullanıcı oturum açmışsa konum takibini başlat
        if (userToken) {
          console.log('HomePage2 - Kullanıcı oturum açmış, konum takibi başlatılıyor...');
          const locationService = LocationTrackingService.getInstance();
          await locationService.startLocationTracking();
        }
      } catch (error) {
        console.error('Error checking authentication', error);
      }
    };
    checkAuthentication();
  }, []);

  // App state değişikliklerini dinle (background/foreground)
  useEffect(() => {
    const handleAppStateChange = async (nextAppState) => {
      const locationService = LocationTrackingService.getInstance();
      
      if (nextAppState === 'active') {
        // App foreground'a geldiğinde konum takibini yeniden başlat
        console.log('App foreground - Konum takibi kontrol ediliyor...');
        if (isAuthenticated && !locationService.isTrackingActive()) {
          console.log('Konum takibi yeniden başlatılıyor...');
          await locationService.startLocationTracking();
        }
      } else if (nextAppState === 'background') {
        // App background'a gittiğinde konum takibi devam etsin
        console.log('App background - Konum takibi devam ediyor...');
        // Battery tasarrufu için isteğe bağlı olarak durdurabilirsin:
        // locationService.stopLocationTracking();
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    
    return () => {
      subscription?.remove();
    };
  }, [isAuthenticated]);

  // Component unmount edildiğinde konum takibini durdur
  useEffect(() => {
    return () => {
      // Sadece app tamamen kapanırken durduralım, tab değişiminde değil
      console.log('HomePage2 component unmounting...');
      // LocationTrackingService.getInstance().stopLocationTracking();
    };
  }, []);

  const renderScreen = () => {
    switch (currentTab) {
      case 'Earthquake':
        return <EarthquakeScreen navigation={navigation} setCameraVisible={setCameraVisible} />;
      case 'Profile':
        return <ProfileScreen />;
      case 'Settings':
        return <SettingsScreen />;
      case 'Chat':
        return <ChatScreen />;
      default:
        return <EarthquakeScreen />;
    }
  };

  const handleEmergencyCall = () => {
    Linking.openURL('tel:112');
  };

  if (!isAuthenticated) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Yükleniyor...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, {marginBottom: insets.bottom}]}>
      {!cameraVisible && (
        <>
          <View style={styles.screenContainer}>{renderScreen()}</View>
          <Animatable.View 
            animation="fadeInUpModern" 
            duration={800}
            style={styles.tabBar}
          >
            <TouchableOpacity
              onPress={() => setCurrentTab('Earthquake')}
              style={[styles.tab, currentTab === 'Earthquake' && styles.activeTab]}
            >
              <Animatable.View 
                animation={currentTab === 'Earthquake' ? 'fadeIn' : null} 
                duration={300}
                style={[styles.tabIconWrapper, currentTab === 'Earthquake' && styles.activeTabIconWrapper]}
              >
                <Ionicons 
                  name={currentTab === 'Earthquake' ? 'home' : 'home-outline'} 
                  size={24} 
                  color={currentTab === 'Earthquake' ? '#fff' : '#bbb'} 
                />
              </Animatable.View>
              <Text style={[styles.tabLabel, currentTab === 'Earthquake' && styles.activeTabLabel]}>Ana Sayfa</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              onPress={() => setCurrentTab('Profile')}
              style={[styles.tab, currentTab === 'Profile' && styles.activeTab]}
            >
              <Animatable.View 
                animation={currentTab === 'Profile' ? 'fadeIn' : null} 
                duration={300}
                style={[styles.tabIconWrapper, currentTab === 'Profile' && styles.activeTabIconWrapper]}
              >
                <Ionicons 
                  name={currentTab === 'Profile' ? 'person' : 'person-outline'} 
                  size={24} 
                  color={currentTab === 'Profile' ? '#fff' : '#bbb'} 
                />
              </Animatable.View>
              <Text style={[styles.tabLabel, currentTab === 'Profile' && styles.activeTabLabel]}>Profil</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              onPress={() => setCurrentTab('Settings')}
              style={[styles.tab, currentTab === 'Settings' && styles.activeTab]}
            >
              <Animatable.View 
                animation={currentTab === 'Settings' ? 'fadeIn' : null} 
                duration={300}
                style={[styles.tabIconWrapper, currentTab === 'Settings' && styles.activeTabIconWrapper]}
              >
                <Ionicons 
                  name={currentTab === 'Settings' ? 'settings' : 'settings-outline'} 
                  size={24} 
                  color={currentTab === 'Settings' ? '#fff' : '#bbb'} 
                />
              </Animatable.View>
              <Text style={[styles.tabLabel, currentTab === 'Settings' && styles.activeTabLabel]}>Ayarlar</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => setCurrentTab('Chat')}
              style={[styles.tab, currentTab === 'Chat' && styles.activeTab]}
            >
              <Animatable.View 
                animation={currentTab === 'Chat' ? 'fadeIn' : null} 
                duration={300}
                style={[styles.tabIconWrapper, currentTab === 'Chat' && styles.activeTabIconWrapper]}
              >
                <Ionicons 
                  name={currentTab === 'Chat' ? 'chatbubbles' : 'chatbubbles-outline'} 
                  size={24} 
                  color={currentTab === 'Chat' ? '#fff' : '#bbb'} 
                />
              </Animatable.View>
              <Text style={[styles.tabLabel, currentTab === 'Chat' && styles.activeTabLabel]}>Sohbet</Text>
            </TouchableOpacity>

          </Animatable.View>
          {currentTab !== 'Chat' && (
            <TouchableOpacity 
              style={styles.emergencyCallButton} 
              onPress={handleEmergencyCall}
            >
              <Ionicons name="call" size={30} color="white" />
            </TouchableOpacity>
          )}
        </>
      )}
    </View>
  );
};

export default HomePage2;

export const styles = StyleSheet.create({
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
    backgroundColor: '#f8f9fa',
  },
  screenContainer: {
    flex: 1,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
    paddingVertical: 25,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    zIndex: 10,
    position: 'relative',
    minHeight: 75,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: width / 2 - 25,
    top: -25,
  },
  whistleButton: {
    position: 'absolute',
    left: 20,
    top: 20,
  },
  info: {
    position: 'absolute',
    right: 20,
    top: 20,
  },
  scrollContent: {
    paddingTop: 20,
    paddingBottom: 100,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
    paddingHorizontal: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  viewAll: {
    color: '#D32F2F',
    fontWeight: 'bold',
  },
  camera: {
    marginTop: 15,
  },
  map: {
    height: 250,
    marginVertical: 20,
    marginHorizontal: 15,
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 5,
  },
  slider: { marginTop: 10 },
  pagination: { 
    flexDirection: 'row', 
    justifyContent: 'center', 
    marginTop: 10 
  },
  dot: { 
    height: 10, 
    width: 10, 
    borderRadius: 5, 
    backgroundColor: '#CCC', 
    marginHorizontal: 5 
  },
  activeDot: { 
    backgroundColor: '#007AFF' 
  },
  earthquakeCard: {
    width: width,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'white',
    marginVertical: 20,
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  magnitudeWrapper: {
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 60,
  },
  circle: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 5,
    borderRadius: 100,
    position: 'absolute',
  },
  magnitudeText: {
    fontSize: 28,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'absolute',
    fontWeight: 'bold',
    color: '#000',
  },
  earthquakeInfo: {
    alignItems: 'center',
  },
  earthquakeLocation: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  earthquakeTime: {
    fontSize: 16,
    color: '#757575',
  },
  earthquakeDate: {
    fontSize: 16,
    color: '#757575',
  },
  seismicWaves: {
    top: '70%',
    width: '100%',
    height: 40,
    right: '14%',
    alignItems: 'center', 
    justifyContent: 'center',
    flexDirection: 'row',
  },
  seismicGraph: {
    width: 150,
    height: 40,
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
  },
  waveContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
    height: 32,
  },
  modernWave: {
    width: 3,
    backgroundColor: '#666',
    borderRadius: 1.5,
    opacity: 0.8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1,
    elevation: 1,
  },
  assemblyButtonsContainer: {
    flexDirection: 'column',
    paddingHorizontal: 16,
    marginVertical: 16,
  },
  assemblyButton: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  assemblyButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  assemblyIconWrapper: {
    backgroundColor: '#D32F2F',
    padding: 12,
    borderRadius: 10,
    marginRight: 15,
  },
  assemblyButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  assemblyDetails: {
    fontSize: 14,
    color: '#555',
    marginTop: 2,
  },
  bigButtonWrapper: {
    alignSelf: 'center',
    marginVertical: 20,
    height: 155,
    width: 155,
    borderRadius: 100,
    overflow: 'visible',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 10,
  },
  bigButton: {
    width: 150,
    height: 150,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 75,
    borderWidth: 3,
    borderColor: '#fff',
  },
  bigButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 5,
  },
  modernEnkazButton: {
    backgroundColor: '#D32F2F',
    borderRadius: 20,
    marginHorizontal: 20,
    marginTop: 20,
    width: '80%',
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    position: 'relative',
  },
  modernButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingVertical: 18,
  },
  modernButtonIcon: {
    marginRight: 15,
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 8,
    borderRadius: 12,
  },
  modernButtonTextContainer: {
    flex: 1,
  },
  modernButtonTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    letterSpacing: 0.5,
  },
  modernButtonSubtitle: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 2,
  },
  modernButtonGlow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 2,
    backgroundColor: 'rgba(255,255,255,0.4)',
  },
  warning: {
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    marginBottom: 20,
    gap: 8,
  },
  modernSmallButton: {
    flex: 1,
    borderRadius: 18,
    overflow: 'hidden',
    elevation: 6,
    height: 80,
    shadowColor: '#2196F3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    marginHorizontal: 8,
    marginBottom: 15,
  },
  smallButtonGradient: {
    backgroundColor: '#2196F3',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 6,
    position: 'relative',
    height: '100%',
  },
  smallButtonIconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 6,
    borderRadius: 10,
    marginBottom: 4,
  },
  modernSmallButtonText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    textAlign: 'center',
    lineHeight: 11,
    letterSpacing: 0.3,
    flexWrap: 'wrap',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#1a1a1a',
    paddingVertical: 16,
    paddingHorizontal: 8,
    borderTopWidth: 0,
    elevation: 25,
    borderTopLeftRadius: 35,
    borderTopRightRadius: 35,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -10 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    marginHorizontal: 3,
    height: 90,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  tab: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 25,
    minWidth: 75,
    minHeight: 55,
    position: 'relative',
  },
  activeTab: {
    backgroundColor: '#D32F2F',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 25,
    elevation: 15,
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.6,
    shadowRadius: 12,
  },
  tabIconWrapper: {
    marginBottom: 4,
    padding: 6,
    borderRadius: 18,
    backgroundColor: 'transparent',
  },
  activeTabIconWrapper: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  tabLabel: {
    color: '#bbb',
    fontSize: 10,
    fontWeight: '600',
    marginTop: 2,
  },
  activeTabLabel: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  emergencyCallButton: {
    position: 'absolute',
    bottom: 110,
    right: 20,
    width: 75,
    height: 75,
    backgroundColor: '#D32F2F',
    borderRadius: 37.5,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 15,
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.6,
    shadowRadius: 12,
    zIndex: 1000,
    borderWidth: 4,
    borderColor: '#fff',
  },
  loadingText: {
    textAlign: 'center',
    padding: 20,
    color: '#666',
  },
  assemblyInfo: {
    flex: 1,
    marginLeft: 10,
  },
  tabContainer: {
    flexDirection: 'row',
    marginHorizontal: 15,
    marginTop: 20,
    marginBottom: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 15,
    padding: 4,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 12,
  },
  activeTabButton: {
    backgroundColor: '#D32F2F',
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  tabIcon: {
    marginRight: 6,
  },
  tabText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  activeTabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  hospitalDetailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
    gap: 10,
  },
  hospitalRating: {
    fontSize: 12,
    color: '#FF9800',
    fontWeight: 'bold',
  },
  hospitalStatus: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
  },
});