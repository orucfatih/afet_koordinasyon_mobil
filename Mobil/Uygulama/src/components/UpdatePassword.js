import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity } from 'react-native';
import { useDispatch } from 'react-redux';
import { updateCipher } from '../redux/userSlice';
import CustomTextInput from './CustomTextInput';
import CustomButton from './CustomButton';

const UpdatePassword = ({setUpdatingScreen}) => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
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
        <CustomTextInput
          placeholder="Eski Şifrenizi Girin"
          secureTextEntry
          value={oldPassword}
          onChangeText={setOldPassword}
        />

        <CustomTextInput
          placeholder="Yeni Şifrenizi Girin"
          secureTextEntry
          value={newPassword}
          onChangeText={setNewPassword}
        />

        <CustomTextInput
          placeholder="Yeni Şifreyi Tekrar Girin"
          secureTextEntry
          value={confirmPassword}
          onChangeText={setConfirmPassword}
        />
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
    width: '70%', // Ebeveyn genişliğini kullan
    marginBottom: 20,
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
