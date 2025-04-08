import { StyleSheet, Text, View, Image, Pressable, Alert, TouchableOpacity } from 'react-native';
import React, { useState } from 'react';
import { CustomButton, CustomTextInput, Loading } from '../components';
import { useDispatch, useSelector } from 'react-redux';
import { register } from '../redux/userSlice';
import { Ionicons } from '@expo/vector-icons';

const SignUpPage2 = ({ navigation }) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [surname, setSurname] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [secureText, setSecureText] = useState(true);

  const dispatch = useDispatch();
  const { isLoading } = useSelector(state => state.user);

  const signUp = () => {
    if (!email || !password || !confirmPassword || !name || !surname || !phone) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurunuz.');
      return;
    }

    dispatch(register({ email, password, confirmPassword, name, surname, phone}))
      .unwrap()
      .catch((errorMessage) => {
        console.log('Giriş başarısız:', errorMessage);
        Alert.alert('Hata', errorMessage, [{ text: 'Tamam', style: 'destructive' }]);
      });
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <View style={styles.container}>

      <Text style={styles.title}>Kaydol</Text>
      <Image style={styles.image} source={require("../../assets/images/login.png")} />

      <View style={styles.inputContainer}>

        <View style={styles.nameInputContainer}>

          <View style={styles.nameInput}>
            <Text style={styles.label}>İsim</Text>
            <CustomTextInput placeholder='İsminizi Girin' onChangeText={setName} value={name} />
          </View>

          <View style={styles.nameInput}>
            <Text style={styles.label}>Soyisim</Text>
            <CustomTextInput placeholder='Soyisminizi Girin' onChangeText={setSurname} value={surname} />
          </View>
          
        </View>

        <Text style={styles.label}>Telefon</Text>
        <CustomTextInput placeholder='Telefon Numaranızı Girin' onChangeText={setPhone} value={phone} />

        <Text style={styles.label}>Email</Text>
        <CustomTextInput placeholder='Email Adresinizi Girin' onChangeText={setEmail} value={email} />

        <Text style={styles.label}>Şifre</Text>
        <View style={styles.passwordInputContainer}>
          <CustomTextInput secureTextEntry={secureText} placeholder='Bir Şifre Oluşturun' onChangeText={setPassword} value={password} />
          <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
            <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Şifre Tekrar</Text>
        <View style={styles.passwordInputContainer}>
          <CustomTextInput secureTextEntry={secureText} placeholder='Şifrenizi Tekrar Girin' onChangeText={setConfirmPassword} value={confirmPassword} />
          <TouchableOpacity onPress={() => setSecureText(!secureText)} style={styles.eyeIcon}>
            <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
          </TouchableOpacity>
        </View>

      </View>


      <CustomButton onPress={signUp} title="Kaydol" />
      <View style={styles.bottomText}>
        <Text>Zaten bir hesabınız var mı? </Text>
        <Pressable onPress={() => navigation.navigate("LoginPage")}>
          <Text style={styles.linkText}>Giriş yapmak için tıklayın.</Text>
        </Pressable>
      </View>
    </View>
  );
};

export default SignUpPage2;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  nameInputContainer:{
    width:"100%",
    flexDirection:"row",
    alignItems: "left",
    justifyContent:"space-between",
  },
  nameInput:{
    width:"47%",
    alignItems: "left",
  },
  label: {
    fontSize: 12,
    color: '#495057',
    marginBottom: 0,
    marginTop:2,
    marginLeft: 4,
    fontWeight: '500',
  },
  title: {
    fontSize: 30,
    fontWeight: "bold",
    marginBottom: 20,
  },
  image: {
    width: 100,
    height: 100,
    marginBottom: 20,
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
  bottomText: {
    flexDirection: "row",
    marginTop: 20,
  },
  linkText: {
    fontWeight: "bold",
    color: "blue",
  },
});
