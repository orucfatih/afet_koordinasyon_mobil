import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity,} from 'react-native';
import { useDispatch, useSelector} from 'react-redux';
import {logout} from '../redux/userSlice';
import {Loading, CustomButton} from './index.js';

const ProfileScreen = () => {

  const dispatch = useDispatch()

  const {isLoading} = useSelector(state=>state.user)

   //LOGOUT
   const handleLogout = () => {
    dispatch(logout())
  }

  if(isLoading){
    return <Loading/>
  }

  const handleEditProfile = () => {
    alert('Profili düzenle seçeneği');
  };

  return (
    <View style={styles.container}>
      {/* Profil Fotoğrafı */}
      <Image
        source={{ uri: 'https://via.placeholder.com/100' }} // Varsayılan bir profil resmi
        style={styles.profileImage}
      />

      {/* Kullanıcı Bilgileri */}
      <Text style={styles.userName}>Ahmet Yılmaz</Text>
      <Text style={styles.userEmail}>test@test.com</Text>

      {/* Düzenle Butonu */}
      <TouchableOpacity style={styles.editButton} onPress={handleEditProfile}>
        <Text style={styles.editButtonText}>Profili Düzenle</Text>
      </TouchableOpacity>

      {/* Çıkış Yap Butonu */}
      <CustomButton title={"Çıkış Yap"} onPress={handleLogout}/>
    </View>
  );
};

export default ProfileScreen;

// Stiller
const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 20,
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#D32F2F',
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 16,
    color: '#757575',
    marginBottom: 20,
  },
  editButton: {
    backgroundColor: '#1976D2',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
    marginBottom: 10,
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: '#D32F2F',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
