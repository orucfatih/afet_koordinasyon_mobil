import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Platform,
  PermissionsAndroid,
  SafeAreaView,
  StatusBar,
  Linking,
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import BleManager from 'react-native-ble-manager';

const UnderDebrisScreen = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // BLE Manager'ı başlat
    BleManager.start({ showAlert: false })
      .then(() => {
        console.log('BLE Manager başlatıldı');
      })
      .catch(error => {
        console.error('BLE Manager başlatma hatası:', error);
      });
  }, []);

  const requestBluetoothPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const permissions = [
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
        ];

        const results = await Promise.all(
          permissions.map(permission => PermissionsAndroid.request(permission))
        );

        return results.every(result => result === PermissionsAndroid.RESULTS.GRANTED);
      } catch (err) {
        console.warn('İzin hatası:', err);
        return false;
      }
    }
    return true;
  };

  const toggleBluetooth = async () => {
    try {
      setIsLoading(true);

      const hasPermission = await requestBluetoothPermission();
      if (!hasPermission) {
        Alert.alert(
          "İzin Gerekli",
          "Bu özelliği kullanmak için gerekli izinlere ihtiyacımız var.",
          [
            { 
              text: "Ayarları Aç", 
              onPress: () => Linking.openSettings() 
            },
            { 
              text: "İptal",
              style: "cancel"
            }
          ]
        );
        return;
      }

      // Sadece Bluetooth'u aç
      await BleManager.enableBluetooth();
      Alert.alert(
        "Bluetooth Açıldı",
        "Bluetooth başarıyla açıldı.",
        [{ text: "Tamam" }]
      );

    } catch (error) {
      console.error('Bluetooth hatası:', error);
      Alert.alert(
        "Hata",
        "Bluetooth açılırken bir hata oluştu. Lütfen tekrar deneyin.",
        [{ text: "Tamam" }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Enkaz Altındayım</Text>
        </View>

        <View style={styles.content}>
          <Text style={styles.infoText}>
            Enkaz altındaysanız, kurtarma ekiplerinin sizi bulabilmesi için lütfen Bluetooth'u açık tutun.
          </Text>

          <TouchableOpacity
            style={[
              styles.bluetoothButton,
              isLoading && styles.bluetoothButtonDisabled
            ]}
            onPress={toggleBluetooth}
            disabled={isLoading}
          >
            <Ionicons
              name="bluetooth-outline"
              size={40}
              color="white"
            />
            <Text style={styles.buttonText}>
              {isLoading ? "İşlem Yapılıyor..." : "Bluetooth'u Aç"}
            </Text>
          </TouchableOpacity>

          <View style={styles.instructionsContainer}>
            <Text style={styles.instructionsTitle}>Önemli Bilgiler:</Text>
            <Text style={styles.instructionText}>
              • Bluetooth sinyali duvarları geçebilir{"\n"}
              • Pil tasarrufu için ekranı kapatabilirsiniz{"\n"}
              • Mümkünse telefonunuzu yüksek bir noktada tutun{"\n"}
              • Bluetooth açıkken kurtarma ekipleri sizi daha kolay bulabilir
            </Text>
          </View>
        </View>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 16,
    color: '#333',
  },
  content: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
    lineHeight: 24,
  },
  bluetoothButton: {
    backgroundColor: '#007AFF',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    width: '80%',
    marginBottom: 20,
  },
  bluetoothButtonDisabled: {
    backgroundColor: '#cccccc',
    opacity: 0.8,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 10,
  },
  instructionsContainer: {
    marginTop: 40,
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
    width: '90%',
  },
  instructionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 24,
  },
});

export default UnderDebrisScreen; 