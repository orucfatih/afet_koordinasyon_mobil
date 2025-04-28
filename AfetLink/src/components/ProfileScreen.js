import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Image, 
  TouchableOpacity, 
  Alert,
  ScrollView,
  TextInput,
  Keyboard,
  SafeAreaView,
  StatusBar,
  Platform,
  Dimensions,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { getUser, logout } from '../redux/userSlice';
import { Loading, CustomButton, UpdatePassword } from './index.js';
import Ionicons from 'react-native-vector-icons/Ionicons';
import firestore from '@react-native-firebase/firestore';
import auth from '@react-native-firebase/auth';

const { width } = Dimensions.get('window');

const ProfileScreen = () => {
  const dispatch = useDispatch();

  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [feedback, setFeedback] = useState({
    title: '',
    description: '',
  });

  useEffect(() => {
    dispatch(getUser())
      .unwrap()
      .then((userData) => {
        setName(userData.name || '');
        setSurname(userData.surname || '');
        setEmail(userData.email || '');
        setPhone(userData.phone || '');
      })
      .catch((error) => {
        console.log('Kullanıcı bilgileri alınırken hata:', error);
        Alert.alert(
          'Hata',
          'Kullanıcı bilgileri alınamadı. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.',
          [
            { 
              text: 'Tekrar Dene', 
              onPress: () => dispatch(getUser()) 
            },
            { 
              text: 'Tamam', 
              style: 'cancel' 
            }
          ]
        );
      });
  }, [dispatch]);

  const [updatingScreen, setUpdatingScreen] = useState(false);
  const { isLoading } = useSelector((state) => state.user);

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleFeedbackSubmit = async () => {
    if (!feedback.title || !feedback.description) {
      Alert.alert('Uyarı', 'Lütfen başlık ve açıklama alanlarını doldurun.');
      return;
    }

    try {
      await firestore().collection('feedbacks').add({
        ...feedback,
        userId: auth().currentUser.uid,
        userEmail: auth().currentUser.email,
        timestamp: firestore.FieldValue.serverTimestamp(),
        status: 'new'
      });

      Alert.alert('Başarılı', 'Geri bildiriminiz başarıyla gönderildi.');
      setFeedback({ title: '', description: '' });
    } catch (error) {
      console.error('Geri bildirim gönderilirken hata:', error);
      Alert.alert('Hata', 'Geri bildirim gönderilirken bir hata oluştu.');
    }
  };

  if (isLoading) {
    return <Loading />;
  }

  if (updatingScreen) {
    return <UpdatePassword setUpdatingScreen={setUpdatingScreen} />;
  }

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        backgroundColor="#2D2D2D"
        barStyle="light-content"
        translucent={true}/>

      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
        </View>

        <ScrollView 
          style={styles.container}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled">

          <TouchableOpacity 
            style={styles.dismissKeyboard} 
            activeOpacity={1} 
            onPress={() => Keyboard.dismiss()}>

            <View style={styles.profileHeader}>
              <Image source={require('../../assets/images/user.png')} style={styles.profileImage} />
              <View style={styles.profileInfo}>
                <Text style={styles.userName}>{name} {surname}</Text>
              </View>
            </View>

            <View style={styles.contentContainer}>
              <View style={styles.infoContainer}>
                <View style={styles.infoRow}>
                  <Ionicons name="mail" size={20} color="#555" style={styles.icon} />
                  <Text style={styles.userData}>{email}</Text>
                </View>
                <View style={styles.infoRow}>
                  <Ionicons name="call" size={20} color="#555" style={styles.icon} />
                  <Text style={styles.userData}>{phone}</Text>
                </View>
              </View>

              <TouchableOpacity style={styles.editButton} onPress={() => setUpdatingScreen(true)}>
                <Text style={styles.editButtonText}>Şifre Yenile</Text>
              </TouchableOpacity>

              <View style={styles.feedbackContainer}>
                <Text style={styles.feedbackTitle}>İstek ve Şikayet Bildir</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Başlık"
                  placeholderTextColor={"lightgray"}
                  value={feedback.title}
                  onChangeText={(text) => setFeedback(prev => ({ ...prev, title: text }))}/>

                <TextInput
                  style={[styles.input, styles.textArea]}
                  placeholder="Açıklama"
                  placeholderTextColor={"lightgray"}
                  value={feedback.description}
                  onChangeText={(text) => setFeedback(prev => ({ ...prev, description: text }))}
                  multiline
                  numberOfLines={4}/>

                <TouchableOpacity style={styles.submitButton} onPress={handleFeedbackSubmit}>
                  <Ionicons name="paper-plane" size={18} color="#fff" style={styles.submitIcon} />
                  <Text style={styles.submitButtonText}>Gönder</Text>
                </TouchableOpacity>
              </View>

              <CustomButton
                title={
                  <View style={styles.logoutButtonContent}>
                    <Ionicons name="log-out" size={20} color="#fff" style={styles.logoutIcon} />
                    <Text style={styles.logoutButtonText}>Çıkış Yap</Text>
                  </View>
                }
                onPress={handleLogout}
                style={styles.logoutButton}/>

            </View>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#2D2D2D',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2D2D2D',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 15,
    minHeight: 75,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: width / 2 - 25,
    marginTop: 10,
  },
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 120,
  },
  dismissKeyboard: {
    flex: 1,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  profileImage: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    borderColor: '#2E86C1',
  },
  profileInfo: {
    marginLeft: 15,
    flex: 1,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  infoContainer: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
    marginBottom: 15,
    width: '90%',
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  icon: {
    marginRight: 15,
  },
  userData: {
    fontSize: 16,
    color: '#555',
    flex: 1,
  },
  editButton: {
    backgroundColor: '#1976D2',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 3 },
    elevation: 3,
    marginBottom: 15,
    alignSelf: 'center',
    width: '70%',
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  feedbackContainer: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
    marginBottom: 15,
    width: '90%',
    alignSelf: 'center',
  },
  feedbackTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    fontSize: 16,
    backgroundColor: '#f8f9fa',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    width: '60%',
    alignSelf: 'center',
  },
  submitIcon: {
    marginRight: 8,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: '#D32F2F',
    padding: 15,
    position: 'relative',
    borderRadius: 10,
    marginBottom: 40,
    marginTop: 20,
    left: 60,
    width: '40%',
  },
  logoutButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutIcon: {
    marginRight: 8,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  contentContainer: {
    padding: 15,
    alignItems:"center",
  },
});

export default ProfileScreen;