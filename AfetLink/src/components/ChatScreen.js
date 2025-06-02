import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, TextInput, FlatList, ScrollView, SafeAreaView, Image, KeyboardAvoidingView, Platform, StatusBar, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Ionicons from 'react-native-vector-icons/Ionicons';
import database from '@react-native-firebase/database';
import auth from '@react-native-firebase/auth';

const ChatScreen = ({ navigation }) => {
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
  
  const currentUser = auth().currentUser;

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
      const teamRef = database().ref('teams').push();
      await teamRef.set({
        name: newTeamName.trim(),
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
      // Email'den userID bul
      const emailRef = database().ref(`emailToUserId/${addMemberEmail.toLowerCase().trim()}`);
      const emailSnapshot = await emailRef.once('value');
      
      if (!emailSnapshot.exists()) {
        Alert.alert('Hata', 'Bu email ile kayıtlı kullanıcı bulunamadı.');
        return;
      }
      
      const userId = emailSnapshot.val();
      const selectedTeamData = teams.find(team => team.id === selectedTeam);
      
      // Zaten üye mi kontrol et
      if (selectedTeamData.members.includes(userId)) {
        Alert.alert('Bilgi', 'Bu kullanıcı zaten ekip üyesi.');
        return;
      }
      
      // Kullanıcıyı ekibe ekle
      const updatedMembers = [...selectedTeamData.members, userId];
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

  const renderMessage = ({ item }) => (
    <View
      style={[styles.messageBubble, item.senderId === currentUser.uid ? styles.userMessage : styles.otherMessage]}
    >
      {item.senderId !== currentUser.uid && (
        <Text style={styles.senderName}>{item.senderName}</Text>
      )}
      <Text style={styles.messageText}>{item.text}</Text>
      <Text style={styles.messageTime}>
        {new Date(item.timestamp).toLocaleTimeString('tr-TR', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })}
      </Text>
    </View>
  );

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
    console.log(`${option} seçildi.`);
    closeAttachmentMenu();
  };

  const selectedTeamData = teams.find(team => team.id === selectedTeam);

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}/>

      <SafeAreaView style={styles.safeArea}>
        {/* Tek Dinamik TopBar */}
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.menuButtonTop} onPress={toggleMenu}>
            <Icon name="menu" size={24} color="white" />
          </TouchableOpacity>
          <Text style={styles.topBarTitle}>
            {selectedTeamData ? selectedTeamData.name : 'Ekip Sohbeti'}
          </Text>
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

        <View style={styles.container}>
          {/* Sol Menü */}
          <View style={[styles.sidebar, { width: menuOpen ? 250 : 0 }]}>
            <View style={styles.sidebarContent}>
              <Text style={styles.sidebarTitle}>Ekipler</Text>

              {/* Menü öğeleri sadece menü açıkken görünsün */}
              {menuOpen && (
                <>
                  {/* Ekip Arama */}
                  <TextInput
                    style={styles.searchInput}
                    placeholder="Ekip Ara..."
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                  />

                  {/* Yeni Ekip Ekle */}
                  <TextInput
                    style={styles.newTeamInput}
                    placeholder="Yeni Ekip Adı"
                    value={newTeamName}
                    onChangeText={setNewTeamName}
                  />
                  <TouchableOpacity 
                    style={[styles.addTeamButton, loading && styles.buttonDisabled]} 
                    onPress={addTeam}
                    disabled={loading}
                  >
                    <Text style={styles.buttonText}>
                      {loading ? 'Oluşturuluyor...' : 'Ekip Ekle'}
                    </Text>
                  </TouchableOpacity>
                </>
              )}

              <ScrollView style={styles.teamsScrollView}>
                {filteredTeams.map((team, index) => (
                  <View key={team.id} style={styles.teamItemContainer}>
                    <TouchableOpacity
                      style={[styles.teamItem, selectedTeam === team.id && styles.selectedTeam]}
                      onPress={() => {
                        setSelectedTeam(team.id);
                        setMenuOpen(false);
                      }}
                    >
                      <Text style={styles.teamText}>{team.name}</Text>
                      <Text style={styles.teamMemberCount}>
                        {team.members ? team.members.length : 0} üye
                      </Text>
                    </TouchableOpacity>

                    {/* Ekip Silme - Sadece oluşturan kişi */}
                    {team.createdBy === currentUser?.uid && (
                      <TouchableOpacity
                        style={styles.deleteButton}
                        onPress={() => deleteTeam(team.id)}
                      >
                        <Icon name="delete" size={20} color="white" />
                      </TouchableOpacity>
                    )}
                  </View>
                ))}
              </ScrollView>
            </View>
          </View>

          <KeyboardAvoidingView 
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={styles.keyboardAvoidingView}
            keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
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
                  />

                  <View style={styles.inputContainer}>
                    <TouchableOpacity style={styles.addAttachmentButton} onPress={openAttachmentMenu}>
                      <Icon name="attach-file" size={24} color="#D32F2F" />
                    </TouchableOpacity>
                    <TextInput
                      style={styles.input}
                      placeholder="Mesaj yazın..."
                      placeholderTextColor="#aaa"
                      value={input}
                      onChangeText={setInput}
                      multiline
                    />
                    <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
                      <Icon name="send" size={20} color="white" />
                    </TouchableOpacity>
                  </View>

                  {/* Ekler Menüsü */}
                  {attachmentMenuOpen && (
                    <View style={styles.attachmentOptions}>
                      <TouchableOpacity
                        style={styles.attachmentOption}
                        onPress={() => selectAttachmentOption('Resim')}
                      >
                        <Icon name="image" size={24} color="#D32F2F" />
                        <Text style={styles.attachmentText}>Resim</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.attachmentOption}
                        onPress={() => selectAttachmentOption('Fotoğraf')}
                      >
                        <Icon name="photo-camera" size={24} color="#D32F2F" />
                        <Text style={styles.attachmentText}>Fotoğraf</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.attachmentOption}
                        onPress={() => selectAttachmentOption('Belge')}
                      >
                        <Icon name="attach-file" size={24} color="#D32F2F" />
                        <Text style={styles.attachmentText}>Belge</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.attachmentOption}
                        onPress={closeAttachmentMenu}
                      >
                        <Icon name="map" size={24} color="#D32F2F" />
                        <Text style={styles.attachmentText}>Konum</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.attachmentOption}
                        onPress={closeAttachmentMenu}
                      >
                        <Icon name="cancel" size={24} color="#D32F2F" />
                        <Text style={styles.attachmentText}>Kapat</Text>
                      </TouchableOpacity>
                    </View>
                  )}
                </>
              ) : (
                <View style={styles.emptyState}>
                  <Ionicons name="chatbubbles-outline" size={60} color="#D32F2F" />
                  <Text style={styles.emptyStateText}>Lütfen bir ekip seçin veya yeni ekip oluşturun.</Text>
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
              <Text style={styles.modalTitle}>Ekibe Üye Ekle</Text>
              <TextInput
                style={styles.modalInput}
                placeholder="Üye Email Adresi"
                value={addMemberEmail}
                onChangeText={setAddMemberEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
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
                    {loading ? 'Ekleniyor...' : 'Ekle'}
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
    backgroundColor: '#2D2D2D',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  topBar: {
    backgroundColor: '#2D2D2D',
    paddingVertical: 15,
    paddingHorizontal: 16,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    elevation: 5,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 60,
  },
  menuButtonTop: {
    backgroundColor: '#FF5252',
    padding: 8,
    borderRadius: 20,
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  topBarTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
    textAlign: 'center',
  },
  topBarRight: {
    width: 40, // Menü butonu ile aynı genişlik için balance
  },
  container: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
    backgroundColor: '#D32F2F', 
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    zIndex: 2,
    overflow: 'hidden',
  },
  sidebarContent: {
    flex: 1,
    paddingTop: 20,
    paddingHorizontal: 10,
  },
  sidebarTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  teamsScrollView: {
    flex: 1,
  },
  teamItemContainer: {
    position: 'relative',
    marginBottom: 8,
  },
  teamItem: {
    paddingVertical: 12,
    paddingHorizontal: 15,
    paddingRight: 45, // Silme butonu için yer bırak
    borderRadius: 8,
    backgroundColor: '#FFCDD2',
  },
  selectedTeam: {
    backgroundColor: '#FF5252',
  },
  teamText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  teamMemberCount: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 12,
    marginTop: 2,
  },
  deleteButton: {
    position: 'absolute',
    right: 10,
    top: '50%',
    transform: [{ translateY: -10 }],
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 15,
    padding: 5,
  },
  searchInput: {
    height: 40,
    borderRadius: 20,
    paddingHorizontal: 15,
    backgroundColor: '#FFEBEE',
    marginBottom: 10,
    fontSize: 14,
  },
  newTeamInput: {
    height: 40,
    borderRadius: 20,
    paddingHorizontal: 15,
    backgroundColor: '#FFEBEE',
    marginBottom: 10,
    fontSize: 14,
  },
  addTeamButton: {
    backgroundColor: '#FF5252',
    padding: 10,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  chatArea: {
    flex: 1,
    backgroundColor: '#FFEBEE',
  },
  messagesContainer: {
    flex: 1,
    paddingHorizontal: 10,
  },
  messagesContent: {
    paddingTop: 10,
    paddingBottom: 10,
  },
  messageBubble: {
    maxWidth: '70%',
    padding: 10,
    borderRadius: 15,
    marginVertical: 5,
  },
  userMessage: {
    backgroundColor: '#FFCDD2',
    alignSelf: 'flex-end',
  },
  otherMessage: {
    backgroundColor: '#FFFFFF',
    alignSelf: 'flex-start',
  },
  messageText: {
    fontSize: 16,
    color: '#333',
  },
  senderName: {
    color: '#D32F2F',
    fontWeight: 'bold',
    fontSize: 12,
    marginBottom: 4,
  },
  messageTime: {
    color: '#666',
    fontSize: 10,
    marginTop: 4,
    alignSelf: 'flex-end',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  input: {
    flex: 1,
    maxHeight: 100,
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    backgroundColor: '#F0F0F0',
    fontSize: 16,
  },
  sendButton: {
    marginLeft: 10,
    backgroundColor: '#D32F2F',
    padding: 10,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addAttachmentButton: {
    backgroundColor: '#FFEBEE',
    padding: 10,
    borderRadius: 20,
    marginRight: 5,
  },
  attachmentOptions: {
    position: 'absolute',
    bottom: 70,
    left: 10,
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 10,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  attachmentOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
  },
  attachmentText: {
    marginLeft: 10,
    fontSize: 16,
    color: '#D32F2F',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyStateText: {
    fontSize: 18,
    color: '#D32F2F',
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 30,
  },
  emptyStateButton: {
    backgroundColor: '#D32F2F',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 3,
  },
  emptyStateButtonText: {
    color: 'white',
    marginLeft: 8,
    fontSize: 16,
    fontWeight: 'bold',
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
    padding: 20,
    borderRadius: 15,
    width: '85%',
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  modalInput: {
    height: 45,
    borderRadius: 10,
    paddingHorizontal: 15,
    backgroundColor: '#F5F5F5',
    marginBottom: 20,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 5,
  },
  cancelButton: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#D32F2F',
  },
  cancelButtonText: {
    color: '#D32F2F',
    fontWeight: 'bold',
    fontSize: 16,
  },
  confirmButton: {
    backgroundColor: '#D32F2F',
  },
  confirmButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  addMemberButton: {
    backgroundColor: '#FF5252',
    padding: 8,
    borderRadius: 20,
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

