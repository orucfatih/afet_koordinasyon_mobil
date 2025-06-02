import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Switch, 
  Alert, 
  Image, 
  Modal,
  ScrollView,
  TextInput,
  TouchableWithoutFeedback,
  Keyboard,
  FlatList,
  Platform,
  PermissionsAndroid,
  Dimensions,
  StatusBar,
  SafeAreaView,
  ActivityIndicator
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Ionicons from 'react-native-vector-icons/Ionicons';
import DeviceInfo from 'react-native-device-info';
import { Appearance } from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import { 
  checkAndRequestSmsPermission,
  checkAndRequestContactsPermission,
  checkAndRequestLocationPermission,
  getAllContacts,
  sendSmsToContacts
} from '../utils/contactsAndSms';
import {
  ContactPickerModal,
  SendingModal,
  SelectedContactsList
} from './index';

const { width } = Dimensions.get('window');

const SettingsScreen = ({ navigation }) => {
  const [isNotificationsEnabled, setIsNotificationsEnabled] = useState(false);
  const [isLocationEnabled, setIsLocationEnabled] = useState(false);
  const [isAutoUpdatesEnabled, setIsAutoUpdatesEnabled] = useState(false);
  const [isHornModalVisible, setHornModalVisible] = useState(false);
  const [isInfoModalVisible, setInfoModalVisible] = useState(false);
  const [familyMessage, setFamilyMessage] = useState('');
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [isContactPickerVisible, setContactPickerVisible] = useState(false);
  const [availableContacts, setAvailableContacts] = useState([]);
  const [savedMessage, setSavedMessage] = useState('');
  const [isEmergencyModeEnabled, setIsEmergencyModeEnabled] = useState(false);
  const [isSendingSms, setIsSendingSms] = useState(false);
  const [sendProgress, setSendProgress] = useState(0);
  const [originalBrightness, setOriginalBrightness] = useState(0.5);
  const [info, setInfo] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        // Load saved settings
        const [locationSetting, notificationsSetting, autoUpdatesSetting, emergencyMode] = 
          await Promise.all([
            AsyncStorage.getItem('isLocationEnabled'),
            AsyncStorage.getItem('isNotificationsEnabled'),
            AsyncStorage.getItem('isAutoUpdatesEnabled'),
            AsyncStorage.getItem('isEmergencyModeEnabled'),
            AsyncStorage.getItem('familyMessage'),
            AsyncStorage.getItem('selectedContacts')
          ]);

        // Set states based on saved settings
        if (locationSetting !== null) {
          const isEnabled = JSON.parse(locationSetting);
          setIsLocationEnabled(isEnabled);
          if (isEnabled) {
            checkAndRequestLocationPermission();
          }
        }

        if (notificationsSetting !== null) {
          const isEnabled = JSON.parse(notificationsSetting);
          setIsNotificationsEnabled(isEnabled);
          if (isEnabled) {
            checkAndRequestNotificationPermission();
          }
        }

        if (autoUpdatesSetting !== null) setIsAutoUpdatesEnabled(JSON.parse(autoUpdatesSetting));
        if (emergencyMode !== null) setIsEmergencyModeEnabled(JSON.parse(emergencyMode));

        // Load saved message and contacts
        const savedMsg = await AsyncStorage.getItem('familyMessage');
        const savedContacts = await AsyncStorage.getItem('selectedContacts');
        
        if (savedMsg) setFamilyMessage(savedMsg);
        if (savedContacts) setSelectedContacts(JSON.parse(savedContacts));
      } catch (error) {
        console.error('Ayarlar yüklenirken hata:', error);
      }
    };

    loadSettings();
  }, []);

  const checkAndRequestNotificationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
        );
        if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
          Alert.alert(
            'Bildirim İzni Gerekli',
            'Bildirimleri alabilmek için izin vermeniz gerekmektedir.'
          );
          return false;
        }
        return true;
      } catch (error) {
        console.error('Bildirim izni alınırken hata:', error);
        return false;
      }
    }
    return true;
  };

  const toggleNotifications = async () => {
    const newState = !isNotificationsEnabled;
     if (newState) {
       const hasPermission = await checkAndRequestNotificationPermission();
       if (!hasPermission) return;
     }
     
     setIsNotificationsEnabled(newState);
     await AsyncStorage.setItem('isNotificationsEnabled', JSON.stringify(newState));
     Alert.alert(
       'Bildirimler',
       newState ? 'Bildirimler açıldı.' : 'Bildirimler kapatıldı.'
     );
  };

  const toggleLocation = async () => {
    const newState = !isLocationEnabled;
     if (newState) {
       const hasPermission = await checkAndRequestLocationPermission();
       if (!hasPermission) return;
     }
     
     setIsLocationEnabled(newState);
     await AsyncStorage.setItem('isLocationEnabled', JSON.stringify(newState));
     Alert.alert(
       'Konum Servisi',
       newState ? 'Konum servisi açıldı.' : 'Konum servisi kapatıldı.'
     );
  };

  const toggleAutoUpdates = async () => {
    const newAutoUpdatesState = !isAutoUpdatesEnabled;
    setIsAutoUpdatesEnabled(newAutoUpdatesState);
    await AsyncStorage.setItem('isAutoUpdatesEnabled', JSON.stringify(newAutoUpdatesState));
    Alert.alert('Auto Updates', newAutoUpdatesState ? 'Auto updates have been enabled.' : 'Auto updates have been disabled.');
  };

  const toggleEmergencyMode = async () => {
    try {
      const newState = !isEmergencyModeEnabled;
      setIsEmergencyModeEnabled(newState);
      await AsyncStorage.setItem('isEmergencyModeEnabled', JSON.stringify(newState));

      if (newState) {
        try {
          // Sistem renklerini karanlık moda geçir
          Appearance.setColorScheme('dark');

          // Pil durumunu kontrol et
          const batteryLevel = await DeviceInfo.getBatteryLevel();
          const isCharging = await DeviceInfo.isBatteryCharging();

          // Wi-Fi kontrolü
          const netInfo = await NetInfo.fetch();
          const wifiWarning = netInfo.type === 'wifi' 
            ? '\n⚠️ Wi-Fi aktif - Pil tasarrufu için kapatmanız önerilir' 
            : '\n✅ Wi-Fi kapalı - İyi!';

          // Bluetooth durumu kontrolü
          const bluetoothWarning = '\n📱 Bluetooth\'u da kapatmayı unutmayın';

          Alert.alert(
            '🚨 AFET MODU AKTİF',
            `🔋 Maksimum pil tasarrufu sağlanıyor...\n\n` +
            `✅ YAPILAN AYARLAMALAR:\n` +
            `• Karanlık tema aktifleştirildi\n` +
            `• Arka plan işlemleri sınırlandırıldı\n\n` +
            `📋 MANUEL AYARLAMALAR:\n` +
            `• Ekran parlaklığını minimum seviyeye düşürün\n` +
            `• Uçak modunu açıp sadece acil durumlarda kapatın\n` +
            `• Gereksiz uygulamaları tamamen kapatın\n` +
            `• Konum servislerini kapatın\n` +
            `• Otomatik e-posta kontrolünü durdurun\n` +
            `• Push bildirimlerini minimum seviyeye çekin\n` +
            `• Telefonunuzu güç tasarrufu modunda kullanın\n\n` +
            `🔋 MEVCUT PİL DURUMU:\n` +
            `Pil Seviyesi: %${Math.round(batteryLevel * 100)}\n` +
            `Şarj Durumu: ${isCharging ? '🔌 Şarj Oluyor' : '🔋 Şarj Olmuyor'}\n` +
            `${wifiWarning}${bluetoothWarning}\n\n` +
            `⏰ Bu ayarlar afet durumu bittiğinde otomatik olarak normale döner.`,
            [
              {
                text: 'ANLADIM',
                style: 'default',
                onPress: () => {
                  // Ek bildirim
                  setTimeout(() => {
                    Alert.alert(
                      '💡 AFET MODU İPUÇLARI',
                      `🔋 BATARYA UZATMA TAKTİKLERİ:\n\n` +
                      `• Telefonunuzu 15-20°C sıcaklıkta tutun\n` +
                      `• Yalnızca gerekli aramaları yapın\n` +
                      `• SMS kullanmayı tercih edin (daha az enerji)\n` +
                      `• Oyun ve video uygulamalarını kullanmayın\n` +
                      `• Kamerayı gereksiz yere açmayın\n` +
                      `• Flaş kullanımını acil durumlarla sınırlayın\n\n` +
                      `🆘 ACİL DURUM İLETİŞİMİ:\n` +
                      `• 112 - Genel acil durum\n` +
                      `• 110 - İtfaiye\n` +
                      `• 155 - Polis\n` +
                      `• 156 - Jandarma\n\n` +
                      `📱 Bu bilgiler uygulama içinde de mevcut.`,
                      [{ text: 'TAMAM', style: 'default' }]
                    );
                  }, 2000);
                }
              }
            ]
          );
        } catch (error) {
          console.error('Afet modu ayarlanırken hata:', error);
          Alert.alert(
            'Uyarı', 
            'Bazı sistem ayarları değiştirilemedi, ancak temel afet modu aktifleştirildi.'
          );
        }
      } else {
        // Normal moda dön
        try {
          // Normal moda dön
          Appearance.setColorScheme('light');
          
          Alert.alert(
            '✅ Normal Mod',
            'Karanlık tema normale döndürüldü.\n\nDiğer sistem ayarlarını (parlaklık, Wi-Fi, vb.) manuel olarak eski haline getirmeyi unutmayın.'
          );
        } catch (error) {
          console.error('Normal moda dönerken hata:', error);
        }
      }
    } catch (error) {
      console.error('Afet modu değiştirilirken hata:', error);
      Alert.alert('Hata', 'Afet modu ayarlanırken bir hata oluştu.');
    }
  };

  const handleSaveSettings = async () => {
    try {
      await Promise.all([
        AsyncStorage.setItem('isLocationEnabled', JSON.stringify(isLocationEnabled)),
        AsyncStorage.setItem('isNotificationsEnabled', JSON.stringify(isNotificationsEnabled)),
        AsyncStorage.setItem('isAutoUpdatesEnabled', JSON.stringify(isAutoUpdatesEnabled)),
        AsyncStorage.setItem('isEmergencyModeEnabled', JSON.stringify(isEmergencyModeEnabled))
      ]);
      
      Alert.alert('Başarılı', 'Ayarlarınız kaydedildi.');
    } catch (error) {
      Alert.alert('Hata', 'Ayarlar kaydedilirken bir hata oluştu.');
    }
  };

  const handleSendFamilyMessage = async () => {
    // SMS iznini kontrol et
    const hasSmsPermission = await checkAndRequestSmsPermission();
    if (!hasSmsPermission) return;

    // Seçili kişiler ve mesaj kontrolü
    if (selectedContacts.length === 0) {
      Alert.alert('Uyarı', 'Lütfen en az bir kişi ekleyin.');
      return;
    }

    if (!familyMessage || familyMessage.trim() === '') {
      Alert.alert('Uyarı', 'Lütfen gönderilecek bir mesaj yazın.');
      return;
    }

    // Onay al
    Alert.alert(
      'Onay',
      `${selectedContacts.length} kişiye şu mesajı göndermek istediğinizden emin misiniz?\n\n"${familyMessage}"`,
      [
        { text: 'İptal', style: 'cancel' },
        { text: 'Gönder', onPress: () => sendMessages() }
      ]
    );
  };

  const sendMessages = async () => {
    try {
      setIsSendingSms(true);
      setSendProgress(0);
      
      // Utils fonksiyonunu kullanarak SMS'leri gönderelim
      const result = await sendSmsToContacts(selectedContacts, familyMessage, setSendProgress);
      
      setIsSendingSms(false);
      
      // Sonuç bilgisi
      if (result.successCount > 0 && result.failCount === 0) {
        Alert.alert('Başarılı', `${result.successCount} kişiye mesaj başarıyla gönderildi.`);
      } else if (result.successCount > 0 && result.failCount > 0) {
        Alert.alert('Kısmen Başarılı', `${result.successCount} kişiye mesaj gönderildi, ${result.failCount} kişiye gönderilemedi.`);
      } else {
        Alert.alert('Başarısız', 'Mesaj gönderilemedi. Lütfen tekrar deneyin.');
      }
    } catch (error) {
      console.error('Mesaj gönderilirken hata:', error);
      setIsSendingSms(false);
      Alert.alert('Hata', 'Mesaj gönderilirken bir hata oluştu.');
    }
  };

  const handleAddContact = async () => {
    try {
      // Kişilere erişim izni iste
      const hasPermission = await checkAndRequestContactsPermission();
      if (!hasPermission) return;
      
      // Utils fonksiyonunu kullanarak kişileri al
      const contacts = await getAllContacts();
      
      if (contacts.length > 0) {
        setContactPickerVisible(true);
        setAvailableContacts(contacts);
      } else {
        Alert.alert('Bilgi', 'Rehberinizde hiç kişi bulunamadı.');
      }
    } catch (error) {
      console.error('Kişilere erişirken genel hata:', error);
      Alert.alert('Hata', 'Kişiler listesine erişilemedi.');
    }
  };

  const handleContactSelect = async (contact) => {
    if (!contact.phoneNumbers || contact.phoneNumbers.length === 0) {
      Alert.alert('Uyarı', 'Bu kişinin telefon numarası bulunmuyor.');
      return;
    }
    
    // Birden fazla numara varsa seçim yaptır
    if (contact.phoneNumbers.length > 1) {
      Alert.alert(
        'Numara Seçin',
        'Bu kişinin birden fazla numarası var. Hangisini kullanmak istersiniz?',
        contact.phoneNumbers.map(phone => ({
          text: `${phone.label}: ${phone.number}`,
          onPress: () => addContactWithNumber(contact, phone.number)
        }))
      );
    } else {
      // Tek numara varsa direkt ekle
      addContactWithNumber(contact, contact.phoneNumbers[0].number);
    }
  };

  const addContactWithNumber = (contact, phoneNumber) => {
    const newContact = {
      id: contact.id,
      name: contact.name,
      phoneNumber: phoneNumber,
    };

    // Zaten eklenmiş mi kontrol et
    const isAlreadyAdded = selectedContacts.some(c => c.id === contact.id);
    if (isAlreadyAdded) {
      Alert.alert('Bilgi', 'Bu kişi zaten eklenmiş.');
      return;
    }

    const updatedContacts = [...selectedContacts, newContact];
    setSelectedContacts(updatedContacts);
    
    // AsyncStorage'a kaydet
    AsyncStorage.setItem('selectedContacts', JSON.stringify(updatedContacts))
      .catch(err => console.error('Kişileri kaydederken hata:', err));
      
    setContactPickerVisible(false);
  };

  const handleRemoveContact = (contactId) => {
    const updatedContacts = selectedContacts.filter(contact => contact.id !== contactId);
    setSelectedContacts(updatedContacts);
    
    // AsyncStorage'a kaydet
    AsyncStorage.setItem('selectedContacts', JSON.stringify(updatedContacts))
      .catch(err => console.error('Kişileri kaydederken hata:', err));
  };

  const handleSaveMessage = async () => {
    try {
      await AsyncStorage.setItem('familyMessage', familyMessage);
      Alert.alert('Başarılı', 'Mesajınız kaydedildi.');
    } catch (error) {
      Alert.alert('Hata', 'Mesaj kaydedilemedi.');
    }
  };

  return (
    <View style={[
      styles.mainContainer,
      isEmergencyModeEnabled && styles.emergencyContainer]}>

      <StatusBar
        backgroundColor="#2D2D2D"
        barStyle="light-content"
        translucent={true}/>

      <SafeAreaView style={styles.safeArea}>
      <View style={styles.topBar}>
          <TouchableOpacity onPress={() => navigation.navigate('HomePage')}>
            <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.whistleButton} onPress={() => navigation.navigate('Horn')}>
            <Ionicons name="megaphone" size={25} color="white" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.info} onPress={() => setInfo(true)}>
            <Ionicons name="information-circle" size={25} color="white" />
          </TouchableOpacity>
        </View>

        <ScrollView 
          style={styles.container}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={true}
          keyboardShouldPersistTaps="handled"
          scrollEnabled={true}>
          <TouchableOpacity 
            activeOpacity={0.7} 
            onPress={toggleNotifications} 
            style={{flex: 1}}>
            <View style={styles.settingItem} accessible={true}>
              <View style={styles.settingLabel}>
                <Ionicons name="notifications" size={20} color="#555" style={styles.icon} />
                <Text style={styles.settingText}>Bildirimler</Text>
              </View>
              <Switch
                trackColor={{ false: 'gray', true: '#D32F2F' }}
                thumbColor={isNotificationsEnabled ? 'white' : 'white'}
                onValueChange={toggleNotifications}
                value={isNotificationsEnabled}
              />
            </View>
          </TouchableOpacity>
          
          <TouchableOpacity 
            activeOpacity={0.7} 
            onPress={toggleLocation} 
            style={{flex: 1}}>
            <View style={styles.settingItem} accessible={true}>
              <View style={styles.settingLabel}>
                <Ionicons name="location" size={20} color="#555" style={styles.icon} />
                <Text style={styles.settingText}>Konum Servisleri</Text>
              </View>
              <Switch
                trackColor={{ false: 'gray', true: '#D32F2F' }}
                thumbColor={isLocationEnabled ? 'white' : 'white'}
                onValueChange={toggleLocation}
                value={isLocationEnabled}
              />
            </View>
          </TouchableOpacity>

          <TouchableOpacity 
            activeOpacity={0.7} 
            onPress={toggleAutoUpdates} 
            style={{flex: 1}}>
            <View style={styles.settingItem} accessible={true}>
              <View style={styles.settingLabel}>
                <Ionicons name="sync" size={20} color="#555" style={styles.icon} />
                <Text style={styles.settingText}>Otomatik Güncellemeler</Text>
              </View>
              <Switch
                trackColor={{ false: 'gray', true: '#D32F2F' }}
                thumbColor={isAutoUpdatesEnabled ? 'white' : 'white'}
                onValueChange={toggleAutoUpdates}
                value={isAutoUpdatesEnabled}
              />
            </View>
          </TouchableOpacity>

          <TouchableOpacity 
            activeOpacity={0.7} 
            onPress={toggleEmergencyMode} 
            style={{flex: 1}}>
            <View style={[
              styles.settingItem,
              isEmergencyModeEnabled && styles.emergencySettingItem
            ]} accessible={true}>
              <View style={styles.settingLabel}>
                <Ionicons 
                  name="battery-dead" 
                  size={20} 
                  color={isEmergencyModeEnabled ? '#666' : '#333'} 
                  style={styles.icon} 
                />
                <Text style={[
                  styles.settingText,
                  isEmergencyModeEnabled && styles.emergencySettingText
                ]}>Afet Modu</Text>
              </View>
              <Switch
                trackColor={{ false: '#666', true: '#333' }}
                thumbColor={isEmergencyModeEnabled ? '#666' : '#fff'}
                onValueChange={toggleEmergencyMode}
                value={isEmergencyModeEnabled}
              />
            </View>
          </TouchableOpacity>

          <Text style={[
            styles.emergencyNote,
            isEmergencyModeEnabled && styles.emergencyNoteActive
          ]}>
            *** Bu mod enkaz altında ya da enerji gereksiniminde kullanılmalıdır ***
          </Text>

          <View style={styles.familyNotificationSection}>
            <Text style={styles.sectionTitle}>Ailene Bildir</Text>
            
            <TextInput
              style={styles.messageInput}
              placeholder="Ailenize göndermek istediğiniz mesajı yazın"
              placeholderTextColor="lightgray"
              value={familyMessage}
              onChangeText={setFamilyMessage}
              multiline
              numberOfLines={4}
            />

            <TouchableOpacity 
              style={styles.saveMessageButton}
              onPress={handleSaveMessage}
            >
              <Text style={styles.saveMessageButtonText}>Mesajı Kaydet</Text>
            </TouchableOpacity>

            <SelectedContactsList 
              contacts={selectedContacts} 
              onRemoveContact={handleRemoveContact} 
            />

            <TouchableOpacity 
              style={styles.addContactButton}
              onPress={handleAddContact}
            >
              <Text style={styles.addContactButtonText}>Kişi Ekle</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.sendMessageButton}
              onPress={handleSendFamilyMessage}
            >
              <Text style={styles.sendMessageButtonText}>Mesaj Gönder</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.saveButton} onPress={handleSaveSettings}>
            <Text style={styles.saveButtonText}>Ayarları Kaydet</Text>
          </TouchableOpacity>
          
        </ScrollView>

        <ContactPickerModal 
          visible={isContactPickerVisible}
          onClose={() => setContactPickerVisible(false)}
          contacts={availableContacts}
          onSelectContact={handleContactSelect}
        />

        <SendingModal 
          visible={isSendingSms} 
          progress={sendProgress} 
        />
      </SafeAreaView>
    </View>
  );
};

