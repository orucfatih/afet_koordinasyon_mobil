import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { getUser, logout } from '../redux/userSlice';
import { Loading, CustomButton, UpdatePassword } from './index.js';
import Icon from 'react-native-vector-icons/FontAwesome';

const ProfileScreen = () => {
  const dispatch = useDispatch();
  const { user, loading } = useSelector(state => state.user);
  const [isUpdatePasswordVisible, setIsUpdatePasswordVisible] = useState(false);

  useEffect(() => {
    dispatch(getUser());
  }, [dispatch]);

  const handleLogout = () => {
    Alert.alert(
      'Çıkış Yap',
      'Çıkış yapmak istediğinizden emin misiniz?',
      [
        {
          text: 'İptal',
          style: 'cancel'
        },
        {
          text: 'Çıkış Yap',
          onPress: () => dispatch(logout())
        }
      ]
    );
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Image 
          source={require('../../assets/images/deneme.png')} 
          style={styles.logo}
        />
        <Text style={styles.title}>Profil</Text>
      </View>

      <View style={styles.profileInfo}>
        <View style={styles.infoRow}>
          <Icon name="envelope" size={20} color="#333" />
          <Text style={styles.infoText}>{user?.email || 'E-posta bulunamadı'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Icon name="phone" size={20} color="#333" />
          <Text style={styles.infoText}>{user?.phone || 'Telefon bulunamadı'}</Text>
        </View>
      </View>

      <View style={styles.buttonContainer}>
        <CustomButton
          title="Şifre Değiştir"
          onPress={() => setIsUpdatePasswordVisible(true)}
        />
        <CustomButton
          title="Çıkış Yap"
          onPress={handleLogout}
          style={styles.logoutButton}
          icon={<Icon name="sign-out" size={20} color="#fff" />}
        />
      </View>

      {isUpdatePasswordVisible && (
        <UpdatePassword
          visible={isUpdatePasswordVisible}
          onClose={() => setIsUpdatePasswordVisible(false)}
        />
      )}
    </View>
  );
};

export default ProfileScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  profileInfo: {
    marginBottom: 30,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  infoText: {
    marginLeft: 10,
    fontSize: 16,
    color: '#333',
  },
  buttonContainer: {
    marginTop: 20,
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    marginTop: 10,
  },
});