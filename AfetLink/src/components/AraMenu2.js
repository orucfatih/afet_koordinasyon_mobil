import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, StatusBar, Dimensions } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import * as Animatable from 'react-native-animatable';

const { width } = Dimensions.get('window');

const AraMenu2 = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
      
      {/* Background Gradient */}
      <View style={styles.backgroundGradient} />
      
      {/* Header with Back Button */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => navigation.navigate("AnaMenu")}
          activeOpacity={0.8}
        >
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Personel Girişi</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Main Content */}
      <Animatable.View 
        animation="fadeInUp" 
        duration={800}
        style={styles.contentContainer}
      >
        <View style={styles.iconContainer}>
          <View style={styles.iconWrapper}>
            <Ionicons name="shield-checkmark" size={80} color="#2196F3" />
          </View>
        </View>

        <Text style={styles.welcomeText}>Personel Girişi</Text>
        <Text style={styles.subtitleText}>Yetkili personel giriş yönteminizi seçin</Text>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.modernButton}
            onPress={() => alert('E-devlet ile giriş henüz uygulanmadı.')}
            activeOpacity={0.8}
          >
            <View style={styles.buttonContent}>
              <View style={styles.buttonIconWrapper}>
                <Ionicons name="shield-checkmark" size={28} color="white" />
              </View>
              <View style={styles.buttonTextContainer}>
                <Text style={styles.buttonText}>E-devlet ile Giriş</Text>
                <Text style={styles.buttonSubtext}>Güvenli devlet sistemi</Text>
              </View>
              <View style={styles.buttonArrow}>
                <Ionicons name="arrow-forward" size={20} color="rgba(255,255,255,0.8)" />
              </View>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.modernButton, styles.emailButton]}
            onPress={() => navigation.navigate('LoginPage2')}
            activeOpacity={0.8}
          >
            <View style={styles.buttonContent}>
              <View style={[styles.buttonIconWrapper, styles.emailIconWrapper]}>
                <Ionicons name="mail" size={28} color="white" />
              </View>
              <View style={styles.buttonTextContainer}>
                <Text style={styles.buttonText}>E-mail ile Giriş</Text>
                <Text style={styles.buttonSubtext}>Personel email adresinizle giriş yapın</Text>
              </View>
              <View style={styles.buttonArrow}>
                <Ionicons name="arrow-forward" size={20} color="rgba(255,255,255,0.8)" />
              </View>
            </View>
          </TouchableOpacity>
        </View>

        {/* Security Notice */}
        <View style={styles.securitySection}>
          <Ionicons name="lock-closed" size={20} color="#2196F3" />
          <Text style={styles.securityText}>
            Bu giriş sadece yetkili personel içindir. Giriş işlemleri güvenlik için loglanmaktadır.
          </Text>
        </View>

        {/* Emergency Contact */}
        <View style={styles.emergencySection}>
          <Ionicons name="call" size={18} color="#D32F2F" />
          <Text style={styles.emergencyText}>Acil Durum: 112</Text>
        </View>
      </Animatable.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  backgroundGradient: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '50%',
    backgroundColor: '#2D2D2D',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  placeholder: {
    width: 44,
  },
  contentContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 40,
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  iconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.95)',
    padding: 25,
    borderRadius: 50,
    shadowColor: '#2196F3',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 10,
  },
  welcomeText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitleText: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    textAlign: 'center',
    marginBottom: 40,
  },
  buttonContainer: {
    gap: 20,
    marginBottom: 30,
  },
  modernButton: {
    backgroundColor: '#2196F3',
    borderRadius: 18,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#2196F3',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  emailButton: {
    backgroundColor: '#4CAF50',
    shadowColor: '#4CAF50',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  buttonIconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 12,
    borderRadius: 12,
    marginRight: 16,
  },
  emailIconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  buttonTextContainer: {
    flex: 1,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  buttonSubtext: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
  },
  buttonArrow: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: 8,
    borderRadius: 20,
  },
  securitySection: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  securityText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: 'rgba(255,255,255,0.9)',
    lineHeight: 20,
  },
  emergencySection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.95)',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    marginTop: 20,
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  emergencyText: {
    color: '#D32F2F',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});

export default AraMenu2;
