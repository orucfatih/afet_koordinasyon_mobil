import React from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Modal, 
  FlatList, 
  TextInput 
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const ContactPickerModal = ({ 
  visible, 
  onClose, 
  contacts, 
  onSelectContact 
}) => {
  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}>

      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Kişi Seçin</Text>
          
          {/* Arama kutusu */}
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={20} color="#666" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Kişi ara..."
              placeholderTextColor="#999"
              onChangeText={(text) => {
                // Arama fonksiyonelliği eklenebilir
              }}
            />
          </View>

          <FlatList
            style={styles.contactList}
            data={contacts}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.contactListItem}
                onPress={() => onSelectContact(item)}
              >
                <View style={styles.contactAvatarContainer}>
                  <View style={styles.contactAvatar}>
                    <Text style={styles.contactInitial}>{item.name.charAt(0).toUpperCase()}</Text>
                  </View>
                </View>
                <View style={styles.contactInfo}>
                  <Text style={styles.contactListName}>{item.name}</Text>
                  {item.phoneNumbers && item.phoneNumbers.length > 0 && (
                    <Text style={styles.contactListPhone}>
                      {item.phoneNumbers[0].label}: {item.phoneNumbers[0].number}
                    </Text>
                  )}
                </View>
                <Ionicons name="add-circle-outline" size={24} color="#D32F2F" />
              </TouchableOpacity>
            )}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
          />
          <TouchableOpacity
            style={styles.closeButton}
            onPress={onClose}
          >
            <Text style={styles.closeButtonText}>Kapat</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    maxHeight: '80%',
    width: '90%',
    padding: 0,
    borderRadius: 15,
    backgroundColor: '#fff',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 15,
    color: '#333',
    textAlign: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    marginHorizontal: 15,
    marginBottom: 15,
    paddingHorizontal: 10,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
  },
  contactList: {
    marginHorizontal: 15,
    width: '90%',
  },
  contactListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 10,
    marginBottom: 10,
    width: '100%',
  },
  contactAvatarContainer: {
    marginRight: 15,
  },
  contactAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
  },
  contactInitial: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  contactInfo: {
    flex: 1,
  },
  contactListName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  contactListPhone: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  separator: {
    height: 1,
    backgroundColor: '#eee',
    marginLeft: 65,
  },
  closeButton: {
    backgroundColor: '#D32F2F',
    padding: 15,
    alignItems: 'center',
    margin: 15,
    borderRadius: 10,
  },
  closeButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default ContactPickerModal; 