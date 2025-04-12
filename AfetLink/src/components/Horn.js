import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Vibration } from 'react-native';
import Sound from 'react-native-sound';
import Ionicons from 'react-native-vector-icons/Ionicons';

const Horn = ({ setHorn }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [sound, setSound] = useState(null);

  useEffect(() => {
    // Enable playback in silence mode
    Sound.setCategory('Playback');
    
    const sirenSound = new Sound('siren.mp3', Sound.MAIN_BUNDLE, (error) => {
      if (error) {
        console.log('failed to load the sound', error);
        return;
      }
      setSound(sirenSound);
    });

    return () => {
      if (sound) {
        sound.release();
      }
    };
  }, []);

  const playSound = () => {
    if (sound) {
      setIsPlaying(true);
      Vibration.vibrate([0, 500, 200, 500], true); // Sürekli titreşim
      
      sound.play((success) => {
        if (!success) {
          console.log('Sound playback failed');
        }
      });
    }
  };

  const stopSound = () => {
    if (sound) {
      setIsPlaying(false);
      Vibration.cancel();
      sound.stop();
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.button, isPlaying ? styles.buttonActive : null]}
        onPress={isPlaying ? stopSound : playSound}
      >
        <Ionicons 
          name={isPlaying ? "volume-high" : "volume-mute"} 
          size={40} 
          color={isPlaying ? "#ff4444" : "#000000"} 
        />
        <Text style={styles.buttonText}>
          {isPlaying ? 'SİRENİ DURDUR' : 'SİRENİ ÇALIŞTIR'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  button: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    borderRadius: 10,
    backgroundColor: '#f0f0f0',
    width: '80%',
  },
  buttonActive: {
    backgroundColor: '#ffe0e0',
  },
  buttonText: {
    marginTop: 10,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
});

export default Horn;