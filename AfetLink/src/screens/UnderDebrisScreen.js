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
import {
  advertiseStart,
  advertiseStop,
  scanStart,
  scanStop,
} from 'react-native-ble-phone-to-phone';
import DeviceInfo from 'react-native-device-info';

// Event emitter setup for BLE phone-to-phone
const eventEmitter = new NativeEventEmitter(NativeModules.BLEAdvertiser);

const UnderDebrisScreen = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [scannedDevices, setScannedDevices] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [isBluetoothEnabled, setIsBluetoothEnabled] = useState(false);
  const [isAdvertising, setIsAdvertising] = useState(false);
  const [uniqueDeviceId, setUniqueDeviceId] = useState(null);

  // Unique device ID oluştur
  useEffect(() => {
    const generateUniqueDeviceId = async () => {
      try {
        // Önce device ID'yi almaya çalış
        let deviceId = await DeviceInfo.getUniqueId();
        
        // Eğer device ID null ise, zamana dayalı unique ID oluştur
        if (!deviceId || deviceId === 'unknown' || deviceId === 'null') {
          const timestamp = Date.now();
          const randomSuffix = Math.random().toString(36).substr(2, 9);
          deviceId = `time_${timestamp}_${randomSuffix}`;
        }
        
        setUniqueDeviceId(deviceId);
        console.log('Unique Device ID:', deviceId);
      } catch (error) {
        console.warn('Device ID alınamadı, zamana dayalı ID oluşturuluyor:', error);
        const timestamp = Date.now();
        const randomSuffix = Math.random().toString(36).substr(2, 9);
        const fallbackId = `fallback_${timestamp}_${randomSuffix}`;
        setUniqueDeviceId(fallbackId);
      }
    };

    generateUniqueDeviceId();
  }, []);

  // Sabit UUID kullan (tüm cihazlar için aynı)
  const getAfetLinkUUID = () => {
    return '26f08670-ffdf-40eb-9067-78b9ae6e7919';
  };

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
  
  useEffect(() => {
    checkBluetoothState();
    
    // Event listener'ları ekle
    const foundUuidListener = eventEmitter.addListener('foundUuid', (data) => {
      console.log('Found UUID data:', data);
    });
    
    const foundDeviceListener = eventEmitter.addListener('foundDevice', (data) => {
      console.log('Found device data:', data);
      // Cihazı listeye ekle
      setScannedDevices(prevDevices => {
        const deviceUuid = data.uuids && data.uuids.length > 0 ? data.uuids[0] : null;
        const deviceAddress = data.deviceAddress || data.id || `device_${Date.now()}`;
        
        // AfetLink cihazı mı kontrol et (base UUID ile başlıyor mu)
        const isAfetLinkDevice = deviceUuid && deviceUuid.startsWith('26f08670-ffdf-40eb-9067-78b9ae6e7919');
        
        if (!isAfetLinkDevice) {
          // AfetLink cihazı değilse ekleme
          return prevDevices;
        }
        
        // Aynı adrese sahip cihaz var mı kontrol et (ana tanımlayıcı olarak adres kullan)
        const existingDeviceByAddress = prevDevices.find(device => 
          device.address === deviceAddress || device.id === deviceAddress
        );
        
        if (existingDeviceByAddress) {
          // Aynı adrese sahip cihaz varsa, sadece RSSI ve lastSeen güncelle
          console.log('Aynı adres cihaz güncelleniyor:', deviceAddress);
          return prevDevices.map(device => {
            if (device.address === deviceAddress || device.id === deviceAddress) {
              return {
                ...device,
                rssi: data.rssi || device.rssi,
                lastSeen: Date.now()
              };
            }
            return device;
          });
        }
        
        // Yeni AfetLink cihazı ekle
        console.log('Yeni AfetLink cihazı ekleniyor:', deviceAddress);
        
        // Device ID'yi adresten türet (kısa ve unique)
        const deviceId = deviceAddress.replace(/[^a-zA-Z0-9]/g, '').substring(0, 8);
        
        return [...prevDevices, {
          id: deviceAddress,
          name: `AfetLink Cihazı (${deviceId})`,
          rssi: data.rssi || 'N/A',
          address: deviceAddress,
          uuids: data.uuids || [],
          lastSeen: Date.now(),
          deviceId: deviceId
        }];
      });
    });
    
    const logListener = eventEmitter.addListener('log', (log) => {
      console.log('BLE Log:', log);
    });

    return () => {
      // Event listener'ları temizle
      foundUuidListener.remove();
      foundDeviceListener.remove();
      logListener.remove();
    };
  }, []);

  const requestBluetoothPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const androidVersion = Platform.Version;
        console.log('Android sürümü:', androidVersion);
        
        let permissions = [];
        
        // Android 12+ (API 31+) için yeni izinler
        if (androidVersion >= 31) {
          permissions = [
            PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
            PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
            PermissionsAndroid.PERMISSIONS.BLUETOOTH_ADVERTISE,
            PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
          ];
        } else if (androidVersion >= 23) {
          // Android 6+ için eski izinler
          permissions = [
            PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
            PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION
          ];
        }

        console.log('İstenen izinler:', permissions);

        const results = {};
        for (const permission of permissions) {
          try {
            const result = await PermissionsAndroid.request(permission, {
              title: 'Bluetooth İzni',
              message: 'Bu uygulama Bluetooth kullanabilmek için izin istiyor.',
              buttonNeutral: 'Daha Sonra',
              buttonNegative: 'İptal',
              buttonPositive: 'Tamam',
            });
            results[permission] = result;
            console.log(`${permission}: ${result}`);
          } catch (err) {
            console.warn(`İzin hatası (${permission}):`, err);
            results[permission] = PermissionsAndroid.RESULTS.DENIED;
          }
        }

        const allGranted = Object.values(results).every(result => 
          result === PermissionsAndroid.RESULTS.GRANTED
        );

        console.log('Tüm izinler verildi mi:', allGranted);
        return allGranted;
      } catch (err) {
        console.warn('Genel izin hatası:', err);
        return false;
      }
    }
    return true;
  };

  const checkBluetoothState = async () => {
    try {
      const state = await BleManager.checkState();
      console.log('Bluetooth durumu:', state);
      const isEnabled = state === 'on';
      setIsBluetoothEnabled(isEnabled);
      return isEnabled;
    } catch (error) {
      console.log('Bluetooth durumu kontrol hatası:', error);
      return false;
    }
  };

  const toggleBluetooth = async () => {
    try {
      setIsLoading(true);
      
      // Önce izinleri kontrol et
      const hasPermission = await requestBluetoothPermission();
      if (!hasPermission) {
        Alert.alert(
          "İzin Gerekli", 
          "Bluetooth kullanabilmek için gerekli izinler verilmedi. Lütfen uygulama ayarlarından izinleri manuel olarak verin.",
          [
            { text: "Ayarları Aç", onPress: () => Linking.openSettings() },
            { text: "İptal", style: "cancel" }
          ]
        );
        return;
      }

      // Bluetooth durumunu kontrol et
      const currentState = await checkBluetoothState();
      console.log('Mevcut Bluetooth durumu:', currentState);

      if (currentState) {
        Alert.alert("Bluetooth Zaten Açık", "Bluetooth zaten açık durumda.", [{ text: "Tamam" }]);
        return;
      }

             // Android'de Bluetooth açma işlemi
       if (Platform.OS === 'android') {
         try {
           console.log('Bluetooth açılmaya çalışılıyor...');
           
           // Bluetooth açma isteği gönder
           const result = await BleManager.enableBluetooth();
           console.log('BleManager.enableBluetooth sonucu:', result);
           
           // Biraz bekleyip durumu kontrol et
           setTimeout(async () => {
             const newState = await checkBluetoothState();
             console.log('3 saniye sonra bluetooth durumu:', newState);
             if (newState) {
               Alert.alert("Bluetooth Açıldı", "Bluetooth başarıyla açıldı!", [{ text: "Tamam" }]);
             }
           }, 3000);

         } catch (error) {
           console.error('Bluetooth açma hatası:', error);
           console.error('Hata detayı:', JSON.stringify(error));
           
           let errorMessage = "Bluetooth açılırken bir hata oluştu.";
           if (error.message) {
             errorMessage += `\n\nHata: ${error.message}`;
           }
           
           Alert.alert(
             "Bluetooth Açılamadı", 
             errorMessage + "\n\nLütfen manuel olarak açmayı deneyin.",
             [
               { text: "Bluetooth Ayarlarını Aç", onPress: () => Linking.sendIntent('android.settings.BLUETOOTH_SETTINGS') },
               { text: "Tamam" }
             ]
           );
         }
       }

    } catch (error) {
      console.error('Genel Bluetooth hatası:', error);
      Alert.alert(
        "Hata", 
        "Bluetooth işlemi sırasında bir hata oluştu.",
        [
          { text: "Bluetooth Ayarlarını Aç", onPress: () => Linking.sendIntent('android.settings.BLUETOOTH_SETTINGS') },
          { text: "Tamam" }
        ]
      );
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
    if (!hasPermission) {
      Alert.alert(
        "İzin Gerekli",
        "Bluetooth taraması için gerekli izinler verilmedi.",
        [
          { text: "Ayarları Aç", onPress: () => Linking.openSettings() },
          { text: "İptal", style: "cancel" }
        ]
      );
      return;
    }

    if (isScanning) return;

    setScannedDevices([]);
    setIsScanning(true);

    try {
      console.log("BLE phone-to-phone tarama başlatılıyor...");
      
      // Base AfetLink UUID'si ile tarama başlat (tüm AfetLink cihazlarını bul)
      const baseAfetLinkUuid = '26f08670-ffdf-40eb-9067-78b9ae6e7919';
      await scanStart([baseAfetLinkUuid].join());
      
      console.log("Tarama başlatıldı");

      // 10 saniye sonra taramayı durdur
      setTimeout(async () => {
        try {
          await scanStop();
          setIsScanning(false);
          console.log("Tarama durduruldu.");
          
          // Eski cihazları temizle (30 saniyeden eski)
          setScannedDevices(prevDevices => {
            const now = Date.now();
            const thirtySecondsAgo = now - 30000; // 30 saniye
            return prevDevices.filter(device => 
              device.lastSeen && device.lastSeen > thirtySecondsAgo
            );
          });
          
        } catch (error) {
          console.error("Tarama durdurma hatası:", error);
          setIsScanning(false);
        }
      }, 10000);

    } catch (error) {
      console.error("Tarama başlatma hatası:", error);
      setIsScanning(false);
      Alert.alert("Tarama Hatası", "Cihaz taraması başlatılamadı.");
    }
  };

  const startAdvertising = async () => {
    const hasPermission = await requestBluetoothPermission();
    if (!hasPermission) {
      Alert.alert(
        "İzin Gerekli",
        "Bluetooth advertising için gerekli izinler verilmedi.",
        [
          { text: "Ayarları Aç", onPress: () => Linking.openSettings() },
          { text: "İptal", style: "cancel" }
        ]
      );
      return;
    }

    try {
      setIsAdvertising(true);
      console.log("BLE phone-to-phone advertising başlatılıyor...");

      // Sabit AfetLink UUID ile advertising başlat
      const afetLinkUUID = getAfetLinkUUID();
      await advertiseStart(afetLinkUUID);

      console.log("Advertising başlatıldı - UUID:", afetLinkUUID);
      Alert.alert("Bağlantı İçin Hazır", "Diğer AfetLink cihazları sizi bulabilir.");

    } catch (error) {
      console.error("Advertising başlatma hatası:", error);
      setIsAdvertising(false);
      Alert.alert("Hata", "Bağlantı için hazır olma işlemi başarısız oldu.");
    }
  };

  const stopAdvertising = async () => {
    try {
      await advertiseStop();
      setIsAdvertising(false);
      console.log("Advertising durduruldu");
      Alert.alert("Bağlantı Durduruldu", "Artık diğer cihazlar tarafından görülmüyorsunuz.");
    } catch (error) {
      console.error("Advertising durdurma hatası:", error);
    }
  };

  const renderDevice = ({ item }) => {
    const timeAgo = item.lastSeen ? Math.floor((Date.now() - item.lastSeen) / 1000) : null;
    
    return (
      <View
        style={[
          styles.deviceItem,
          item.name && item.name.includes('AfetLink') && styles.afetLinkDeviceItem
        ]}
      >
        <Text style={styles.deviceName}>
          {item.name}
          {item.name && item.name.includes('AfetLink') && ' 🚨'}
        </Text>
        <Text style={styles.deviceId}>Adres: {item.address || item.id}</Text>
        <Text style={styles.deviceRssi}>RSSI: {item.rssi}</Text>
        {item.deviceId && item.deviceId !== 'Unknown' && (
          <Text style={styles.deviceUniqueId}>Cihaz ID: {item.deviceId}</Text>
        )}
        {item.uuids && item.uuids.length > 0 && (
          <Text style={styles.deviceUuid}>UUID: {item.uuids[0]}</Text>
        )}
        {timeAgo !== null && (
          <Text style={styles.deviceTimeAgo}>
            {timeAgo < 60 ? `${timeAgo}s önce` : `${Math.floor(timeAgo / 60)}d önce`}
          </Text>
        )}
      </View>
    );
  };

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
            style={[
              styles.bluetoothButton, 
              (isLoading || !isBluetoothEnabled) && styles.bluetoothButtonDisabled
            ]}
            onPress={isAdvertising ? stopAdvertising : startAdvertising}
            disabled={isLoading || !isBluetoothEnabled}>
            <Ionicons name={isAdvertising ? "radio" : "radio-outline"} size={30} color="white" />
            <Text style={styles.buttonText}>
              {isAdvertising ? "Reklam Yayınını Durdur" : 
               !isBluetoothEnabled ? "Bluetooth Kapalı" : "Bağlantı İçin Hazır"}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Cihaz listesi için ayrı ScrollView */}
        <View style={styles.deviceSection}>
          <Text style={styles.devicesTitle}>Bulunan Cihazlar</Text>
          <ScrollView style={styles.deviceScrollView}>
            {scannedDevices.length > 0 ? (
              <FlatList
                data={scannedDevices}
                renderItem={renderDevice}
                keyExtractor={(item) => item.id}
                style={styles.deviceList}
                scrollEnabled={false}
              />
            ) : (
              <View style={styles.noDevicesContainer}>
                <Text style={styles.noDevicesText}>Henüz cihaz bulunamadı</Text>
              </View>
            )}
          </ScrollView>
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
    padding: 20,
    alignItems: 'center',
    paddingBottom: 10,
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
  deviceSection: {
    flex: 1,
    marginTop: 10,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  devicesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  deviceScrollView: {
    flex: 1,
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
  deviceRssi: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  deviceUuid: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
  deviceTimeAgo: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  deviceList: {
    width: '100%',
  },
  afetLinkDeviceItem: {
    backgroundColor: '#ffd7d7',
    borderWidth: 2,
    borderColor: '#ff0000',
  },
  noDevicesContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  noDevicesText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  deviceUniqueId: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: 'bold',
  },
});

export default UnderDebrisScreen;

