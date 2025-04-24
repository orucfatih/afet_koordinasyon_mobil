import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, TextInput, FlatList, ScrollView, SafeAreaView, Image, KeyboardAvoidingView, Platform } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const ChatScreen = () => {
  const [selectedTeam, setSelectedTeam] = useState('');
  const [teams, setTeams] = useState([
    { name: 'Ekip 1', members: ['Ahmet', 'Mehmet', 'Ayşe'], messages: [] },
    { name: 'Ekip 2', members: ['Fatma', 'Ali', 'Deniz'], messages: [] },
    { name: 'Ekip 3', members: ['Cem', 'Zeynep'], messages: [] },
  ]);
  const [input, setInput] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [attachmentMenuOpen, setAttachmentMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleSend = () => {
    if (input.trim() !== '' && selectedTeam) {
      setTeams((prevTeams) =>
        prevTeams.map((team) =>
          team.name === selectedTeam
            ? {
                ...team,
                messages: [
                  ...team.messages,
                  { id: Date.now().toString(), text: input, isUser: true },
                ],
              }
            : team
        )
      );
      setInput('');
    }
  };

  const addTeam = () => {
    if (newTeamName.trim() === '') return;
    const newTeam = {
      name: newTeamName,
      members: [],
      messages: [],
    };
    setTeams([...teams, newTeam]);
    setNewTeamName('');
  };

  const deleteTeam = (teamName) => {
    setTeams(teams.filter((team) => team.name !== teamName));
    if (selectedTeam === teamName) {
      setSelectedTeam('');
    }
  };

  const renderMessage = ({ item }) => (
    <View
      style={[styles.messageBubble, item.isUser ? styles.userMessage : styles.otherMessage]}
    >
      <Text style={styles.messageText}>{item.text}</Text>
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

  return (
    <SafeAreaView style={styles.container}>
      {/* Sol Menü */}
      <View style={[styles.sidebar, { width: menuOpen ? 250 : 0 }]}>
        <TouchableOpacity style={styles.menuButton} onPress={toggleMenu}>
          <Icon name={menuOpen ? 'close' : 'menu'} size={30} color="white" />
        </TouchableOpacity>
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
            <TouchableOpacity style={styles.addTeamButton} onPress={addTeam}>
              <Text style={styles.buttonText}>Ekip Ekle</Text>
            </TouchableOpacity>
          </>
        )}

        <ScrollView>
          {filteredTeams.map((team, index) => (
            <View key={index}>
              <TouchableOpacity
                style={[styles.teamItem, selectedTeam === team.name && styles.selectedTeam]}
                onPress={() => {
                  setSelectedTeam(team.name);
                  setMenuOpen(false); // Ekip seçildiğinde menü kapanacak
                }}
              >
                <Text style={styles.teamText}>{team.name}</Text>
              </TouchableOpacity>

              {/* Ekip Silme */}
              <TouchableOpacity
                style={styles.deleteButton}
                onPress={() => deleteTeam(team.name)}
              >
                <Icon name="delete" size={20} color="white" />
              </TouchableOpacity>
            </View>
          ))}
        </ScrollView>
      </View>

      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
      >
      {/* Ana Mesajlaşma Ekranı */}
      <View style={styles.chatArea}>
        {selectedTeam ? (
          <>
            <View style={styles.header}>
              <Text style={styles.headerText}>{selectedTeam}</Text>
            </View>

            <FlatList
              data={teams.find((team) => team.name === selectedTeam).messages}
              keyExtractor={(item) => item.id}
              renderItem={renderMessage}
              style={styles.messagesContainer}
              inverted
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
                  onPress={() => selectAttachmentOption('Belge')}
                >
                  <Icon name="cancel" size={24} color="#D32F2F" />
                  <Text style={styles.attachmentText}>Kapat</Text>
                </TouchableOpacity>
              </View>
            )}
          </>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>Lütfen bir ekip seçin.</Text>
          </View>
        )}
      </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default ChatScreen; 

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
    backgroundColor: '#D32F2F', 
    paddingTop: 10,
    paddingHorizontal: 0,
    justifyContent: 'flex-start',
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    zIndex: 2,
    transition: 'all 0.3s ease-in-out',
  },
  menuButton: {
    position: 'absolute',
    top: 25,
    left: 10,
    zIndex: 1,
    backgroundColor: '#FF5252',
    padding: 10,
    borderRadius: 50,
  },
  sidebarTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    top: 30,
    marginBottom: 60,
    textAlign: 'center',
  },
  teamItem: {
    paddingVertical: 10,
    paddingHorizontal: 5,
    borderRadius: 5,
    marginHorizontal: 5,
    marginBottom: 5,
    backgroundColor: '#FFCDD2',
  },
  selectedTeam: {
    backgroundColor: '#FF5252',
  },
  teamText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  deleteButton: {
    position: 'absolute',
    right: 10,
    top: 10,
  },
  searchInput: {
    height: 40,
    borderRadius: 20,
    paddingHorizontal: 15,
    backgroundColor: '#FFEBEE',
    marginBottom: 10,
    marginHorizontal: 5,
    fontSize: 16,
  },
  newTeamInput: {
    height: 40,
    borderRadius: 20,
    paddingHorizontal: 15,
    backgroundColor: '#FFEBEE',
    marginBottom: 10,
    marginHorizontal: 5,
    fontSize: 16,
  },
  addTeamButton: {
    backgroundColor: '#FF5252',
    padding: 10,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  chatArea: {
    flex: 1,
    backgroundColor: '#FFEBEE',
    marginLeft: 0,
    paddingLeft: 0,
  },
  header: {
    height: 60,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  messagesContainer: {
    flex: 1,
    paddingHorizontal: 10,
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
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#FFFFFF',
  },
  input: {
    flex: 1,
    height: 40,
    borderRadius: 20,
    paddingHorizontal: 15,
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
  },
  attachmentOptions: {
    position: 'absolute',
    bottom: 60,
    left: 10,
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 5,
    elevation: 5,
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
  },
  emptyStateText: {
    fontSize: 18,
    color: '#D32F2F',
  },
});

