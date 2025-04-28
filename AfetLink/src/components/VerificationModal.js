import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, Modal, Animated, Alert, StyleSheet } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { verifyPhoneCode, resendPhoneCode } from '../redux/userSlice';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { Loading } from './index';

const VerificationModal = ({ visible, onClose, verificationId, staffData }) => {
  const dispatch = useDispatch();
  const { resendCooldown } = useSelector(state => state.user);
  const { isLoading } = useSelector(state => state.user);

  const [code, setCode] = useState('');
  const [timer, setTimer] = useState(resendCooldown || 60);
  const [isTimerRunning, setIsTimerRunning] = useState(true);
  const progressAnim = useState(new Animated.Value(1))[0];

  useEffect(() => {
    let interval;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimer(prev => {
          if (prev <= 1) {
            clearInterval(interval);
            setIsTimerRunning(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      Animated.timing(progressAnim, {
        toValue: 0,
        duration: timer * 1000,
        useNativeDriver: false,
      }).start();
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  const handleVerify = () => {
    if (code.length !== 6) {
      Alert.alert(
        'Eksik Kod', 
        'Lütfen telefonunuza gönderilen 6 haneli doğrulama kodunu eksiksiz olarak giriniz.', 
        [{ text: 'Tamam', style: 'default' }]
      );
      return;
    }
    dispatch(verifyPhoneCode({ verificationId, code, staffData }))
      .unwrap()
      .then(() => {
        Alert.alert(
          'Doğrulama Başarılı', 
          'Telefon numaranız başarıyla doğrulandı. Sisteme giriş yapabilirsiniz.',
          [{ text: 'Tamam', style: 'default' }]
        );
        onClose(true);
      })
      .catch((error) => {
        Alert.alert(
          'Doğrulama Hatası', 
          error || 'Doğrulama işlemi başarısız oldu. Lütfen tekrar deneyiniz.', 
          [{ text: 'Tamam', style: 'destructive' }]
        );
      });
  };

  const handleResendCode = () => {
    dispatch(resendPhoneCode())
      .unwrap()
      .then((res) => {
        setTimer(resendCooldown || 60);
        setIsTimerRunning(true);
        progressAnim.setValue(1);
        Alert.alert(
          'Kod Gönderildi', 
          'Yeni doğrulama kodu kayıtlı telefon numaranıza gönderildi. Lütfen kontrol ediniz.',
          [{ text: 'Tamam', style: 'default' }]
        );
      })
      .catch((error) => {
        Alert.alert(
          'Kod Gönderme Hatası', 
          error || 'Yeni kod gönderme işlemi başarısız oldu. Lütfen daha sonra tekrar deneyiniz.', 
          [{ text: 'Tamam', style: 'destructive' }]
        );
      });
  };

  const handleModalClose = () => {
    Alert.alert(
      'Doğrulama İptal', 
      'Doğrulama işlemini iptal ederseniz oturumunuz sonlandırılacaktır. Devam etmek istiyor musunuz?',
      [
        { text: 'Hayır', style: 'cancel' },
        { text: 'Evet, Çıkış Yap', style: 'destructive', onPress: () => onClose(false) }
      ]
    );
  };

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={handleModalClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <TouchableOpacity 
            style={styles.closeButton} 
            onPress={handleModalClose}
          >
            <Ionicons name="close-circle" size={28} color="#6B7280" />
          </TouchableOpacity>
          
          <View style={styles.headerContainer}>
            <Ionicons name="shield-checkmark" size={48} color="#3B82F6" style={styles.headerIcon} />
            <Text style={styles.headerTitle}>Telefon Doğrulaması</Text>
            <Text style={styles.headerSubtitle}>
              Telefonunuza gönderilen 6 haneli kodu girin
            </Text>
          </View>

          <View style={styles.codeInputContainer}>
            <TextInput
              style={styles.codeInput}
              placeholder="000000"
              placeholderTextColor="#9CA3AF"
              keyboardType="number-pad"
              maxLength={6}
              value={code}
              onChangeText={setCode}
            />
          </View>

          <TouchableOpacity
            style={styles.verifyButton}
            activeOpacity={0.8}
            onPress={handleVerify}
          >
            <Text style={styles.verifyButtonText}>Kodu Doğrula</Text>
          </TouchableOpacity>

          <View style={styles.progressContainer}>
            <Animated.View
              style={[
                styles.progressBar,
                {
                  width: progressWidth,
                },
              ]}
            />
          </View>

          {isTimerRunning ? (
            <View style={styles.timerContainer}>
              <Ionicons name="time-outline" size={18} color="#6B7280" />
              <Text style={styles.timerText}>{timer} saniye içinde kod gelmeli</Text>
            </View>
          ) : (
            <TouchableOpacity style={styles.resendContainer} onPress={handleResendCode}>
              <Ionicons name="refresh" size={18} color="#3B82F6" />
              <Text style={styles.resendText}>Kod Almadınız mı? Tekrar Gönder</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    padding: 20,
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 24,
    padding: 24,
    width: '92%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    elevation: 10,
  },
  closeButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    zIndex: 10,
  },
  headerContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  headerIcon: {
    marginBottom: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  codeInputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  codeInput: {
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 16,
    fontSize: 20,
    textAlign: 'center',
    letterSpacing: 8,
    backgroundColor: '#F9FAFB',
    fontWeight: 'bold',
    color: '#111827',
  },
  verifyButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
    width: '100%',
    alignItems: 'center',
    marginBottom: 24,
  },
  verifyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  progressContainer: {
    width: '100%',
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#3B82F6',
  },
  timerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  timerText: {
    color: '#6B7280',
    marginLeft: 6,
    fontSize: 14,
  },
  resendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  resendText: {
    color: '#3B82F6',
    marginLeft: 6,
    fontSize: 14,
    fontWeight: '600',
  },
});

export default VerificationModal;
