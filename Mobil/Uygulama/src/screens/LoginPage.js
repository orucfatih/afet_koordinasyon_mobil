import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';

import React, { useState, useEffect } from 'react';
import { Loading, CustomTextInput, CustomButton } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import { setIsLoading, login, autoLogin } from '../redux/userSlice.js';

const LoginPage = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  //UserSlice içine veri göndeilmesi
  const dispatch = useDispatch();

  // Auto Login
  useEffect(() => {
    dispatch(autoLogin());
  }, []);

  // useSlice içindeki verilerin okunması
  const { isLoading } = useSelector((state) => state.user);

  //Giriş fonksiyonu
  const handleLogin = () => {
    if (!email || !password) {
          Alert.alert('Hata', 'Lütfen tüm alanları doldurunuz.');
          return;
        }

    dispatch(login({email, password}))
      .unwrap()
      .catch((errorMessage) => {
        console.log('Giriş başarısız:', errorMessage);
        Alert.alert('Hata', errorMessage, [{ text: 'Tamam', style: 'destructive' }]);
      });
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <Text style={styles.title}>Hoşgeldiniz</Text>

      <Image
        style={styles.image}
        source={require('../../assets/images/login.png')}
      />

      <View style={styles.inputContainer}>
        <Text style={styles.label}>Email</Text>
        <CustomTextInput
          secureTextEntry={false}
          placeholder="Email Adresinizi Girin"
          onChangeText={(email) => setEmail(email)}
          value={email}
        />

        <Text style={styles.label}>Şifre</Text>
        <CustomTextInput
          secureTextEntry={true}
          placeholder="Şifre Girin"
          onChangeText={(password) => setPassword(password)}
          value={password}
        />
      </View>

      <CustomButton
        onPress={handleLogin}
        title="Giriş Yap"
        style={styles.primaryButton}
      />

      <TouchableOpacity onPress={() => navigation.navigate('SignUpPage')}>
        <Text style={styles.linkText}>Hesabınız yok mu? Kaydolun</Text>
      </TouchableOpacity>

      {isLoading ? (
        <Loading changeIsLoading={() => dispatch(setIsLoading(false))} />
      ) : null}
    </KeyboardAvoidingView>
  );
};

export default LoginPage;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#343A40',
    marginBottom: 20,
  },
  image: {
    width: 75,
    height: 75,
    marginBottom: 30,
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    color: '#495057',
    marginBottom: 8,
    marginLeft: 4,
    fontWeight: '500',
  },
  primaryButton: {
    backgroundColor: '#007BFF',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginBottom: 15,
  },
  linkText: {
    fontSize: 14,
    color: '#007BFF',
    textDecorationLine: 'underline',
    marginTop: 10,
  },
});
