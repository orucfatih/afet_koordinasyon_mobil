import React, { useState, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Vibration, SafeAreaView, StatusBar, Platform } from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome5';
import Sound from 'react-native-sound';
import * as Animatable from 'react-native-animatable';

Sound.setCategory('Playback');

const Horn = ({ navigation }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSound, setActiveSound] = useState(null);
  const soundRef = useRef(null);

  const stopSound = () => {
    if (soundRef.current) {
      soundRef.current.stop();
      soundRef.current.release();
      Vibration.cancel();
      setIsPlaying(false);
      setActiveSound(null);
    }
  };

  const playSound = async (fileName) => {
    if (isPlaying) {
      stopSound();
      return;
    }

    setIsPlaying(true);
    setActiveSound(fileName);

    try {
      const PATTERN = [0, 1000, 500];
      Vibration.vibrate(PATTERN, true);

      console.log('Loading sound file:', fileName);
      const sound = new Sound(fileName, Sound.MAIN_BUNDLE, (error) => {
        if (error) {
          console.error('Failed to load sound', error);
          setIsPlaying(false);
          setActiveSound(null);
          return;
        }

        soundRef.current = sound;
        console.log('Sound loaded, playing...');
        sound.play((success) => {
          if (success) {
            console.log('Sound finished playing');
          } else {
            console.log('Sound playback failed');
          }
          sound.release();
          setIsPlaying(false);
          setActiveSound(null);
          Vibration.cancel();
        });
      });
    } catch (error) {
      console.error('Error playing sound:', error);
      setIsPlaying(false);
      setActiveSound(null);
      Vibration.cancel();
    }
  };

  const renderSoundCard = (fileName, iconName, title, description, color) => {
    const isActive = isPlaying && activeSound === fileName;
    return (
      <Animatable.View
        animation={isActive ? 'pulse' : 'fadeInUp'}
        iterationCount={isActive ? 'infinite' : 1}
        duration={isActive ? 2000 : 800}
        style={styles.cardContainer}
      >
        <TouchableOpacity
          style={[
            styles.soundCard,
            { backgroundColor: color },
            isActive && styles.activeSoundCard
          ]}
          onPress={() => playSound(fileName)}
          activeOpacity={0.8}
        >
          <View style={styles.cardHeader}>
            <View style={[styles.iconContainer, { backgroundColor: `${color}22` }]}>
              <Icon name={iconName} size={32} color="white" />
            </View>
            <View style={styles.statusIndicator}>
              <View style={[styles.statusDot, { backgroundColor: isActive ? '#4CAF50' : '#666' }]} />
              <Text style={styles.statusText}>
                {isActive ? 'ÇALIYOR' : 'HAZIR'}
              </Text>
            </View>
          </View>
          
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>{title}</Text>
            <Text style={styles.cardDescription}>{description}</Text>
            
            <View style={styles.waveformContainer}>
              {[...Array(8)].map((_, index) => (
                <Animatable.View
                  key={index}
                  animation={isActive ? 'slideInUp' : null}
                  delay={index * 100}
                  iterationCount={isActive ? 'infinite' : 1}
                  duration={1000}
                  style={[
                    styles.waveBar,
                    {
                      height: isActive ? Math.random() * 30 + 10 : 5,
                      backgroundColor: isActive ? 'white' : 'rgba(255,255,255,0.3)'
                    }
                  ]}
                />
              ))}
            </View>
          </View>
          
          <View style={styles.cardFooter}>
            <Text style={styles.actionText}>
              {isActive ? 'Durdurmak için dokun' : 'Başlatmak için dokun'}
            </Text>
          </View>
        </TouchableOpacity>
      </Animatable.View>
    );
  };

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="dark-content"
        backgroundColor="#f8f9fa"
        translucent={true}
      />
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Icon name="arrow-left" size={20} color="#2D2D2D" />
          </TouchableOpacity>
          <Text style={styles.topBarTitle}>Sesini Duyur</Text>
          <View style={styles.placeholder} />
        </View>
        
        <View style={styles.container}>
          <View style={styles.headerSection}>
            <Text style={styles.mainTitle}>Acil Durum Sesleri</Text>
            <Text style={styles.subtitle}>Yardım almak için kullanın</Text>
          </View>

          <View style={styles.soundCardsContainer}>
            {renderSoundCard(
              'megaphone.mp3', 
              'wind', 
              'Düdük Sesi', 
              'Dikkat çekmek için ideal',
              '#D32F2F'
            )}
            {renderSoundCard(
              'highpitch.mp3', 
              'wave-square', 
              'Tiz Ses', 
              'Uzun mesafe için güçlü',
              '#B71C1C'
            )}
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    height: 56,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    marginTop: Platform.OS === 'ios' ? 0 : 10,
    elevation: 2,
  },
  backButton: {
    padding: 8,
  },
  topBarTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2D2D2D',
  },
  placeholder: {
    width: 36,
  },
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 20,
    paddingTop: 30,
  },
  headerSection: {
    alignItems: 'center',
    marginBottom: 40,
  },
  mainTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  soundCardsContainer: {
    flex: 1,
  },
  cardContainer: {
    marginBottom: 25,
  },
  soundCard: {
    borderRadius: 20,
    padding: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  activeSoundCard: {
    elevation: 16,
    shadowOpacity: 0.25,
    shadowRadius: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: 'white',
    letterSpacing: 1,
  },
  cardContent: {
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 20,
  },
  waveformContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 40,
  },
  waveBar: {
    width: 4,
    borderRadius: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  cardFooter: {
    alignItems: 'center',
  },
  actionText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '600',
  },
});

export default Horn;
