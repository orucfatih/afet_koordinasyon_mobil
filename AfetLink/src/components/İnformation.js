import React from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  Image,
  StatusBar,
  SafeAreaView,
  Platform,
  Linking,
  Alert
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const Information = ({ navigation }) => {

  const openYouTubeVideo = (videoId) => {
    const url = `https://www.youtube.com/watch?v=${videoId}`;
    Linking.openURL(url).catch(err => {
      Alert.alert('Hata', 'Video açılamadı. Lütfen YouTube uygulamasının yüklü olduğundan emin olun.');
      console.error("YouTube video açma hatası:", err);
    });
  };

  const emergencyKitItems = [
    {
      title: "Su ve Gıda",
      description: "Kişi başı günde 4 litre su, 3 günlük gıda rezervi",
      icon: "water"
    },
    {
      title: "İlk Yardım Malzemeleri",
      description: "Bandaj, antiseptik, ağrı kesici, kişisel ilaçlar",
      icon: "medical"
    },
    {
      title: "El Feneri ve Piller",
      description: "LED fener, yedek piller, şarj aleti",
      icon: "flashlight"
    },
    {
      title: "Radyo",
      description: "Pilli radyo veya dinamo ile çalışan radyo",
      icon: "radio"
    },
    {
      title: "Kişisel Belgeler",
      description: "Kimlik, pasaport, sigorta poliçeleri (su geçirmez torba içinde)",
      icon: "document-text"
    },
    {
      title: "Nakit Para",
      description: "Küçük banknotlar halinde acil durum parası",
      icon: "cash"
    },
    {
      title: "Kıyafet ve Battaniye",
      description: "Mevsime uygun kıyafetler, sıcak tutan battaniye",
      icon: "shirt"
    },
    {
      title: "Araçlar",
      description: "Çakı, kibrit, plastik poşetler, ip",
      icon: "construct"
    }
  ];

  const duringEarthquakeSteps = [
    {
      title: "Sakin Kalın",
      description: "Panik yapmayın, soğukkanlılığınızı koruyun",
      icon: "heart"
    },
    {
      title: "Çök, Korun, Tutun",
      description: "Yere çökün, masa altına sığının, sağlam bir yere tutunun",
      icon: "shield"
    },
    {
      title: "Açık Alanda Kalın",
      description: "Açık alandaysanız, binalardan ve ağaçlardan uzak durun",
      icon: "locate"
    },
    {
      title: "Asansör Kullanmayın",
      description: "Merdivenleri kullanın, asansörde sıkışabilirsiniz",
      icon: "warning"
    },
    {
      title: "Kapı Çerçevesinden Uzak Durun",
      description: "Modern binalarda kapı çerçeveleri güvenli değil",
      icon: "close-circle"
    },
    {
      title: "Cam ve Aynalardan Uzak Durun",
      description: "Kırılabilecek nesnelerden uzaklaşın",
      icon: "triangle"
    }
  ];

  const afterEarthquakeSteps = [
    {
      title: "Yaralıları Kontrol Edin",
      description: "Önce kendinizi, sonra çevrenizdekileri kontrol edin",
      icon: "people"
    },
    {
      title: "Gaz Vanalarını Kapatın",
      description: "Gaz kaçağı olabileceği için ana vanayı kapatın",
      icon: "flame"
    },
    {
      title: "Elektriği Kesin",
      description: "Elektrik kaçağı riski için ana şalteri kapatın",
      icon: "flash-off"
    },
    {
      title: "Binayı Terk Edin",
      description: "Hasarlı görünse de görünmese de binayı terk edin",
      icon: "exit"
    },
    {
      title: "Açık Alana Çıkın",
      description: "Toplanma alanına gidin veya güvenli açık alana çıkın",
      icon: "checkmark-circle"
    },
    {
      title: "Haberleşmeyi Sınırlı Tutun",
      description: "Sadece acil durumlar için telefon kullanın",
      icon: "call"
    }
  ];

  const youtubeVideos = [
    {
      title: "Deprem Çantası Nasıl Hazırlanır?",
      description: "AFAD'ın resmi deprem çantası hazırlama videosu",
      videoId: "dQw4w9WgXcQ", // Bu örnek bir video ID'si, gerçek ID ile değiştirilmeli
      thumbnail: "📦"
    },
    {
      title: "Deprem Anında Ne Yapmalı?",
      description: "Deprem sırasında hayat kurtaran bilgiler",
      videoId: "dQw4w9WgXcQ", // Bu örnek bir video ID'si, gerçek ID ile değiştirilmeli
      thumbnail: "🏠"
    },
    {
      title: "Deprem Sonrası İlk Yardım",
      description: "Deprem sonrası yapılması gerekenler",
      videoId: "dQw4w9WgXcQ", // Bu örnek bir video ID'si, gerçek ID ile değiştirilmeli
      thumbnail: "🚑"
    }
  ];

  const renderInfoCard = (item, index) => (
    <View key={index} style={styles.infoCard}>
      <View style={styles.cardIcon}>
        <Ionicons name={item.icon} size={24} color="#D32F2F" />
      </View>
      <View style={styles.cardContent}>
        <Text style={styles.cardTitle}>{item.title}</Text>
        <Text style={styles.cardDescription}>{item.description}</Text>
      </View>
    </View>
  );

  const renderVideoCard = (video, index) => (
    <TouchableOpacity 
      key={index} 
      style={styles.videoCard}
      onPress={() => openYouTubeVideo(video.videoId)}
    >
      <View style={styles.videoThumbnail}>
        <Text style={styles.thumbnailEmoji}>{video.thumbnail}</Text>
        <Ionicons name="play-circle" size={30} color="#D32F2F" style={styles.playIcon} />
      </View>
      <View style={styles.videoInfo}>
        <Text style={styles.videoTitle}>{video.title}</Text>
        <Text style={styles.videoDescription}>{video.description}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          <View style={styles.placeholder} />
        </View>

        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.headerSection}>
            <Ionicons name="information-circle" size={60} color="#D32F2F" />
            <Text style={styles.mainTitle}>Deprem Bilgilendirme</Text>
            <Text style={styles.subtitle}>Hayat kurtaran bilgiler</Text>
          </View>

          {/* Deprem Çantası Bölümü */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🎒 Deprem Çantası İçeriği</Text>
            <Text style={styles.sectionDescription}>
              Deprem çantanızda bulunması gereken temel malzemeler:
            </Text>
            {emergencyKitItems.map((item, index) => renderInfoCard(item, index))}
          </View>

          {/* Deprem Anında Bölümü */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>⚡ Deprem Anında Yapılacaklar</Text>
            <Text style={styles.sectionDescription}>
              Deprem sırasında hayatınızı kurtarabilecek önemli adımlar:
            </Text>
            {duringEarthquakeSteps.map((item, index) => renderInfoCard(item, index))}
          </View>

          {/* Deprem Sonrası Bölümü */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>✅ Deprem Sonrası Yapılacaklar</Text>
            <Text style={styles.sectionDescription}>
              Deprem sonrası güvenliğiniz için atmanız gereken adımlar:
            </Text>
            {afterEarthquakeSteps.map((item, index) => renderInfoCard(item, index))}
          </View>

          {/* Video Bölümü */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📺 Eğitim Videoları</Text>
            <Text style={styles.sectionDescription}>
              Deprem konusunda detaylı bilgi almak için bu videoları izleyebilirsiniz:
            </Text>
            {youtubeVideos.map((video, index) => renderVideoCard(video, index))}
          </View>

          {/* Acil Durum Numaraları */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📞 Acil Durum Numaraları</Text>
            <View style={styles.emergencyNumbers}>
              <TouchableOpacity 
                style={styles.emergencyButton}
                onPress={() => Linking.openURL('tel:112')}
              >
                <Ionicons name="call" size={24} color="#fff" />
                <Text style={styles.emergencyText}>112 - Acil Çağrı</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.emergencyButton}
                onPress={() => Linking.openURL('tel:110')}
              >
                <Ionicons name="flame" size={24} color="#fff" />
                <Text style={styles.emergencyText}>110 - İtfaiye</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.emergencyButton}
                onPress={() => Linking.openURL('tel:156')}
              >
                <Ionicons name="shield" size={24} color="#fff" />
                <Text style={styles.emergencyText}>156 - Jandarma</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.bottomPadding} />
        </ScrollView>
      </SafeAreaView>
    </View>
  );
};

export default Information;

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: '#2D2D2D',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
    paddingVertical: 25,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    zIndex: 10,
    position: 'relative',
    minHeight: 75,
  },
  backButton: {
    position: 'absolute',
    left: 20,
    top: 20,
    zIndex: 20,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: '50%',
    marginLeft: -25,
    top: 10,
  },
  placeholder: {
    width: 44,
  },
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  headerSection: {
    alignItems: 'center',
    paddingVertical: 30,
    paddingHorizontal: 20,
  },
  mainTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginTop: 15,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 10,
  },
  sectionDescription: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    lineHeight: 24,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#FFF5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 4,
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  videoCard: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  videoThumbnail: {
    width: 80,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
    position: 'relative',
  },
  thumbnailEmoji: {
    fontSize: 30,
  },
  playIcon: {
    position: 'absolute',
    bottom: -5,
    right: -5,
    backgroundColor: 'white',
    borderRadius: 15,
  },
  videoInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  videoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 4,
  },
  videoDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  emergencyNumbers: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
  },
  emergencyButton: {
    backgroundColor: '#D32F2F',
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    width: '30%',
    marginBottom: 10,
    elevation: 3,
  },
  emergencyText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 5,
    textAlign: 'center',
  },
  bottomPadding: {
    height: 50,
  },
});