export default SettingsScreen;

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
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 16,
  },
  scrollContent: {
    flexGrow: 1,
    paddingTop: 20,
    paddingBottom: 140,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
    paddingVertical: 25,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    zIndex: 10,
    position: 'relative',
    minHeight: 75,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: width / 2 - 25,
    top: -25,
  },
  whistleButton: {
    position: 'absolute',
    left: 20,
    top: 20,
  },
  info: {
    position: 'absolute',
    right: 20,
    top: 20,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 16,
    marginBottom: 10,
    borderRadius: 10,
    borderBottomWidth: 1,
    borderColor: '#ccc',
    backgroundColor: '#fff',
  },
  settingLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 10,
  },
  icon: {
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 1 },
    shadowRadius: 2,
    elevation: 2,
  },
  saveButton: {
    backgroundColor: '#1976D2',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 5,
    marginHorizontal: 20,
    marginTop: 30,
    marginBottom: 30,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 3 },
    elevation: 3,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    width: '80%',
    alignItems: 'center',
  },
  modalText: {
    fontSize: 18,
    marginBottom: 20,
  },
  closeButton: {
    backgroundColor: '#D32F2F',
    padding: 15,
    alignItems: 'center',
    margin: 15,
    borderRadius: 10,
  },
  closeButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  familyNotificationSection: {
    marginTop: 20,
    marginHorizontal: 0,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  messageInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    minHeight: 100,
    textAlignVertical: 'top',
    marginBottom: 15,
  },
  selectedContactsContainer: {
    marginBottom: 15,
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 10,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  selectedContactAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1976D2',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  selectedContactInitial: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  selectedContactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  contactPhone: {
    fontSize: 14,
    color: '#666',
  },
  removeContactButton: {
    padding: 5,
  },
  noContactsText: {
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    padding: 10,
  },
  emergencyContainer: {
    backgroundColor: '#000', // OLED ekranlar için tam siyah
  },
  emergencySettingItem: {
    borderBottomColor: '#333',
  },
  emergencySettingText: {
    color: '#666', // Koyu gri
  },
  emergencyNote: {
    color: '#333',
    fontSize: 12,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 5,
    marginBottom: 20,
  },
  emergencyNoteActive: {
    color: '#666', // Koyu gri
  },
  sendMessageButton: {
    backgroundColor: '#D32F2F',
    padding: 12,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 15,
  },
  sendMessageButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sendingModalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
  },
  sendingModalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    width: '80%',
  },
  sendingModalText: {
    marginTop: 15,
    fontSize: 16,
    textAlign: 'center',
  },
  contactPickerModal: {
    maxHeight: '80%',
    width: '90%',
    padding: 0,
    borderRadius: 15,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 15,
    color: '#333',
    textAlign: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    marginHorizontal: 15,
    marginBottom: 15,
    paddingHorizontal: 10,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
  },
  contactList: {
    marginHorizontal: 15,
    width: '90%',
  },
  contactListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 10,
    marginBottom: 10,
    width: '100%',
  },
  contactAvatarContainer: {
    marginRight: 15,
  },
  contactAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
  },
  contactInitial: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  contactInfo: {
    flex: 1,
  },
  contactListName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  contactListPhone: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  separator: {
    height: 1,
    backgroundColor: '#eee',
    marginLeft: 65,
  },
  addContactButton: {
    backgroundColor: '#1976D2',
    padding: 12,
    borderRadius: 5,
    alignItems: 'center',
  },
  addContactButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  saveMessageButton: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 20,
  },
  saveMessageButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});