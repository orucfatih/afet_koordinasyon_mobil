import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const AraMenu2 = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.button}
        onPress={() => alert('E-devlet ile giriş henüz uygulanmadı.')}
      >
        <Text style={styles.buttonText}>E-devlet ile giriş</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.button}
        onPress={() => navigation.navigate('LoginPage2')}
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

export default AraMenu2;
