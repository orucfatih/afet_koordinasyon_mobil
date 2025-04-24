import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  TextInput,
  Image,
  Platform,
  Keyboard,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { getAuth } from 'firebase/auth';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { getFirestore, doc, setDoc } from 'firebase/firestore';
import app from '../../firebaseConfig';
import * as Location from 'expo-location';
import { Picker } from '@react-native-picker/picker';

const Missing = ({ navigation }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [image, setImage] = useState(null);
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    age: '',
    gender: 'erkek',
    district: '',
    clothingDescription: '',
    otherInfo: '',
    lastSeenLocation: null
  });

  const auth = getAuth(app);
  const storage = getStorage(app);
  const db = getFirestore(app);

  const districts = [
    'Aliağa', 'Balçova', 'Bayraklı', 'Bornova', 'Buca', 'Çiğli', 'Gaziemir',
    'Güzelbahçe', 'Karabağlar', 'Karşıyaka', 'Konak', 'Menemen', 'Narlıdere'
  ];

  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const takePicture = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [3, 4],
        quality: 1,
      });

      if (!result.canceled) {
        setImage(result.assets[0].uri);
      }
    } catch (error) {
      console.error('Fotoğraf çekilirken hata:', error);
      Alert.alert('Hata', 'Fotoğraf çekilirken bir hata oluştu.');
    }
  };

  const selectLocation = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Konum izni gerekli', 'Son görülme konumunu seçmek için konum iznine ihtiyacımız var.');
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
      setFormData(prev => ({
        ...prev,
        lastSeenLocation: {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude
        }
      }));

      Alert.alert('Başarılı', 'Konum başarıyla kaydedildi.');
    } catch (error) {
      console.error('Konum alınırken hata:', error);
      Alert.alert('Hata', 'Konum alınırken bir hata oluştu.');
    }
  };

  const handleSubmit = async () => {
    if (!image) {
      Alert.alert('Uyarı', 'Lütfen bir fotoğraf çekin.');
      return;
    }

    if (!formData.fullName || !formData.phone || !formData.age || !formData.district) {
      Alert.alert('Uyarı', 'Lütfen zorunlu alanları doldurun.');
      return;
    }

    try {
      setUploading(true);

      // Fotoğrafı yükle
      const response = await fetch(image);
      const blob = await response.blob();
      const fileName = `missing_${auth.currentUser.uid}_${Date.now()}.jpg`;
      const storageRef = ref(storage, `missing-reports/${auth.currentUser.uid}/${fileName}`);
      
      await uploadBytes(storageRef, blob);
      const imageUrl = await getDownloadURL(storageRef);

      // Firestore'a kaydet
      const docRef = doc(db, 'missing-reports', `${auth.currentUser.uid}_${Date.now()}`);
      await setDoc(docRef, {
        ...formData,
        imageUrl,
        reporterId: auth.currentUser.uid,
        reporterEmail: auth.currentUser.email,
        timestamp: new Date(),
        status: 'active'
      });

      Alert.alert('Başarılı', 'Kayıp ihbarı başarıyla gönderildi.', [
        { text: 'Tamam', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      console.error('Kayıp ihbarı gönderilirken hata:', error);
      Alert.alert('Hata', 'Kayıp ihbarı gönderilirken bir hata oluştu.');
    } finally {
      setUploading(false);
    }
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>İzin kontrolü yapılıyor...</Text></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.container}><Text>Kamera izni gerekli</Text></View>;
  }

  return (
    <ScrollView 
      style={styles.container}
      keyboardShouldPersistTaps="handled"
    >
      <TouchableOpacity 
        style={styles.dismissKeyboard} 
        activeOpacity={1} 
        onPress={() => Keyboard.dismiss()}
      >
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.title}>Kayıp İhbarı</Text>
        </View>

        <View style={styles.content}>
          {image ? (
            <View style={styles.imageContainer}>
              <Image source={{ uri: image }} style={styles.previewImage} />
              <TouchableOpacity style={styles.retakeButton} onPress={takePicture}>
                <Text style={styles.retakeButtonText}>Yeniden Çek</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity style={styles.cameraButton} onPress={takePicture}>
              <Ionicons name="camera" size={40} color="#fff" />
              <Text style={styles.cameraButtonText}>Fotoğraf Çek</Text>
            </TouchableOpacity>
          )}

          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Ad Soyad"
              value={formData.fullName}
              onChangeText={(text) => setFormData(prev => ({ ...prev, fullName: text }))}
            />

            <TextInput
              style={styles.input}
              placeholder="Telefon"
              value={formData.phone}
              onChangeText={(text) => setFormData(prev => ({ ...prev, phone: text }))}
              keyboardType="phone-pad"
            />

            <TextInput
              style={styles.input}
              placeholder="Yaş"
              value={formData.age}
              onChangeText={(text) => setFormData(prev => ({ ...prev, age: text }))}
              keyboardType="numeric"
            />

            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.gender}
                onValueChange={(value) => setFormData(prev => ({ ...prev, gender: value }))}
                style={styles.picker}
              >
                <Picker.Item label="Erkek" value="erkek" />
                <Picker.Item label="Kadın" value="kadın" />
              </Picker>
            </View>

            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={formData.district}
                onValueChange={(value) => setFormData(prev => ({ ...prev, district: value }))}
                style={styles.picker}
              >
                <Picker.Item label="İlçe Seçin" value="" />
                {districts.map((district, index) => (
                  <Picker.Item key={index} label={district} value={district} />
                ))}
              </Picker>
            </View>

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Kıyafet Tanımı"
              value={formData.clothingDescription}
              onChangeText={(text) => setFormData(prev => ({ ...prev, clothingDescription: text }))}
              multiline
              numberOfLines={3}
            />

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Diğer Bilgiler"
              value={formData.otherInfo}
              onChangeText={(text) => setFormData(prev => ({ ...prev, otherInfo: text }))}
              multiline
              numberOfLines={3}
            />

            <TouchableOpacity style={styles.locationButton} onPress={selectLocation}>
              <Text style={styles.locationButtonText}>
                {formData.lastSeenLocation ? 'Son Görülme Konumu Seçildi' : 'Son Görülme Konumu Seç'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.submitButton}
              onPress={handleSubmit}
              disabled={uploading}
            >
              {uploading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.submitButtonText}>İhbar Gönder</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backButton: {
    marginRight: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    padding: 20,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  previewImage: {
    width: 300,
    height: 400,
    borderRadius: 10,
    marginBottom: 10,
  },
  retakeButton: {
    backgroundColor: '#666',
    padding: 10,
    borderRadius: 5,
  },
  retakeButtonText: {
    color: '#fff',
    fontSize: 16,
  },
  cameraButton: {
    backgroundColor: '#007AFF',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 10,
  },
  form: {
    gap: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  locationButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  locationButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#D32F2F',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  dismissKeyboard: {
    flex: 1,
  },
});

export default Missing; 
