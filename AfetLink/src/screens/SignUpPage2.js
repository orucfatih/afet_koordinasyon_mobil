import { StyleSheet, Text, View, Image, Pressable, Alert, TouchableOpacity, StatusBar, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import React, { useState } from 'react';
import { CustomButton, CustomTextInput, Loading } from '../components';
import { useDispatch, useSelector } from 'react-redux';
import { register } from '../redux/userSlice';
import Ionicons from 'react-native-vector-icons/Ionicons';
import * as Animatable from 'react-native-animatable';

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
            onPress={() => navigation.goBack()}
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
            Kaydol
          </Animatable.Text>
          
          <Animatable.View 
            animation="zoomIn" 
            delay={400}
            style={styles.iconContainer}
          >
            <View style={styles.iconWrapper}>
              <Ionicons name="person-add-outline" size={60} color="#FF9800" />
            </View>
          </Animatable.View>

          <Animatable.View 
            animation="fadeInUp" 
            delay={600}
            style={styles.inputContainer}
          >
            <View style={styles.nameInputContainer}>
              <View style={styles.nameInput}>
                <Text style={styles.label}>İsim</Text>
                <CustomTextInput 
                  placeholder='İsminizi Girin' 
                  onChangeText={setName} 
                  value={name} 
                  style={styles.textInput}
                />
              </View>

              <View style={styles.nameInput}>
                <Text style={styles.label}>Soyisim</Text>
                <CustomTextInput 
                  placeholder='Soyisminizi Girin' 
                  onChangeText={setSurname} 
                  value={surname} 
                  style={styles.textInput}
                />
              </View>
            </View>

            <Text style={styles.label}>Telefon</Text>
            <CustomTextInput 
              placeholder='Telefon Numaranızı Girin' 
              onChangeText={setPhone} 
              value={phone} 
              style={styles.textInput}
            />

            <Text style={styles.label}>Email</Text>
            <CustomTextInput 
              placeholder='Email Adresinizi Girin' 
              onChangeText={setEmail} 
              value={email} 
              style={styles.textInput}
            />

            <Text style={styles.label}>Şifre</Text>
            <View style={styles.passwordInputContainer}>
              <CustomTextInput 
                secureTextEntry={secureText} 
                placeholder='Bir Şifre Oluşturun' 
                onChangeText={setPassword} 
                value={password} 
                style={styles.textInput}
              />
              <TouchableOpacity 
                onPress={() => setSecureText(!secureText)} 
                style={styles.eyeIcon}
                activeOpacity={0.7}
              >
                <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <Text style={styles.label}>Şifre Tekrar</Text>
            <View style={styles.passwordInputContainer}>
              <CustomTextInput 
                secureTextEntry={secureText} 
                placeholder='Şifrenizi Tekrar Girin' 
                onChangeText={setConfirmPassword} 
                value={confirmPassword} 
                style={styles.textInput}
              />
              <TouchableOpacity 
                onPress={() => setSecureText(!secureText)} 
                style={styles.eyeIcon}
                activeOpacity={0.7}
              >
                <Ionicons name={secureText ? "eye-off" : "eye"} size={24} color="#666" />
              </TouchableOpacity>
            </View>
          </Animatable.View>

          <Animatable.View 
            animation="fadeInUp" 
            delay={800}
            style={styles.buttonSection}
          >
            <CustomButton onPress={signUp} title="Kaydol" style={styles.signUpButton} />
            
            <View style={styles.bottomText}>
              <Text style={styles.bottomTextNormal}>Zaten bir hesabınız var mı? </Text>
              <Pressable onPress={() => navigation.navigate("LoginPage2")}>
                <Text style={styles.linkText}>Giriş yapmak için tıklayın.</Text>
              </Pressable>
            </View>
          </Animatable.View>
        </Animatable.View>
      </ScrollView>
    </View>
  );
};

export default SignUpPage2;

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
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
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
    shadowColor: '#FF9800',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 10,
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  nameInputContainer: {
    width: "100%",
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 12,
  },
  nameInput: {
    flex: 1,
    alignItems: "flex-start",
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
    marginBottom: 10,
  },
  passwordInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    position: 'relative',
  },
  eyeIcon: {
    position: 'absolute',
    right: 18,
    top: '50%',
    transform: [{ translateY: -22 }],
    padding: 5,
  },
  buttonSection: {
    width: '100%',
    alignItems: 'center',
  },
  signUpButton: {
    backgroundColor: '#FF9800',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    width: '100%',
    shadowColor: '#FF9800',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 6 },
    elevation: 8,
    marginBottom: 20,
  },
  bottomText: {
    flexDirection: "row",
    alignItems: 'center',
    marginTop: 10,
  },
  bottomTextNormal: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.9)',
  },
  linkText: {
    fontWeight: "bold",
    color: "#FF9800",
    textDecorationLine: 'underline',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 40,
  },
  scrollView: {
    flex: 1,
  },
});
