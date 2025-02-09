import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Dimensions, FlatList, Platform} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { Svg, Path } from 'react-native-svg';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { ProfileScreen, SettingsScreen, ChatScreen, Info} from "../components/index";
import axios from 'axios';
import Icon from 'react-native-vector-icons/MaterialIcons';  
import AsyncStorage from '@react-native-async-storage/async-storage'; 
import { RNCamera } from 'react-native-camera'; // Kamera modülünü import ediyoruz

const { width } = Dimensions.get('window'); 

const EarthquakeScreen = ({ setCameraVisible, navigation }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [earthquakeData, setEarthquakeData] = useState([]);
  const [info, setInfo] = useState(false); //info ekranı için

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
        const response = await axios.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson');
        const data = response.data.features.map(item => ({
          id: item.id,
          magnitude: item.properties.mag,
          location: item.properties.place,
          time: new Date(item.properties.time).toLocaleTimeString(),
          date: new Date(item.properties.time).toLocaleDateString(),
          lat: item.geometry.coordinates[1],
          lon: item.geometry.coordinates[0],
        }));
  
        setEarthquakeData(data.slice(0, 10)); // İlk 10 depremi al
      } catch (error) {
        console.error('Error fetching earthquake data', error);
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
      latitude: Math.max(
        Math.min(newRegion.latitude, TURKEY_BOUNDS.maxLatitude),
        TURKEY_BOUNDS.minLatitude
      ),
      longitude: Math.max(
        Math.min(newRegion.longitude, TURKEY_BOUNDS.maxLongitude),
        TURKEY_BOUNDS.minLongitude
      ),
      latitudeDelta: Math.max(
        Math.min(newRegion.latitudeDelta, 15),
        0.1
      ),
      longitudeDelta: Math.max(
        Math.min(newRegion.longitudeDelta, 15),
        0.1
      ),
    };
    setRegion(limitedRegion);
  };
  const checkAndRequestCameraPermission = async () => {
    try {
      let permission;
  
      if (Platform.OS === 'android') {
        permission = await request(PERMISSIONS.ANDROID.CAMERA);
      } else if (Platform.OS === 'ios') {
        permission = await request(PERMISSIONS.IOS.CAMERA);
      }
  
      if (permission === RESULTS.GRANTED) {
        setCameraVisible(true);
      } else if (permission === RESULTS.BLOCKED) {
        Alert.alert(
          'Kamera İzni Engellendi',
          'Lütfen cihaz ayarlarından kameraya erişim izni verin.'
        );
      } else {
        Alert.alert(
          'Kamera İzni Gerekli',
          'Kamerayı kullanabilmek için izin vermeniz gerekiyor.'
        );
      }
    } catch (error) {
      console.error('Kamera izni kontrolü sırasında hata oluştu:', error);
      Alert.alert('Hata', 'Kamera izni alınırken bir hata oluştu.');
    }
  };  
  const renderEarthquakeCard = ({ item }) => {
    // Deprem şiddetine göre renk belirleme
    const getMagnitudeColor = (magnitude) => {
      if (magnitude < 4) return '#4CAF50'; // Yeşil (Normal)
      if (magnitude < 6) return '#FFC107'; // Sarı (Orta)
      return '#D32F2F'; // Kırmızı (Şiddetli)
    };
  
    // Dinamik yazı boyutu
    const getFontSize = (circleSize) => {
      // Yuvarlağın boyutunun %20'si kadar yazı boyutu
      return Math.floor(circleSize * 0.2);
    };
  
    const circleSize = 120; // Yuvarlağın büyüklüğü
  
    return (
      <View style={styles.earthquakeCard}>
        {/* İç içe 4 yuvarlak */}
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
  
        {/* Deprem bilgileri */}
        <View style={styles.earthquakeInfo}>
          <Text style={styles.earthquakeLocation}>{item.location}</Text>
          <Text style={styles.earthquakeTime}>{item.time}</Text>
          <Text style={styles.earthquakeDate}>{item.date}</Text>
        </View>
  
        {/* Alttaki Sismik Dalga İşareti */}
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

  //Kullanım Kılavuzu
  if(info){
    return <Info setInfo = {setInfo} />
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.topBar}>
        <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
        <TouchableOpacity style={styles.info} onPress={() => setInfo(true)}>
          <Icon name="info-outline" size={25} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Son Depremler</Text>
        <TouchableOpacity onPress={() => navigation.navigate('ViewAll')}>
          <Text style={styles.viewAll}>Tümünü Gör</Text>
        </TouchableOpacity>
      </View>

      <FlatList
  data={earthquakeData.slice(0, 10)} // İlk 10 veriyi al
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
          <View
            key={index}
            style={[styles.dot, currentIndex === index && styles.activeDot]}
          />
        ))}
      </View>
      <TouchableOpacity style={styles.bigButton} onPress={checkAndRequestCameraPermission}>
        <Text style={styles.bigButtonText}>AFET BİLDİR</Text>
        <Ionicons style={styles.camera} name="camera" size={30} color="white" />
      </TouchableOpacity>
      <TouchableOpacity style={styles.bigButton2} onPress={checkAndRequestCameraPermission}>
        <Text style={styles.bigButtonText2}>ENKAZ ALTINDAYIM</Text>
      </TouchableOpacity>
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
        <Image
          source={require('../../assets/images/assembly-icon.png')}
          style={styles.assemblyIcon}
        />
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
  );
};

