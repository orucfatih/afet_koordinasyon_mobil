import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

const AnaMenu = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/images/deneme.png')}
        style={styles.logo}
      />
      <Text style={styles.title}>Ana Menü</Text>
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.navigate('AraMenu')}>

          <View style={styles.buttonContent}>
            <MaterialCommunityIcons name="account" size={24} color="white" />
            <Text style={styles.buttonText}>Vatandaş Giriş</Text>
          </View>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.navigate('AraMenu2')}>
            
          <View style={styles.buttonContent}>
            <MaterialCommunityIcons name="account-tie" size={24} color="white" />
            <Text style={styles.buttonText}>Personel Giriş</Text>
          </View>
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
    borderRadius: 120,
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
    backgroundColor: 'red',
    padding: 12,
    borderRadius: 10,
    width: '48%',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});

export default AnaMenu;