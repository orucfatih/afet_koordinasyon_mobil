import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  TextInput,
  Modal,
  Platform,
  ScrollView,
  Alert,
  ActivityIndicator,
  StatusBar,
  SafeAreaView,
  PermissionsAndroid,
  KeyboardAvoidingView
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import DateTimePicker from '@react-native-community/datetimepicker';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { Picker } from '@react-native-picker/picker';
import firestore from '@react-native-firebase/firestore';
import auth from '@react-native-firebase/auth';
import app from '../../firebaseConfig';
import { GOOGLE_CLOUD_API_KEY } from '@env';
import AudioRecorderPlayer, {
  AVEncoderAudioQualityIOSType,
  AVEncodingOption,
  AudioEncoderAndroidType,
  AudioSourceAndroidType,
  OutputFormatAndroidType,
} from 'react-native-audio-recorder-player';
import RNFS from 'react-native-fs';

const Report = ({ navigation }) => {
  const [reports, setReports] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [searchRegion, setSearchRegion] = useState('');
  const [searchType, setSearchType] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [currentField, setCurrentField] = useState('');
  const [audioRecorderPlayer, setAudioRecorderPlayer] = useState(null);
  const [recordingPath, setRecordingPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [recordingTimer, setRecordingTimer] = useState(0);
  const [recordingInterval, setRecordingInterval] = useState(null);

  // Yeni rapor için state'ler
  const [newReport, setNewReport] = useState({
    bolge: '',
    tur: 'Durum Değerlendirme Raporu',
    ozet: '',
    detaylar: '',
    ihtiyaclar: '',
    tarih: new Date().toISOString(),
    created_at: Date.now() / 1000,
    updated_at: Date.now() / 1000
  });

  const reportTypes = [
    { label: 'Durum Değerlendirme Raporu', value: 'Durum Değerlendirme Raporu' },
    { label: 'Hasar Tespit Raporu', value: 'Hasar Tespit Raporu' },
    { label: 'İhtiyaç Analiz Raporu', value: 'İhtiyaç Analiz Raporu' },
    { label: 'Müdahale Raporu', value: 'Müdahale Raporu' },
    { label: 'Koordinasyon Raporu', value: 'Koordinasyon Raporu' },
  ];

  useEffect(() => {
    // AudioRecorderPlayer instance'ını oluştur
    const audioRecorderPlayer = new AudioRecorderPlayer();
    setAudioRecorderPlayer(audioRecorderPlayer);

    // Cleanup function
    return () => {
      if (audioRecorderPlayer) {
        audioRecorderPlayer.stopRecorder();
        audioRecorderPlayer.removeRecordBackListener();
      }
      if (recordingInterval) {
        clearInterval(recordingInterval);
      }
    };
  }, []);

  useEffect(() => {
    // Authentication state dinleyicisi
    const unsubscribe = auth().onAuthStateChanged((user) => {
      setUser(user);
      setAuthLoading(false);
      if (user) {
        console.log('Kullanıcı oturum açmış:', user.email);
      } else {
        console.log('Kullanıcı oturum açmamış');
      }
    });

    return unsubscribe; // Cleanup
  }, []);

  useEffect(() => {
    if (!authLoading) {
      loadReports();
    }
  }, [authLoading, user]);

  const requestMicrophonePermission = async () => {
    try {
      if (Platform.OS === 'android') {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          {
            title: 'Mikrofon İzni',
            message: 'Sesli not almak için mikrofon izni gerekiyor.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      }
      return true;
    } catch (err) {
      console.error('Mikrofon izni hatası:', err);
      return false;
    }
  };

  const getRecordingPath = () => {
    const timestamp = Date.now();
    const fileName = Platform.OS === 'ios' ? `recording_${timestamp}.m4a` : `recording_${timestamp}.mp3`;
    
    if (Platform.OS === 'ios') {
      return `${RNFS.DocumentDirectoryPath}/${fileName}`;
    } else {
      return `${RNFS.ExternalDirectoryPath}/${fileName}`;
    }
  };

  const startListening = async (field) => {
    try {
      const hasPermission = await requestMicrophonePermission();
      if (!hasPermission) {
        Alert.alert('Hata', 'Mikrofon izni verilmedi');
        return;
      }

      setCurrentField(field);
      setIsListening(true);

      const path = getRecordingPath();
      setRecordingPath(path);

      const audioSet = Platform.OS === 'ios' ? {
        AVEncoderAudioQualityKeyIOS: AVEncoderAudioQualityIOSType.high,
        AVNumberOfChannelsKeyIOS: 1,
        AVFormatIDKeyIOS: AVEncodingOption.aac,
      } : {
        AudioEncoderAndroid: AudioEncoderAndroidType.AAC,
        AudioSourceAndroid: AudioSourceAndroidType.MIC,
        OutputFormatAndroid: OutputFormatAndroidType.MPEG_4,
      };

      const uri = await audioRecorderPlayer.startRecorder(path, audioSet);
      console.log('Ses kaydı başladı:', uri);

      // Timer başlat
      setRecordingTimer(0);
      const interval = setInterval(() => {
        setRecordingTimer(prev => {
          if (prev >= 60) { // 60 saniye sonra otomatik durdur
            stopListening();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
      setRecordingInterval(interval);

    } catch (error) {
      console.error('Ses kaydı başlatma hatası:', error);
      Alert.alert('Hata', 'Ses kaydı başlatılırken bir hata oluştu.');
      setIsListening(false);
    }
  };

  const stopListening = async () => {
    try {
      if (!audioRecorderPlayer) return;

      // Timer'ı durdur
      if (recordingInterval) {
        clearInterval(recordingInterval);
        setRecordingInterval(null);
      }

      const result = await audioRecorderPlayer.stopRecorder();
      console.log('Ses kaydı durduruldu:', result);
      
      setIsListening(false);

      // Ses dosyasını Google Cloud Speech-to-Text API'ye gönder
      await transcribeAudio(recordingPath, currentField);

    } catch (error) {
      console.error('Ses kaydı durdurma hatası:', error);
      Alert.alert('Hata', 'Ses kaydı durdurulurken bir hata oluştu.');
      setIsListening(false);
    }
  };

  const transcribeAudio = async (audioPath, field) => {
    try {
      setLoading(true);

      // Ses dosyasının var olup olmadığını kontrol et
      const exists = await RNFS.exists(audioPath);
      if (!exists) {
        throw new Error('Ses dosyası bulunamadı');
      }

      // Ses dosyasını base64'e çevir
      const audioData = await RNFS.readFile(audioPath, 'base64');
      
      if (!audioData || audioData.length === 0) {
        throw new Error('Ses dosyası boş');
      }

      console.log('Ses dosyası boyutu:', audioData.length, 'bytes');
      
      // Google Cloud Speech-to-Text API'ye istek gönder
      const response = await fetch(
        `https://speech.googleapis.com/v1/speech:recognize?key=${GOOGLE_CLOUD_API_KEY}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            config: {
              encoding: Platform.OS === 'ios' ? 'MP3' : 'MP3',
              sampleRateHertz: 44100,
              languageCode: 'tr-TR',
              enableAutomaticPunctuation: true,
              model: 'default',
              useEnhanced: true,
            },
            audio: {
              content: audioData,
            },
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Hatası:', response.status, errorText);
        throw new Error(`API Hatası: ${response.status}`);
      }

      const data = await response.json();
      console.log('API Yanıtı:', data);
      
      if (data.results && data.results[0] && data.results[0].alternatives && data.results[0].alternatives[0]) {
        const transcription = data.results[0].alternatives[0].transcript;
        
        // Mevcut metne ekle
        if (selectedReport) {
          const currentText = selectedReport[field] || '';
          const newText = currentText + (currentText ? ' ' : '') + transcription;
          setSelectedReport(prev => ({
            ...prev,
            [field]: newText
          }));
        } else {
          const currentText = newReport[field] || '';
          const newText = currentText + (currentText ? ' ' : '') + transcription;
          setNewReport(prev => ({
            ...prev,
            [field]: newText
          }));
        }

        Alert.alert('Başarılı', 'Ses başarıyla metne çevrildi.');
      } else {
        Alert.alert('Uyarı', 'Ses tanınamadı. Lütfen tekrar deneyin.');
      }

      // Geçici ses dosyasını sil
      try {
        await RNFS.unlink(audioPath);
      } catch (deleteError) {
        console.log('Ses dosyası silinemedi:', deleteError);
      }

    } catch (error) {
      console.error('Ses tanıma hatası:', error);
      Alert.alert('Hata', `Ses tanıma sırasında bir hata oluştu: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadReports = async () => {
    setLoading(true);
    try {
      const savedReports = await AsyncStorage.getItem('reports');
      if (savedReports) {
        setReports(JSON.parse(savedReports));
      }
    } catch (error) {
      console.error('Raporlar yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveReports = async (updatedReports) => {
    try {
      await AsyncStorage.setItem('reports', JSON.stringify(updatedReports));
      setReports(updatedReports);
    } catch (error) {
      console.error('Raporlar kaydedilirken hata:', error);
    }
  };

  const handleAddReport = async () => {
    if (!newReport.bolge || !newReport.ozet || !newReport.detaylar || !newReport.ihtiyaclar) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurun.');
      return;
    }

    setLoading(true);

    const report = {
      id: Date.now().toString(),
      ...newReport,
      created_at: Date.now() / 1000,
      updated_at: Date.now() / 1000
    };

    try {
      // Önce yerel listeyi güncelle
    const updatedReports = [...reports, report];
    await saveReports(updatedReports);
      
      // Eğer kullanıcı oturum açmışsa Firestore'a da kaydet
      if (auth().currentUser) {
        await firestore()
          .collection('reports')
          .doc(`${auth().currentUser.uid}_${Date.now()}`)
          .set({
            ...report,
            requesterId: auth().currentUser.uid,
            requesterEmail: auth().currentUser.email,
            timestamp: new Date(),
            status: 'active'
          });
      }
      
    setModalVisible(false);
    setNewReport({
      bolge: '',
      tur: 'Durum Değerlendirme Raporu',
      ozet: '',
      detaylar: '',
      ihtiyaclar: '',
      tarih: new Date().toISOString(),
      created_at: Date.now() / 1000,
      updated_at: Date.now() / 1000
    });
      
      Alert.alert('Başarılı', 'Rapor başarıyla kaydedildi.');
      
    } catch (error) {
      console.error('Rapor ekleme hatası:', error);
      Alert.alert('Hata', 'Rapor kaydedilirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateReport = async () => {
    if (!selectedReport) return;

    setLoading(true);

    const updatedReport = {
      ...selectedReport,
      updated_at: Date.now() / 1000
    };

    try {
    const updatedReports = reports.map(report =>
      report.id === selectedReport.id ? updatedReport : report
    );

    await saveReports(updatedReports);
    setEditModalVisible(false);
    setSelectedReport(null);
      
      Alert.alert('Başarılı', 'Rapor başarıyla güncellendi.');
      
    } catch (error) {
      console.error('Rapor güncelleme hatası:', error);
      Alert.alert('Hata', 'Rapor güncellenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReport = async (reportId) => {
    Alert.alert(
      'Onay',
      'Bu raporu silmek istediğinizden emin misiniz?',
      [
        {
          text: 'İptal',
          style: 'cancel',
        },
        {
          text: 'Sil',
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
            const updatedReports = reports.filter(report => report.id !== reportId);
            await saveReports(updatedReports);
              Alert.alert('Başarılı', 'Rapor başarıyla silindi.');
            } catch (error) {
              console.error('Rapor silme hatası:', error);
              Alert.alert('Hata', 'Rapor silinirken bir hata oluştu.');
            } finally {
              setLoading(false);
            }
          },
        },
      ],
    );
  };

  const filterReports = () => {
    return reports.filter(report => {
      const regionMatch = searchRegion
        ? report.bolge.toLowerCase().includes(searchRegion.toLowerCase())
        : true;
      const typeMatch = searchType
        ? report.tur === searchType
        : true;
      return regionMatch && typeMatch;
    });
  };

  const renderInputWithVoice = (label, value, onChangeText, field) => (
    <View style={styles.inputContainer}>
      <Text style={styles.inputLabel}>{label}</Text>
      <View style={styles.inputWrapper}>
        <TextInput
          style={[styles.input, field === 'detaylar' && styles.textArea]}
          multiline={field === 'detaylar' || field === 'ihtiyaclar'}
          numberOfLines={field === 'detaylar' || field === 'ihtiyaclar' ? 4 : 1}
          value={value}
          onChangeText={onChangeText}
          placeholder={`${label} giriniz...`}
          placeholderTextColor="#999"
          autoCorrect={false}
          spellCheck={false}
          autoCapitalize="none"
          keyboardType="default"
          returnKeyType={field === 'detaylar' || field === 'ihtiyaclar' ? 'default' : 'next'}
          blurOnSubmit={field === 'detaylar' || field === 'ihtiyaclar' ? false : true}
          {...(Platform.OS === 'ios' && {
            clearButtonMode: 'while-editing',
          })}
        />
        <TouchableOpacity
          style={[
            styles.voiceButton,
            isListening && currentField === field && styles.voiceButtonActive
          ]}
          onPress={() => isListening ? stopListening() : startListening(field)}
          disabled={loading}
        >
          <Ionicons
            name={isListening && currentField === field ? "stop" : "mic-outline"}
            size={24}
            color={isListening && currentField === field ? "white" : "#666"}
          />
        </TouchableOpacity>
      </View>
      {isListening && currentField === field && (
        <View style={styles.recordingIndicator}>
          <View style={styles.recordingDot} />
          <Text style={styles.recordingText}>
            Ses kaydediliyor... ({Math.floor(recordingTimer / 60)}:{(recordingTimer % 60).toString().padStart(2, '0')})
          </Text>
        </View>
      )}
      {loading && currentField === field && (
        <View style={styles.processingIndicator}>
          <ActivityIndicator size="small" color="#4CAF50" />
          <Text style={styles.processingText}>Ses işleniyor...</Text>
        </View>
      )}
    </View>
  );

  const renderReportItem = ({ item }) => (
    <View style={styles.reportItem}>
      <View style={styles.reportHeader}>
        <Text style={styles.reportTitle}>{item.bolge}</Text>
        <View style={styles.reportActions}>
          <TouchableOpacity
            onPress={() => {
              setSelectedReport(item);
              setEditModalVisible(true);
            }}
            style={styles.actionButton}
          >
            <Ionicons name="create-outline" size={24} color="#2196F3" />
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => handleDeleteReport(item.id)}
            style={styles.actionButton}
          >
            <Ionicons name="trash-outline" size={24} color="#D32F2F" />
          </TouchableOpacity>
        </View>
      </View>
      <Text style={styles.reportType}>Tür: {item.tur}</Text>
      <Text style={styles.reportDescription}>Özet: {item.ozet}</Text>
      <Text style={styles.reportDate}>
        Tarih: {new Date(item.tarih).toLocaleString('tr-TR')}
      </Text>
    </View>
  );

  const renderEmptyList = () => (
    <View style={styles.emptyListContainer}>
      <Ionicons name="document-text-outline" size={60} color="#ccc" />
      <Text style={styles.emptyListText}>Henüz rapor bulunmuyor</Text>
      <Text style={styles.emptyListSubText}>Yeni bir rapor eklemek için sağ üstteki "Yeni Rapor" butonunu kullanın</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#D32F2F" />
          <Text style={styles.loadingText}>İşlem yapılıyor...</Text>
        </View>
      )}
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Raporlar</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setModalVisible(true)}
            disabled={loading}
          >
            <Ionicons name="add" size={24} color="white" />
            <Text style={styles.addButtonText}>Yeni Rapor</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.filterContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Afet Bölgesi Ara"
            placeholderTextColor="#999"
            value={searchRegion}
            onChangeText={setSearchRegion}
            autoCorrect={false}
            spellCheck={false}
            autoCapitalize="none"
            keyboardType="default"
            returnKeyType="search"
            {...(Platform.OS === 'ios' && {
              clearButtonMode: 'while-editing',
            })}
          />

          <View style={styles.typePickerContainer}>
            <Picker
              selectedValue={searchType}
              onValueChange={setSearchType}
              style={styles.typePicker}
              mode="dropdown"
            >
              <Picker.Item label="Tüm Türler" value="" color="#999" />
              {reportTypes.map(type => (
                <Picker.Item
                  key={type.value}
                  label={type.label}
                  value={type.value}
                  color="#999"
                />
              ))}
            </Picker>
          </View>
        </View>

        <FlatList
          data={filterReports()}
          renderItem={renderReportItem}
          keyExtractor={item => item.id}
          style={styles.list}
          contentContainerStyle={filterReports().length === 0 ? {flex: 1} : {paddingBottom: 20}}
          ListEmptyComponent={renderEmptyList}
          refreshing={loading}
          onRefresh={loadReports}
        />

        {/* Yeni Rapor Modalı */}
        <Modal
          visible={modalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setModalVisible(false)}
        >
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.modalContainer}
          >
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Yeni Rapor</Text>
                <TouchableOpacity onPress={() => setModalVisible(false)}>
                  <Ionicons name="close" size={24} color="#333" />
                </TouchableOpacity>
              </View>
              
              <ScrollView style={styles.modalScrollView}>
                {renderInputWithVoice(
                  "Afet Bölgesi",
                  newReport.bolge,
                  text => setNewReport({...newReport, bolge: text}),
                  "bolge"
                )}

                <View style={styles.pickerContainer}>
                  <Text style={styles.inputLabel}>Rapor Türü</Text>
                  <View style={styles.pickerWrapper}>
                    <Picker
                      selectedValue={newReport.tur}
                      onValueChange={value => setNewReport({...newReport, tur: value})}
                      style={styles.picker}
                      mode="dropdown"
                    >
                      {reportTypes.map(type => (
                        <Picker.Item
                          key={type.value}
                          label={type.label}
                          value={type.value}
                          color="#999"
                        />
                      ))}
                    </Picker>
                  </View>
                </View>

                {renderInputWithVoice(
                  "Durum Özeti",
                  newReport.ozet,
                  text => setNewReport({...newReport, ozet: text}),
                  "ozet"
                )}

                {renderInputWithVoice(
                  "Detaylı Bilgiler",
                  newReport.detaylar,
                  text => setNewReport({...newReport, detaylar: text}),
                  "detaylar"
                )}

                {renderInputWithVoice(
                  "İhtiyaçlar ve Öneriler",
                  newReport.ihtiyaclar,
                  text => setNewReport({...newReport, ihtiyaclar: text}),
                  "ihtiyaclar"
                )}

                <View style={styles.modalButtons}>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.cancelButton]}
                    onPress={() => setModalVisible(false)}
                    disabled={loading}
                  >
                    <Text style={styles.modalButtonText}>İptal</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.saveButton, loading && styles.disabledButton]}
                    onPress={handleAddReport}
                    disabled={loading}
                  >
                    {loading ? (
                      <ActivityIndicator size="small" color="white" />
                    ) : (
                    <Text style={styles.modalButtonText}>Kaydet</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </ScrollView>
            </View>
          </KeyboardAvoidingView>
        </Modal>

        {/* Düzenleme Modalı */}
        <Modal
          visible={editModalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setEditModalVisible(false)}
        >
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.modalContainer}
          >
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Raporu Düzenle</Text>
                <TouchableOpacity onPress={() => setEditModalVisible(false)}>
                  <Ionicons name="close" size={24} color="#333" />
                </TouchableOpacity>
              </View>
              
              <ScrollView style={styles.modalScrollView}>
                {renderInputWithVoice(
                  "Afet Bölgesi",
                  selectedReport?.bolge || '',
                  text => setSelectedReport({...selectedReport, bolge: text}),
                  "bolge"
                )}

                <View style={styles.pickerContainer}>
                  <Text style={styles.inputLabel}>Rapor Türü</Text>
                  <View style={styles.pickerWrapper}>
                    <Picker
                      selectedValue={selectedReport?.tur}
                      onValueChange={value => setSelectedReport({...selectedReport, tur: value})}
                      style={styles.picker}
                      mode="dropdown"
                    >
                      {reportTypes.map(type => (
                        <Picker.Item
                          key={type.value}
                          label={type.label}
                          value={type.value}
                          color="#999"
                        />
                      ))}
                    </Picker>
                  </View>
                </View>

                {renderInputWithVoice(
                  "Durum Özeti",
                  selectedReport?.ozet || '',
                  text => setSelectedReport({...selectedReport, ozet: text}),
                  "ozet"
                )}

                {renderInputWithVoice(
                  "Detaylı Bilgiler",
                  selectedReport?.detaylar || '',
                  text => setSelectedReport({...selectedReport, detaylar: text}),
                  "detaylar"
                )}

                {renderInputWithVoice(
                  "İhtiyaçlar ve Öneriler",
                  selectedReport?.ihtiyaclar || '',
                  text => setSelectedReport({...selectedReport, ihtiyaclar: text}),
                  "ihtiyaclar"
                )}

                <View style={styles.modalButtons}>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.cancelButton]}
                    onPress={() => setEditModalVisible(false)}
                    disabled={loading}
                  >
                    <Text style={styles.modalButtonText}>İptal</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.saveButton, loading && styles.disabledButton]}
                    onPress={handleUpdateReport}
                    disabled={loading}
                  >
                    {loading ? (
                      <ActivityIndicator size="small" color="white" />
                    ) : (
                    <Text style={styles.modalButtonText}>Güncelle</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </ScrollView>
            </View>
          </KeyboardAvoidingView>
        </Modal>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#2D2D2D',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#2D2D2D',
    paddingTop: Platform.OS === 'android' ? 20 : 16,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    zIndex: 1000,
    position: 'relative',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    flex: 1,
    textAlign: 'center',
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4CAF50',
    padding: 8,
    borderRadius: 8,
  },
  addButtonText: {
    color: 'white',
    marginLeft: 4,
  },
  filterContainer: {
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    zIndex: 999,
    position: 'relative',
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    backgroundColor: '#fafafa',
    color: 'black',
  },
  typePickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#fafafa',
  },
  typePicker: {
    height: 50,
    color: '#black',
  },
  list: {
    flex: 1,
    paddingTop: 8,
  },
  reportItem: {
    backgroundColor: 'white',
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  reportHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  reportTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
    color: '#333',
  },
  reportActions: {
    flexDirection: 'row',
  },
  actionButton: {
    padding: 4,
    marginLeft: 8,
  },
  reportType: {
    color: '#666',
    marginBottom: 4,
  },
  reportDescription: {
    marginBottom: 8,
    color: '#333',
  },
  reportDate: {
    color: '#666',
    fontSize: 12,
  },
  emptyListContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyListText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginTop: 10,
  },
  emptyListSubText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    margin: 20,
    borderRadius: 12,
    maxHeight: '90%',
    overflow: 'hidden',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  modalScrollView: {
    padding: 16,
    maxHeight: '100%',
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 16,
    marginBottom: 8,
    color: '#333',
    fontWeight: '500',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    backgroundColor: '#fafafa',
  },
  input: {
    flex: 1,
    padding: 12,
    fontSize: 16,
    color: 'black',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  voiceButton: {
    padding: 12,
    borderLeftWidth: 1,
    borderLeftColor: '#ddd',
    borderRadius: 4,
  },
  voiceButtonActive: {
    backgroundColor: '#D32F2F',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    padding: 8,
    backgroundColor: '#fff3cd',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#ffeaa7',
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#D32F2F',
    marginRight: 8,
  },
  recordingText: {
    color: '#856404',
    fontSize: 12,
    fontWeight: '500',
  },
  processingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    padding: 8,
    backgroundColor: '#d4edda',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#c3e6cb',
  },
  processingText: {
    color: '#155724',
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 8,
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    backgroundColor: '#fafafa',
    overflow: 'hidden',
  },
  picker: {
    height: 50,
    color: 'black',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 16,
    marginBottom: 20,
  },
  modalButton: {
    padding: 12,
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
    marginLeft: 8,
  },
  cancelButton: {
    backgroundColor: '#666',
  },
  saveButton: {
    backgroundColor: '#4CAF50',
  },
  modalButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  },
  loadingText: {
    color: 'white',
    marginTop: 10,
    fontSize: 16,
  },
  disabledButton: {
    opacity: 0.7,
  },
});

export default Report;