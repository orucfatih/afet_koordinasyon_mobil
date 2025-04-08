import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity } from 'react-native';
import { useDispatch } from 'react-redux';
import { updateCipher } from '../redux/userSlice';
import CustomTextInput from './CustomTextInput';
import CustomButton from './CustomButton';
import { Ionicons } from '@expo/vector-icons';

const UpdatePassword = ({setUpdatingScreen}) => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [secureText, setSecureText] = useState(true);
  
  const dispatch = useDispatch();

  const handleUpdatePassword = () => {
    if (!oldPassword || !newPassword || !confirmPassword) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurunuz.');
      return;
    }

    dispatch(updateCipher({ oldPassword, newPassword, confirmPassword }))
      .unwrap()
      .then((message) => {
        Alert.alert('Başarılı', message, [{ text: 'Tamam', style: 'default' }]);
      })
      .catch((error) => {
        Alert.alert('Hata', error, [{ text: 'Tamam', style: 'destructive' }]);
      });
  };

  return (
    <View style={styles.container}>

        <TouchableOpacity
          onPress={()=> setUpdatingScreen(false)}
          style={[{}, styles.closeButtonContainer]}>
            <Text style={styles.closeButton}>X</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Şifrenizi Güncelleyin</Text>

      <View style={styles.inputContainer}>

        <Text style={styles.label}>Eski Şifre</Text>
        <View style={styles.passwordInputContainer}>
          <CustomTextInput secureTextEntry={secureText} placeholder='Eski Şifrenizi Girin' onChangeText={setOldPassword} value={oldPassword} />
          <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
            <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Yeni Şifre</Text>
        <View style={styles.passwordInputContainer}>
          <CustomTextInput secureTextEntry={secureText} placeholder='Yeni Şifrenizi Girin' onChangeText={setNewPassword} value={newPassword} />
          <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
            <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Yeni Şifre Tekrar</Text>
        <View style={styles.passwordInputContainer}>
          <CustomTextInput secureTextEntry={secureText} placeholder='Yeni Şifrenizi Tekrar Girin' onChangeText={setConfirmPassword} value={confirmPassword} />
          <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
            <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
          </TouchableOpacity>
        </View>

      </View>

      <CustomButton title="Şifreyi Güncelle" onPress={handleUpdatePassword} />
    </View>
  );
};

export default UpdatePassword;

const styles = StyleSheet.create({
  container: {
    flex: 1, // Tüm alanı kaplayacak şekilde ayarla
    justifyContent: 'center', // Dikey olarak ortala
    alignItems: 'center', // Yatay olarak ortala
    padding: 20,
    backgroundColor: '#f9f9f9',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  label: {
    fontSize: 12,
    color: '#495057',
    marginBottom: 0,
    marginTop:2,
    marginLeft: 4,
    fontWeight: '500',
  },
  passwordInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
  },
  eyeIcon: {
    position: 'absolute',
    right: 15,
  },
  closeButton:{
    color:"black",
    fontWeight:"bold",
    textAlign:"center",
  },
  closeButtonContainer:{
      backgroundColor:"lightgray",
      width:"30",
      height:"30",
      borderRadius:30,
      alignItems:"center",
      justifyContent:"center",
      position:"absolute",
      top:"50",
      right:"15",
}
});
