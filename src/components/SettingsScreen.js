import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Switch, Alert, Image, Modal } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';

const SettingsScreen = () => {
  const [isNotificationsEnabled, setIsNotificationsEnabled] = useState(false);
  const [isLocationEnabled, setIsLocationEnabled] = useState(false);
  const [isAutoUpdatesEnabled, setIsAutoUpdatesEnabled] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isLanguageModalVisible, setIsLanguageModalVisible] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      const locationSetting = await AsyncStorage.getItem('isLocationEnabled');
      const notificationsSetting = await AsyncStorage.getItem('isNotificationsEnabled');
      const autoUpdatesSetting = await AsyncStorage.getItem('isAutoUpdatesEnabled');
      const languageSetting = await AsyncStorage.getItem('selectedLanguage');

      if (locationSetting !== null) setIsLocationEnabled(JSON.parse(locationSetting));
      if (notificationsSetting !== null) setIsNotificationsEnabled(JSON.parse(notificationsSetting));
      if (autoUpdatesSetting !== null) setIsAutoUpdatesEnabled(JSON.parse(autoUpdatesSetting));
      if (languageSetting !== null) setSelectedLanguage(languageSetting);
    };
    loadSettings();
  }, []);

  const toggleNotifications = async () => {
    const newNotificationsState = !isNotificationsEnabled;
    setIsNotificationsEnabled(newNotificationsState);
    await AsyncStorage.setItem('isNotificationsEnabled', JSON.stringify(newNotificationsState));
    Alert.alert('Notifications', newNotificationsState ? 'Notifications have been enabled.' : 'Notifications have been disabled.');
  };

  const toggleLocation = async () => {
    const newLocationState = !isLocationEnabled;
    setIsLocationEnabled(newLocationState);
    await AsyncStorage.setItem('isLocationEnabled', JSON.stringify(newLocationState));
    Alert.alert('Location Service', newLocationState ? 'Location service has been enabled.' : 'Location service has been disabled.');
  };

  const toggleAutoUpdates = async () => {
    const newAutoUpdatesState = !isAutoUpdatesEnabled;
    setIsAutoUpdatesEnabled(newAutoUpdatesState);
    await AsyncStorage.setItem('isAutoUpdatesEnabled', JSON.stringify(newAutoUpdatesState));
    Alert.alert('Auto Updates', newAutoUpdatesState ? 'Auto updates have been enabled.' : 'Auto updates have been disabled.');
  };

  const handleLanguageChange = async (value) => {
    setSelectedLanguage(value);
    await AsyncStorage.setItem('selectedLanguage', value);
    Alert.alert('Language Changed', `The app language has been changed to ${value === 'en' ? 'English' : 'Türkçe'}.`);
  };

  const handleSaveSettings = () => {
    Alert.alert('Settings Saved', 'Your changes have been saved successfully.');
  };

  return (
    <View style={styles.container}>
            <View style={styles.topBar}>
              <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
              <TouchableOpacity style={styles.info}>
                <Icon name="info-outline" size={25} color="white" />
              </TouchableOpacity>
            </View>

      <View style={styles.settingItem}>
        <Text style={styles.settingText}>Language</Text>
        <TouchableOpacity onPress={() => setIsLanguageModalVisible(true)}>
          <Text style={styles.languageText}>{selectedLanguage === 'en' ? 'English' : 'Türkçe'}</Text>
        </TouchableOpacity>
      </View>

      <Modal
        visible={isLanguageModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setIsLanguageModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Language</Text>
            <Picker
              selectedValue={selectedLanguage}
              onValueChange={(itemValue) => {
                handleLanguageChange(itemValue);
                setIsLanguageModalVisible(false);
              }}
            >
              <Picker.Item label="Türkçe" value="tr" />
              <Picker.Item label="English" value="en" />
            </Picker>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setIsLanguageModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      <View style={styles.settingItem}>
        <Text style={styles.settingText}>Notifications</Text>
        <Switch
          trackColor={{ false: 'gray', true: '#D32F2F' }}
          thumbColor={isNotificationsEnabled ? 'white' : 'white'}
          onValueChange={toggleNotifications}
          value={isNotificationsEnabled}
        />
      </View>

      <View style={styles.settingItem}>
        <Text style={styles.settingText}>Location Services</Text>
        <Switch
          trackColor={{ false: 'gray', true: '#D32F2F' }}
          thumbColor={isLocationEnabled ? 'white' : 'white'}
          onValueChange={toggleLocation}
          value={isLocationEnabled}
        />
      </View>

      <View style={styles.settingItem}>
        <Text style={styles.settingText}>Auto Updates</Text>
        <Switch
          trackColor={{ false: 'gray', true: '#D32F2F' }}
          thumbColor={isAutoUpdatesEnabled ? 'white' : 'white'}
          onValueChange={toggleAutoUpdates}
          value={isAutoUpdatesEnabled}
        />
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={handleSaveSettings}>
        <Text style={styles.saveButtonText}>Save Settings</Text>
      </TouchableOpacity>
    </View>
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
    backgroundColor: '#2D2D2D', // Koyu arka plan
    paddingVertical: 15,
    borderTopWidth: 2,
    borderTopColor: '#444',
    marginHorizontal: 0,
    elevation: 5,  // Gölgeleme efekti
    borderBottomLeftRadius: 20, // Üst sol köşe radius
    borderBottomRightRadius: 20, // Üst sağ köşe radius
  },
  logoImage: {
    width: 50,
    top: 5,
    left: 30,
    height: 50,
  },
  info: {
    top: 20,
    right: 40,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderColor: '#ccc',
  },
  languageText: {
    color: '#1976D2',
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 10,
    width: '80%',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  closeButton: {
    backgroundColor: '#D32F2F',
    padding: 10,
    borderRadius: 5,
    marginTop: 10,
    alignItems: 'center',
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  saveButton: {
    backgroundColor: '#1976D2',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 5,
    marginHorizontal: 20,
    marginTop: 30,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
