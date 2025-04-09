import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity } from 'react-native';
import { useDispatch } from 'react-redux';
import { updatePassword } from '../redux/userSlice';
import CustomTextInput from './CustomTextInput';
import CustomButton from './CustomButton';
import Icon from 'react-native-vector-icons/Ionicons';

const UpdatePassword = ({setUpdatingScreen}) => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [secureText, setSecureText] = useState(true);
  
  const dispatch = useDispatch();

  const handleUpdatePassword = async () => {
    if (newPassword !== confirmPassword) {
      Alert.alert('Hata', 'Yeni şifreler eşleşmiyor');
      return;
    }

    try {
      await dispatch(updatePassword({ oldPassword, newPassword })).unwrap();
      Alert.alert('Başarılı', 'Şifreniz başarıyla güncellendi');
      setUpdatingScreen(false);
    } catch (error) {
      Alert.alert('Hata', error.message || 'Şifre güncellenirken bir hata oluştu');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => setUpdatingScreen(false)}>
          <Icon name="close" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Şifre Güncelle</Text>
      </View>

      <CustomTextInput
        placeholder="Eski Şifre"
        value={oldPassword}
        onChangeText={setOldPassword}
        secureTextEntry
      />
      <CustomTextInput
        placeholder="Yeni Şifre"
        value={newPassword}
        onChangeText={setNewPassword}
        secureTextEntry
      />
      <CustomTextInput
        placeholder="Yeni Şifre Tekrar"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
      />

      <CustomButton
        title="Şifreyi Güncelle"
        onPress={handleUpdatePassword}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});

export default UpdatePassword;
