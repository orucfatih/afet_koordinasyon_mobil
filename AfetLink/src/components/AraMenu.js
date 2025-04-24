import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const AraMenu = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
                  {/* Geri Butonu */}
                  <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate("AnaMenu")}>
        <Ionicons name="arrow-back" size={24} color="black" />
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.button}
        onPress={() => alert('E-devlet ile giriş henüz uygulanmadı.')}
      >
        <Text style={styles.buttonText}>E-devlet ile giriş</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('LoginPage')}
      >
        <Text style={styles.buttonText}>E-mail ile giriş</Text>
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
  },
  backButton: {
    position: "absolute",
    top: 40, // Üstten boşluk
    left: 20, // Soldan boşluk
    padding: 10,
  },
  button: {
    backgroundColor: 'red', // Arka plan rengi
    paddingVertical: 12,
    paddingHorizontal: 24,
    width: '80%',
    borderRadius: 8,
    marginVertical: 10,
  },
  buttonText: {
    color: 'white', // Yazı rengi
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default AraMenu;
