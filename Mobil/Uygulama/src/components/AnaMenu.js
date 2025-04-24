import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faUser, faUserTie } from '@fortawesome/free-solid-svg-icons';

const AnaMenu = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/images/deneme3.png')} // Logo remains an image
        style={styles.logo}
      />
      <Text style={styles.title}>Ana Menü</Text>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('AraMenu')}  
      >
        <FontAwesomeIcon icon={faUser} size={24} color="white" style={styles.icon} />
        <Text style={styles.buttonText}>Vatandaş Giriş</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('AraMenu2')}
      >
        <FontAwesomeIcon icon={faUserTie} size={24} color="white" style={styles.icon} />
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