import React, { useState, useEffect, useRef } from 'react';
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
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import Icon from 'react-native-vector-icons/FontAwesome';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ProfileScreen, SettingsScreen, Info, Horn } from '../components/index';
import * as Animatable from 'react-native-animatable';

const { width } = Dimensions.get('window');

const EarthquakeScreen = ({ setCameraVisible, navigation }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [earthquakeData, setEarthquakeData] = useState([]);
  const [info, setInfo] = useState(false);

  const TURKEY_BOUNDS = {
    minLatitude: 32.0,
    maxLatitude: 44.0,
    minLongitude: 22.0,
    maxLongitude: 48.0,
  };

  const [region, setRegion] = useState({
    latitude: 38.9637,
    longitude: 35.2433,
    latitudeDelta: 5,
    longitudeDelta: 5,
  });

  const [assemblyAreas, setAssemblyAreas] = useState([
    { id: 1, name: 'Toplanma Alanı 1', distance: '1.2 km', capacity: '500 kişi', latitude: 39.9637, longitude: 35.2433 },
    { id: 2, name: 'Toplanma Alanı 2', distance: '2.5 km', capacity: '300 kişi', latitude: 38.9737, longitude: 35.2533 },
    { id: 3, name: 'Toplanma Alanı 3', distance: '4.0 km', capacity: '1000 kişi', latitude: 37.9537, longitude: 35.2333 },
  ]);

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

  const handleRegionChange = (newRegion) => {
    const limitedRegion = {
      latitude: Math.max(Math.min(newRegion.latitude, TURKEY_BOUNDS.maxLatitude), TURKEY_BOUNDS.minLatitude),
      longitude: Math.max(Math.min(newRegion.longitude, TURKEY_BOUNDS.maxLongitude), TURKEY_BOUNDS.minLongitude),
      latitudeDelta: Math.max(Math.min(newRegion.latitudeDelta, 15), 0.1),
      longitudeDelta: Math.max(Math.min(newRegion.longitudeDelta, 15), 0.1),
    };
    setRegion(limitedRegion);
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
      </View>
    );
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
          <Icon name="bullhorn" size={25} color="white" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.info} onPress={() => setInfo(true)}>
          <Icon name="info-circle" size={25} color="white" />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
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
            <Icon name="camera" size={30} color="white" style={styles.camera} />
          </TouchableOpacity>
        </Animatable.View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={styles.largeButton} 
            onPress={() => navigation.navigate('Camera')}
          >
            <View style={styles.buttonContent}>
              <Icon name="exclamation-triangle" size={18} color="white" style={styles.buttonIcon} />
              <Text 
                style={styles.largeButtonText}
                numberOfLines={1}
                adjustsFontSizeToFit
              >
                ENKAZ ALTINDAYIM
              </Text>
            </View>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.smallButton} 
            onPress={() => console.log('Ailene Bildir')}
          >
            <View style={styles.buttonContent}>
              <Icon name="bell" size={16} color="white" style={styles.buttonIcon} />
              <Text style={styles.smallButtonText}>AİLENE BİLDİR</Text>
            </View>
          </TouchableOpacity>
        </View>

        <MapView
          style={styles.map}
          region={region}
          onRegionChangeComplete={handleRegionChange}
        >
          {earthquakeData.map((item) => (
            <Marker
              key={item.id}
              coordinate={{ latitude: item.lat, longitude: item.lon }}
              title={item.location}
              description={`Şiddet: ${item.magnitude}`}
              pinColor="red"
            />
          ))}
          {assemblyAreas.map(area => (
            <Marker
              key={area.id}
              coordinate={{ latitude: area.latitude, longitude: area.longitude }}
              title={area.name}
              description={`Uzaklık: ${area.distance}, Kapasite: ${area.capacity}`}
              pinColor="green"
            />
          ))}
        </MapView>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Toplanma Alanları</Text>
          <TouchableOpacity>
            <Text style={styles.viewAll}>Tümünü Gör</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.assemblyButtonsContainer}>
          {assemblyAreas.slice(0, 6).map((area) => (
            <TouchableOpacity
              key={area.id}
              style={styles.assemblyButton}
              onPress={() => handleNavigateToAssemblyArea(area.latitude, area.longitude)}
            >
              <View style={styles.assemblyButtonContent}>
                <View style={styles.assemblyIconWrapper}>
                  <Icon name="users" size={30} color="white" />
                </View>
                <View>
                  <Text style={styles.assemblyButtonText}>{area.name}</Text>
                  <Text style={styles.assemblyDetails}>Uzaklık: {area.distance}</Text>
                  <Text style={styles.assemblyDetails}>Kapasite: {area.capacity}</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );
};

const HomePage = ({ navigation }) => {
  const [currentTab, setCurrentTab] = useState('Earthquake');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [cameraVisible, setCameraVisible] = useState(false);
  const [user, setUser] = useState(null);
  const fadeAnim = useRef(new Animatable.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

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

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await AsyncStorage.getItem('user');
        if (userData) {
          setUser(JSON.parse(userData));
        }
      } catch (error) {
        console.error('Kullanıcı bilgileri yüklenirken hata:', error);
      }
    };

    loadUser();

    // Animasyonları başlat
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 1000,
        useNativeDriver: true,
      }),
    ]).start();
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
                <Icon 
                  name="home" 
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
                <Icon 
                  name="user" 
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
                <Icon 
                  name="cog" 
                  size={currentTab === 'Settings' ? 30 : 24} 
                  color={currentTab === 'Settings' ? '#fff' : '#ccc'} 
                />
              </Animatable.View>
              <Text style={styles.tabLabel}>Ayarlar</Text>
            </TouchableOpacity>
          </Animatable.View>
          <TouchableOpacity 
            style={styles.emergencyButton} 
            onPress={handleEmergencyCall}
          >
            <Icon name="phone" size={30} color="white" />
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
    paddingBottom: 20,
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
    marginVertical: 30,
    height: 155,
    width: 155,
    borderRadius: 100,
    overflow: 'visible', // Taşmaları gizler
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
    fontSize: 14,
    fontWeight: 'bold',
    color: 'white',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: 20,
  },
  smallButton: {
    width: 150,
    height: 50,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 5,
    marginHorizontal: 10,
    borderWidth: 1,
    borderColor: '#fff',
  },
  largeButton: {
    width: 190, // Increased width for emphasis
    height: 50,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 5,
    marginHorizontal: 10,
    borderWidth: 1,
    borderColor: '#fff',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  buttonIcon: {
    marginRight: 8,
  },
  smallButtonText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  largeButtonText: {
    fontSize: 14, // Slightly larger text for emphasis
    fontWeight: 'bold',
    color: 'white',
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
  emergencyButton: {
    position: 'absolute',
    bottom: 100,
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
  },
});