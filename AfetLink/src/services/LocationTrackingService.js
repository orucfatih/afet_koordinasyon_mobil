import { Platform, PermissionsAndroid } from 'react-native';
import database from '@react-native-firebase/database';
import auth from '@react-native-firebase/auth';
import Geolocation from 'react-native-geolocation-service';

class LocationTrackingService {
  static instance = null;
  static locationInterval = null;

  static getInstance() {
    if (!LocationTrackingService.instance) {
      LocationTrackingService.instance = new LocationTrackingService();
    }
    return LocationTrackingService.instance;
  }

  async requestLocationPermission() {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Konum İzni',
            message: 'Güvenliğiniz için konumunuzu takip etmemiz gerekiyor.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  }

  async startLocationTracking() {
    const hasPermission = await this.requestLocationPermission();
    if (!hasPermission) {
      console.log('Konum izni verilmedi');
      return;
    }

    console.log('Konum takibi başlatılıyor...');
    
    // Eğer zaten çalışıyorsa durdurup yeniden başlat
    if (LocationTrackingService.locationInterval) {
      this.stopLocationTracking();
    }
    
    // İlk konumu hemen al
    this.getCurrentLocationAndSave();
    
    // 30 saniyede bir konum al
    LocationTrackingService.locationInterval = setInterval(() => {
      this.getCurrentLocationAndSave();
    }, 30000); // 30 saniye
  }

  getCurrentLocationAndSave() {
    const currentUser = auth().currentUser;
    if (!currentUser) {
      console.log('Kullanıcı oturum açmamış, konum kaydedilmiyor');
      return;
    }

    Geolocation.getCurrentPosition(
      (position) => {
        const locationData = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: database.ServerValue.TIMESTAMP,
          speed: position.coords.speed || 0,
          heading: position.coords.heading || 0,
          altitude: position.coords.altitude || 0,
          lastUpdated: new Date().toISOString(),
        };

        // Firebase Realtime Database'e kaydet
        database()
          .ref(`userLocations/${currentUser.uid}`)
          .set(locationData)
          .then(() => {
            console.log('Konum kaydedildi:', {
              lat: locationData.latitude,
              lng: locationData.longitude,
              accuracy: locationData.accuracy
            });
          })
          .catch((error) => {
            console.error('Konum kaydetme hatası:', error);
          });

        // Son aktivite zamanını da güncelle
        database()
          .ref(`userActivity/${currentUser.uid}`)
          .set({
            lastActive: database.ServerValue.TIMESTAMP,
            status: 'active'
          })
          .catch((error) => {
            console.error('Aktivite kaydetme hatası:', error);
          });
      },
      (error) => {
        console.log('Konum alma hatası:', error.code, error.message);
        
        // Hata durumunda kullanıcı durumunu güncelle
        const currentUser = auth().currentUser;
        if (currentUser) {
          database()
            .ref(`userActivity/${currentUser.uid}`)
            .set({
              lastActive: database.ServerValue.TIMESTAMP,
              status: 'location_error',
              error: error.message
            })
            .catch((err) => {
              console.error('Hata durumu kaydetme hatası:', err);
            });
        }
      },
      { 
        enableHighAccuracy: true, 
        timeout: 15000, 
        maximumAge: 10000,
        distanceFilter: 10, // 10 metre hareket ettiğinde güncelle
        forceRequestLocation: true,
        showLocationDialog: true,
      }
    );
  }

  stopLocationTracking() {
    if (LocationTrackingService.locationInterval) {
      clearInterval(LocationTrackingService.locationInterval);
      LocationTrackingService.locationInterval = null;
      console.log('Konum takibi durduruldu');

      // Son durumu kaydet
      const currentUser = auth().currentUser;
      if (currentUser) {
        database()
          .ref(`userActivity/${currentUser.uid}`)
          .update({
            lastActive: database.ServerValue.TIMESTAMP,
            status: 'tracking_stopped'
          })
          .catch((error) => {
            console.error('Durum güncelleme hatası:', error);
          });
      }
    }
  }

  // Manuel konum güncelleme
  async updateLocationNow() {
    console.log('Manuel konum güncelleme başlatılıyor...');
    this.getCurrentLocationAndSave();
  }

  // Takip durumunu kontrol et
  isTrackingActive() {
    return LocationTrackingService.locationInterval !== null;
  }
}

export default LocationTrackingService; 