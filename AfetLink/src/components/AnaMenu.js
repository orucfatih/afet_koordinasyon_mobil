import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const AnaMenu = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/images/deneme3.png')} // Logo remains an image
        style={styles.logo}
      />
      <Text style={styles.title}>Ana Menü</Text>
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.navigate('LoginPage')}
        >
          <Ionicons name="person" size={30} color="#fff" />
          <Text style={styles.buttonText}>Kullanıcı Girişi</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.navigate('LoginPage2')}
        >
          <Ionicons name="people" size={30} color="#fff" />
          <Text style={styles.buttonText}>Personel Girişi</Text>
        </TouchableOpacity>
      </View>
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
  logo: {
    padding: 10,
    width: 160,
    height: 160,
    marginBottom: 20,
    borderRadius: 120, // Circular logo
    borderWidth: 1,
    borderColor: '#D9DDDC',
    backgroundColor: '#fff',
    shadowColor: 'gray',
    shadowOffset: { width: 10, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 6,
    elevation: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#333',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '80%',
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: 'red',
    padding: 12,
    borderRadius: 10,
    width: '48%',
  },
  icon: {
    marginRight: 10, // Space between icon and text
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    marginLeft: 40, // Adjust this if needed for spacing
    fontWeight: 'bold',
  },
});

export default AnaMenu;