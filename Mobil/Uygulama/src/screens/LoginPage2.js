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
  Modal,
  ScrollView,
} from 'react-native';

import React, { useState, useEffect } from 'react';
import { Loading, CustomTextInput, CustomButton } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import { setIsLoading, login, autoLogin } from '../redux/userSlice.js';
import { Ionicons } from '@expo/vector-icons';

const generateCaptcha = () => {
  return Math.random().toString(36).substring(2, 6).toUpperCase(); // 4 karakterlik captcha
};

const LoginPage2 = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState(generateCaptcha());
  const [attempts, setAttempts] = useState(0);
  const [secureText, setSecureText] = useState(true);
  const [isTermsAccepted, setIsTermsAccepted] = useState(false);
  const [isTermsModalVisible, setIsTermsModalVisible] = useState(false);

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(autoLogin());
  }, []);

  useEffect(() => {
    if (isTermsAccepted) {
      setIsTermsModalVisible(false);
    }
  }, [isTermsAccepted]);
  

  const { isLoading } = useSelector((state) => state.user);

  const handleLogin = () => {
    if (!email || !password) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurunuz.');
      return;
    }

    if (!isTermsAccepted) {
      Alert.alert('Hata', 'Devam etmek için kullanıcı sözleşmesini kabul etmelisiniz.');
      return;
    }
        

    if (captchaInput.toUpperCase() !== captchaCode) {
      Alert.alert('Hata', 'Captcha doğrulaması başarısız. Tekrar deneyin.');
      setCaptchaCode(generateCaptcha()); // Yeni Captcha oluştur
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
    >
            {/* Geri Butonu */}
            <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate("AraMenu")}>
        <Ionicons name="arrow-back" size={24} color="black" />
      </TouchableOpacity>
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
        <View style={styles.passwordInputContainer}>
          <CustomTextInput
            secureTextEntry={secureText} // Şifreyi göster veya gizle
            placeholder="Şifre Girin"
            onChangeText={(password) => setPassword(password)}
            value={password}
          />
          <TouchableOpacity
            onPress={() => setSecureText(!secureText)}
            style={styles.eyeIcon}
            accessibilityLabel={secureText ? "Şifreyi Göster" : "Şifreyi Gizle"}
          >
            <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#000000" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Captcha Gösterimi */}
      <View style={styles.captchaContainer}>
        <Text style={styles.captchaCode}>{captchaCode}</Text>
        <TouchableOpacity onPress={() => setCaptchaCode(generateCaptcha())} style={styles.refreshCaptcha}>
    <Ionicons name="refresh-circle" size={30} color="#007BFF" />
  </TouchableOpacity>
      </View>
      
      {/* Captcha Girişi */}
      <TextInput
        style={styles.captchaInput}
        placeholder="Captcha Girin"
        onChangeText={(text) => setCaptchaInput(text)}
        value={captchaInput}
      />
      <View style={styles.termsContainer}>
  {/* Checkbox */}
  <TouchableOpacity onPress={() => setIsTermsAccepted(!isTermsAccepted)}>
    <Ionicons
      name={isTermsAccepted ? 'checkbox-outline' : 'square-outline'}
      size={24}
      color="#007BFF"
    />
  </TouchableOpacity>

  {/* Kullanıcı Sözleşmesi Metni */}
  <TouchableOpacity onPress={() => setIsTermsModalVisible(true)}>
    <Text style={styles.termsText}>Kullanıcı Sözleşmesini Okudum ve Kabul Ediyorum</Text>
  </TouchableOpacity>
</View>

