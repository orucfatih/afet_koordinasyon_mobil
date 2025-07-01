import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, StatusBar, Dimensions, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import * as Animatable from 'react-native-animatable';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

const AraMenu = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, { marginBottom: insets.bottom }]}>
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
        <Text style={styles.headerTitle}>Vatandaş Girişi</Text>
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
            <Ionicons name="person-circle" size={80} color="#D32F2F" />
          </View>
        </View>

        <Text style={styles.welcomeText}>Hoş Geldiniz</Text>
        <Text style={styles.subtitleText}>Giriş yönteminizi seçin</Text>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.modernButton}
            onPress={() => Alert.alert(
              'Bilgi',
              'E-devlet ile giriş henüz uygulanmadı.',
              [{ text: 'Tamam', style: 'default' }]
            )}
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
            onPress={() => navigation.navigate('LoginPage')}
            activeOpacity={0.8}
          >
            <View style={styles.buttonContent}>
              <View style={[styles.buttonIconWrapper, styles.emailIconWrapper]}>
                <Ionicons name="mail" size={28} color="white" />
              </View>
              <View style={styles.buttonTextContainer}>
                <Text style={styles.buttonText}>E-mail ile Giriş</Text>
                <Text style={styles.buttonSubtext}>Email adresinizle giriş yapın</Text>
              </View>
              <View style={styles.buttonArrow}>
                <Ionicons name="arrow-forward" size={20} color="rgba(255,255,255,0.8)" />
              </View>
            </View>
          </TouchableOpacity>
        </View>

        {/* Info Section */}
        <View style={styles.infoSection}>
          <Ionicons name="information-circle" size={20} color="#666" />
          <Text style={styles.infoText}>
            Hesabınız yoksa giriş sayfasından kaydolabilirsiniz
          </Text>
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
    shadowColor: '#D32F2F',
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
    marginBottom: 40,
  },
  modernButton: {
    backgroundColor: '#D32F2F',
    borderRadius: 18,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  emailButton: {
    backgroundColor: '#2196F3',
    shadowColor: '#2196F3',
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
  infoSection: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.95)',
    padding: 16,
    borderRadius: 12,
    marginTop: 20,
  },
  infoText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});

export default AraMenu;
