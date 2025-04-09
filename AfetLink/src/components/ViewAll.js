import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Image,
  ScrollView,
  Dimensions,
} from 'react-native';
import axios from 'axios';
import Icon from 'react-native-vector-icons/FontAwesome';

const ViewAll = ({ navigation }) => {
  const [earthquakeData, setEarthquakeData] = useState([]);

  useEffect(() => {
    const fetchEarthquakeData = async () => {
      try {
        const response = await axios.get(
          'https://us-central1-afad-proje.cloudfunctions.net/scrapeKoeriEarthquakes'
        );
        const data = response.data.data.map(item => ({
          id: `${item.Date}-${item.Magnitude}`,
          magnitude: parseFloat(item.Magnitude) || 0,
          location: item.Place || 'Bilinmeyen Yer',
          time: item.Date.split(' ')[1] || 'Bilinmeyen Saat',
          date: item.Date.split(' ')[0] || 'Bilinmeyen Tarih',
          lat: parseFloat(item.Lat) || null, // Enlem eklendi
          lon: parseFloat(item.Lon) || null, // Boylam eklendi
          depth: parseFloat(item.Depth) || null, // Derinlik eklendi
        }));
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
      <View style={styles.topBar}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Icon name="arrow-left" size={24} color="white" />
        </TouchableOpacity>
        <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
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
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#2D2D2D',
    paddingVertical: 15,
    borderTopWidth: 2,
    borderTopColor: '#444',
    marginHorizontal: 0,
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  backButton: {
    padding: 10,
    left: 10,
    top: 5,
  },
  logoImage: {
    width: 50,
    height: 50,
    top: 5,
    position: 'relative',
    right: '43%',
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
  earthquakeDetails: { // Yeni stil eklendi
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
  earthquakeList: {},
});

export default ViewAll;