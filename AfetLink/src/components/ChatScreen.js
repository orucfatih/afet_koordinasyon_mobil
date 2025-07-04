import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, TextInput, FlatList, ScrollView, SafeAreaView, Image, KeyboardAvoidingView, Platform, StatusBar, Alert, PermissionsAndroid, Linking } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Ionicons from 'react-native-vector-icons/Ionicons';
import database from '@react-native-firebase/database';
import auth from '@react-native-firebase/auth';
import storage from '@react-native-firebase/storage';
import { launchImageLibrary, launchCamera } from 'react-native-image-picker';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import Geolocation from 'react-native-geolocation-service';
import RNFS from 'react-native-fs';

const audioRecorderPlayer = new AudioRecorderPlayer();

const ChatScreen = ({ navigation }) => {
  // Component unmount olduğunda ses kaydını temizle
  useEffect(() => {
    return () => {
      if (audioRecorderPlayer) {
        audioRecorderPlayer.stopRecorder();
        audioRecorderPlayer.stopPlayer();
        audioRecorderPlayer.removeRecordBackListener();
        audioRecorderPlayer.removePlayBackListener();
      }
    };
  }, []);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [teams, setTeams] = useState([]);
  const [input, setInput] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [attachmentMenuOpen, setAttachmentMenuOpen] = useState(false);
  const [addMemberEmail, setAddMemberEmail] = useState('');
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Ses kaydı için state'ler
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioPath, setAudioPath] = useState('');
  
  // Dosya yükleme için loading state
  const [uploadingMedia, setUploadingMedia] = useState(false);
  
  const currentUser = auth().currentUser;

  // İzin isteme fonksiyonları
  const requestCameraPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA,
          {
            title: 'Kamera İzni',
            message: 'Fotoğraf çekebilmek için kamera izni gerekiyor.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  const requestAudioPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          {
            title: 'Mikrofon İzni',
            message: 'Ses kaydı yapabilmek için mikrofon izni gerekiyor.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  const requestLocationPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Konum İzni',
            message: 'Konumunuzu paylaşabilmek için konum izni gerekiyor.',
            buttonNeutral: 'Daha Sonra Sor',
            buttonNegative: 'İptal',
            buttonPositive: 'Tamam',
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  // Dosya yükleme fonksiyonu
  const uploadFileToStorage = async (uri, fileName, folder = 'chat-media') => {
    try {
      console.log('Dosya yükleniyor:', uri, fileName, folder);
      
      // Dosyanın var olup olmadığını kontrol et
      const fileExists = await RNFS.exists(uri);
      if (!fileExists) {
        throw new Error('Dosya bulunamadı: ' + uri);
      }
      
      // Dosya boyutunu kontrol et
      const fileStats = await RNFS.stat(uri);
      console.log('Dosya boyutu:', fileStats.size, 'bytes');
      
      if (fileStats.size === 0) {
        throw new Error('Dosya boş');
      }
      
      const reference = storage().ref(`${folder}/${selectedTeam}/${fileName}`);
      await reference.putFile(uri);
      const downloadURL = await reference.getDownloadURL();
      
      console.log('Dosya başarıyla yüklendi:', downloadURL);
      return downloadURL;
    } catch (error) {
      console.error('Dosya yükleme hatası:', error);
      throw error;
    }
  };

  // Resim seçme fonksiyonu
  const selectImage = () => {
    const options = {
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    };

    launchImageLibrary(options, async (response) => {
      if (response.assets && response.assets[0]) {
        setUploadingMedia(true);
        setAttachmentMenuOpen(false);
        
        try {
          const asset = response.assets[0];
          const fileName = `image_${Date.now()}.jpg`;
          const downloadURL = await uploadFileToStorage(asset.uri, fileName);
          
          await sendMediaMessage('image', downloadURL, {
            fileName: asset.fileName || fileName,
            fileSize: asset.fileSize,
            width: asset.width,
            height: asset.height
          });
        } catch (error) {
          Alert.alert('Hata', 'Resim gönderilemedi: ' + error.message);
        } finally {
          setUploadingMedia(false);
        }
      }
    });
  };

  // Fotoğraf çekme fonksiyonu
  const takePhoto = async () => {
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) {
      Alert.alert('Hata', 'Kamera izni gerekiyor');
      return;
    }

    const options = {
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    };

    launchCamera(options, async (response) => {
      if (response.assets && response.assets[0]) {
        setUploadingMedia(true);
        setAttachmentMenuOpen(false);
        
        try {
          const asset = response.assets[0];
          const fileName = `photo_${Date.now()}.jpg`;
          const downloadURL = await uploadFileToStorage(asset.uri, fileName);
          
          await sendMediaMessage('image', downloadURL, {
            fileName: asset.fileName || fileName,
            fileSize: asset.fileSize,
            width: asset.width,
            height: asset.height
          });
        } catch (error) {
          Alert.alert('Hata', 'Fotoğraf gönderilemedi: ' + error.message);
        } finally {
          setUploadingMedia(false);
        }
      }
    });
  };

  // Ses kaydı başlatma
  const startRecording = async () => {
    const hasPermission = await requestAudioPermission();
    if (!hasPermission) {
      Alert.alert('Hata', 'Mikrofon izni gerekiyor');
      return;
    }

    try {
      // Önceki kayıtları temizle
      if (isRecording) {
        await audioRecorderPlayer.stopRecorder();
        audioRecorderPlayer.removeRecordBackListener();
      }

      // Dosya yolu oluştur
      const fileName = `audio_${Date.now()}.${Platform.OS === 'ios' ? 'm4a' : 'mp3'}`;
      const path = Platform.select({
        ios: `${RNFS.DocumentDirectoryPath}/${fileName}`,
        android: `${RNFS.CachesDirectoryPath}/${fileName}`,
      });

      console.log('Ses kaydı başlatılıyor:', path);
      
      // Dizin var mı kontrol et, yoksa oluştur
      const dirPath = Platform.select({
        ios: RNFS.DocumentDirectoryPath,
        android: RNFS.CachesDirectoryPath,
      });
      
      const dirExists = await RNFS.exists(dirPath);
      if (!dirExists) {
        await RNFS.mkdir(dirPath);
      }
      
      setAudioPath(path);
      setIsRecording(true);
      setRecordingTime(0);
      setAttachmentMenuOpen(false);

      // Kayıt başlat
      const result = await audioRecorderPlayer.startRecorder(path, {
        AudioEncoderAndroid: audioRecorderPlayer.AUDIO_ENCODER_AAC,
        AudioSourceAndroid: audioRecorderPlayer.AUDIO_SOURCE_MIC,
        AVEncoderAudioQualityKeyIOS: audioRecorderPlayer.AV_ENCODER_AUDIO_QUALITY_HIGH,
        AVNumberOfChannelsKeyIOS: 1,
        AVFormatIDKeyIOS: audioRecorderPlayer.AV_FILE_TYPE_MPEG4AAC,
      });
      
      console.log('Kayıt başlatıldı:', result);
      
      // Zamanlayıcı başlat
      audioRecorderPlayer.addRecordBackListener((e) => {
        console.log('Kayıt süresi:', e.currentPosition);
        setRecordingTime(Math.floor(e.currentPosition / 1000));
      });
    } catch (error) {
      console.error('Ses kaydı başlatma hatası:', error);
      Alert.alert('Hata', 'Ses kaydı başlatılamadı: ' + error.message);
      setIsRecording(false);
      setAudioPath('');
    }
  };

  // Ses kaydı durdurma
  const stopRecording = async () => {
    try {
      console.log('Ses kaydı durduruluyor...');
      setUploadingMedia(true);
      
      const result = await audioRecorderPlayer.stopRecorder();
      console.log('Kayıt durduruldu:', result);
      
      setIsRecording(false);
      audioRecorderPlayer.removeRecordBackListener();

      if (result && audioPath) {
        // Dosyanın var olup olmadığını kontrol et
        const fileExists = await RNFS.exists(audioPath);
        console.log('Dosya mevcut mu:', fileExists, audioPath);
        
        if (fileExists) {
          // Dosya boyutunu kontrol et
          const fileStats = await RNFS.stat(audioPath);
          console.log('Kayıt dosyası boyutu:', fileStats.size, 'bytes');
          
          if (fileStats.size < 1000) { // 1KB'dan küçükse kayıt başarısız
            throw new Error('Kayıt çok kısa veya başarısız');
          }
          
          const fileName = `audio_${Date.now()}.${Platform.OS === 'ios' ? 'm4a' : 'mp3'}`;
          const downloadURL = await uploadFileToStorage(audioPath, fileName, 'chat-audio');
          
          await sendMediaMessage('audio', downloadURL, {
            fileName,
            duration: recordingTime
          });
          
          console.log('Ses mesajı gönderildi');
          
          // Başarılı yüklemeden sonra dosyayı sil
          try {
            await RNFS.unlink(audioPath);
            console.log('Geçici ses dosyası silindi');
          } catch (deleteError) {
            console.log('Geçici dosya silinemedi:', deleteError);
          }
        } else {
          throw new Error('Kayıt dosyası bulunamadı');
        }
      } else {
        throw new Error('Kayıt sonucu alınamadı');
      }
    } catch (error) {
      console.error('Ses kaydı durdurma hatası:', error);
      Alert.alert('Hata', 'Ses kaydı gönderilemedi: ' + error.message);
    } finally {
      setUploadingMedia(false);
      setRecordingTime(0);
      setAudioPath('');
    }
  };

  // Konum paylaşma
  const shareLocation = async () => {
    const hasPermission = await requestLocationPermission();
    if (!hasPermission) {
      Alert.alert('Hata', 'Konum izni gerekiyor');
      return;
    }

    setAttachmentMenuOpen(false);
    setUploadingMedia(true);

    Geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          
          await sendMediaMessage('location', null, {
            latitude,
            longitude,
            address: 'Konum paylaşıldı'
          });
        } catch (error) {
          Alert.alert('Hata', 'Konum gönderilemedi: ' + error.message);
        } finally {
          setUploadingMedia(false);
        }
      },
      (error) => {
        Alert.alert('Hata', 'Konum alınamadı: ' + error.message);
        setUploadingMedia(false);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
    );
  };

  // Medya mesajı gönderme
  const sendMediaMessage = async (type, url, metadata) => {
    if (!selectedTeam || !currentUser) return;

    try {
      const messageRef = database().ref(`teams/${selectedTeam}/messages`).push();
      await messageRef.set({
        type,
        url,
        metadata,
        senderId: currentUser.uid,
        senderName: currentUser.displayName || currentUser.email,
        timestamp: database.ServerValue.TIMESTAMP,
        isUser: true
      });
    } catch (error) {
      throw error;
    }
  };

  // Ekipleri dinle
  useEffect(() => {
    if (!currentUser) return;

    const teamsRef = database().ref('teams');
    const unsubscribe = teamsRef.on('value', (snapshot) => {
      if (snapshot.exists()) {
        const teamsData = snapshot.val();
        const teamsList = Object.keys(teamsData)
          .map(teamId => {
            const team = teamsData[teamId];
            // Mesajları array'e çevir ve sırala
            const messages = team.messages ? 
              Object.keys(team.messages)
                .map(messageId => ({
                  id: messageId,
                  ...team.messages[messageId]
                }))
                .sort((a, b) => b.timestamp - a.timestamp) 
              : [];

            return {
              id: teamId,
              ...team,
              messages
            };
          })
          .filter(team => team.members && team.members.includes(currentUser.uid));
        
        setTeams(teamsList);
      } else {
        setTeams([]);
      }
    });

    return () => teamsRef.off('value', unsubscribe);
  }, [currentUser]);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleSend = async () => {
    if (input.trim() !== '' && selectedTeam && currentUser) {
      try {
        const messageRef = database().ref(`teams/${selectedTeam}/messages`).push();
        await messageRef.set({
          text: input.trim(),
          type: 'text',
          senderId: currentUser.uid,
          senderName: currentUser.displayName || currentUser.email,
          timestamp: database.ServerValue.TIMESTAMP,
          isUser: true
        });
      setInput('');
      } catch (error) {
        Alert.alert('Hata', 'Mesaj gönderilemedi: ' + error.message);
      }
    }
  };

  const addTeam = async () => {
    if (newTeamName.trim() === '' || !currentUser) return;
    
    setLoading(true);
    try {
      // Sadece Firebase'de yasak karakterleri temizle
      const cleanTeamName = newTeamName.trim()
        .replace(/[.#$\[\]]/g, ''); // Sadece Firebase yasak karakterleri
      
      // Aynı isimde ekip var mı kontrol et
      const existingTeamRef = database().ref(`teams/${cleanTeamName}`);
      const existingTeamSnapshot = await existingTeamRef.once('value');
      
      if (existingTeamSnapshot.exists()) {
        Alert.alert('Hata', 'Bu isimde bir ekip zaten mevcut. Lütfen farklı bir isim seçin.');
        setLoading(false);
        return;
      }
      
      // Ekibi direkt isim ile kaydet
      await existingTeamRef.set({
        name: newTeamName.trim(), // Orijinal ismi sakla
        members: [currentUser.uid],
        createdBy: currentUser.uid,
        createdAt: database.ServerValue.TIMESTAMP,
        admins: [currentUser.uid],
        messages: {} // Boş mesaj objesi
      });
      
      setNewTeamName('');
      Alert.alert('Başarılı', 'Ekip başarıyla oluşturuldu!');
    } catch (error) {
      Alert.alert('Hata', 'Ekip oluşturulamadı: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteTeam = async (teamId) => {
    const team = teams.find(t => t.id === teamId);
    if (!team || team.createdBy !== currentUser.uid) {
      Alert.alert('Hata', 'Bu ekibi silme yetkiniz yok.');
      return;
    }

    Alert.alert(
      'Ekip Sil',
      'Bu ekibi silmek istediğinizden emin misiniz? Tüm mesajlar da silinecek.',
      [
        { text: 'İptal', style: 'cancel' },
        {
          text: 'Sil',
          style: 'destructive',
          onPress: async () => {
            try {
              await database().ref(`teams/${teamId}`).remove();
              if (selectedTeam === teamId) {
      setSelectedTeam('');
              }
              Alert.alert('Başarılı', 'Ekip ve tüm mesajları silindi.');
            } catch (error) {
              Alert.alert('Hata', 'Ekip silinemedi: ' + error.message);
            }
          }
        }
      ]
    );
  };

  const addMemberByEmail = async () => {
    if (!addMemberEmail.trim() || !selectedTeam) return;
    
    setLoading(true);
    try {
      // Yeni yapıya göre email'den userID bul
      const emailRef = database().ref('emailToUserId');
      const emailSnapshot = await emailRef.once('value');
      
      if (!emailSnapshot.exists()) {
        Alert.alert('Hata', 'Kullanıcı veritabanı bulunamadı.');
        setLoading(false);
        return;
      }
      
      const emailData = emailSnapshot.val();
      let foundUserId = null;
      
      // Tüm kullanıcıları tarayarak email eşleşmesi bul
      Object.keys(emailData).forEach(key => {
        const user = emailData[key];
        if (user.email && user.email.toLowerCase() === addMemberEmail.toLowerCase().trim()) {
          foundUserId = user.id;
        }
      });
      
      if (!foundUserId) {
        Alert.alert('Hata', 'Bu email ile kayıtlı kullanıcı bulunamadı.');
        setLoading(false);
        return;
      }
      
      const selectedTeamData = teams.find(team => team.id === selectedTeam);
      
      // Zaten üye mi kontrol et
      if (selectedTeamData.members.includes(foundUserId)) {
        Alert.alert('Bilgi', 'Bu kullanıcı zaten ekip üyesi.');
        setLoading(false);
        return;
      }
      
      // Kullanıcıyı ekibe ekle
      const updatedMembers = [...selectedTeamData.members, foundUserId];
      await database().ref(`teams/${selectedTeam}/members`).set(updatedMembers);
      
      setAddMemberEmail('');
      setShowAddMemberModal(false);
      Alert.alert('Başarılı', 'Kullanıcı ekibe eklendi!');
      
    } catch (error) {
      Alert.alert('Hata', 'Kullanıcı eklenemedi: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = ({ item }) => {
    const isCurrentUser = item.senderId === currentUser.uid;

    return (
      <View style={[styles.messageContainer, isCurrentUser ? styles.currentUserContainer : styles.otherUserContainer]}>
        <View style={[styles.messageBubble, isCurrentUser ? styles.currentUserBubble : styles.otherUserBubble]}>
          {!isCurrentUser && (
            <Text style={styles.senderName}>{item.senderName}</Text>
          )}
          
          {/* Mesaj tipine göre içerik render et */}
          {item.type === 'image' && (
            <View style={styles.mediaContainer}>
              <Image 
                source={{ uri: item.url }} 
                style={styles.messageImage}
                resizeMode="cover"
              />
              {item.metadata?.fileName && (
                <Text style={[styles.mediaFileName, isCurrentUser ? styles.currentUserText : styles.otherUserText]}>
                  {item.metadata.fileName}
                </Text>
              )}
            </View>
          )}
          
          {item.type === 'audio' && (
            <View style={styles.mediaContainer}>
              <View style={styles.audioMessage}>
                <Ionicons 
                  name="musical-notes" 
                  size={20} 
                  color={isCurrentUser ? 'white' : '#D32F2F'} 
                />
                <Text style={[styles.audioText, isCurrentUser ? styles.currentUserText : styles.otherUserText]}>
                  Ses Kaydı {item.metadata?.duration ? `(${item.metadata.duration}s)` : ''}
                </Text>
                <TouchableOpacity 
                  onPress={() => playAudio(item.url)}
                  style={styles.playButton}
                >
                  <Ionicons 
                    name="play" 
                    size={16} 
                    color={isCurrentUser ? 'white' : '#D32F2F'} 
                  />
                </TouchableOpacity>
              </View>
            </View>
          )}
          
          {item.type === 'location' && (
            <View style={styles.mediaContainer}>
              <View style={styles.locationMessage}>
                <Ionicons 
                  name="location" 
                  size={20} 
                  color={isCurrentUser ? 'white' : '#D32F2F'} 
                />
                <Text style={[styles.locationText, isCurrentUser ? styles.currentUserText : styles.otherUserText]}>
                  {item.metadata?.address || 'Konum paylaşıldı'}
                </Text>
                <TouchableOpacity 
                  onPress={() => {
                    const { latitude, longitude } = item.metadata;
                    const url = Platform.select({
                      ios: `maps:0,0?q=${latitude},${longitude}`,
                      android: `geo:0,0?q=${latitude},${longitude}`
                    });
                    Linking.openURL(url);
                  }}
                  style={styles.mapButton}
                >
                  <Ionicons 
                    name="map" 
                    size={16} 
                    color={isCurrentUser ? 'white' : '#D32F2F'} 
                  />
                </TouchableOpacity>
              </View>
            </View>
          )}
          
          {(!item.type || item.type === 'text') && (
            <Text style={[styles.messageText, isCurrentUser ? styles.currentUserText : styles.otherUserText]}>
              {item.text}
            </Text>
          )}
          
          <Text style={[styles.messageTime, isCurrentUser ? styles.currentUserTime : styles.otherUserTime]}>
            {new Date(item.timestamp).toLocaleTimeString('tr-TR', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Text>
        </View>
      </View>
    );
  };

  const filteredTeams = teams.filter((team) =>
    team.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const openAttachmentMenu = () => {
    setAttachmentMenuOpen(true);
  };

  const closeAttachmentMenu = () => {
    setAttachmentMenuOpen(false);
  };

  const selectAttachmentOption = (option) => {
    switch (option) {
      case 'Resim':
        selectImage();
        break;
      case 'Fotoğraf':
        takePhoto();
        break;
      case 'Ses':
        startRecording();
        break;
      case 'Konum':
        shareLocation();
        break;
      default:
        closeAttachmentMenu();
    }
  };

  const selectedTeamData = teams.find(team => team.id === selectedTeam);

  // Ses dosyası oynatma fonksiyonu
  const playAudio = async (audioUrl) => {
    try {
      console.log('Ses dosyası oynatılıyor:', audioUrl);
      
      // Önceki oynatmayı durdur
      await audioRecorderPlayer.stopPlayer();
      audioRecorderPlayer.removePlayBackListener();
      
      // Yeni ses dosyasını oynat
      await audioRecorderPlayer.startPlayer(audioUrl);
      
      audioRecorderPlayer.addPlayBackListener((e) => {
        console.log('Oynatma durumu:', e.currentPosition, '/', e.duration);
        if (e.currentPosition === e.duration) {
          audioRecorderPlayer.stopPlayer();
          audioRecorderPlayer.removePlayBackListener();
        }
      });
    } catch (error) {
      console.error('Ses oynatma hatası:', error);
      Alert.alert('Hata', 'Ses dosyası oynatılamadı: ' + error.message);
    }
  };

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#D32F2F"
        translucent={true}/>

      <SafeAreaView style={styles.safeArea}>
        {/* TopBar */}
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.menuButtonTop} onPress={toggleMenu}>
            <Icon name="menu" size={24} color="white" />
          </TouchableOpacity>
          <View style={styles.topBarCenter}>
            <Text style={styles.topBarTitle}>
              {selectedTeamData ? selectedTeamData.name : 'AfetLink Sohbet'}
            </Text>
            {selectedTeamData && (
              <Text style={styles.topBarSubtitle}>
                {selectedTeamData.members ? selectedTeamData.members.length : 0} üye aktif
              </Text>
            )}
          </View>
          {selectedTeam && (
            <TouchableOpacity 
              style={styles.addMemberButton} 
              onPress={() => setShowAddMemberModal(true)}
            >
              <Icon name="person-add" size={24} color="white" />
            </TouchableOpacity>
          )}
          {!selectedTeam && <View style={styles.topBarRight} />}
        </View>

        {/* Recording indicator */}
        {isRecording && (
          <View style={styles.recordingIndicator}>
            <View style={styles.recordingContent}>
              <Ionicons name="mic" size={24} color="#D32F2F" />
              <Text style={styles.recordingText}>Kayıt ediliyor... {recordingTime}s</Text>
              <TouchableOpacity 
                style={styles.stopRecordingButton}
                onPress={stopRecording}
              >
                <Ionicons name="stop" size={20} color="white" />
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Upload indicator */}
        {uploadingMedia && (
          <View style={styles.uploadIndicator}>
            <Text style={styles.uploadText}>Yükleniyor...</Text>
          </View>
        )}

        <View style={styles.container}>
          {/* Sol Menü */}
          <View style={[styles.sidebar, { width: menuOpen ? 280 : 0 }]}>
            <View style={styles.sidebarContent}>
            <Text style={styles.sidebarTitle}>Ekiplerim</Text>

            {/* Menü öğeleri sadece menü açıkken görünsün */}
            {menuOpen && (
              <>
                {/* Ekip Arama */}
                <View style={styles.searchContainer}>
                  <Icon name="search" size={20} color="#666" style={styles.searchIcon} />
                  <TextInput
                    style={styles.searchInput}
                    placeholder="Ekip ara..."
                    placeholderTextColor="#999"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                  />
                </View>

                {/* Yeni Ekip Ekle */}
                <View style={styles.newTeamContainer}>
                  <TextInput
                    style={styles.newTeamInput}
                    placeholder="Yeni ekip adı"
                    placeholderTextColor="#999"
                    value={newTeamName}
                    onChangeText={setNewTeamName}
                  />
                  <TouchableOpacity 
                    style={[styles.addTeamButton, loading && styles.buttonDisabled]} 
                    onPress={addTeam}
                    disabled={loading}
                  >
                    <Icon name="add" size={20} color="white" />
                    <Text style={styles.buttonText}>
                      {loading ? 'Oluşturuluyor' : 'Ekip Oluştur'}
                    </Text>
                  </TouchableOpacity>
                </View>
              </>
            )}

              <ScrollView style={styles.teamsScrollView} showsVerticalScrollIndicator={false}>
              {filteredTeams.map((team, index) => (
                  <View key={team.id} style={styles.teamItemContainer}>
                  <TouchableOpacity
                      style={[styles.teamItem, selectedTeam === team.id && styles.selectedTeam]}
                    onPress={() => {
                        setSelectedTeam(team.id);
                        setMenuOpen(false);
                    }}
                  >
                    <View style={styles.teamHeader}>
                      <Text style={[styles.teamText, selectedTeam === team.id && styles.selectedTeamText]}>
                        {team.name}
                      </Text>
                      <Text style={[styles.teamMemberCount, selectedTeam === team.id && styles.selectedTeamMemberCount]}>
                        {team.members ? team.members.length : 0} üye
                      </Text>
                    </View>
                    {team.messages && team.messages.length > 0 && (
                      <Text style={[styles.lastMessage, selectedTeam === team.id && styles.selectedLastMessage]} numberOfLines={1}>
                        {team.messages[0].text}
                      </Text>
                    )}
                  </TouchableOpacity>

                    {/* Ekip Silme - Sadece oluşturan kişi */}
                    {team.createdBy === currentUser?.uid && (
                  <TouchableOpacity
                    style={styles.deleteButton}
                        onPress={() => deleteTeam(team.id)}
                  >
                    <Icon name="delete" size={18} color="#D32F2F" />
                  </TouchableOpacity>
                    )}
                </View>
              ))}
            </ScrollView>
            </View>
          </View>

          <KeyboardAvoidingView 
            behavior="padding"
            style={styles.keyboardAvoidingView}
            keyboardVerticalOffset={Platform.OS === "ios" ? 160 : 100}
          >
          {/* Ana Mesajlaşma Ekranı */}
          <View style={styles.chatArea}>
            {selectedTeam ? (
              <>
                <FlatList
                    data={selectedTeamData?.messages || []}
                  keyExtractor={(item) => item.id}
                  renderItem={renderMessage}
                  style={styles.messagesContainer}
                  inverted
                    contentContainerStyle={styles.messagesContent}
                    showsVerticalScrollIndicator={false}
                />

                <View style={styles.inputContainer}>
                  <TouchableOpacity style={styles.attachmentButton} onPress={openAttachmentMenu}>
                    <Icon name="add" size={24} color="#D32F2F" />
                  </TouchableOpacity>
                  
                  <View style={styles.inputWrapper}>
                    <TextInput
                      style={styles.messageInput}
                      placeholder="Mesajınızı yazın..."
                      placeholderTextColor="#999"
                      value={input}
                      onChangeText={setInput}
                        multiline
                        maxLength={500}
                    />
                  </View>
                  
                  <TouchableOpacity 
                    style={[styles.sendButton, input.trim() ? styles.sendButtonActive : styles.sendButtonInactive]} 
                    onPress={handleSend}
                    disabled={!input.trim()}
                  >
                    <Icon name="send" size={20} color="white" />
                  </TouchableOpacity>
                </View>

                {/* Gelişmiş Ekler Menüsü */}
                {attachmentMenuOpen && (
                  <View style={styles.attachmentMenu}>
                    <TouchableOpacity style={styles.attachmentOption} onPress={() => selectAttachmentOption('Resim')}>
                      <Icon name="image" size={24} color="#D32F2F" />
                      <Text style={styles.attachmentText}>Resim Seç</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.attachmentOption} onPress={() => selectAttachmentOption('Fotoğraf')}>
                      <Icon name="photo-camera" size={24} color="#D32F2F" />
                      <Text style={styles.attachmentText}>Fotoğraf Çek</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.attachmentOption} onPress={() => selectAttachmentOption('Ses')}>
                      <Icon name="mic" size={24} color="#D32F2F" />
                      <Text style={styles.attachmentText}>Ses Kaydı</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.attachmentOption} onPress={() => selectAttachmentOption('Konum')}>
                      <Icon name="location-on" size={24} color="#D32F2F" />
                      <Text style={styles.attachmentText}>Konum Paylaş</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.attachmentOption} onPress={closeAttachmentMenu}>
                      <Icon name="close" size={24} color="#D32F2F" />
                      <Text style={styles.attachmentText}>Kapat</Text>
                    </TouchableOpacity>
                  </View>
                )}
              </>
            ) : (
              <View style={styles.emptyState}>
                <View style={styles.emptyStateIcon}>
                  <Ionicons name="chatbubbles-outline" size={80} color="#D32F2F" />
                </View>
                <Text style={styles.emptyStateTitle}>Hoş Geldiniz!</Text>
                <Text style={styles.emptyStateText}>
                  Ekibinizle iletişim kurmaya başlamak için{'\n'}
                  bir ekip seçin veya yeni ekip oluşturun.
                </Text>
                <TouchableOpacity 
                    style={styles.emptyStateButton} 
                  onPress={toggleMenu}
                >
                    <Icon name="group-add" size={24} color="white" />
                    <Text style={styles.emptyStateButtonText}>Ekipleri Göster</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
          </KeyboardAvoidingView>
        </View>

        {/* Üye Ekleme Modal */}
        {showAddMemberModal && (
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Ekibe Üye Ekle</Text>
                <TouchableOpacity 
                  style={styles.modalCloseButton}
                  onPress={() => {
                    setShowAddMemberModal(false);
                    setAddMemberEmail('');
                  }}
                >
                  <Icon name="close" size={24} color="#666" />
                </TouchableOpacity>
              </View>
              
              <View style={styles.modalInputContainer}>
                <Icon name="email" size={20} color="#666" style={styles.modalInputIcon} />
                <TextInput
                  style={styles.modalInput}
                  placeholder="örnek@email.com"
                  placeholderTextColor="#999"
                  value={addMemberEmail}
                  onChangeText={setAddMemberEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>
              
              <View style={styles.modalButtons}>
                <TouchableOpacity
                  style={[styles.modalButton, styles.cancelButton]}
                  onPress={() => {
                    setShowAddMemberModal(false);
                    setAddMemberEmail('');
                  }}
                >
                  <Text style={styles.cancelButtonText}>İptal</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modalButton, styles.confirmButton, loading && styles.buttonDisabled]}
                  onPress={addMemberByEmail}
                  disabled={loading}
                >
                  <Text style={styles.confirmButtonText}>
                    {loading ? 'Ekleniyor...' : 'Üye Ekle'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        )}
      </SafeAreaView>
    </View>
  );
};

export default ChatScreen; 

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#D32F2F',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  topBar: {
    backgroundColor: '#D32F2F',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 70,
  },
  menuButtonTop: {
    backgroundColor: '#FF5252',
    padding: 10,
    borderRadius: 25,
    width: 45,
    height: 45,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
  },
  topBarCenter: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  topBarTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  topBarSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    marginTop: 2,
  },
  topBarRight: {
    width: 45,
  },
  container: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
    backgroundColor: '#FFFFFF', 
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    zIndex: 2,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 4, height: 0 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  sidebarContent: {
    flex: 1,
    paddingTop: 20,
    paddingHorizontal: 16,
  },
  sidebarTitle: {
    color: '#D32F2F',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 25,
    paddingHorizontal: 16,
    marginBottom: 16,
    height: 48,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#333',
  },
  newTeamContainer: {
    marginBottom: 20,
  },
  newTeamInput: {
    height: 48,
    borderRadius: 25,
    paddingHorizontal: 16,
    backgroundColor: '#F5F5F5',
    marginBottom: 12,
    fontSize: 16,
    color: '#333',
  },
  addTeamButton: {
    backgroundColor: '#D32F2F',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    elevation: 4,
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
    marginLeft: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  teamsScrollView: {
    flex: 1,
  },
  teamItemContainer: {
    position: 'relative',
    marginBottom: 8,
  },
  teamItem: {
    paddingVertical: 16,
    paddingHorizontal: 16,
    paddingRight: 50,
    borderRadius: 16,
    backgroundColor: '#F8F9FA',
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  selectedTeam: {
    backgroundColor: '#D32F2F',
    borderColor: '#D32F2F',
    elevation: 4,
  },
  teamHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  teamText: {
    color: '#333',
    fontWeight: '600',
    fontSize: 16,
    flex: 1,
  },
  selectedTeamText: {
    color: 'white',
  },
  teamMemberCount: {
    color: '#666',
    fontSize: 12,
    fontWeight: '500',
  },
  selectedTeamMemberCount: {
    color: 'rgba(255, 255, 255, 0.8)',
  },
  lastMessage: {
    color: '#999',
    fontSize: 14,
    marginTop: 4,
  },
  selectedLastMessage: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  deleteButton: {
    position: 'absolute',
    right: 12,
    top: '50%',
    transform: [{ translateY: -12 }],
    backgroundColor: '#FFEBEE',
    borderRadius: 12,
    padding: 6,
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  chatArea: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    marginBottom: 100,
  },
  messagesContainer: {
    flex: 1,
    paddingHorizontal: 16,
  },
  messagesContent: {
    paddingTop: 16,
    paddingBottom: 16,
  },
  messageContainer: {
    marginVertical: 4,
  },
  currentUserContainer: {
    alignItems: 'flex-end',
  },
  otherUserContainer: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '75%',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  currentUserBubble: {
    backgroundColor: '#D32F2F',
    borderBottomRightRadius: 6,
  },
  otherUserBubble: {
    backgroundColor: '#FFFFFF',
    borderBottomLeftRadius: 6,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  senderName: {
    color: '#D32F2F',
    fontWeight: '600',
    fontSize: 12,
    marginBottom: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  currentUserText: {
    color: 'white',
  },
  otherUserText: {
    color: '#333',
  },
  messageTime: {
    fontSize: 11,
    marginTop: 4,
    alignSelf: 'flex-end',
  },
  currentUserTime: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  otherUserTime: {
    color: '#999',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 16,
    paddingBottom: Platform.OS === 'ios' ? 50 : 32,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    elevation: 4,
  },
  attachmentButton: {
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 25,
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  inputWrapper: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    borderRadius: 25,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    paddingHorizontal: 16,
    paddingVertical: 4,
  },
  messageInput: {
    minHeight: 40,
    maxHeight: 100,
    fontSize: 16,
    color: '#333',
    paddingVertical: 12,
    paddingHorizontal: 4,
  },
  sendButton: {
    padding: 12,
    borderRadius: 25,
    marginLeft: 12,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
  },
  sendButtonActive: {
    backgroundColor: '#D32F2F',
  },
  sendButtonInactive: {
    backgroundColor: '#CCCCCC',
  },
  attachmentMenu: {
    position: 'absolute',
    bottom: 90,
    left: 16,
    backgroundColor: 'white',
    borderRadius: 15,
    paddingVertical: 12,
    paddingHorizontal: 16,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    minWidth: 140,
  },
  attachmentOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
  },
  attachmentText: {
    fontSize: 16,
    color: '#333',
    marginLeft: 12,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyStateIcon: {
    marginBottom: 24,
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#D32F2F',
    marginBottom: 12,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  emptyStateButton: {
    backgroundColor: '#D32F2F',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 30,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 4,
  },
  emptyStateButtonText: {
    color: 'white',
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 20,
    width: '90%',
    maxWidth: 400,
    elevation: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  modalCloseButton: {
    padding: 4,
  },
  modalInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 24,
    marginVertical: 20,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  modalInputIcon: {
    marginRight: 12,
  },
  modalInput: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#333',
  },
  modalButtons: {
    flexDirection: 'row',
    paddingHorizontal: 24,
    paddingBottom: 24,
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButton: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  cancelButtonText: {
    color: '#666',
    fontWeight: '600',
    fontSize: 16,
  },
  confirmButton: {
    backgroundColor: '#D32F2F',
  },
  confirmButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  addMemberButton: {
    backgroundColor: '#FF5252',
    padding: 10,
    borderRadius: 25,
    width: 45,
    height: 45,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
  },
  recordingIndicator: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  recordingContent: {
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  recordingText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#D32F2F',
    marginHorizontal: 10,
  },
  stopRecordingButton: {
    padding: 10,
    borderRadius: 20,
    backgroundColor: '#D32F2F',
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadIndicator: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  uploadText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
  mediaContainer: {
    marginBottom: 10,
  },
  messageImage: {
    width: '100%',
    height: 200,
    borderRadius: 10,
  },
  mediaFileName: {
    fontSize: 12,
    marginTop: 4,
    fontStyle: 'italic',
  },
  audioMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
  },
  audioText: {
    flex: 1,
    marginHorizontal: 10,
  },
  playButton: {
    padding: 8,
    borderRadius: 15,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  locationMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
  },
  locationText: {
    flex: 1,
    marginHorizontal: 10,
  },
  mapButton: {
    padding: 8,
    borderRadius: 15,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
});