const HomePage = ({navigation}) => {
  const [currentTab, setCurrentTab] = useState('Earthquake');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [cameraVisible, setCameraVisible] = useState(false); // Kamera görünürlüğü için state

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const userToken = await AsyncStorage.getItem('userToken');
        if (userToken) {
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
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
      case 'Chat':
        return <ChatScreen />;
      default:
        return <EarthquakeScreen />;
    }
  };

  if (!isAuthenticated) {
    return <Text>Loading...</Text>;
  }


  return (
    <View style={styles.container}>
      {cameraVisible && (
        <RNCamera
          style={{ flex: 1 }}
          type={RNCamera.Constants.Type.back}
          flashMode={RNCamera.Constants.FlashMode.on}
          onCapture={async (data) => {
            console.log(data.uri); // Çekilen fotoğrafın URI'sini al
            setCameraVisible(false); // Kamerayı kapat
          }}
        />
      )}

      {!cameraVisible && (
        <>
          <View style={styles.screenContainer}>{renderScreen()}</View>
          <View style={styles.tabBar}>
            <TouchableOpacity
              onPress={() => setCurrentTab('Earthquake')}
              style={[styles.tab, currentTab === 'Earthquake' && styles.activeTab]}
            >
              <Icon name="home" size={currentTab === 'Earthquake' ? 30 : 24} color={currentTab === 'Earthquake' ? '#fff' : '#ccc'} />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setCurrentTab('Profile')}
              style={[styles.tab, currentTab === 'Profile' && styles.activeTab]}
            >
              <Icon name="person" size={currentTab === 'Profile' ? 30 : 24} color={currentTab === 'Profile' ? '#fff' : '#ccc'} />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setCurrentTab('Settings')}
              style={[styles.tab, currentTab === 'Settings' && styles.activeTab]}
            >
              <Icon name="settings" size={currentTab === 'Settings' ? 30 : 24} color={currentTab === 'Settings' ? '#fff' : '#ccc'} />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setCurrentTab('Chat')}
              style={[styles.tab, currentTab === 'Chat' && styles.activeTab]}
            >
              <Icon name="chat" size={currentTab === 'Chat' ? 30 : 24} color={currentTab === 'Chat' ? '#fff' : '#ccc'} />
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
  );
};

export default HomePage;

