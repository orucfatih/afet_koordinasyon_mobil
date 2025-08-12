import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Image,
  ScrollView,
  StatusBar,
  SafeAreaView,
  Platform,
} from 'react-native';
import axios from 'axios';
import Icon from 'react-native-vector-icons/Ionicons';
import {KOERI_SCRAPER_URL} from '@env';

const ViewAll = ({ navigation }) => {
  const [earthquakeData, setEarthquakeData] = useState([]);

  useEffect(() => {
    const fetchEarthquakeData = async () => {
      try {
        const response = await axios.get(KOERI_SCRAPER_URL);
        
        const data = response.data.data.map(item => ({
          id: `${item.Date}-${item.Magnitude}`,
          magnitude: parseFloat(item.Magnitude) || 0,
          location: item.Place || 'Bilinmeyen Yer',
          time: item.Date.split(' ')[1] || 'Bilinmeyen Saat',
          date: item.Date.split(' ')[0] || 'Bilinmeyen Tarih',
          lat: parseFloat(item.Lat) || null, // Enlem eklendi
          lon: parseFloat(item.Lon) || null, // Boylam eklendi
          depth: parseFloat(item.Depth) || null, // Derinlik eklendi
        })).filter(item => item.magnitude >= 3.0); // 3.0 ve üzeri depremleri filtrele
        setEarthquakeData(data.slice(0, 20));
      } catch (error) {
        console.error('Error fetching earthquake data', error);
      }
    };

    fetchEarthquakeData();
  }, []);

  const renderEarthquakeCard = ({ item }) => {
    const getMagnitudeColor = (magnitude) => {
      if (magnitude < 4) return '#4CAF50';
      if (magnitude < 6) return '#FFC107';
      return '#D32F2F';
    };

    const formatLocation = (location) => {
      const maxLength = 30;
      let fontSize = 18;
      if (location.length > 30) {
        fontSize = 14;
      } else if (location.length > 20) {
        fontSize = 16;
      }
      const shortenedLocation =
        location.length > maxLength ? `${location.substring(0, maxLength - 3)}...` : location;
      return { shortenedLocation, fontSize };
    };

    const { shortenedLocation, fontSize } = formatLocation(item.location || 'Bilinmeyen Yer');

    return (
      <View style={styles.earthquakeCard}>
        <View style={styles.magnitudeWrapper}>
          <View
            style={[
              styles.circle,
              { backgroundColor: getMagnitudeColor(item.magnitude), width: 120, height: 120 },
            ]}
          >
            <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.3)', width: 100, height: 100 }]}>
              <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.5)', width: 80, height: 80 }]}>
                <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.7)', width: 60, height: 60 }]}>
                  <Text style={styles.magnitudeText}>{item.magnitude}</Text>
                </View>
              </View>
            </View>
          </View>
          
          <View style={styles.seismicWaves}>
            <View style={styles.seismicGraph}>
              {/* Basit ve şık sismik dalga */}
              <View style={styles.waveContainer}>
                <View style={[styles.modernWave, { height: 6, marginLeft: 0 }]} />
                <View style={[styles.modernWave, { height: 12, marginLeft: 3 }]} />
                <View style={[styles.modernWave, { height: 20, marginLeft: 3 }]} />
                <View style={[styles.modernWave, { height: 28, marginLeft: 3 }]} />
                <View style={[styles.modernWave, { height: 16, marginLeft: 3 }]} />
                <View style={[styles.modernWave, { height: 10, marginLeft: 3 }]} />
                <View style={[styles.modernWave, { height: 14, marginLeft: 3 }]} />
                <View style={[styles.modernWave, { height: 8, marginLeft: 3 }]} />
              </View>
            </View>
          </View>
        </View>

        <View style={styles.earthquakeInfo}>
          <Text style={[styles.earthquakeLocation, { fontSize }]}>{shortenedLocation}</Text>
          <Text style={styles.earthquakeTime}>{item.time}</Text>
          <Text style={styles.earthquakeDate}>{item.date}</Text>
          {/* Koordinatlar ve Derinlik Eklendi */}
          {item.lat && item.lon && (
            <Text style={styles.earthquakeDetails}>
              Koordinatlar: {item.lat.toFixed(4)}, {item.lon.toFixed(4)}
            </Text>
          )}
          {item.depth && (
            <Text style={styles.earthquakeDetails}>Derinlik: {item.depth} km</Text>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Icon name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          <View style={styles.placeholder} />
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Son Depremler</Text>
        </View>

        <FlatList
          data={earthquakeData}
          renderItem={renderEarthquakeCard}
          keyExtractor={(item) => item.id}
          style={styles.earthquakeList}
        />

        {/* Dalga efekti yerine basit bir View */}
        <View style={[styles.dalga, { backgroundColor: '#808080', height: 2 }]} />
      </SafeAreaView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#2D2D2D',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
    paddingVertical: 25,
    paddingHorizontal: 20,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    zIndex: 10,
    position: 'relative',
    minHeight: 75,
  },
  backButton: {
    padding: 10,
    zIndex: 20,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: '50%',
    marginLeft: -25,
    top: 10,
  },
  placeholder: {
    width: 44,
  },
  sectionHeader: {
    alignItems: 'center',
    marginTop: 20,
    paddingBottom: 10,
    paddingHorizontal: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  earthquakeCard: {
    marginVertical: 10,
    padding: 10,
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  earthquakeInfo: {
    marginTop: 10,
    alignItems: 'center',
  },
  earthquakeLocation: {
    fontWeight: 'bold',
    numberOfLines: 1,
    ellipsizeMode: 'tail',
  },
  earthquakeTime: {
    fontSize: 14,
    color: '#757575',
  },
  earthquakeDate: {
    fontSize: 14,
    color: '#757575',
  },
  earthquakeDetails: {
    fontSize: 12,
    color: '#555',
  },
  magnitudeWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  circle: {
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  magnitudeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
  },
  dalga: {
    width: '100%',
    marginVertical: 10,
    opacity: 0.5
  },
  seismicWaves: {
    marginTop: 15,
    width: '100%',
    height: 35,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  seismicGraph: {
    width: 130,
    height: 35,
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
  },
  waveContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
    height: 28,
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
  earthquakeList: {},
});

export default ViewAll;