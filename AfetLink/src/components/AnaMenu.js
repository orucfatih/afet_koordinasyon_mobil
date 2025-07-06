import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet, StatusBar, Dimensions, Linking } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { Loading } from './index.js';
import * as Animatable from 'react-native-animatable';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

const AnaMenu = ({ navigation }) => {
  const { isLoading } = useSelector((state) => state.user);
  const insets = useSafeAreaInsets();


  if (isLoading) {
    return <Loading />;
  }

  return (
    <View style={[styles.container, { marginBottom: insets.bottom }]}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
      
      {/* Background Gradient Effect */}
      <View style={styles.backgroundGradient} />
      
      {/* Header Section */}
      <Animatable.View 
        animation="fadeInDown" 
        duration={800}
        style={styles.headerSection}
      >
        <Image
          source={require('../../assets/images/deneme.png')}
          style={styles.logo}
        />
        <Text style={styles.title}>AfetLink</Text>
        <Text style={styles.subtitle}>Afet Yönetim Sistemi</Text>
      </Animatable.View>

      {/* Main Content */}
      <Animatable.View 
        animation="fadeInUp" 
        duration={800} 
        delay={200}
        style={styles.contentContainer}
      >
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.modernButton}
            onPress={() => navigation.navigate('AraMenu')}
            activeOpacity={0.8}
          >
            <View style={styles.buttonGradient}>
              <View style={styles.buttonContent}>
                <View style={styles.iconWrapper}>
                  <MaterialCommunityIcons name="account" size={28} color="white" />
                </View>
                <View style={styles.textContainer}>
                  <Text style={styles.buttonText}>Vatandaş Girişi</Text>
                  <Text style={styles.buttonSubtext}>Vatandaş olarak giriş yapın</Text>
                </View>
                <MaterialCommunityIcons name="arrow-right" size={24} color="rgba(255,255,255,0.8)" />
              </View>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.modernButton}
            onPress={() => navigation.navigate('AraMenu2')}
            activeOpacity={0.8}
          >
            <View style={[styles.buttonGradient, styles.staffButtonGradient]}>
              <View style={styles.buttonContent}>
                <View style={[styles.iconWrapper, styles.staffIconWrapper]}>
                  <MaterialCommunityIcons name="account-tie" size={28} color="white" />
                </View>
                <View style={styles.textContainer}>
                  <Text style={styles.buttonText}>Personel Girişi</Text>
                  <Text style={styles.buttonSubtext}>Yetkili personel girişi</Text>
                </View>
                <MaterialCommunityIcons name="arrow-right" size={24} color="rgba(255,255,255,0.8)" />
              </View>
            </View>
          </TouchableOpacity>
        </View>

        {/* Emergency Info */}
        <TouchableOpacity
          onPress={() => Linking.openURL('tel:112')}
          activeOpacity={0.8}
        >
          <Animatable.View 
            animation="pulse" 
            iterationCount="infinite" 
            duration={2000}
            style={styles.emergencyInfo}
          >
            <MaterialCommunityIcons name="phone" size={20} color="#D32F2F" />
            <Text style={styles.emergencyText}>Acil Durum: 112</Text>
          </Animatable.View>
        </TouchableOpacity>
      </Animatable.View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>© 2024 AfetLink - Güvenliğiniz İçin</Text>
      </View>
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
    height: '60%',
    backgroundColor: '#2D2D2D',
    borderBottomLeftRadius: 40,
    borderBottomRightRadius: 40,
  },
  headerSection: {
    alignItems: 'center',
    paddingTop: 80,
    paddingBottom: 40,
  },
  logo: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 4,
    borderColor: '#fff',
    backgroundColor: '#fff',
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 15,
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  contentContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  buttonContainer: {
    flex: 1,
    justifyContent: 'center',
    gap: 20,
  },
  modernButton: {
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  buttonGradient: {
    backgroundColor: '#D32F2F',
    padding: 4,
  },
  staffButtonGradient: {
    backgroundColor: '#2196F3',
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 16,
  },
  iconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 12,
    borderRadius: 12,
    marginRight: 16,
  },
  staffIconWrapper: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  textContainer: {
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
  emergencyInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.95)',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    marginVertical: 20,
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
  footer: {
    alignItems: 'center',
    paddingBottom: 30,
  },
  footerText: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 12,
  },
});

export default AnaMenu;