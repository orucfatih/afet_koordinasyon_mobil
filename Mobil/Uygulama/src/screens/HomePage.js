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
  Alert,
  Platform,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { Svg, Path } from 'react-native-svg';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faHome, faUser, faCog, faCamera, faPhone, faExclamationTriangle, faUsers, faInfoCircle, faBullhorn, faBell, faExclamationCircle, faMapMarkerAlt, faUserAlt } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ProfileScreen, SettingsScreen, Info} from '../components';
import * as Animatable from 'react-native-animatable';
import * as Location from 'expo-location';
import SendSMS from 'react-native-sms';
import toplanmaAlanlari from './afet_toplanma_alanlari.json';

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

const EarthquakeScreen = ({ setCameraVisible, navigation }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [earthquakeData, setEarthquakeData] = useState([]);
  const [info, setInfo] = useState(false);
  const [assemblyAreas, setAssemblyAreas] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

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
      latitudeDelta: Math.max(Math.min(newRegion.latitudeDelta, 15), 0.1),
      longitudeDelta: Math.max(Math.min(newRegion.longitudeDelta, 15), 0.1),
    };
    setRegion(limitedRegion);
  };

  useEffect(() => {
    const getUserLocationAndSortAreas = async () => {
      try {
        setIsLoading(true);
        let { status } = await Location.requestForegroundPermissionsAsync();
        
        if (status === 'granted') {
          let location = await Location.getCurrentPositionAsync({});
          setUserLocation(location.coords);
          console.log('Kullanıcı konumu alındı:', location.coords);

          // JSON dosyasından toplanma alanlarını al ve mesafeye göre sırala
          const areasWithDistance = toplanmaAlanlari
            .filter(area => {
              // Geçerli koordinatları olan alanları filtrele
              const hasValidCoords = area.ENLEM && area.BOYLAM && 
                !isNaN(parseFloat(area.ENLEM)) && !isNaN(parseFloat(area.BOYLAM));
              if (!hasValidCoords) {
                console.log('Geçersiz koordinat:', area);
              }
              return hasValidCoords;
            })
            .map(area => {
              const distance = calculateDistance(
                location.coords.latitude,
                location.coords.longitude,
                parseFloat(area.ENLEM),
                parseFloat(area.BOYLAM)
              );
              return {
                id: area.ACIKLAMA || Math.random().toString(),
                name: area.ADI || 'İsimsiz Toplanma Alanı',
                district: area.ILCE || '',
                neighborhood: area.MAHALLE || '',
                street: area.YOL || '',
                latitude: parseFloat(area.ENLEM),
                longitude: parseFloat(area.BOYLAM),
                distance: distance
              };
            })
            .sort((a, b) => a.distance - b.distance) // Mesafeye göre sırala
            .slice(0, 4); // En yakın 4 alanı al

          console.log('En yakın 4 toplanma alanı:', areasWithDistance);
          setAssemblyAreas(areasWithDistance);
          
          // Kullanıcının konumuna göre haritayı güncelle
          setRegion({
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            latitudeDelta: 0.05,
            longitudeDelta: 0.05,
          });
        } else {
          console.log('Konum izni verilmedi');
          Alert.alert(
            'Konum İzni Gerekli',
            'En yakın toplanma alanlarını görebilmek için konum izni vermeniz gerekmektedir.',
            [
              { text: 'Tamam', onPress: () => console.log('Konum izni reddedildi') }
            ]
          );
          // Konum izni verilmediğinde varsayılan toplanma alanlarını göster
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
        console.error('Konum veya toplanma alanları yüklenirken hata:', error);
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
        const response = await axios.get('https://us-central1-afad-proje.cloudfunctions.net/scrapeKoeriEarthquakes');
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
          .filter(item => item !== null)
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
        </View>
        <View style={styles.earthquakeInfo}>
          <Text style={[styles.earthquakeLocation, { fontSize: getFontSizeByLocation(item.location) }]}>{item.location}</Text>
          <Text style={styles.earthquakeTime}>{item.time}</Text>
          <Text style={styles.earthquakeDate}>{item.date}</Text>
        </View>
        <Svg style={styles.dalga} height="30" width="100" viewBox="0 0 100 30">
          <Path
            d="M 0,20 L 10,5 L 20,15 L 30,10 L 40,20 L 50,10 L 60,25 L 70,15 L 80,20 L 90,10 L 100,30 L 110,15 L 120,20"
            stroke="#808080"
            strokeWidth="3"
            fill="none"
          />
        </Svg>
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

      const phoneNumbers = selectedContacts.map(contact => contact.phoneNumber);

      SendSMS.send({
        body: familyMessage,
        recipients: phoneNumbers,
        successTypes: ['sent', 'queued'],
        allowAndroidSendWithoutReadPermission: true,
      }, (completed, cancelled, error) => {
        if (completed) {
          Alert.alert('Başarılı', 'SMS başarıyla gönderildi');
        } else if (cancelled) {
          Alert.alert('İptal', 'SMS gönderimi iptal edildi');
        } else if (error) {
          Alert.alert('Hata', 'SMS gönderilemedi');
        }
      });

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
    <View style={styles.container}>
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => navigation.navigate('HomePage')}>
          <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
        </TouchableOpacity>
        <TouchableOpacity style={styles.whistleButton} onPress={() => navigation.navigate('Horn')}>
          <FontAwesomeIcon icon={faBullhorn} size={25} color="white" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.info} onPress={() => setInfo(true)}>
          <FontAwesomeIcon icon={faInfoCircle} size={25} color="white" />
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.container}
        contentContainerStyle={styles.scrollContent}
      >
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

        <Animatable.View
          animation="pulseBorder"
          iterationCount="infinite"
          duration={2000}
          style={styles.bigButtonWrapper}
        >
          <TouchableOpacity 
            style={styles.bigButton} 
            onPress={() => navigation.navigate('Camera')}
          >
            <Text style={styles.bigButtonText}>ENKAZ BİLDİR</Text>
            <FontAwesomeIcon icon={faExclamationTriangle} size={30} color="white" style={styles.camera} />
          </TouchableOpacity>
        </Animatable.View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={styles.smallButton}
            onPress={handleFamilyNotification}
          >
            <FontAwesomeIcon icon={faBell} size={24} color="#fff" />
            <Text style={styles.smallButtonText}>Ailene Bildir</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.smallButton}
            onPress={() => navigation.navigate('Missing')}
          >
            <FontAwesomeIcon icon={faUserAlt} size={24} color="#fff" />
            <Text style={styles.smallButtonText}>Kayıp İhbar</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.smallButton} 
            onPress={() => navigation.navigate('Missing')}
          >
            <FontAwesomeIcon icon={faInfoCircle} size={24} color="#fff" />
            <Text style={styles.smallButtonText}>Deprem Bilgilendirme</Text>
          </TouchableOpacity>
        </View>

        <MapView
          style={styles.map}
          region={region}
          onRegionChangeComplete={handleRegionChange}
          zoomEnabled={true}
          zoomControlEnabled={true}
          showsUserLocation={true}
        >
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
                Linking.openURL(url);
              }}
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

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>En Yakın Toplanma Alanları</Text>
          <TouchableOpacity onPress={() => navigation.navigate('ViewAll2')}>
            <Text style={styles.viewAll}>Tümünü Gör</Text>
          </TouchableOpacity>
        </View>

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
                  <FontAwesomeIcon icon={faUsers} size={30} color="white" />
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
      </ScrollView>
    </View>
  );
};

