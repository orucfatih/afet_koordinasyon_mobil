import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Dimensions, FlatList } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import Icon from 'react-native-vector-icons/MaterialIcons';
import axios from 'axios';

const { width } = Dimensions.get('window');

const EarthquakeScreen = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [earthquakeData, setEarthquakeData] = useState([]);

  useEffect(() => {
    // Kandilli Rasathanesi API URL'si
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
        setEarthquakeData(data); // Veriyi state'e kaydediyoruz
      } catch (error) {
        console.error('Error fetching earthquake data', error);
      }
    };

    fetchEarthquakeData();
  }, []); // Bu efekt sadece bileşen ilk render edildiğinde çalışacak

  const handleScroll = (event) => {
    const scrollX = event.nativeEvent.contentOffset.x;
    setCurrentIndex(Math.round(scrollX / width));
  };

  const renderEarthquakeCard = ({ item }) => (
    <View style={styles.earthquakeCard}>
      <View style={styles.magnitudeCircle}>
        <Text style={styles.magnitudeText}>{item.magnitude}</Text>
      </View>
      <View style={styles.earthquakeInfo}>
        <Text style={styles.earthquakeLocation}>{item.location}</Text>
        <Text style={styles.earthquakeTime}>{item.time}</Text>
        <Text style={styles.earthquakeDate}>{item.date}</Text>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.topBar}>
        <Image source={require('../../assets/images/afad-logo2.png')} style={styles.logoImage} />
        <TouchableOpacity>
          <Icon name="info-outline" size={25} color="white" />
        </TouchableOpacity>
      </View>

      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Son Depremler</Text>
        <TouchableOpacity>
          <Text style={styles.viewAll}>Tümünü Gör</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={earthquakeData}
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

      <TouchableOpacity style={styles.bigButton}>
        <Text style={styles.bigButtonText}>ENKAZ ALTINDAYIM</Text>
      </TouchableOpacity>

      <MapView
        style={styles.map}
        initialRegion={{
          latitude: 38.9637, // Türkiye'nin ortalama koordinatları
          longitude: 35.2433,
          latitudeDelta: 5,
          longitudeDelta: 5,
        }}
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
      </MapView>

    </ScrollView>
  );
};

const ProfileScreen = () => (
  <View style={styles.screen}>
    <Icon name="person" size={100} color="white" />
    <Text style={styles.screenText}>Profil Sayfası</Text>
  </View>
);

const SettingsScreen = () => (
  <View style={styles.screen}>
    <Icon name="settings" size={100} color="white" />
    <Text style={styles.screenText}>Ayarlar Sayfası</Text>
  </View>
);

const ChatScreen = () => (
  <View style={styles.screen}>
    <Icon name="chat" size={100} color="white" />
    <Text style={styles.screenText}>Chat Sayfası</Text>
  </View>
);

const HomePage = () => {
  const [currentTab, setCurrentTab] = useState('Earthquake');

  const renderScreen = () => {
    switch (currentTab) {
      case 'Earthquake':
        return <EarthquakeScreen />;
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

  return (
    <View style={styles.container}>
      <View style={styles.screenContainer}>{renderScreen()}</View>
      <View style={styles.tabBar}>
        <TouchableOpacity
          onPress={() => setCurrentTab('Earthquake')}
          style={[styles.tab, currentTab === 'Earthquake' && styles.activeTab]}
        >
          <Icon name="home" size={30} color={currentTab === 'Earthquake' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setCurrentTab('Profile')}
          style={[styles.tab, currentTab === 'Profile' && styles.activeTab]}
        >
          <Icon name="person" size={30} color={currentTab === 'Profile' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setCurrentTab('Settings')}
          style={[styles.tab, currentTab === 'Settings' && styles.activeTab]}
        >
          <Icon name="settings" size={30} color={currentTab === 'Settings' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setCurrentTab('Chat')}
          style={[styles.tab, currentTab === 'Chat' && styles.activeTab]}
        >
          <Icon name="chat" size={30} color={currentTab === 'Chat' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default HomePage;



// Stiller
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  screenContainer: {
    flex: 1,
  },
  screen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ff1744',
  },
  screenText: {
    color: 'white',
    fontSize: 20,
    marginTop: 10,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#D32F2F',
    padding: 20,
  },
  logoImage: {
    width: 150,
    height: 40,
    resizeMode: 'cover',
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
  map: { height: 300, marginVertical: 10 },
  slider: { marginTop: 10 },
  pagination: { flexDirection: 'row', justifyContent: 'center', marginTop: 10 },
  dot: { height: 10, width: 10, borderRadius: 5, backgroundColor: '#CCC', marginHorizontal: 5 },
  activeDot: { backgroundColor: '#007AFF' },
  slider: {
    marginTop: 10,
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
  magnitudeCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#E0E0E0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  magnitudeText: {
    fontSize: 24,
    fontWeight: 'bold',
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
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 10,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#E0E0E0',
    marginHorizontal: 5,
  },
  activeDot: {
    backgroundColor: '#D32F2F',
    width: 12,
    height: 12,
  },
  bigButton: {
    marginVertical: 20,
    marginHorizontal: 15,
    padding: 15,
    backgroundColor: '#D32F2F',
    borderRadius: 10,
    alignItems: 'center',
  },
  bigButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#D32F2F',
    paddingVertical: 10,
  },
  tab: {
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: 'white',
  },
});

