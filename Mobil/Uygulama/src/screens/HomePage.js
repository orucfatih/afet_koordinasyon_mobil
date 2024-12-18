import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Dimensions, FlatList } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons'; // İkon setini seçebilirsiniz


const { width } = Dimensions.get('window'); // Ekran genişliği

// Ekran Bileşenleri
const EarthquakeScreen = () => {
  const [currentIndex, setCurrentIndex] = useState(0); // Sayfa göstergesi için state

  const earthquakeData = [
    { id: '1', magnitude: '3.6', location: 'OLUCAK - NURDAĞI (GAZİANTEP)', time: '14:35', date: '09.12.2024' },
    { id: '2', magnitude: '4.2', location: 'İSTANBUL (SARIYER)', time: '12:45', date: '09.12.2024' },
    { id: '3', magnitude: '2.8', location: 'ANKARA (ÇANKAYA)', time: '11:15', date: '09.12.2024' },
    // Daha fazla deprem verisi buraya eklenebilir
  ];

  const handleScroll = (event) => {
    const scrollX = event.nativeEvent.contentOffset.x;
    const activeIndex = Math.round(scrollX / width);
    setCurrentIndex(activeIndex);
  };

  const renderEarthquakeCard = ({ item }) => (
    <View style={styles.earthquakeCard}>
      <View style={styles.magnitudeCircle}>
        <Text style={styles.magnitudeText}>{item.magnitude}</Text>
      </View>
      <View style={styles.earthquakeInfo}>
        <Text style={styles.earthquakeLocation}>{item.location}</Text>
        <Text style={styles.earthquakeTime}>{item.time}</Text>
        <Text style={styles.earthquakeDate}>{item.date}</Text>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Üst Bar */}
      <View style={styles.topBar}>
        <Image source={require('../../assets/images/afad-logo2.png')} style={styles.logoImage} />
        <TouchableOpacity>
          <Icon name="info-outline" size={25} color="white" />
        </TouchableOpacity>
      </View>

      {/* Son Depremler Başlık */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Son Depremler</Text>
        <TouchableOpacity>
          <Text style={styles.viewAll}>Tümünü Gör</Text>
        </TouchableOpacity>
      </View>

      {/* Deprem Kartları */}
      <FlatList
        data={earthquakeData}
        renderItem={renderEarthquakeCard}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onScroll={handleScroll}
        style={styles.slider}
      />

      {/* Sayfa Göstergesi */}
      <View style={styles.pagination}>
        {earthquakeData.map((_, index) => (
          <View
            key={index}
            style={[styles.dot, currentIndex === index && styles.activeDot]}
          />
        ))}
      </View>

      {/* Enkaz Altındayım Butonu */}
      <TouchableOpacity style={styles.bigButton}>
        <Text style={styles.bigButtonText}>ENKAZ ALTINDAYIM</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const ProfileScreen = () => (
  <View style={styles.screen}>
    <Icon name="person" size={100} color="white" />
    <Text style={styles.screenText}>Profil Sayfası</Text>
  </View>
);

const SettingsScreen = () => (
  <View style={styles.screen}>
    <Icon name="settings" size={100} color="white" />
    <Text style={styles.screenText}>Ayarlar Sayfası</Text>
  </View>
);
const ChatScreen = () => (
  <View style={styles.screen}>
    <Icon name="chat" size={100} color="white" />
    <Text style={styles.screenText}>Chat Sayfası</Text>
  </View>
);
// Ana Bileşen
const HomePage = () => {
  const [currentTab, setCurrentTab] = useState('Earthquake');

  const renderScreen = () => {
    switch (currentTab) {
      case 'Earthquake':
        return <EarthquakeScreen />;
      case 'Profile':
        return <ProfileScreen />;
      case 'Settings':  
        return <SettingsScreen />;
      case 'Chat':
        return <ChatScreen />  
      default:
        return <EarthquakeScreen />;
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.screenContainer}>{renderScreen()}</View>
      <View style={styles.tabBar}>
        <TouchableOpacity
          onPress={() => setCurrentTab('Earthquake')}
          style={[styles.tab, currentTab === 'Earthquake' && styles.activeTab]}
        >
          <Icon name="home" size={currentTab === 'Earthquake' ? 30 : 24} color={currentTab === 'Earthquake' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setCurrentTab('Profile')}
          style={[styles.tab, currentTab === 'Profile' && styles.activeTab]}
        >
          <Icon name="person" size={currentTab === 'Profile' ? 30 : 24} color={currentTab === 'Profile' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setCurrentTab('Settings')}
          style={[styles.tab, currentTab === 'Settings' && styles.activeTab]}
        >
          <Icon name="settings" size={currentTab === 'Settings' ? 30 : 24} color={currentTab === 'Settings' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setCurrentTab('Chat')}
          style={[styles.tab, currentTab === 'Chat' && styles.activeTab]}
        >
          <Icon name="chat" size={currentTab === 'Chat' ? 30 : 24} color={currentTab === 'Chat' ? '#fff' : '#ccc'} />
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default HomePage;

// Stiller
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  screenContainer: {
    flex: 1,
  },
  screen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ff1744',
  },
  screenText: {
    color: 'white',
    fontSize: 20,
    marginTop: 10,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#D32F2F',
    padding: 20,
  },
  logoImage: {
    width: 150,
    height: 40,
    resizeMode: 'cover',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
    paddingHorizontal: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  viewAll: {
    color: '#D32F2F',
    fontWeight: 'bold',
  },
  slider: {
    marginTop: 10,
  },
  earthquakeCard: {
    width: width,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'white',
    marginVertical: 20,
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  magnitudeCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#E0E0E0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  magnitudeText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  earthquakeInfo: {
    alignItems: 'center',
  },
  earthquakeLocation: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  earthquakeTime: {
    fontSize: 16,
    color: '#757575',
  },
  earthquakeDate: {
    fontSize: 16,
    color: '#757575',
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 10,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#E0E0E0',
    marginHorizontal: 5,
  },
  activeDot: {
    backgroundColor: '#D32F2F',
    width: 12,
    height: 12,
  },
  bigButton: {
    marginVertical: 20,
    marginHorizontal: 15,
    padding: 15,
    backgroundColor: '#D32F2F',
    borderRadius: 10,
    alignItems: 'center',
  },
  bigButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#D32F2F',
    paddingVertical: 10,
  },
  tab: {
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: 'white',
  },
});
