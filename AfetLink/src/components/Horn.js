import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Vibration } from 'react-native';
import Sound from 'react-native-sound';
import Icon from 'react-native-vector-icons/FontAwesome';

// Ses dosyalarını yapılandır
Sound.setCategory('Playback');

const Horn = ({ setHorn }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSound, setCurrentSound] = useState(null);

  const playSound = (soundName) => {
    if (isPlaying) {
      console.log('Zaten çalınıyor, atlanıyor...');
      return;
    }

    setIsPlaying(true);

    try {
      // Önceki sesi durdur
      if (currentSound) {
        currentSound.stop();
        currentSound.release();
      }

      // Ses dosyasını belirle
      let soundPath;
      if (soundName === 'megaphone') {
        soundPath = require('../../assets/sounds/megaphone.mp3');
      } else if (soundName === 'highpitch') {
        soundPath = require('../../assets/sounds/highpitch.mp3');
      }

      // Yeni sesi yükle ve çal
      const sound = new Sound(soundPath, (error) => {
        if (error) {
          console.error('Ses yüklenirken hata:', error);
          setIsPlaying(false);
          return;
        }

        // Titreşimi başlat
        const DURATION = 20000;
        const PATTERN = [0, 1000, 500];
        Vibration.vibrate(PATTERN, true);
        setTimeout(() => Vibration.cancel(), DURATION);

        // Sesi çal
        sound.play((success) => {
          if (success) {
            console.log('Ses başarıyla çalındı');
          } else {
            console.log('Ses çalınırken hata oluştu');
          }
          setIsPlaying(false);
          Vibration.cancel();
          sound.release();
        });

        setCurrentSound(sound);
      });
    } catch (error) {
      console.error('Ses çalınırken hata:', error);
      setIsPlaying(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sesini Duyurma</Text>
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, { opacity: isPlaying ? 0.5 : 1 }]}
          onPress={() => playSound('megaphone')}
          disabled={isPlaying}
        >
          <Icon name="bullhorn" size={30} color="white" style={styles.icon} />
          <Text style={styles.buttonText}>Megafon Sesi</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, { opacity: isPlaying ? 0.5 : 1 }]}
          onPress={() => playSound('highpitch')}
          disabled={isPlaying}
        >
          <Icon name="wave-square" size={30} color="white" style={styles.icon} />
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