const HomePage = ({ navigation }) => {
  const [currentTab, setCurrentTab] = useState('Earthquake');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [cameraVisible, setCameraVisible] = useState(false);

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const userToken = await AsyncStorage.getItem('userToken');
        setIsAuthenticated(!!userToken);
      } catch (error) {
        console.error('Error checking authentication', error);
      }
    };
    checkAuthentication();
  }, []);

  const renderScreen = () => {
    switch (currentTab) {
      case 'Earthquake':
        return <EarthquakeScreen navigation={navigation} setCameraVisible={setCameraVisible} />;
      case 'Profile':
        return <ProfileScreen />;
      case 'Settings':
        return <SettingsScreen />;
      default:
        return <EarthquakeScreen />;
    }
  };

  const handleEmergencyCall = () => {
    Linking.openURL('tel:112');
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

      const phoneNumbers = selectedContacts.map(contact => contact.phoneNumber);

      SendSMS.send({
        body: familyMessage,
        recipients: phoneNumbers,
        successTypes: ['sent', 'queued'],
        allowAndroidSendWithoutReadPermission: true,
      }, (completed, cancelled, error) => {
        if (completed) {
          Alert.alert('Başarılı', 'SMS başarıyla gönderildi');
        } else if (cancelled) {
          Alert.alert('İptal', 'SMS gönderimi iptal edildi');
        } else if (error) {
          Alert.alert('Hata', 'SMS gönderilemedi');
        }
      });

    } catch (error) {
      console.error('SMS gönderme hatası:', error);
      Alert.alert(
        'Hata',
        'SMS gönderilemedi. Lütfen tekrar deneyin.'
      );
    }
  };

  if (!isAuthenticated) {
    return <Text>Loading...</Text>;
  }

  return (
    <View style={styles.container}>
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
                animation={currentTab === 'Earthquake' ? 'modernPulse' : null} 
                iterationCount="infinite"
                duration={1500}
              >
                <FontAwesomeIcon 
                  icon={faHome} 
                  size={currentTab === 'Earthquake' ? 30 : 24} 
                  color={currentTab === 'Earthquake' ? '#fff' : '#ccc'} 
                />
              </Animatable.View>
              <Text style={styles.tabLabel}>Ana Sayfa</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setCurrentTab('Profile')}
              style={[styles.tab, currentTab === 'Profile' && styles.activeTab]}
            >
              <Animatable.View 
                animation={currentTab === 'Profile' ? 'modernPulse' : null} 
                iterationCount="infinite"
                duration={1500}
              >
                <FontAwesomeIcon 
                  icon={faUser} 
                  size={currentTab === 'Profile' ? 30 : 24} 
                  color={currentTab === 'Profile' ? '#fff' : '#ccc'} 
                />
              </Animatable.View>
              <Text style={styles.tabLabel}>Profil</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setCurrentTab('Settings')}
              style={[styles.tab, currentTab === 'Settings' && styles.activeTab]}
            >
              <Animatable.View 
                animation={currentTab === 'Settings' ? 'modernPulse' : null} 
                iterationCount="infinite"
                duration={1500}
              >
                <FontAwesomeIcon 
                  icon={faCog} 
                  size={currentTab === 'Settings' ? 30 : 24} 
                  color={currentTab === 'Settings' ? '#fff' : '#ccc'} 
                />
              </Animatable.View>
              <Text style={styles.tabLabel}>Ayarlar</Text>
            </TouchableOpacity>
          </Animatable.View>
          <TouchableOpacity 
            style={styles.emergencyCallButton} 
            onPress={handleEmergencyCall}
          >
            <FontAwesomeIcon icon={faPhone} size={30} color="white" />
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};

