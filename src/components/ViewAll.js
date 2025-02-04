import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, FlatList, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Svg, Path } from 'react-native-svg';
import axios from 'axios';

const ViewAll = (navigation) => {
  const [earthquakeData, setEarthquakeData] = useState([]);

  // Deprem verilerini al
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
        }));
        setEarthquakeData(data.slice(0, 20)); // Son 20 depremi al
      } catch (error) {
        console.error('Error fetching earthquake data', error);
      }
    };

    fetchEarthquakeData();
  }, []);

  // Deprem kartını render et
  const renderEarthquakeCard = ({ item }) => {
    const getMagnitudeColor = (magnitude) => {
      if (magnitude < 4) return '#4CAF50'; // Yeşil (Normal)
      if (magnitude < 6) return '#FFC107'; // Sarı (Orta)
      return '#D32F2F'; // Kırmızı (Şiddetli)
    };

    return (
      <View style={styles.earthquakeCard}>
        {/* İç içe 4 yuvarlak */}
        <View style={styles.magnitudeWrapper}>
          <View style={[styles.circle, { backgroundColor: getMagnitudeColor(item.magnitude), width: 120, height: 120 }]}>
            <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.3)', width: 100, height: 100 }]}>
              <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.5)', width: 80, height: 80 }]}>
                <View style={[styles.circle, { backgroundColor: 'rgba(255,255,255,0.7)', width: 60, height: 60 }]}>
                  <Text style={styles.magnitudeText}>{item.magnitude}</Text>
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

        {/* Sismik Dalga İşareti */}
        <Svg height="30" width="100" viewBox="0 0 100 30">
          <Path
            d="M 0,15 L 10,5 L 20,15 L 30,10 L 40,20 L 50,10 L 60,25 L 70,15 L 80,20 L 90,10 L 100,30 L 110,15 L 120,20"
            stroke="#D32F2F"
            strokeWidth="3"
            fill="none"
          />
        </Svg>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={() => navigation.goBack()}>
        <Text style={styles.goBack}>Geri</Text>
      </TouchableOpacity>

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
    padding: 10,
  },
  goBack: {
    fontSize: 18,
    color: '#007BFF',
    marginBottom: 10,
  },
  earthquakeCard: {
    marginVertical: 10,
    padding: 10,
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
    fontSize: 16,
    fontWeight: 'bold',
  },
  earthquakeTime: {
    fontSize: 14,
    color: '#757575',
  },
  earthquakeDate: {
    fontSize: 14,
    color: '#757575',
  },
  magnitudeWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  circle: {
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  magnitudeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  earthquakeList: {
    marginTop: 20,
  },
});

export default ViewAll;
