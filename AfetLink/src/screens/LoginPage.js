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
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import React, { useState, useEffect } from 'react';
import { Loading, CustomTextInput, CustomButton } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import { setIsLoading, login, autoLogin } from '../redux/userSlice.js';
import Ionicons from 'react-native-vector-icons/Ionicons';
import * as Animatable from 'react-native-animatable';
//import { useSafeAreaInsets } from 'react-native-safe-area-context';

const generateCaptcha = () => {
  return Math.random().toString(36).substring(2, 6).toUpperCase(); // 4 karakterlik captcha
};

const LoginPage = ({ navigation }) => {
  //const insets = useSafeAreaInsets();
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

    console.log('Captcha Kontrolü:', {
      girilen: captchaInput.toUpperCase(),
      beklenen: captchaCode,
      esit: captchaInput.toUpperCase() === captchaCode
    });

    if (captchaInput.toUpperCase() !== captchaCode) {
      Alert.alert('Hata', 'Captcha doğrulaması başarısız. Tekrar deneyin.');
      setCaptchaCode(generateCaptcha());
      setCaptchaAngle(Math.random() * 20 - 10);
      setCaptchaInput('');
      return;
    }

    dispatch(login({ email, password }))
      .unwrap()
      .then(() => {
        // Başarılı giriş sonrası captcha'yı temizle
        setCaptchaInput('');
        setCaptchaCode(generateCaptcha());
        setCaptchaAngle(Math.random() * 20 - 10);
      })
      .catch((errorMessage) => {
        setAttempts(attempts + 1);
        console.log('Giriş başarısız:', errorMessage);
        Alert.alert('Hata', errorMessage, [{ text: 'Tamam', style: 'destructive' }]);
        // Hatalı giriş sonrası captcha'yı yenile
        setCaptchaCode(generateCaptcha());
        setCaptchaAngle(Math.random() * 20 - 10);
        setCaptchaInput('');
      });
  };

  return (
    <KeyboardAvoidingView 
      style={[styles.container, { /*marginBottom: insets.bottom */ }]}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={0}
    >
      <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
      
      {/* Background Gradient */}
      <View style={styles.backgroundGradient} />
      
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContainer} 
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
        keyboardDismissMode="on-drag"
      >
        {/* Header with Back Button */}
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => navigation.navigate('AraMenu')}
            activeOpacity={0.8}
          >
            <Ionicons name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
        </View>

        {/* Main Content */}
        <Animatable.View 
          animation="fadeInUp" 
          duration={800}
          style={styles.contentContainer}
        >
          <Animatable.Text 
            animation="fadeInDown" 
            delay={200}
            style={styles.title}
          >
            Hoş Geldiniz
          </Animatable.Text>
          
          <Animatable.View 
            animation="zoomIn" 
            delay={400}
            style={styles.iconContainer}
          >
            <View style={styles.iconWrapper}>
              <Ionicons name="log-in-outline" size={60} color="#D32F2F" />
            </View>
          </Animatable.View>

          <Animatable.View 
            animation="fadeInUp" 
            delay={600}
            style={styles.inputContainer}
          >
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
                activeOpacity={0.7}
              >
                <Ionicons name={secureText ? 'eye-off' : 'eye'} size={24} color="#666" />
              </TouchableOpacity>
            </View>
          </Animatable.View>

          {/* Captcha Section */}
          <Animatable.View 
            animation="fadeInUp" 
            delay={800}
            style={styles.captchaSection}
          >
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
                  setCaptchaInput('');
                }}
                style={styles.refreshCaptcha}
                activeOpacity={0.8}
              >
                <Ionicons name="refresh-circle" size={32} color="#D32F2F" />
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.captchaInput}
              placeholder="Captcha Kodunu Girin"
              placeholderTextColor="#999"
              onChangeText={(text) => setCaptchaInput(text)}
              value={captchaInput}
              textAlign="center"
              autoCapitalize="characters"
              maxLength={4}
              autoCorrect={false}
            />
          </Animatable.View>

          <Animatable.View 
            animation="fadeInUp" 
            delay={1000}
            style={styles.buttonSection}
          >
            <CustomButton 
              onPress={handleLogin} 
              title="Giriş Yap" 
              style={styles.primaryButton} 
            />

            <TouchableOpacity 
              onPress={() => navigation.navigate('SignUpPage')}
              style={styles.linkContainer}
            >
              <Text style={styles.linkText}>Hesabınız yok mu? Kaydolun</Text>
            </TouchableOpacity>
          </Animatable.View>
        </Animatable.View>

        {isLoading ? <Loading changeIsLoading={() => dispatch(setIsLoading(false))} /> : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default LoginPage;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  backgroundGradient: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '50%',
    backgroundColor: '#2D2D2D',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  scrollView: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 40,
  },
  header: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  contentContainer: {
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 20,
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  iconContainer: {
    marginBottom: 30,
  },
  iconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.95)',
    padding: 25,
    borderRadius: 50,
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 10,
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    marginBottom: 8,
    marginLeft: 4,
    fontWeight: '600',
  },
  textInput: {
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderRadius: 12,
    paddingVertical: 15,
    paddingHorizontal: 18,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
    fontSize: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  passwordInputContainer: {
    position: 'relative',
    width: '100%',
  },
  eyeIcon: {
    position: 'absolute',
    right: 18,
    top: '50%',
    transform: [{ translateY: -12 }],
    padding: 5,
  },
  captchaSection: {
    width: '100%',
    marginBottom: 20,
  },
  captchaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  captchaWrapper: {
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
  },
  captchaCode: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    letterSpacing: 4,
    paddingHorizontal: 10,
  },
  captchaStrike: {
    position: 'absolute',
    width: '100%',
    height: 2,
    backgroundColor: '#666',
    opacity: 0.7,
  },
  captchaStrikeSecondary: {
    position: 'absolute',
    width: '80%',
    height: 1.5,
    backgroundColor: '#888',
    opacity: 0.6,
    top: -5,
  },
  refreshCaptcha: {
    marginLeft: 15,
    padding: 8,
    borderRadius: 25,
    backgroundColor: 'rgba(255,255,255,0.95)',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
  },
  captchaInput: {
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderRadius: 12,
    paddingVertical: 15,
    paddingHorizontal: 18,
    textAlign: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
    fontSize: 16,
  },
  buttonSection: {
    width: '100%',
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#D32F2F',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    width: '100%',
    shadowColor: '#D32F2F',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 6 },
    elevation: 8,
    marginBottom: 20,
  },
  linkContainer: {
    padding: 10,
  },
  linkText: {
    fontSize: 16,
    color: '#D32F2F',
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
});