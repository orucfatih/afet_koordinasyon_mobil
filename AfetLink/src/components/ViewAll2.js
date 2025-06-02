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
  Linking,
  Image
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
    <View style={styles.mainContainer}>
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

        <ScrollView style={styles.scrollView}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Toplanma Alanları</Text>
          </View>

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
      </SafeAreaView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainContainer: {
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