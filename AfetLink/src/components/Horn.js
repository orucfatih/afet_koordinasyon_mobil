import React, { useState, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Vibration, SafeAreaView, StatusBar, Platform } from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome5';
import Sound from 'react-native-sound';

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

  const renderButton = (fileName, iconName, title) => {
    const isActive = isPlaying && activeSound === fileName;
    return (
      <TouchableOpacity
        style={[
          styles.button,
          isActive && styles.activeButton
        ]}
        onPress={() => playSound(fileName)}
      >
        <Icon name={iconName} size={24} color="white" style={styles.icon} />
        <View style={styles.buttonTextContainer}>
          <Text style={styles.buttonText}>{title}</Text>
          <Text style={styles.buttonSubText}>
            {isActive ? 'Durdurmak için dokun' : 'Başlatmak için dokun'}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="dark-content"
        backgroundColor="#ffffff"
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
          <View style={styles.buttonContainer}>
            {renderButton('megaphone.mp3', 'bullhorn', 'Megafon Sesi')}
            {renderButton('highpitch.mp3', 'wave-square', 'Tiz Ses')}
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
};

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
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
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  buttonContainer: {
    alignItems: 'stretch',
    width: '100%',
  },
  button: {
    flexDirection: 'row',
    backgroundColor: '#D32F2F',
    padding: 20,
    borderRadius: 15,
    marginVertical: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
  },
  activeButton: {
    backgroundColor: '#9C1E1E',
  },
  icon: {
    marginRight: 15,
  },
  buttonTextContainer: {
    flex: 1,
  },
  buttonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  buttonSubText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
  }
});

export default Horn;
