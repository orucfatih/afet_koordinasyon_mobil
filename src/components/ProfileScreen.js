import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity,} from 'react-native';
import { useDispatch, useSelector,} from 'react-redux';
import { useState, useEffect } from 'react';
import {getUser, logout} from '../redux/userSlice';
import {Loading, CustomButton, UpdatePassword} from './index.js';

const ProfileScreen = () => {

  const dispatch = useDispatch()
  
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")

  useEffect(() => {
    const user = getUser();

    if (user) {
      setName(user.displayName || ""); // Kullanıcının adı yoksa boş string
      setEmail(user.email || "");     // Kullanıcının e-posta adresi
    }
  }, []); // Sadece bileşen ilk kez yüklendiğinde çalışır

  //Şifre değiştirme
  const [updatingScreen, setUpdatingScreen] = useState(false)

  const {isLoading} = useSelector(state=>state.user)

   //LOGOUT
   const handleLogout = () => {
    dispatch(logout())
  }

  if(isLoading){
    return <Loading/>
  }

  if(updatingScreen){
    return <UpdatePassword setUpdatingScreen={setUpdatingScreen}/>
  }

  return (
    <View style={styles.container}>
      {/* Profil Fotoğrafı */}
      <Image
        source={require('../../assets/images/user.png')} // Vatandaş Giriş ikonu
        style={styles.profileImage}
      />

      {/* Kullanıcı Bilgileri */}
      <Text style={styles.userName}>{name}</Text>
      <Text style={styles.userEmail}>{email}</Text>

      {/* şifre Yenileme */}
      <TouchableOpacity style={styles.editButton} onPress={() => setUpdatingScreen(true)}>
        <Text style={styles.editButtonText}>Şifre Yenile</Text>
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
