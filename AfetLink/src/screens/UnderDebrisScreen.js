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
  FlatList,
  NativeEventEmitter,
  NativeModules,
  ScrollView,
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import BleManager from 'react-native-ble-manager';
import { Buffer } from 'buffer';

const UnderDebrisScreen = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [scannedDevices, setScannedDevices] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [isBroadcasting, setIsBroadcasting] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [isBluetoothEnabled, setIsBluetoothEnabled] = useState(false);

  useEffect(() => {
    BleManager.start({ showAlert: false }).then(() => {
      console.log("BLE Başlatıldı");
      checkBluetoothState();
    });
  
    const bleManagerEmitter = new NativeEventEmitter(NativeModules.BleManager);
  
    const handleDiscoverPeripheral = (peripheral) => {
      console.log("Cihaz bulundu:", peripheral);
      setScannedDevices(prev => {
        const exists = prev.some(dev => dev.id === peripheral.id);
        return exists ? prev : [...prev, peripheral];
      });
    };
  
    const handleBluetoothStateChange = (state) => {
      setIsBluetoothEnabled(state === 'on');
    };
  
    const discoverListener = bleManagerEmitter.addListener('BleManagerDiscoverPeripheral', handleDiscoverPeripheral);
    const stateChangeListener = bleManagerEmitter.addListener('BleManagerDidUpdateState', handleBluetoothStateChange);
    const stopListener = bleManagerEmitter.addListener('BleManagerStopScan', () => setIsScanning(false));
  
    return () => {
      discoverListener.remove();
      stateChangeListener.remove();
      stopListener.remove();
    };
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

  const checkBluetoothState = async () => {
    try {
      const enabled = await BleManager.checkState();
      setIsBluetoothEnabled(enabled === 'on');
      return enabled === 'on';
    } catch (error) {
      console.log('Bluetooth durumu kontrol hatası:', error);
      return false;
    }
  };

  const toggleBluetooth = async () => {
    try {
      setIsLoading(true);
      const hasPermission = await requestBluetoothPermission();
      if (!hasPermission) {
        Alert.alert("İzin Gerekli", "Gerekli izinler alınamadı.", [
          { text: "Ayarları Aç", onPress: () => Linking.openSettings() },
          { text: "İptal", style: "cancel" }
        ]);
        return;
      }

      await BleManager.enableBluetooth();
      setIsBluetoothEnabled(true);
      Alert.alert("Bluetooth Açıldı", "Bluetooth başarıyla açıldı.", [{ text: "Tamam" }]);
    } catch (error) {
      console.error('Bluetooth hatası:', error);
      Alert.alert("Hata", "Bluetooth açılırken bir hata oluştu.", [{ text: "Tamam" }]);
    } finally {
      setIsLoading(false);
    }
  };

  const startScan = async () => {
    const isEnabled = await checkBluetoothState();
    if (!isEnabled) {
      Alert.alert(
        "Bluetooth Kapalı",
        "Cihaz taraması yapabilmek için Bluetooth'un açık olması gerekiyor.",
        [
          { text: "İptal", style: "cancel" },
          { text: "Bluetooth'u Aç", onPress: toggleBluetooth }
        ]
      );
      return;
    }

    const hasPermission = await requestBluetoothPermission();
    if (!hasPermission) return;
  
    if (isScanning) return;
  
    setScannedDevices([]);
    setIsScanning(true);
  
    try {
      await BleManager.scan([], 6, true);
      console.log("Tarama başlatıldı...");
  
      setTimeout(async () => {
        try {
          await BleManager.stopScan();
          setIsScanning(false);
          console.log("Tarama durduruldu. Bulunan cihaz sayısı: " + scannedDevices.length);
        } catch (error) {
          console.warn("Tarama durdurulamadı:", error);
        }
      }, 6000);
  
    } catch (error) {
      console.log("Tarama başlatılamadı:", error);
      setIsScanning(false);
      Alert.alert("Hata", "Tarama başlatılamadı. Lütfen tekrar deneyin.");
    }
  };

  const startBroadcast = async () => {
    const hasPermission = await requestBluetoothPermission();
    if (!hasPermission) return;
  
    try {
      setIsBroadcasting(true);
      console.log("Beacon yayını başlatılıyor...");
  
      await BleManager.startAdvertising(
        'EnkazAltıYayını', // cihaz adı
        '12345678-1234-1234-1234-123456789abc', // UUID
        1, // major
        2, // minor
      );
  
      Alert.alert("Beacon Yayını Başladı", "Yakındaki cihazlar sizi algılayabilir.");
    } catch (error) {
      console.warn("Yayın başlatma hatası:", error);
      Alert.alert("Hata", "Beacon yayını başlatılamadı.");
    } finally {
      setIsBroadcasting(false);
    }
  };
  

  const connectToDevice = (deviceId) => {
    BleManager.connect(deviceId)
      .then(() => {
        Alert.alert('Bağlandı', `Cihaza bağlanıldı: ${deviceId}`);
        // Veri gönderme örneği
        sendData(deviceId);
      })
      .catch(err => {
        Alert.alert('Bağlantı Hatası', 'Cihaza bağlanılamadı.');
        console.log('Bağlantı hatası:', err);
      });
  };

  const sendData = async (deviceId) => {
    const serviceUUID = '0000ffe0-0000-1000-8000-00805f9b34fb';
    const characteristicUUID = '0000ffe1-0000-1000-8000-00805f9b34fb';
    const data = Buffer.from('ENKAZ_ALTINDAYIM').toString('base64');

    try {
      await BleManager.write(deviceId, serviceUUID, characteristicUUID, data);
      Alert.alert("Mesaj Gönderildi", "Bluetooth cihazına veri gönderildi.");
    } catch (error) {
      console.error('Veri gönderme hatası:', error);
    }
  };

  const connectAndSendMessage = async (deviceId) => {
    try {
      setIsLoading(true);
  
      await BleManager.connect(deviceId);
      await BleManager.retrieveServices(deviceId);
  
      const serviceUUID = '0000ffe0-0000-1000-8000-00805f9b34fb';
      const characteristicUUID = '0000ffe1-0000-1000-8000-00805f9b34fb';
  
      const data = [69, 78, 75, 65, 90, 95, 65, 76, 84, 73, 78, 68, 65, 89, 73, 77]; // 'ENKAZ_ALTINDAYIM'
  
      await BleManager.writeWithoutResponse(deviceId, serviceUUID, characteristicUUID, data);
  
      Alert.alert('Mesaj Gönderildi', 'Bluetooth cihazına mesaj gönderildi.');
    } catch (error) {
      console.log('Bağlantı veya gönderme hatası:', error);
      Alert.alert('Hata', 'Cihaza bağlanılamadı veya veri gönderilemedi.');
    } finally {
      setIsLoading(false);
    }
  };
  

  const renderDevice = ({ item }) => (
    <TouchableOpacity
      onPress={() => setSelectedDevice(item)}
      style={[
        styles.deviceItem,
        selectedDevice?.id === item.id && styles.selectedDeviceItem
      ]}
    >
      <Text style={styles.deviceName}>{item.name || 'Bilinmeyen Cihaz'}</Text>
      <Text style={styles.deviceId}>{item.id}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Enkaz Altındayım</Text>
        </View>

        <ScrollView style={styles.scrollView}>
          <View style={styles.content}>
            <Text style={styles.infoText}>
              Enkaz altındaysanız, kurtarma ekiplerinin sizi bulabilmesi için lütfen Bluetooth'u açık tutun.
            </Text>

            <TouchableOpacity
              style={[styles.bluetoothButton, isLoading && styles.bluetoothButtonDisabled]}
              onPress={toggleBluetooth}
              disabled={isLoading}>
              <Ionicons name="bluetooth-outline" size={40} color="white" />
              <Text style={styles.buttonText}>
                {isLoading ? "İşlem Yapılıyor..." : 
                 isBluetoothEnabled ? "Bluetooth Açık" : "Bluetooth'u Aç"}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.bluetoothButton, 
                (isScanning || !isBluetoothEnabled) && styles.bluetoothButtonDisabled
              ]}
              onPress={startScan}
              disabled={isScanning || !isBluetoothEnabled}>
              <Ionicons name="search-outline" size={30} color="white" />
              <Text style={styles.buttonText}>
                {isScanning ? "Taranıyor..." : 
                 !isBluetoothEnabled ? "Bluetooth Kapalı" : "Cihaz Tara"}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.bluetoothButton, isBroadcasting && styles.bluetoothButtonDisabled]}
              onPress={startBroadcast}
              disabled={isBroadcasting}>
              <Ionicons name="radio-outline" size={40} color="white" />
              <Text style={styles.buttonText}>
                {isBroadcasting ? "Yayınlanıyor..." : "Beacon Yayını Başlat"}
              </Text>
            </TouchableOpacity>

            {scannedDevices.length > 0 && (
              <View style={styles.devicesContainer}>
                <Text style={styles.devicesTitle}>Bulunan Cihazlar:</Text>
                <FlatList
                  data={scannedDevices}
                  keyExtractor={item => item.id}
                  renderItem={renderDevice}
                  style={styles.devicesList}
                  scrollEnabled={false}
                />
              </View>
            )}
            
            <TouchableOpacity
              style={[
                styles.bluetoothButton,
                (!selectedDevice || isLoading) && styles.bluetoothButtonDisabled
              ]}
              onPress={() => selectedDevice && connectAndSendMessage(selectedDevice.id)}
              disabled={!selectedDevice || isLoading}>
              <Ionicons name="radio-outline" size={40} color="white" />
              <Text style={styles.buttonText}>
                {selectedDevice ? 'Seçili Cihaza Bağlan ve Mesaj Gönder' : 'Lütfen bir cihaz seçin'}
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
    marginBottom: 15,
  },
  bluetoothButtonDisabled: {
    backgroundColor: '#cccccc',
    opacity: 0.8,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 6,
  },
  instructionsContainer: {
    marginTop: 30,
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
    width: '100%',
  },
  instructionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  deviceItem: {
    backgroundColor: '#eef',
    padding: 15,
    borderRadius: 10,
    marginVertical: 5,
    width: '100%',
  },
  deviceName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  deviceId: {
    fontSize: 12,
    color: '#666',
  },
  scrollView: {
    flex: 1,
  },
  devicesContainer: {
    width: '100%',
    marginVertical: 15,
  },
  devicesTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  devicesList: {
    width: '100%',
  },
  selectedDeviceItem: {
    backgroundColor: '#e3e3ff',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
});

export default UnderDebrisScreen;
