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
import { BleManager as BlePlxManager } from 'react-native-ble-plx';

// Event emitter setup for BLE phone-to-phone
const eventEmitter = new NativeEventEmitter(NativeModules.BLEAdvertiser);

// BLE PLX manager for connection and messaging
const blePlxManager = new BlePlxManager();

const UnderDebrisScreen = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [scannedDevices, setScannedDevices] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [isBluetoothEnabled, setIsBluetoothEnabled] = useState(false);
  const [isAdvertising, setIsAdvertising] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [connectedDevice, setConnectedDevice] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [messages, setMessages] = useState([]);

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

    // Peripheral mode event listener'ları (A cihazı için)
    const handlePeripheralConnected = (data) => {
      console.log("Peripheral: Başka bir cihaz bize bağlandı:", data);
      setConnectedDevice({
        id: data.peripheral || data.deviceId,
        name: data.name || 'AfetLink Cihazı'
      });
      Alert.alert(
        'Kurtarma Ekibi Bağlandı!', 
        `${data.name || data.peripheral} cihazı size bağlandı! Kurtarma ekibi sizi buldu!`,
        [{ text: "Tamam" }]
      );
    };

    const handlePeripheralDisconnected = (data) => {
      console.log("Peripheral: Cihaz bağlantısı kesildi:", data);
      setConnectedDevice(null);
      Alert.alert(
        'Bağlantı Kesildi', 
        `${data.name || data.peripheral} cihazı ile bağlantı kesildi.`,
        [{ text: "Tamam" }]
      );
    };

    // Mesaj alma event listener'ı
    const handleCharacteristicRead = (data) => {
      console.log("Peripheral: Karakteristik okundu:", data);
      try {
        // Base64'ten string'e çevir
        const messageString = atob(data.value);
        const message = JSON.parse(messageString);
        console.log("Alınan mesaj:", message);
        
        if (message.type === 'test') {
          Alert.alert(
            'Test Mesajı Alındı!', 
            `Gönderen: ${message.sender}\nMesaj: ${message.message}\nZaman: ${new Date(message.timestamp).toLocaleTimeString()}`,
            [{ text: "Tamam" }]
          );
        }
      } catch (error) {
        console.warn("Mesaj parse hatası:", error);
        // Alternatif parse yöntemi dene
        try {
          const message = JSON.parse(data.value);
          console.log("Alınan mesaj (alternatif):", message);
          
          if (message.type === 'test') {
            Alert.alert(
              'Test Mesajı Alındı!', 
              `Gönderen: ${message.sender}\nMesaj: ${message.message}\nZaman: ${new Date(message.timestamp).toLocaleTimeString()}`,
              [{ text: "Tamam" }]
            );
          }
        } catch (error2) {
          console.warn("Alternatif parse de başarısız:", error2);
        }
      }
    };

    // Mesaj yazma event listener'ı
    const handleCharacteristicWrite = (data) => {
      console.log("Peripheral: Karakteristik yazıldı:", data);
      try {
        // String olarak parse et
        const message = JSON.parse(data.value);
        console.log("Yazılan mesaj:", message);
        
        if (message.type === 'test') {
          Alert.alert(
            'Test Mesajı Alındı!', 
            `Gönderen: ${message.sender}\nMesaj: ${message.message}\nZaman: ${new Date(message.timestamp).toLocaleTimeString()}`,
            [{ text: "Tamam" }]
          );
        }
      } catch (error) {
        console.warn("Yazılan mesaj parse hatası:", error);
      }
    };

    // Karakteristik değişiklik event listener'ı
    const handleCharacteristicChanged = (data) => {
      console.log("Peripheral: Karakteristik değişti:", data);
      try {
        // String olarak parse et
        const message = JSON.parse(data.value);
        console.log("Değişen mesaj:", message);
        
        if (message.type === 'test') {
          Alert.alert(
            'Test Mesajı Alındı!', 
            `Gönderen: ${message.sender}\nMesaj: ${message.message}\nZaman: ${new Date(message.timestamp).toLocaleTimeString()}`,
            [{ text: "Tamam" }]
          );
        }
      } catch (error) {
        console.warn("Değişen mesaj parse hatası:", error);
      }
    };
  
    const discoverListener = bleManagerEmitter.addListener('BleManagerDiscoverPeripheral', handleDiscoverPeripheral);
    const stateChangeListener = bleManagerEmitter.addListener('BleManagerDidUpdateState', handleBluetoothStateChange);
    const stopListener = bleManagerEmitter.addListener('BleManagerStopScan', () => setIsScanning(false));
    
    // Peripheral mode event listener'ları
    const peripheralConnectedListener = bleManagerEmitter.addListener('BleManagerPeripheralConnected', handlePeripheralConnected);
    const peripheralDisconnectedListener = bleManagerEmitter.addListener('BleManagerPeripheralDisconnected', handlePeripheralDisconnected);
    const characteristicReadListener = bleManagerEmitter.addListener('BleManagerCharacteristicRead', handleCharacteristicRead);
    const characteristicWriteListener = bleManagerEmitter.addListener('BleManagerCharacteristicWrite', handleCharacteristicWrite);
    const characteristicChangedListener = bleManagerEmitter.addListener('BleManagerCharacteristicChanged', handleCharacteristicChanged);
  
    return () => {
      discoverListener.remove();
      stateChangeListener.remove();
      stopListener.remove();
      peripheralConnectedListener.remove();
      peripheralDisconnectedListener.remove();
      characteristicReadListener.remove();
      characteristicWriteListener.remove();
      characteristicChangedListener.remove();
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
        // UUID bazlı tekil kontrol
        const deviceUuid = data.uuids && data.uuids.length > 0 ? data.uuids[0] : null;
        const deviceAddress = data.deviceAddress || data.id || `device_${Date.now()}`;
        
        // Aynı UUID'ye sahip cihaz var mı kontrol et
        const existingDeviceByUuid = deviceUuid ? prevDevices.find(device => 
          device.uuids && device.uuids.length > 0 && device.uuids[0] === deviceUuid
        ) : null;
        
        // Aynı adrese sahip cihaz var mı kontrol et
        const existingDeviceByAddress = prevDevices.find(device => 
          device.address === deviceAddress || device.id === deviceAddress
        );
        
        if (existingDeviceByUuid) {
          // Aynı UUID'ye sahip cihaz varsa, sadece RSSI ve adres bilgisini güncelle
          console.log('Aynı UUID cihaz güncelleniyor:', deviceUuid);
          return prevDevices.map(device => {
            if (device.uuids && device.uuids.length > 0 && device.uuids[0] === deviceUuid) {
              return {
                ...device,
                rssi: data.rssi || device.rssi,
                address: deviceAddress, // Yeni adresi güncelle
                lastSeen: Date.now()
              };
            }
            return device;
          });
        }
        
        if (existingDeviceByAddress) {
          // Aynı adrese sahip cihaz varsa, UUID bilgisini güncelle
          console.log('Aynı adres cihaz güncelleniyor:', deviceAddress);
          return prevDevices.map(device => {
            if (device.address === deviceAddress || device.id === deviceAddress) {
              return {
                ...device,
                uuids: data.uuids || device.uuids,
                rssi: data.rssi || device.rssi,
                lastSeen: Date.now()
              };
            }
            return device;
          });
        }
        
        // Yeni cihaz ekle
        console.log('Yeni cihaz ekleniyor:', deviceAddress);
        return [...prevDevices, {
          id: deviceAddress,
          name: data.deviceName || 'AfetLink Cihazı',
          rssi: data.rssi || 'N/A',
          address: deviceAddress,
          uuids: data.uuids || [],
          lastSeen: Date.now()
        }];
      });
    });
    
    const logListener = eventEmitter.addListener('log', (log) => {
      console.log('BLE Log:', log);
    });

    // react-native-ble-phone-to-phone tüm olası event'leri dinle
    const connectionListener = eventEmitter.addListener('connection', (data) => {
      console.log('BLE Phone-to-Phone: Bağlantı olayı:', data);
      if (data.type === 'connected') {
        setConnectedDevice({
          id: data.deviceId || data.deviceAddress,
          name: data.deviceName || 'AfetLink Cihazı'
        });
        Alert.alert(
          'Kurtarma Ekibi Bağlandı!', 
          `${data.deviceName || data.deviceId} cihazı size bağlandı! Kurtarma ekibi sizi buldu!`,
          [{ text: "Tamam" }]
        );
      } else if (data.type === 'disconnected') {
        setConnectedDevice(null);
        Alert.alert(
          'Bağlantı Kesildi', 
          `${data.deviceName || data.deviceId} cihazı ile bağlantı kesildi.`,
          [{ text: "Tamam" }]
        );
      }
    });

    // Diğer olası event isimleri
    const connectListener = eventEmitter.addListener('connect', (data) => {
      console.log('BLE Phone-to-Phone: Connect event:', data);
    });

    const disconnectListener = eventEmitter.addListener('disconnect', (data) => {
      console.log('BLE Phone-to-Phone: Disconnect event:', data);
    });

    const peripheralListener = eventEmitter.addListener('peripheral', (data) => {
      console.log('BLE Phone-to-Phone: Peripheral event:', data);
    });

    const clientListener = eventEmitter.addListener('client', (data) => {
      console.log('BLE Phone-to-Phone: Client event:', data);
    });

    const errorListener = eventEmitter.addListener('error', (error) => {
      console.log('BLE Phone-to-Phone Error:', error);
    });

    // BLE PLX event listener'ları ekle
    // react-native-ble-plx kütüphanesinin kendi event sistemini kullan
    const stateChangeListener = blePlxManager.onStateChange((state) => {
      console.log('BLE PLX State changed:', state);
    }, true);

    return () => {
      // Event listener'ları temizle
      foundUuidListener.remove();
      foundDeviceListener.remove();
      logListener.remove();
      connectionListener.remove();
      connectListener.remove();
      disconnectListener.remove();
      peripheralListener.remove();
      clientListener.remove();
      errorListener.remove();
      stateChangeListener.remove();
    };
  }, []);

  // Bağlantı kesilme event listener'ı
  useEffect(() => {
    let disconnectSubscription;
    if (connectedDevice) {
      disconnectSubscription = blePlxManager.onDeviceDisconnected(
        connectedDevice.id,
        (error, device) => {
          console.log('BLE PLX: Cihaz bağlantısı kesildi:', device);
          setConnectedDevice(null);
          Alert.alert(
            'Bağlantı Kesildi',
            `${device?.name || device?.id} cihazı ile bağlantı kesildi.`,
            [{ text: "Tamam" }]
          );
        }
      );
    }
    return () => {
      if (disconnectSubscription) {
        disconnectSubscription.remove();
      }
    };
  }, [connectedDevice]);

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
           
           // Kullanıcıya bilgi ver - artık manuel olarak açması gerekiyor
           Alert.alert(
             "Bluetooth Açma İsteği Gönderildi", 
             "Sistemin bluetooth açma isteği gönderildi. Lütfen gelen uyarıyı onaylayın veya manuel olarak bluetooth'u açın.",
             [
               { text: "Bluetooth Ayarlarını Aç", onPress: () => Linking.sendIntent('android.settings.BLUETOOTH_SETTINGS') },
               { text: "Tamam" }
             ]
           );
           
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
      
      // AfetLink UUID'si ile tarama başlat
      const afetLinkUuid = '26f08670-ffdf-40eb-9067-78b9ae6e7919';
      await scanStart([afetLinkUuid].join());
      
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

      // AfetLink UUID'si ile advertising başlat
      const afetLinkUuid = '26f08670-ffdf-40eb-9067-78b9ae6e7919';
      await advertiseStart(afetLinkUuid);

      console.log("Advertising başlatıldı");
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

  const connectToDevice = async (device) => {
    try {
      setIsConnecting(true);
      console.log("Cihaza bağlanılıyor:", device.name || device.id);

      // BLE PLX ile cihaza bağlan
      const connectedDevice = await blePlxManager.connectToDevice(device.id);
      console.log("Cihaza bağlanıldı:", connectedDevice.name || connectedDevice.id);

      // Gerçekten bağlı mı kontrol et
      const isConnected = await connectedDevice.isConnected();
      console.log("Gerçekten bağlı mı:", isConnected);

      if (!isConnected) {
        throw new Error("Bağlantı kurulamadı - cihaz bağlı değil");
      }

      // Servisleri ve karakteristikleri keşfet
      try {
        await connectedDevice.discoverAllServicesAndCharacteristics();
        console.log("Servisler ve karakteristikler keşfedildi");
        
        // Servisleri listele
        const services = await connectedDevice.services();
        console.log("Bulunan servisler:", services.map(s => s.uuid));
        
        if (services.length === 0) {
          console.warn("Hiç servis bulunamadı - bağlantı gerçek olmayabilir");
        }
      } catch (discoverError) {
        console.warn("Servis keşfi başarısız:", discoverError);
        // Servis keşfi başarısız olsa bile bağlantıyı kabul et
      }

      setConnectedDevice(connectedDevice);
      
      Alert.alert(
        'Bağlantı Başarılı', 
        `${device.name || device.id} cihazına başarıyla bağlanıldı!\nBağlantı durumu: ${isConnected ? 'Bağlı' : 'Bağlı değil'}`,
        [{ text: "Tamam" }]
      );

    } catch (error) {
      console.error('Bağlantı hatası:', error);
      Alert.alert('Bağlantı Hatası', `Cihaza bağlanılamadı: ${error.message}`);
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectFromDevice = async () => {
    try {
      if (connectedDevice) {
        await connectedDevice.cancelConnection();
        console.log("Bağlantı kesildi");
        setConnectedDevice(null);
        Alert.alert("Bağlantı Kesildi", "Cihaz ile bağlantı kesildi.");
      }
    } catch (error) {
      console.error('Bağlantı kesme hatası:', error);
      Alert.alert('Hata', 'Bağlantı kesilirken hata oluştu.');
    }
  };

  const testConnection = async () => {
    if (!connectedDevice) {
      Alert.alert('Hata', 'Bağlı cihaz yok');
      return;
    }

    try {
      console.log('Bağlantı testi başlatılıyor...');
      
      // Bağlantı durumunu tekrar kontrol et
      const isConnected = await connectedDevice.isConnected();
      console.log('Test sırasında bağlantı durumu:', isConnected);
      
      if (!isConnected) {
        Alert.alert('Bağlantı Testi', 'Cihaz bağlı değil!');
        setConnectedDevice(null);
        return;
      }

      // Servisleri kontrol et
      const services = await connectedDevice.services();
      console.log('Test sırasında servisler:', services.map(s => s.uuid));
      
      Alert.alert(
        'Bağlantı Testi', 
        `Bağlantı durumu: ${isConnected ? 'Bağlı' : 'Bağlı değil'}\nServis sayısı: ${services.length}`
      );

    } catch (error) {
      console.error('Bağlantı testi hatası:', error);
      Alert.alert('Test Hatası', `Bağlantı testi başarısız: ${error.message}`);
      setConnectedDevice(null);
    }
  };

  const sendTestMessage = async () => {
    if (!connectedDevice) {
      Alert.alert('Hata', 'Bağlı cihaz bulunamadı!');
      return;
    }

    console.log('Test mesajı gönderiliyor...');
    
    const testMessage = {
      type: 'test',
      message: 'Merhaba! Bu bir test mesajıdır.',
      timestamp: Date.now(),
      sender: 'B_Cihazı'
    };

    console.log('Gönderilecek mesaj:', testMessage);
    console.log('Mevcut servisler:', Object.keys(services));

    // Tüm servisleri kontrol et
    for (const serviceUUID of Object.keys(services)) {
      console.log('Servis kontrol ediliyor:', serviceUUID);
      const service = services[serviceUUID];
      console.log(`Servis ${serviceUUID} karakteristikleri:`, Object.keys(service));
      
      // Bu servisteki tüm karakteristikleri kontrol et
      for (const characteristicUUID of Object.keys(service)) {
        const characteristic = service[characteristicUUID];
        console.log(`Karakteristik ${characteristicUUID} özellikleri:`, characteristic);
        
        // Yazılabilir karakteristik ara
        if (characteristic.properties && 
            (characteristic.properties.write || 
             characteristic.properties.writeWithoutResponse || 
             characteristic.properties.indicate || 
             characteristic.properties.notify)) {
          
          console.log(`Yazılabilir karakteristik bulundu: ${characteristicUUID} (servis: ${serviceUUID})`);
          
          try {
            // JSON string'i doğrudan gönder
            const messageString = JSON.stringify(testMessage);
            console.log('Gönderilecek string:', messageString);
            
            // writeWithoutResponse ile gönder
            await BleManager.writeWithoutResponse(
              connectedDevice.id,
              serviceUUID,
              characteristicUUID,
              messageString
            );
            
            console.log('Test mesajı writeWithoutResponse ile gönderildi!');
            Alert.alert('Başarılı', 'Test mesajı gönderildi!');
            return;
            
          } catch (error) {
            console.log('Mesaj yazma hatası:', error);
            
            // write ile dene
            try {
              await BleManager.write(
                connectedDevice.id,
                serviceUUID,
                characteristicUUID,
                messageString
              );
              
              console.log('Test mesajı write ile gönderildi!');
              Alert.alert('Başarılı', 'Test mesajı gönderildi!');
              return;
              
            } catch (writeError) {
              console.log('Write hatası da:', writeError);
            }
          }
        }
      }
      
      console.log(`Servis ${serviceUUID}'de yazılabilir karakteristik bulunamadı`);
    }
    
    Alert.alert('Hata', 'Yazılabilir karakteristik bulunamadı!');
  };

  const renderDevice = ({ item }) => {
    const timeAgo = item.lastSeen ? Math.floor((Date.now() - item.lastSeen) / 1000) : null;
    
    return (
      <TouchableOpacity
        onPress={() => setSelectedDevice(item)}
        style={[
          styles.deviceItem,
          selectedDevice?.id === item.id && styles.selectedDeviceItem,
          item.name && item.name.includes('AfetLink') && styles.afetLinkDeviceItem
        ]}
      >
        <Text style={styles.deviceName}>
          {item.name}
          {item.name && item.name.includes('AfetLink') && ' 🚨'}
        </Text>
        <Text style={styles.deviceId}>Adres: {item.address || item.id}</Text>
        <Text style={styles.deviceRssi}>RSSI: {item.rssi}</Text>
        {item.uuids && item.uuids.length > 0 && (
          <Text style={styles.deviceUuid}>UUID: {item.uuids[0]}</Text>
        )}
        {timeAgo !== null && (
          <Text style={styles.deviceTimeAgo}>
            {timeAgo < 60 ? `${timeAgo}s önce` : `${Math.floor(timeAgo / 60)}d önce`}
          </Text>
        )}
      </TouchableOpacity>
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

            <TouchableOpacity
              style={[
                styles.bluetoothButton,
                (!selectedDevice || isConnecting || !isBluetoothEnabled) && styles.bluetoothButtonDisabled
              ]}
              onPress={() => selectedDevice && connectToDevice(selectedDevice)}
              disabled={!selectedDevice || isConnecting || !isBluetoothEnabled}>
              <Ionicons name="bluetooth" size={30} color="white" />
              <Text style={styles.buttonText}>
                {isConnecting ? "Bağlanıyor..." : 
                 !selectedDevice ? "Lütfen bir cihaz seçin" : 
                 connectedDevice ? "Bağlı" : "Seçili Cihaza Bağlan"}
              </Text>
            </TouchableOpacity>

            {/* Bağlantı Durumu Göstergesi */}
            {connectedDevice && (
              <View style={styles.connectionStatusContainer}>
                <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
                <Text style={styles.connectionStatusText}>
                  {isAdvertising 
                    ? `Kurtarma ekibi (${connectedDevice.name || connectedDevice.id}) bağlandı!`
                    : `${connectedDevice.name || connectedDevice.id} ile bağlı`
                  }
                </Text>
                <TouchableOpacity
                  style={styles.disconnectButton}
                  onPress={disconnectFromDevice}>
                  <Ionicons name="close-circle" size={20} color="#FF6B6B" />
                </TouchableOpacity>
              </View>
            )}

            {/* Bağlantı Testi Butonu */}
            {connectedDevice && (
              <TouchableOpacity
                style={styles.testButton}
                onPress={testConnection}>
                <Ionicons name="checkmark-circle-outline" size={20} color="#007AFF" />
                <Text style={styles.testButtonText}>Bağlantıyı Test Et</Text>
              </TouchableOpacity>
            )}

            {/* Mesaj Gönderme Butonu */}
            {connectedDevice && (
              <TouchableOpacity
                style={styles.messageButton}
                onPress={sendTestMessage}>
                <Ionicons name="send" size={20} color="#4CAF50" />
                <Text style={styles.messageButtonText}>Test Mesajı Gönder</Text>
              </TouchableOpacity>
            )}

            {/* Advertising Durumu Göstergesi */}
            {isAdvertising && !connectedDevice && (
              <View style={styles.advertisingStatusContainer}>
                <Ionicons name="radio" size={24} color="#FF9800" />
                <Text style={styles.advertisingStatusText}>
                  Kurtarma ekiplerini bekliyorsunuz...
                </Text>
              </View>
            )}

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

        {/* Cihaz listesi ScrollView dışında */}
        {scannedDevices.length > 0 ? (
          <View style={styles.deviceListContainer}>
            <Text style={styles.devicesTitle}>Bulunan Cihazlar:</Text>
            <FlatList
              data={scannedDevices}
              renderItem={renderDevice}
              keyExtractor={(item) => item.id}
              style={styles.deviceList}
              scrollEnabled={false}
            />
          </View>
        ) : (
          <View style={styles.deviceListContainer}>
            <Text style={styles.noDevicesText}>Henüz cihaz bulunamadı</Text>
          </View>
        )}
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
  deviceRssi: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  scrollView: {
    flex: 1,
  },
  deviceList: {
    width: '100%',
  },
  afetLinkDeviceItem: {
    backgroundColor: '#ffd7d7',
    borderWidth: 2,
    borderColor: '#ff0000',
  },
  noDevicesText: {
    fontSize: 16,
    color: '#666',
    marginTop: 20,
  },
  deviceUuid: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
  deviceListContainer: {
    marginTop: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    width: '100%',
  },
  devicesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  selectedDeviceItem: {
    backgroundColor: '#e3e3ff',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  connectionStatusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 10,
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
    width: '100%',
  },
  connectionStatusText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 10,
    flex: 1,
  },
  disconnectButton: {
    padding: 5,
    borderRadius: 15,
    marginLeft: 10,
  },
  advertisingStatusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    padding: 10,
    backgroundColor: '#FFF3E0',
    borderRadius: 10,
    width: '100%',
    borderWidth: 1,
    borderColor: '#FF9800',
  },
  advertisingStatusText: {
    fontSize: 14,
    color: '#E65100',
    marginLeft: 10,
    fontWeight: '500',
  },
  deviceTimeAgo: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
  },
  testButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    width: '80%',
    marginTop: 15,
  },
  testButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 6,
  },
  messageButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    width: '80%',
    marginTop: 15,
  },
  messageButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 6,
  },
});

export default UnderDebrisScreen;

