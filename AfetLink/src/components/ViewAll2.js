import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Platform,
  StatusBar,
  SafeAreaView,
  Alert,
  PermissionsAndroid,
  Linking
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import Geolocation from 'react-native-geolocation-service';
import toplanmaAlanlari from '../../afet_toplanma_alanlari.json';

const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
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
  }
  return true;
};

const ViewAll2 = ({ navigation }) => {
  const [assemblyAreas, setAssemblyAreas] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getUserLocationAndSortAreas = async () => {
      try {
        setIsLoading(true);
        
        if (Platform.OS === 'android') {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
          );
          if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
            throw new Error('Konum izni reddedildi');
          }
        }

        // Konum alma
        const hasPermission = await requestLocationPermission();
        if (!hasPermission) {
          throw new Error('Konum izni alınamadı');
        }

        Geolocation.getCurrentPosition(
          async (position) => {
            const userLoc = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            };

            // Tüm toplanma alanlarını mesafeye göre sırala
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
              .sort((a, b) => a.distance - b.distance); // En yakından en uzağa sırala

            setAssemblyAreas(areasWithDistance);
            setIsLoading(false);
          },
          (error) => {
            console.log('Konum alınamadı:', error);
            Alert.alert('Hata', 'Konum alınamadı');
            setIsLoading(false);
          },
          { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
        );

      } catch (error) {
        console.log('Toplanma alanları yüklenirken hata:', error);
        Alert.alert('Hata', 'Toplanma alanları yüklenirken bir hata oluştu.');
        setIsLoading(false);
      }
    };

    getUserLocationAndSortAreas();
  }, []);

  const handleAreaPress = (area) => {
    Alert.alert(
      area.name,
      `${area.district} - ${area.neighborhood}\n${area.street}\nUzaklık: ${area.distance.toFixed(2)} km`,
      [
        {
          text: "İptal",
          style: "cancel"
        },
        {
          text: "Yol Tarifi Al",
          onPress: () => {
            const scheme = Platform.select({ ios: 'maps:0,0?q=', android: 'geo:0,0?q=' });
            const latLng = `${area.latitude},${area.longitude}`;
            const label = area.name;
            const url = Platform.select({
              ios: `${scheme}${label}@${latLng}`,
              android: `${scheme}${latLng}(${label})`
            });
            Linking.openURL(url);
          }
        }
      ]
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Icon name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Toplanma Alanları</Text>
        </View>

        <ScrollView style={styles.scrollView}>
          <View style={styles.content}>
            {isLoading ? (
              <Text style={styles.loadingText}>Toplanma alanları yükleniyor...</Text>
            ) : (
              assemblyAreas.map((area, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.assemblyButton}
                  onPress={() => handleAreaPress(area)}
                >
                  <View style={styles.assemblyButtonContent}>
                    <View style={styles.assemblyIconWrapper}>
                      <Icon name="people" size={30} color="white" />
                    </View>
                    <View style={styles.assemblyInfo}>
                      <Text style={styles.assemblyButtonText}>{area.name}</Text>
                      <Text style={styles.assemblyDetails}>{area.district} - {area.neighborhood}</Text>
                      <Text style={styles.assemblyDetails}>{area.street}</Text>
                      <Text style={styles.assemblyDetails}>
                        Mesafe: {area.distance.toFixed(2)} km
                      </Text>
                    </View>
                  </View>
                </TouchableOpacity>
              ))
            )}
          </View>
        </ScrollView>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0
  },
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#2D2D2D',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    elevation: 2,
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 16,
    color: 'white',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  loadingText: {
    textAlign: 'center',
    padding: 20,
    color: '#666',
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
    backgroundColor: '#D32F2F',
    padding: 8,
    borderRadius: 8,
    marginRight: 12,
  },
  assemblyInfo: {
    flex: 1,
  },
  assemblyButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  assemblyDetails: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
});

export default ViewAll2;