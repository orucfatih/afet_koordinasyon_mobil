import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';

const AnaMenu = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/images/deneme3.png')} // Logo için örnek bir resim
        style={styles.logo}
      />
      <Text style={styles.title}>Ana Menü</Text>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('AraMenu')}  
      >
        <Image
          source={require('../../assets/images/vatandas-icon.png')} // Vatandaş Giriş ikonu
          style={styles.icon}
        />
        <Text style={styles.buttonText}>Vatandaş Giriş</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('AraMenu2')}
      >
        <Image
          source={require('../../assets/images/personel-icon.png')} // Personel Giriş ikonu
          style={styles.icon}
        />
        <Text style={styles.buttonText}>Personel Giriş</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    padding: 20,
  },
  welcomeText: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  logo: {
    padding: 10,
    width: 160,
    height: 160,
    marginBottom: 20,
    borderRadius: 120, // Tam bir daire için
    borderWidth: 1,
    borderColor: '#D9DDDC', // Hafif bir çerçeve rengi
    backgroundColor: '#fff', // Arka plan rengini beyaz yapıyoruz
    // Gölgelendirme (iOS)
    shadowColor: 'gray', // Gölgenin rengi
    shadowOffset: { width: 10, height: 10 }, // Gölge yönü
    shadowOpacity: 0.5, // Gölge opaklığı
    shadowRadius: 6, // Gölge yayılımı
    // Gölgelendirme (Android)
    elevation: 20, // Yüksekliği artırarak gölgeyi daha belirgin yapabilirsiniz
  },  
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#333',
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: 'red',
    padding: 12,
    borderRadius: 10,
    width: '80%',
    marginBottom: 15,
  },
  icon: {
    width: 24,
    height: 24,
    marginRight: 10, // İkon ve metin arasındaki boşluk
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    marginLeft: 40,
    fontWeight: 'bold',
  },
});

export default AnaMenu;