{/* Kullanıcı Sözleşmesi Modalı */}
{/* Kullanıcı Sözleşmesi Modalı */}
<Modal visible={isTermsModalVisible} transparent animationType="slide">
  <View style={styles.modalContainer}>
    <View style={styles.modalContent}>
      {/* Kapatma Butonu */}
      <TouchableOpacity style={styles.closeButton} onPress={() => setIsTermsModalVisible(false)}>
        <Ionicons name="close" size={24} color="black" />
      </TouchableOpacity>

      {/* Başlık */}
      <Text style={styles.modalTitle}>Kullanıcı Sözleşmesi</Text>

      {/* Kaydırılabilir İçerik */}
      <ScrollView style={styles.scrollContainer}>
        <Text style={styles.sectionTitle}>1. Taraflar</Text>
        <Text style={styles.modalText}>
          İşbu Kullanıcı Sözleşmesi (“Sözleşme”), aşağıda bilgileri verilen taraflar arasında akdedilmiştir:
        </Text>
        <Text style={styles.modalText}>
          - **Hizmet Sağlayıcı:** [İlgili Kurum/Kuruluş] (“İlgili Kurum/Kuruluş”) {"\n"}
          - **Kullanıcı:** Uygulamaya kayıt olan ve hizmetlerden faydalanan kişi (“Kullanıcı”)
        </Text>

        <Text style={styles.sectionTitle}>2. Kişisel Verilerin İşlenmesi ve Korunması</Text>
        <Text style={styles.modalText}>İlgili Kurum/Kuruluş, Kullanıcı’nın aşağıdaki kişisel verilerini toplayabilir:</Text>
        <Text style={styles.bulletPoint}>• Ad ve soyad</Text>
        <Text style={styles.bulletPoint}>• Lokasyon bilgisi (GPS veya manuel giriş)</Text>
        <Text style={styles.bulletPoint}>• Telefon numarası</Text>

        <Text style={styles.modalText}>
          Bu veriler aşağıdaki amaçlarla işlenmektedir:
        </Text>
        <Text style={styles.bulletPoint}>• Kullanıcı kimliğinin doğrulanması</Text>
        <Text style={styles.bulletPoint}>• Hizmetlerin kişiselleştirilmesi</Text>
        <Text style={styles.bulletPoint}>• Güvenlik önlemlerinin artırılması</Text>

        <Text style={styles.sectionTitle}>3. Kullanıcı Hak ve Yükümlülükleri</Text>
        <Text style={styles.modalText}>
          Kullanıcı, uygulamayı hukuka uygun şekilde kullanacağını ve kişisel verilerinin işlenmesini kabul ettiğini beyan eder.
        </Text>
        <Text style={styles.bulletPoint}>
          • Kullanıcı, uygulamayı yalnızca meşru amaçlarla kullanacaktır.
        </Text>
        <Text style={styles.bulletPoint}>
          • Kullanıcı, diğer kişilerin haklarını ihlal etmemeyi taahhüt eder.
        </Text>

        <Text style={styles.sectionTitle}>4. Sözleşmenin Yürürlüğe Girmesi ve Feshi</Text>
        <Text style={styles.modalText}>
          Kullanıcı, bu sözleşmeyi onayladığında hükümleri kabul etmiş sayılır.
        </Text>
        <Text style={styles.modalText}>
          İlgili Kurum/Kuruluş, Kullanıcı’nın sözleşmeye aykırı hareket ettiğini tespit ederse, hizmetleri durdurma hakkına sahiptir.
        </Text>

        <Text style={styles.sectionTitle}>5. Uyuşmazlıkların Çözümü</Text>
        <Text style={styles.modalText}>
          İşbu sözleşmeden doğabilecek uyuşmazlıkların çözümünde [İlgili Kurum/Kuruluş]’un bulunduğu ülke/şehrin yetkili mahkemeleri ve icra daireleri yetkilidir.
        </Text>

        <Text style={styles.sectionTitle}>6. Son Hükümler</Text>
        <Text style={styles.modalText}>
          Bu sözleşme, Kullanıcı’nın onayı ile yürürlüğe girer ve taraflar arasında bağlayıcıdır.
        </Text>
      </ScrollView>

      {/* Onay Butonu */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.acceptButton}
          onPress={() => {
            setIsTermsAccepted(true); // Checkbox işaretlensin
            setIsTermsModalVisible(false); // Modal kapansın
          }}
        >
          <Text style={styles.acceptButtonText}>Okudum ve Onaylıyorum</Text>
        </TouchableOpacity>
      </View>
    </View>
  </View>
</Modal>

      <CustomButton
        onPress={handleLogin}
        title="Giriş Yap"
        style={styles.primaryButton}
      />

      <TouchableOpacity onPress={() => navigation.navigate('SignUpPage2')}>
        <Text style={styles.linkText}>Hesabınız yok mu? Kaydolun</Text>
      </TouchableOpacity>

      {isLoading ? (
        <Loading changeIsLoading={() => dispatch(setIsLoading(false))} />
      ) : null}
    </KeyboardAvoidingView>
  );
};

export default LoginPage2;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
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
  captchaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  captchaCode: {
    fontSize: 22,
    fontWeight: 'bold',
    backgroundColor: '#ddd',
    padding: 10,
    borderRadius: 5,
    letterSpacing: 3,
  },
  refreshCaptcha: {
    marginLeft: 10,
    padding: 5,
    borderRadius: 50, // Optional: to give the icon a circular background
    backgroundColor: '#f0f0f0', // Optional: background color for the button
  },  
  captchaInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    width: '80%',
    textAlign: 'center',
    marginBottom: 15,
  },
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  termsText: {
    fontSize: 14,
    color: '#007BFF',
    textDecorationLine: 'underline',
    marginLeft: 5,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)", // Saydam arka plan
    justifyContent: "center",
    alignItems: "center",
  },
  modalContent: {
    width: "85%",
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 20,
    maxHeight: "80%", // Modalın çok büyük olmaması için
    flexGrow: 1, // İçeriğin büyümesine izin verir
    justifyContent: "space-between", // İçeriği dağıtır
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
  scrollContainer: {
    flexGrow: 1, // İçeriğin tam kaydırılmasını sağlar
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginTop: 10,
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
  acceptButton: {
    backgroundColor: '#007BFF',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
  },
  
  acceptButtonText: {
    color: 'white',
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
