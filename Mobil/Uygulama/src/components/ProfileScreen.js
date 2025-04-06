import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { getUser, logout } from '../redux/userSlice';
import { Loading, CustomButton, UpdatePassword } from './index.js';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faEnvelope, faPhone, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';

const ProfileScreen = () => {
  const dispatch = useDispatch();

  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  useEffect(() => {
    dispatch(getUser())
      .unwrap()
      .then((userData) => {
        setName(userData.name || '');
        setSurname(userData.surname || '');
        setEmail(userData.email || '');
        setPhone(userData.phone || '');
      })
      .catch((error) => console.log('Kullanıcı bilgileri alınırken hata:', error));
  }, [dispatch]);

  const [updatingScreen, setUpdatingScreen] = useState(false);
  const { isLoading } = useSelector((state) => state.user);

  const handleLogout = () => {
    dispatch(logout());
  };

  if (isLoading) {
    return <Loading />;
  }

  if (updatingScreen) {
    return <UpdatePassword setUpdatingScreen={setUpdatingScreen} />;
  }

  return (
    <View style={styles.container}>
      <Image source={require('../../assets/images/user.png')} style={styles.profileImage} />
      <Text style={styles.userName}>{name} {surname}</Text>

      <View style={styles.infoContainer}>
        <View style={styles.infoRow}>
          <FontAwesomeIcon icon={faEnvelope} size={20} color="#555" style={styles.icon} />
          <Text style={styles.userData}>{email}</Text>
        </View>
        <View style={styles.infoRow}>
          <FontAwesomeIcon icon={faPhone} size={20} color="#555" style={styles.icon} />
          <Text style={styles.userData}>{phone}</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.editButton} onPress={() => setUpdatingScreen(true)}>
        <Text style={styles.editButtonText}>Şifre Yenile</Text>
      </TouchableOpacity>

      <CustomButton
        title={
          <View style={styles.logoutButtonContent}>
            <FontAwesomeIcon icon={faSignOutAlt} size={20} color="#fff" style={styles.logoutIcon} />
            <Text style={styles.logoutButtonText}>Çıkış Yap</Text>
          </View>
        }
        onPress={handleLogout}
        style={styles.logoutButton}
      />
    </View>
  );
};

export default ProfileScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f4f4f4',
    paddingHorizontal: 20,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    marginBottom: 15,
    borderWidth: 3,
    borderColor: '#2E86C1',
  },
  userName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  infoContainer: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    width: '90%',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  icon: {
    marginRight: 10,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 1 },
    shadowRadius: 2,
    elevation: 2,
  },
  userData: {
    fontSize: 16,
    color: '#555',
  },
  editButton: {
    backgroundColor: '#1976D2',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 8,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 3 },
    elevation: 3,
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: '#D32F2F',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoutIcon: {
    marginRight: 8,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 1 },
    shadowRadius: 2,
    elevation: 2,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});