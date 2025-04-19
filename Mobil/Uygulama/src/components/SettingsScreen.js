import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Switch, Alert, Image, Modal, TextInput, FlatList, Keyboard, TouchableWithoutFeedback, ScrollView, Platform, Appearance, useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faBell, faMapMarkerAlt, faSyncAlt, faBullhorn, faInfoCircle, faBatteryQuarter } from '@fortawesome/free-solid-svg-icons';
import { Dimensions } from 'react-native';
import * as Contacts from 'expo-contacts';
import * as Notifications from 'expo-notifications';
import * as Location from 'expo-location';
import * as Brightness from 'expo-brightness';
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
    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
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
  };

  const checkAndRequestLocationPermission = async () => {
    try {
      const { status: existingStatus } = await Location.getForegroundPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Location.requestForegroundPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
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
          // Ekran parlaklığını azalt
          const { status } = await Brightness.requestPermissionsAsync();
          if (status === 'granted') {
            await Brightness.setBrightnessAsync(0.1); // Daha da azalttık
          }

          // Sistem renklerini karanlık moda geçir
          Appearance.setColorScheme('dark');

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
            'Pil tasarrufu için aşağıdaki önlemler alındı:\n\n' +
            '- Ekran parlaklığı minimuma indirildi\n' +
            '- Karanlık tema aktifleştirildi (OLED ekranlarda maksimum tasarruf)\n' +
            '- Arka plan işlemleri sınırlandırıldı\n\n' +
            'Öneriler:\n' +
            '- Koyu renk uygulamalar kullanın\n' +
            '- Wi-Fi ve Bluetooth\'u kapatın\n' +
            '- Gereksiz uygulamaları kapatın\n' +
            '- Telefonu güç tasarrufu modunda kullanın'
          );
        } catch (error) {
          console.error('Afet modu ayarlanırken hata:', error);
        }
      } else {
        // Normal moda dön
        try {
          const { status } = await Brightness.requestPermissionsAsync();
          if (status === 'granted') {
            await Brightness.setBrightnessAsync(0.5);
          }
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
      onRequestClose={() => setContactPickerVisible(false)}
    >
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
        styles.container,
        isEmergencyModeEnabled && styles.emergencyContainer
      ]}>
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.whistleButton} onPress={() => setHornModalVisible(true)}>
            <FontAwesomeIcon icon={faBullhorn} size={25} color="white" style={styles.icon} />
          </TouchableOpacity>
          <TouchableOpacity onPress={() => navigation.navigate('HomePage')}>
            <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.info} onPress={() => setInfoModalVisible(true)}>
            <FontAwesomeIcon icon={faInfoCircle} size={25} color="white" style={styles.icon} />
          </TouchableOpacity>
        </View>

        {/* Horn Modal */}
        <Modal
          visible={isHornModalVisible}
          transparent={true}
          animationType="slide"
          onRequestClose={() => setHornModalVisible(false)}
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalText}>Whistle Button Pressed!</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setHornModalVisible(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* Info Modal */}
        <Modal
          visible={isInfoModalVisible}
          transparent={true}
          animationType="slide"
          onRequestClose={() => setInfoModalVisible(false)}
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalText}>Settings Info</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setInfoModalVisible(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        <ScrollView style={styles.settingsContainer}>
          <View style={styles.settingItem}>
            <View style={styles.settingLabel}>
              <FontAwesomeIcon icon={faBell} size={20} color="#555" style={styles.icon} />
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
              <FontAwesomeIcon icon={faMapMarkerAlt} size={20} color="#555" style={styles.icon} />
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
              <FontAwesomeIcon icon={faSyncAlt} size={20} color="#555" style={styles.icon} />
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
              <FontAwesomeIcon 
                icon={faBatteryQuarter} 
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
          
          <Text style={[
            styles.emergencyNote,
            isEmergencyModeEnabled && styles.emergencyNoteActive
          ]}>
            *** Bu mod enkaz altında ya da enerji gereksiniminde kullanılmalıdır ***
          </Text>
        </ScrollView>

        {renderContactPicker()}
      </View>
    </TouchableWithoutFeedback>
  );
};

export default SettingsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  logoImage: {
    width: 50,
    height: 50,
  },
  whistleButton: {
    padding: 10,
  },
  info: {
    padding: 10,
  },
  settingsContainer: {
    flex: 1,
    marginTop: 10,
    paddingHorizontal: 15,
    marginBottom: 20,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderColor: '#ccc',
    backgroundColor: '#fff',
  },
  settingLabel: {
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
    padding: 15,
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