export default HomePage;

export const styles = StyleSheet.create({
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
    paddingVertical: 30,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
  },
  logoImage: {
    width: 50,
    height: 50,
    top: -20,
    position: 'absolute',
    left: width / 2 - 25,
  },
  whistleButton: {
    position: 'absolute',
    left: 20,
  },
  info: {
    right: 40,
  },
  scrollContent: {
    paddingTop: 80,
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
  dalga: {
    bottom: 100,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  assemblyButtonsContainer: {
    flexDirection: 'column',
    paddingHorizontal: 16,
    marginVertical: 16,
  },
  assemblyButton: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  assemblyButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  assemblyIconWrapper: {
    backgroundColor: 'red', // Orange background for assembly icon
    padding: 8,
    borderRadius: 8,
    marginRight: 12,
  },
  assemblyButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  assemblyDetails: {
    fontSize: 14,
    color: '#555',
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
    shadowColor: 'red',
    shadowOffset: { width: 2, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  bigButton: {
    width: 150,
    height: 150,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 75,
    borderWidth: 2,
    borderColor: '#fff',
  },
  bigButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 5,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  smallButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  smallButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 5,
    textAlign: 'center',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#2D2D2D',
    paddingVertical: 15,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 10,
    borderTopLeftRadius: 25,
    borderTopRightRadius: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  tab: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
  },
  activeTab: {
    backgroundColor: '#D32F2F',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 20,
    elevation: 5,
  },
  tabLabel: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 5,
  },
  emergencyCallButton: {
    position: 'absolute',
    bottom: 90,
    right: 20,
    width: 60,
    height: 60,
    backgroundColor: '#D32F2F',
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    zIndex: 1000,
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
  areaListContainer: {
    position: 'absolute',
    top: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 10,
    padding: 15,
    maxHeight: '30%',
  },
  areaListTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  areaItem: {
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 5,
  },
  areaName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  areaDetails: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  areaDistance: {
    fontSize: 12,
    color: '#888',
    marginTop: 2,
  },
});