// Stiller
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
    backgroundColor: '#2D2D2D', // Koyu arka plan
    paddingVertical: 15,
    borderTopWidth: 2,
    borderTopColor: '#444',
    marginHorizontal: 0,
    elevation: 5,  // Gölgeleme efekti
    borderBottomLeftRadius: 20, // Üst sol köşe radius
    borderBottomRightRadius: 20, // Üst sağ köşe radius
  },
  logoImage: {
    width: 50,
    top: 5,
    left: 30,
    height: 50,
  },
  info: {
    top: 20,
    right: 40,
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
    top: 15,
    right: 1,
  },
  map: {height: 250, marginVertical: 20, marginHorizontal: 15 , borderRadius: 10, overflow: 'hidden' , marginBottom: 20, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 5, elevation: 5, maxLongitude: 48.0, minLatitude: 32.0, minLongitude: 22.0, maxLatitude: 44.0, maxZoomOut: 15, minZoomIn: 0.5}, 
  slider: { marginTop: 10 },
  pagination: { flexDirection: 'row', justifyContent: 'center', marginTop: 10 },
  dot: { height: 10, width: 10, borderRadius: 5, backgroundColor: '#CCC', marginHorizontal: 5 },
  activeDot: { backgroundColor: '#007AFF' },
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
    borderRadius: 100, // Tam yuvarlak yapar
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
    flexDirection: 'column', // Dikey sıralama
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
    flexDirection: 'row', // Simge ve metni yan yana düzenler
    alignItems: 'center',
  },
  assemblyIcon: {
    width: 45,
    backgroundColor: '#D32F2F',
    padding: 4,
    boxShadow: '0 3px 10px rgba(204, 68, 68, 0.87)',
    height: 45,
    marginRight: 12,
    borderRadius: 8,
  },
  assemblyButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    paddingLeft: 20,
  },
  assemblyDetails: {
    fontSize: 14,
    color: '#555',
    paddingLeft: 20,
  },
  bigButton: {
    width: 150,
    height: 150,
    backgroundColor: '#D32F2F',  // Butonun arka plan rengini seçin
    position: 'relative',
    marginHorizontal: (width - 150) / 2,
    marginBottom: 10,
    marginTop: 30,
    justifyContent: 'center',
    alignItems: 'center',
    boxShadow: '0 3px 10px rgba(204, 68, 68, 0.87)',
    borderRadius: 100,  // Yarı çapını, tam yuvarlak yapmak için butonun yarısına eşitle
  },
  bigButtonText: {
    fontSize: 15,
    fontWeight: 'bold',
    color: 'white',
  },
  bigButton2: {
    width: 300,
    height: 50,
    backgroundColor: '#D32F2F',  // Butonun arka plan rengini seçin
    position: 'relative',
    marginHorizontal: (width - 300) / 2,
    marginBottom: 10,
    marginTop: 20,
    justifyContent: 'center',
    alignItems: 'center',
    boxShadow: '0 3px 10px rgba(204, 68, 68, 0.87)',
    borderRadius: 5,  // Yarı çapını, tam yuvarlak yapmak için butonun yarısına eşitle
  },
  bigButtonText2: {
    fontSize: 15,
    fontWeight: 'bold',
    color: 'white',
  },
    tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#2D2D2D', // Koyu arka plan
    paddingVertical: 12,
    borderTopWidth: 2,
    borderTopColor: '#444',
    marginHorizontal: 0,
    elevation: 5,  // Gölgeleme efekti
    borderTopLeftRadius: 20, // Üst sol köşe radius
    borderTopRightRadius: 20, // Üst sağ köşe radius
  },
  tab: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 15,
    backgroundColor: 'transparent',
    transition: 'background-color 3s',
  },
  activeTab: {
    backgroundColor: '#D32F2F',  // Aktif sekme için kırmızı arka plan
    borderRadius: 50,
    paddingVertical: 12,
    paddingHorizontal: 20,
    elevation: 6,  // Aktif sekme için daha fazla gölge
  },
  tabLabel: {
    color: '#FFF',  // Sekme etiketlerinin beyaz rengi
    fontSize: 12,
    fontWeight: 'bold',  // Etiket metninin kalın olması
    marginTop: 5,
  },
});
