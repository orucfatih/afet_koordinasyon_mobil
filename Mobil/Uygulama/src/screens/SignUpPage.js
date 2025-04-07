import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { CustomButton, CustomTextInput, Loading, Agreement } from '../components';
import { useDispatch, useSelector } from 'react-redux';
import { register } from '../redux/userSlice';
import { Ionicons } from '@expo/vector-icons';

const SignUpPage = ({ navigation }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [surname, setSurname] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [secureText, setSecureText] = useState(true);
  const [isTermsAccepted, setIsTermsAccepted] = useState(false);
  const [isTermsModalVisible, setIsTermsModalVisible] = useState(false);

  const dispatch = useDispatch();
  const { isLoading } = useSelector((state) => state.user);

  const signUp = () => {
    if (!email || !password || !confirmPassword || !name || !surname || !phone) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurunuz.');
      return;
    }

    if (!isTermsAccepted) {
      Alert.alert('Hata', 'Devam etmek için kullanıcı sözleşmesini kabul etmelisiniz.');
      return;
    }

    dispatch(register({ email, password, confirmPassword, name, surname, phone }))
      .unwrap()
      .catch((errorMessage) => {
        console.log('Kayıt başarısız:', errorMessage);
        Alert.alert('Hata', errorMessage, [{ text: 'Tamam', style: 'destructive' }]);
      });
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <Text style={styles.title}>Kaydol</Text>
        <Image style={styles.image} source={require('../../assets/images/login.png')} />

        <View style={styles.inputContainer}>
          <View style={styles.nameInputContainer}>
            <View style={styles.nameInput}>
              <Text style={styles.label}>İsim</Text>
              <CustomTextInput
                placeholder="İsminizi Girin"
                onChangeText={setName}
                value={name}
                style={styles.textInput}
              />
            </View>
            <View style={styles.nameInput}>
              <Text style={styles.label}>Soyisim</Text>
              <CustomTextInput
                placeholder="Soyisminizi Girin"
                onChangeText={setSurname}
                value={surname}
                style={styles.textInput}
              />
            </View>
          </View>

          <Text style={styles.label}>Telefon</Text>
          <CustomTextInput
            placeholder="Telefon Numaranızı Girin"
            onChangeText={setPhone}
            value={phone}
            keyboardType="phone-pad"
            style={styles.textInput}
          />

          <Text style={styles.label}>Email</Text>
          <CustomTextInput
            placeholder="Email Adresinizi Girin"
            onChangeText={setEmail}
            value={email}
            keyboardType="email-address"
            style={styles.textInput}
          />

          <Text style={styles.label}>Şifre</Text>
          <View style={styles.passwordInputContainer}>
            <CustomTextInput
              secureTextEntry={secureText}
              placeholder="Bir Şifre Oluşturun"
              onChangeText={setPassword}
              value={password}
              style={styles.textInput}
            />
            <TouchableOpacity
              onPress={() => setSecureText(!secureText)}
              style={styles.eyeIcon}
              accessibilityLabel={secureText ? 'Şifreyi Göster' : 'Şifreyi Gizle'}
            >
              <Ionicons name={secureText ? 'eye-off' : 'eye'} size={24} color="#555" />
            </TouchableOpacity>
          </View>

          <Text style={styles.label}>Şifre Tekrar</Text>
          <View style={styles.passwordInputContainer}>
            <CustomTextInput
              secureTextEntry={secureText}
              placeholder="Şifrenizi Tekrar Girin"
              onChangeText={setConfirmPassword}
              value={confirmPassword}
              style={styles.textInput}
            />
            <TouchableOpacity
              onPress={() => setSecureText(!secureText)}
              style={styles.eyeIcon}
              accessibilityLabel={secureText ? 'Şifreyi Göster' : 'Şifreyi Gizle'}
            >
              <Ionicons name={secureText ? 'eye-off' : 'eye'} size={24} color="#555" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Kullanıcı Sözleşmesi */}
        <View style={styles.termsContainer}>
          <TouchableOpacity onPress={() => setIsTermsAccepted(!isTermsAccepted)}>
            <Ionicons
              name={isTermsAccepted ? 'checkbox' : 'square-outline'}
              size={24}
              color={isTermsAccepted ? '#1976D2' : '#666'}
            />
          </TouchableOpacity>
          <TouchableOpacity onPress={() => setIsTermsModalVisible(true)}>
            <Text style={styles.termsText}>Kullanıcı Sözleşmesini Okudum ve Kabul Ediyorum</Text>
          </TouchableOpacity>
        </View>

        {/* Kullanıcı Sözleşmesi Modalı */}
        <Agreement
          setIsTermsModalVisible={setIsTermsModalVisible}
          isTermsModalVisible={isTermsModalVisible}
          setIsTermsAccepted={setIsTermsAccepted}
        />

        <CustomButton onPress={signUp} title="Kaydol" style={styles.signUpButton} />

        <View style={styles.bottomText}>
          <Text style={styles.bottomTextNormal}>Zaten bir hesabınız var mı? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('LoginPage')}>
            <Text style={styles.linkText}>Giriş yap</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default SignUpPage;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContainer: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 30,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  image: {
    width: 100,
    height: 100,
    marginBottom: 20,
    borderRadius: 50,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  inputContainer: {
    width: '100%',
    marginBottom: 10,
  },
  nameInputContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  nameInput: {
    width: '48%',
  },
  label: {
    fontSize: 14,
    color: '#495057',
    marginBottom: 5,
    marginLeft: 4,
    fontWeight: '500',
  },
  textInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 10,
    shadowColor: '#000',
    marginBottom: 10,
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  passwordInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    marginBottom: 10,
  },
  eyeIcon: {
    position: 'absolute',
    right: 15,
    padding: 5,
  },
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    width: '90%',
  },
  termsText: {
    fontSize: 14,
    color: '#1976D2',
    textDecorationLine: 'underline',
    marginLeft: 8,
    fontWeight: '500',
  },
  signUpButton: {
    backgroundColor: '#1976D2',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    width: '100%',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 3 },
    elevation: 3,
  },
  bottomText: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
  },
  bottomTextNormal: {
    fontSize: 14,
    color: '#333',
  },
  linkText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1976D2',
    textDecorationLine: 'underline',
  },
});