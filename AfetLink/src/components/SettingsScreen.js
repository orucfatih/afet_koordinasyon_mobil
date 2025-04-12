import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Switch, Alert, Image, Modal } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

const SettingsScreen = ({ navigation }) => {
  const [isNotificationsEnabled, setIsNotificationsEnabled] = useState(false);
  const [isLocationEnabled, setIsLocationEnabled] = useState(false);
  const [isAutoUpdatesEnabled, setIsAutoUpdatesEnabled] = useState(false);
  const [isHornModalVisible, setHornModalVisible] = useState(false);
  const [isInfoModalVisible, setInfoModalVisible] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      const locationSetting = await AsyncStorage.getItem('isLocationEnabled');
      const notificationsSetting = await AsyncStorage.getItem('isNotificationsEnabled');
      const autoUpdatesSetting = await AsyncStorage.getItem('isAutoUpdatesEnabled');

      if (locationSetting !== null) setIsLocationEnabled(JSON.parse(locationSetting));
      if (notificationsSetting !== null) setIsNotificationsEnabled(JSON.parse(notificationsSetting));
      if (autoUpdatesSetting !== null) setIsAutoUpdatesEnabled(JSON.parse(autoUpdatesSetting));
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

  const handleSaveSettings = () => {
    Alert.alert('Settings Saved', 'Your changes have been saved successfully.');
  };

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <TouchableOpacity style={styles.whistleButton} onPress={() => setHornModalVisible(true)}>
          <Ionicons name="megaphone" size={25} color="white" style={styles.icon} />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.navigate('HomePage')}>
          <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
        </TouchableOpacity>
        <TouchableOpacity style={styles.info} onPress={() => setInfoModalVisible(true)}>
          <Ionicons name="information-circle" size={25} color="white" style={styles.icon} />
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

      <View style={styles.settingsContainer}>
        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="notifications" size={24} color="#007BFF" />
            <Text style={styles.settingText}>Bildirimler</Text>
          </View>
          <Switch value={isNotificationsEnabled} onValueChange={toggleNotifications} />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="location" size={24} color="#007BFF" />
            <Text style={styles.settingText}>Konum Servisleri</Text>
          </View>
          <Switch value={isLocationEnabled} onValueChange={toggleLocation} />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Ionicons name="sync" size={24} color="#007BFF" />
            <Text style={styles.settingText}>Verileri Senkronize Et</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.settingItem} onPress={handleSaveSettings}>
          <View style={styles.settingLeft}>
            <Ionicons name="save" size={24} color="#007BFF" />
            <Text style={styles.settingText}>Save Settings</Text>
          </View>
        </TouchableOpacity>
      </View>
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
    marginTop: 10, // topBar yüksekliği kadar boşluk bırakır
    paddingHorizontal: 15,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderColor: '#ccc',
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
});