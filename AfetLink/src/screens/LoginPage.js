import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  TextInput,
  ScrollView,
} from 'react-native';
import React, { useState, useEffect } from 'react';
import { Loading, CustomTextInput, CustomButton } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import { setIsLoading, login, autoLogin } from '../redux/userSlice.js';
import Icon from 'react-native-vector-icons/Ionicons';

const generateCaptcha = () => {
  return Math.random().toString(36).substring(2, 6).toUpperCase(); // 4 karakterlik captcha
};

const LoginPage = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState(generateCaptcha());
  const [captchaAngle, setCaptchaAngle] = useState(Math.random() * 20 - 10);
  const [attempts, setAttempts] = useState(0);
  const [secureText, setSecureText] = useState(true);

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(autoLogin());
  }, []);

  const { isLoading } = useSelector((state) => state.user);

  const handleLogin = () => {
    if (!email || !password) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurunuz.');
      return;
    }

    if (captchaInput.toUpperCase() !== captchaCode) {
      Alert.alert('Hata', 'Captcha doğrulaması başarısız. Tekrar deneyin.');
      setCaptchaCode(generateCaptcha());
      setCaptchaAngle(Math.random() * 20 - 10);
      setCaptchaInput('');
      return;
    }

    dispatch(login({ email, password }))
      .unwrap()
      .catch((errorMessage) => {
        setAttempts(attempts + 1);
        console.log('Giriş başarısız:', errorMessage);
        Alert.alert('Hata', errorMessage, [{ text: 'Tamam', style: 'destructive' }]);
      });
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        {/* Geri Butonu */}
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate('AraMenu')}>
          <Icon name="arrow-back" size={28} color="#333" />
        </TouchableOpacity>

        <Text style={styles.title}>Hoş Geldiniz</Text>
        <Image style={styles.image} source={require('../../assets/images/login.png')} />

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Email</Text>
          <CustomTextInput
            secureTextEntry={false}
            placeholder="Email Adresinizi Girin"
            onChangeText={(email) => setEmail(email)}
            value={email}
            style={styles.textInput}
            keyboardType="email-address"
          />

          <Text style={styles.label}>Şifre</Text>
          <View style={styles.passwordInputContainer}>
            <CustomTextInput
              secureTextEntry={secureText}
              placeholder="Şifre Girin"
              onChangeText={(password) => setPassword(password)}
              value={password}
              style={styles.textInput}
            />
            <TouchableOpacity
              onPress={() => setSecureText(!secureText)}
              style={styles.eyeIcon}
              accessibilityLabel={secureText ? 'Şifreyi Göster' : 'Şifreyi Gizle'}
            >
              <Icon name={secureText ? 'eye-off' : 'eye'} size={24} color="#555" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Captcha Gösterimi */}
        <View style={styles.captchaContainer}>
          <View style={styles.captchaWrapper}>
            <Text style={styles.captchaCode}>{captchaCode}</Text>
            <View style={[styles.captchaStrike, { transform: [{ rotate: `${captchaAngle}deg` }] }]} />
            <View style={[styles.captchaStrikeSecondary, { transform: [{ rotate: `${-captchaAngle}deg` }] }]} />
          </View>
          <TouchableOpacity
            onPress={() => {
              setCaptchaCode(generateCaptcha());
              setCaptchaAngle(Math.random() * 20 - 10);
            }}
            style={styles.refreshCaptcha}
          >
            <Icon name="refresh-circle" size={32} color="#007BFF" />
          </TouchableOpacity>
        </View>

        {/* Captcha Girişi */}
        <TextInput
          style={styles.captchaInput}
          placeholder="Captcha Kodunu Girin"
          onChangeText={(text) => setCaptchaInput(text)}
          value={captchaInput}
          textAlign="center"
        />

        <CustomButton onPress={handleLogin} title="Giriş Yap" style={styles.primaryButton} />

        <TouchableOpacity onPress={() => navigation.navigate('SignUpPage')}>
          <Text style={styles.linkText}>Hesabınız yok mu? Kaydolun</Text>
        </TouchableOpacity>

        {isLoading ? <Loading changeIsLoading={() => dispatch(setIsLoading(false))} /> : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default LoginPage;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6f5',
  },
  scrollContainer: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingVertical: 40,
  },
  backButton: {
    position: 'absolute',
    top: 40,
    left: 15,
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 50,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  image: {
    width: 80,
    height: 80,
    marginBottom: 30,
    borderRadius: 40,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowOffset: { width: 0, height: 3 },
    elevation: 4,
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
  textInput: {
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 15,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  passwordInputContainer: {
    position: 'relative',
    width: '100%',
  },
  eyeIcon: {
    position: 'absolute',
    right: 15,
    top: '50%',
    transform: [{ translateY: -12 }],
    padding: 5,
  },
  captchaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  captchaWrapper: {
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#e9ecef',
    borderRadius: 8,
    padding: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  captchaCode: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
    letterSpacing: 4,
    paddingHorizontal: 10,
  },
  captchaStrike: {
    position: 'absolute',
    width: '100%',
    height: 2,
    backgroundColor: '#888',
    opacity: 0.7,
  },
  captchaStrikeSecondary: {
    position: 'absolute',
    width: '80%',
    height: 1.5,
    backgroundColor: '#666',
    opacity: 0.6,
    top: -5,
  },
  refreshCaptcha: {
    marginLeft: 15,
    padding: 5,
    borderRadius: 50,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  captchaInput: {
    width: '80%',
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 15,
    textAlign: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  primaryButton: {
    backgroundColor: '#007BFF',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 10,
    width: '100%',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 3 },
    elevation: 4,
  },
  linkText: {
    fontSize: 14,
    color: '#007BFF',
    fontWeight: '600',
    textDecorationLine: 'underline',
    marginTop: 15,
  },
});