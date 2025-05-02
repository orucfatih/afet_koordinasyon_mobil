import React from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet 
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const SelectedContactsList = ({ contacts, onRemoveContact }) => {
  const sortedContacts = [...contacts].sort((a, b) => a.name.localeCompare(b.name));
  
  return (
    <View style={styles.selectedContactsContainer}>
      {sortedContacts.length > 0 ? (
        sortedContacts.map(contact => (
          <View key={contact.id} style={styles.contactItem}>
            <View style={styles.selectedContactAvatar}>
              <Text style={styles.selectedContactInitial}>{contact.name.charAt(0).toUpperCase()}</Text>
            </View>
            <View style={styles.selectedContactInfo}>
              <Text style={styles.contactName}>{contact.name}</Text>
              <Text style={styles.contactPhone}>{contact.phoneNumber}</Text>
            </View>
            <TouchableOpacity 
              style={styles.removeContactButton} 
              onPress={() => onRemoveContact(contact.id)}
            >
              <Ionicons name="close-circle" size={24} color="#D32F2F" />
            </TouchableOpacity>
          </View>
        ))
      ) : (
        <Text style={styles.noContactsText}>Henüz kişi eklenmedi</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  selectedContactsContainer: {
    marginBottom: 15,
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 10,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  selectedContactAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1976D2',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  selectedContactInitial: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  selectedContactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  contactPhone: {
    fontSize: 14,
    color: '#666',
  },
  removeContactButton: {
    padding: 5,
  },
  noContactsText: {
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    padding: 10,
  },
});

export default SelectedContactsList; 