import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  TextInput,
  ScrollView,
} from 'react-native';

import React, { useState, useEffect} from 'react';
import { Loading, CustomTextInput, CustomButton, VerificationModal } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import { setIsLoading, staffLogin, staffAutoLogin, logout } from '../redux/userSlice.js';
import Ionicons from 'react-native-vector-icons/Ionicons';

const generateCaptcha = () => {
  return Math.random().toString(36).substring(2, 6).toUpperCase(); // 4 karakterlik captcha
};

const LoginPage2 = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState(generateCaptcha());
  const [captchaAngle, setCaptchaAngle] = useState(Math.random() * 20 - 10);
  const [secureText, setSecureText] = useState(true);
  const [tempVerificationId, setTempVerificationId] = useState(null);
  const [tempStaffData, setTempStaffData] = useState(null);

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(staffAutoLogin());
  }, []);


  const { isLoading } = useSelector((state) => state.user);
  const { isStaffAuth } = useSelector((state) => state.user);

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
  
    dispatch(staffLogin({ email, password }))
      .unwrap()
      .then((response) => {
        console.log('Giriş başarılı:');
        setTempVerificationId(response.verificationId);
        setTempStaffData(response.staffData);
      })
      .catch((error) => {
        console.log('Giriş başarısız:', error);
        Alert.alert('Hata', error, [{ text: 'Tamam', style: 'destructive' }]);
      });
  };

  const handleModalClose = (isSuccess) => {
    if (!isSuccess) {
      dispatch(logout());
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      
      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate("AraMenu")}>
          <Ionicons name="arrow-back" size={24} color="black" />
        </TouchableOpacity>

        <Text style={styles.title}>Hoşgeldiniz</Text>

        <View style={styles.iconContainer}>
            <Ionicons name="log-in-outline" size={100} color="#007BFF" />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Email</Text>
          <CustomTextInput
            secureTextEntry={false}
            placeholder="Email Adresinizi Girin"
            onChangeText={(email) => setEmail(email)}
            value={email}/>

          <Text style={styles.label}>Şifre</Text>
          <View style={styles.passwordInputContainer}>
            <CustomTextInput
              secureTextEntry={secureText} // Şifreyi göster veya gizle
              placeholder="Şifre Girin"
              onChangeText={(password) => setPassword(password)}
              value={password}/>

            <TouchableOpacity
              onPress={() => setSecureText(!secureText)}
              style={styles.eyeIcon}
              accessibilityLabel={secureText ? "Şifreyi Göster" : "Şifreyi Gizle"}>

              <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
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
            style={styles.refreshCaptcha}>

            <Ionicons name="refresh-circle" size={32} color="#007BFF" />
          </TouchableOpacity>
        </View>

        {/* Captcha Girişi */}
        <TextInput
          style={styles.captchaInput}
          placeholder="Captcha Kodunu Girin"
          placeholderTextColor="lightgray"
          onChangeText={(text) => setCaptchaInput(text)}
          value={captchaInput}
          textAlign="center"/>

        <CustomButton
          onPress={handleLogin}
          title="Giriş Yap"
          style={styles.primaryButton}/>

        <VerificationModal
            visible={isStaffAuth}
            onClose={handleModalClose}
            verificationId={tempVerificationId}
            staffData={tempStaffData}/>

        {isLoading ? (
          <Loading changeIsLoading={() => dispatch(setIsLoading(false))} />
        ) : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default LoginPage2;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollContainer: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingVertical: 40,
  },
  backButton: {
    position: "absolute",
    top: 40, // Üstten boşluk
    left: 20, // Soldan boşluk
    padding: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#343A40',
    marginBottom: 20,
  },
  iconContainer: { 
    width: 100,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
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
    width: '100%',
  },
  linkText: {
    fontSize: 14,
    color: '#007BFF',
    textDecorationLine: 'underline',
    marginTop: 10,
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
  closeButton: {
    position: "absolute",
    top: 10,
    right: 10,
    padding: 5,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
    textAlign: "center",
  },
  modalText: {
    fontSize: 14,
    textAlign: "justify",
    marginBottom: 5,
  },
  bulletPoint: {
    fontSize: 14,
    marginLeft: 10,
    marginBottom: 3,
  },
  buttonContainer: {
    alignItems: "center",
    marginTop: 10,
  },
  acceptButton: {
    backgroundColor: "#007BFF",
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 5,
    alignItems: "center",
  },
  acceptButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  closeButton: {
    position: 'absolute',
    top: 10,
    right: 10,
  },
  passwordInputContainer: {
    position: 'relative',
  },
  passwordInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    width: '100%',
    marginBottom: 15,
  },
  eyeIcon: {
    position: 'absolute',
    right: 10,
    top: 10,
  },
});
