import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Modal, 
  ActivityIndicator 
} from 'react-native';

const SendingModal = ({ visible, progress }) => {
  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade">
      <View style={styles.sendingModalContainer}>
        <View style={styles.sendingModalContent}>
          <ActivityIndicator size="large" color="#D32F2F" />
          <Text style={styles.sendingModalText}>
            Mesajlar gönderiliyor... {Math.round(progress)}%
          </Text>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  sendingModalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
  },
  sendingModalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    width: '80%',
  },
  sendingModalText: {
    marginTop: 15,
    fontSize: 16,
    textAlign: 'center',
  },
});

export default SendingModal; 