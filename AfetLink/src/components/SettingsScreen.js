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
  SafeAreaView
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Ionicons from 'react-native-vector-icons/Ionicons';
import DeviceInfo from 'react-native-device-info';
import { Appearance } from 'react-native';
import NetInfo from '@react-native-community/netinfo';

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
          setIsNotificationsEnabled(false);
          await AsyncStorage.setItem('isNotificationsEnabled', 'false');
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

  const checkAndRequestLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
        );
        if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
          Alert.alert(
            'Konum İzni Gerekli',
            'Konum servislerini kullanabilmek için izin vermeniz gerekmektedir.'
          );
          setIsLocationEnabled(false);
          await AsyncStorage.setItem('isLocationEnabled', 'false');
          return false;
        }
        return true;
      } catch (error) {
        console.error('Konum izni alınırken hata:', error);
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
          if (netInfo.type === 'wifi') {
            Alert.alert(
              'Wi-Fi Aktif',
              'Pil tasarrufu için Wi-Fi bağlantınızı kapatmanız önerilir.'
            );
          }

          Alert.alert(
            'Afet Modu Aktif',
            `Pil tasarrufu için aşağıdaki önlemler alındı:\n\n` +
            '- Karanlık tema aktifleştirildi (OLED ekranlarda maksimum tasarruf)\n' +
            '- Arka plan işlemleri sınırlandırıldı\n\n' +
            'Öneriler:\n' +
            '- Koyu renk uygulamalar kullanın\n' +
            '- Wi-Fi ve Bluetooth\'u kapatın\n' +
            '- Gereksiz uygulamaları kapatın\n' +
            '- Telefonu güç tasarrufu modunda kullanın\n\n' +
            `Mevcut Pil Durumu: %${Math.round(batteryLevel * 100)}\n` +
            `Şarj Durumu: ${isCharging ? 'Şarj Oluyor' : 'Şarj Olmuyor'}`
          );
        } catch (error) {
          console.error('Afet modu ayarlanırken hata:', error);
        }
      } else {
        // Normal moda dön
        try {
          Appearance.setColorScheme('light');
        } catch (error) {
          console.error('Normal moda dönerken hata:', error);
        }
      }
    } catch (error) {
      console.error('Afet modu değiştirilirken hata:', error);
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

  const handleAddContact = async () => {
    try {
      const { status } = await Contacts.requestPermissionsAsync();
      if (status === 'granted') {
        const { data } = await Contacts.getContactsAsync({
          fields: [Contacts.Fields.PhoneNumbers, Contacts.Fields.Name],
        });

        if (data.length > 0) {
          setContactPickerVisible(true);
          setAvailableContacts(data);
        }
      }
    } catch (error) {
      console.error('Error accessing contacts:', error);
      Alert.alert('Hata', 'Kişiler listesine erişilemedi.');
    }
  };

  const handleContactSelect = async (contact) => {
    const newContact = {
      id: contact.id,
      name: contact.name,
      phoneNumber: contact.phoneNumbers?.[0]?.number,
    };

    const updatedContacts = [...selectedContacts, newContact];
    setSelectedContacts(updatedContacts);
    await AsyncStorage.setItem('selectedContacts', JSON.stringify(updatedContacts));
    setContactPickerVisible(false);
  };

  const handleRemoveContact = (contactId) => {
    setSelectedContacts(prev => prev.filter(contact => contact.id !== contactId));
  };

  const handleSaveMessage = async () => {
    try {
      await AsyncStorage.setItem('familyMessage', familyMessage);
      Alert.alert('Başarılı', 'Mesajınız kaydedildi.');
    } catch (error) {
      Alert.alert('Hata', 'Mesaj kaydedilemedi.');
    }
  };

  const renderContactPicker = () => (
    <Modal
      visible={isContactPickerVisible}
      transparent={true}
      animationType="slide"
      onRequestClose={() => setContactPickerVisible(false)}>

      <View style={styles.modalContainer}>
        <View style={[styles.modalContent, styles.contactPickerModal]}>
          <Text style={styles.modalTitle}>Kişi Seçin</Text>
          <FlatList
            data={availableContacts}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.contactListItem}
                onPress={() => handleContactSelect(item)}
              >
                <Text style={styles.contactListName}>{item.name}</Text>
                {item.phoneNumbers?.[0] && (
                  <Text style={styles.contactListPhone}>
                    {item.phoneNumbers[0].number}
                  </Text>
                )}
              </TouchableOpacity>
            )}
          />
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => setContactPickerVisible(false)}
          >
            <Text style={styles.closeButtonText}>Kapat</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
   );

   return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={[
        styles.mainContainer,
        isEmergencyModeEnabled && styles.emergencyContainer]}>

        <StatusBar
          backgroundColor="#2D2D2D"
          barStyle="light-content"
          translucent={true}/>

        <SafeAreaView style={styles.safeArea}>
          <View style={styles.topBar}>
            <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          </View>

          <ScrollView 
            style={styles.container}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}>
            <View style={styles.settingItem}>
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
            
            <View style={styles.settingItem}>
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

            <View style={styles.settingItem}>
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

            <View style={[
              styles.settingItem,
              isEmergencyModeEnabled && styles.emergencySettingItem
            ]}>
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
                placeholder="Ailenize göndermek istediğiniz mesajı yazın..."
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

              <View style={styles.selectedContactsContainer}>
                {selectedContacts.map(contact => (
                  <View key={contact.id} style={styles.contactItem}>
                    <Text style={styles.contactName}>{contact.name}</Text>
                    <Text style={styles.contactPhone}>{contact.phoneNumber}</Text>
                    <TouchableOpacity onPress={() => handleRemoveContact(contact.id)}>
                      <Text style={styles.removeContact}>X</Text>
                    </TouchableOpacity>
                  </View>
                ))}
              </View>

              <TouchableOpacity 
                style={styles.addContactButton}
                onPress={handleAddContact}
              >
                <Text style={styles.addContactButtonText}>Kişi Ekle</Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity style={styles.saveButton} onPress={handleSaveSettings}>
              <Text style={styles.saveButtonText}>Ayarları Kaydet</Text>
            </TouchableOpacity>
            
          </ScrollView>

          {renderContactPicker()}
        </SafeAreaView>
      </View>
    </TouchableWithoutFeedback>
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
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2D2D2D',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 15,
    minHeight: 75,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: width / 2 - 25,
    marginTop: 10,
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
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
  },
  closeButtonText: {
    color: '#fff',
    fontWeight: 'bold',
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
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 10,
    borderRadius: 5,
    marginBottom: 5,
  },
  contactName: {
    fontSize: 16,
    color: '#333',
  },
  removeContact: {
    color: '#D32F2F',
    fontSize: 16,
    fontWeight: 'bold',
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
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
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
  contactPickerModal: {
    maxHeight: '80%',
    width: '90%',
  },
  contactListItem: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  contactListName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  contactListPhone: {
    fontSize: 14,
    color: '#666',
  },
  contactPhone: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
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
});