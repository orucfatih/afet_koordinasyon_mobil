import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesomeIcon } from '@fortawesome/react-native-fontawesome';
import { faBullhorn, faWaveSquare } from '@fortawesome/free-solid-svg-icons';
import { Audio } from 'expo-av';
import { Vibration } from 'react-native';

const Horn = ({ setHorn }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  // Request audio permissions
  const requestAudioPermissions = async () => {
    const { status } = await Audio.requestPermissionsAsync();
    if (status !== 'granted') {
      console.log('Audio permissions denied');
      return false;
    }
    return true;
  };

  const playSound = async (file) => {
    if (isPlaying) {
      console.log('Already playing, skipping...');
      return;
    }

    setIsPlaying(true);

    try {
      // Request permissions
      const hasPermission = await requestAudioPermissions();
      if (!hasPermission) {
        setIsPlaying(false);
        return;
      }

      // Configure audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
        shouldDuckAndroid: true,
      });

      // Start vibration
      const DURATION = 20000;
      const PATTERN = [0, 1000, 500];
      Vibration.vibrate(PATTERN, true);
      setTimeout(() => Vibration.cancel(), DURATION);

      // Load and play sound
      console.log('Loading sound file:', file);
      const { sound } = await Audio.Sound.createAsync(file);
      console.log('Sound loaded, playing...');
      await sound.playAsync();

      // Handle playback status
      sound.setOnPlaybackStatusUpdate((status) => {
        if (!status.isPlaying && status.didJustFinish) {
          console.log('Sound finished playing');
          setIsPlaying(false);
          sound.unloadAsync();
        }
      });
    } catch (error) {
      console.error('Error playing sound:', error);
      setIsPlaying(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sesini Duyurma</Text>
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, { opacity: isPlaying ? 0.5 : 1 }]}
          onPress={() => playSound(require('../../assets/sounds/megaphone.mp3'))}
          disabled={isPlaying}
        >
          <FontAwesomeIcon icon={faBullhorn} size={30} color="white" style={styles.icon} />
          <Text style={styles.buttonText}>Megafon Sesi</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, { opacity: isPlaying ? 0.5 : 1 }]}
          onPress={() => playSound(require('../../assets/sounds/highpitch.mp3'))}
          disabled={isPlaying}
        >
          <FontAwesomeIcon icon={faWaveSquare} size={30} color="white" style={styles.icon} />
          <Text style={styles.buttonText}>Tiz Ses</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.closeButton} onPress={() => setHorn(false)}>
          <Text style={styles.closeButtonText}>Kapat</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 40,
  },
  buttonContainer: {
    alignItems: 'center',
    width: '100%',
  },
  button: {
    flexDirection: 'row',
    width: 200,
    height: 80,
    backgroundColor: '#D32F2F',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 10,
    marginVertical: 20,
    borderWidth: 2,
    borderColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  icon: {
    marginRight: 10,
  },
  buttonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  closeButton: {
    marginTop: 20,
    padding: 10,
    backgroundColor: '#2D2D2D',
    borderRadius: 5,
  },
  closeButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default Horn;