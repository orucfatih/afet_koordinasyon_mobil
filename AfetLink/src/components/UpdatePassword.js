import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity } from 'react-native';
import { useDispatch } from 'react-redux';
import { updateCipher } from '../redux/userSlice';
import CustomTextInput from './CustomTextInput';
import CustomButton from './CustomButton';
import Ionicons from 'react-native-vector-icons/Ionicons';

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
        onPress={() => setUpdatingScreen(false)}
        style={styles.closeButtonContainer}>
        <Ionicons name="close-circle" size={32} color="#666" />
      </TouchableOpacity>

      <View style={styles.contentContainer}>
        <Text style={styles.title}>Şifrenizi Güncelleyin</Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Eski Şifre</Text>
          <View style={styles.inputWrapper}>
            <CustomTextInput 
              secureTextEntry={secureText} 
              placeholder='Eski Şifrenizi Girin' 
              onChangeText={setOldPassword} 
              value={oldPassword}
            />
            <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
              <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#666" />
            </TouchableOpacity>
          </View>

          <Text style={styles.label}>Yeni Şifre</Text>
          <View style={styles.inputWrapper}>
            <CustomTextInput 
              secureTextEntry={secureText} 
              placeholder='Yeni Şifrenizi Girin' 
              onChangeText={setNewPassword} 
              value={newPassword}
            />
            <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
              <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#666" />
            </TouchableOpacity>
          </View>

          <Text style={styles.label}>Yeni Şifre Tekrar</Text>
          <View style={styles.inputWrapper}>
            <CustomTextInput 
              secureTextEntry={secureText} 
              placeholder='Yeni Şifrenizi Tekrar Girin' 
              onChangeText={setConfirmPassword} 
              value={confirmPassword}
            />
            <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
              <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#666" />
            </TouchableOpacity>
          </View>
        </View>

        <CustomButton 
          title="Şifreyi Güncelle" 
          onPress={handleUpdatePassword}
          style={styles.updateButton}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9f9f9',
  },
  contentContainer: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 80,
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 40,
    color: '#333',
    textAlign: 'center',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 30,
  },
  label: {
    fontSize: 15,
    color: '#495057',
    marginBottom: 8,
    marginTop: 12,
    marginLeft: 4,
    fontWeight: '600',
  },
  inputWrapper: {
    position: 'relative',
    width: '100%',
    marginBottom: 5,
  },
  eyeIcon: {
    position: 'absolute',
    right: 15,
    top: '50%',
    transform: [{ translateY: -12 }],
    padding: 8,
  },
  closeButtonContainer: {
    position: 'absolute',
    top: 20,
    right: 20,
    zIndex: 1,
    padding: 8,
  },
  updateButton: {
    backgroundColor: '#D32F2F',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 12,
    width: '80%',
    marginTop: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  }
});

export default UpdatePassword;
