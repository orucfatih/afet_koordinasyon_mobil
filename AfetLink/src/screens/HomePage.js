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
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import Ionicons from 'react-native-vector-icons/Ionicons';
import MaterialIcons from 'react-native-vector-icons/MaterialIcons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ProfileScreen, SettingsScreen, Info, Horn } from '../components/index';
import * as Animatable from 'react-native-animatable';

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
        <Ionicons style={styles.dalga} name="water" size={30} color="black" />
      </View>
    );
  };

  if (info) {
    return <Info setInfo={setInfo} />;
  }

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <TouchableOpacity onPress={() => navigation.navigate('HomePage')}>
            <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.whistleButton} onPress={() => navigation.navigate('Horn')}>
            <Ionicons name="megaphone" size={25} color="white" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.info} onPress={() => setInfo(true)}>
            <Ionicons name="information-circle" size={25} color="white" />
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
              <Ionicons name="camera" size={30} color="white" style={styles.camera} />
            </TouchableOpacity>
          </Animatable.View>

          <View style={styles.buttonContainer}>
            <TouchableOpacity 
              style={styles.largeButton} 
              onPress={() => navigation.navigate('UnderDebris')}
            >
              <View style={styles.buttonContent}>
                <Ionicons name="warning" size={18} color="white" style={styles.buttonIcon} />
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
                <Ionicons name="notifications" size={16} color="white" style={styles.buttonIcon} />
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
                    <Ionicons name="people" size={30} color="white" />
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
      </SafeAreaView>
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
                <Ionicons 
                  name={currentTab === 'Earthquake' ? 'home' : 'home-outline'} 
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
                <Ionicons 
                  name={currentTab === 'Profile' ? 'person' : 'person-outline'} 
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
                <Ionicons 
                  name={currentTab === 'Settings' ? 'settings' : 'settings-outline'} 
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
            <Ionicons name="call" size={30} color="white" />
          </TouchableOpacity>
        </>
      )}
    </View>
  );
};

export default HomePage;

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
    minHeight: 100,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: width / 2 - 25,
    top: -20,
  },
  whistleButton: {
    position: 'absolute',
    left: 20,
    top: 35,
  },
  info: {
    position: 'absolute',
    right: 20,
    top: 35,
  },
  scrollContent: {
    paddingTop: 20,
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