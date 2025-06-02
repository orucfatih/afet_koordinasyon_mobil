import { StyleSheet, Text, View, TouchableOpacity, ScrollView, Image, StatusBar, SafeAreaView, Platform, Dimensions } from 'react-native'
import React from 'react'
import Ionicons from 'react-native-vector-icons/Ionicons'

const { width } = Dimensions.get('window');

const Info = ({ setInfo, navigation }) => {
  const handleBack = () => {
    if (navigation && navigation.goBack) {
      navigation.goBack();
    } else {
      setInfo(false);
    }
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
          <TouchableOpacity style={styles.backButton} onPress={handleBack}>
            <Ionicons name="arrow-back" size={20} color="#2D2D2D" />
          </TouchableOpacity>
          <Text style={styles.topBarTitle}>Uygulama Rehberi</Text>
          <View style={styles.placeholder} />
        </View>

        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
          <View style={styles.content}>
            
            {/* Giriş Bölümü */}
            <View style={styles.section}>
              <View style={styles.headerCard}>
                <Image source={require('../../assets/images/deneme.png')} style={styles.appLogo} />
                <Text style={styles.appTitle}>AfetLink</Text>
                <Text style={styles.appSubtitle}>Kapsamlı Afet Yönetim Sistemi</Text>
                <Text style={styles.dataSource}>Kandilli Rasathanesi Verili</Text>
              </View>
            </View>

            {/* Veri Kaynağı Bilgilendirmesi */}
            <View style={styles.section}>
              <View style={styles.dataSourceCard}>
                <View style={styles.dataSourceIcon}>
                  <Ionicons name="analytics" size={24} color="#1976D2" />
                </View>
                <View style={styles.dataSourceContent}>
                  <Text style={styles.dataSourceTitle}>📊 Veri Kaynağımız</Text>
                  <Text style={styles.dataSourceDescription}>
                    Deprem verileri <Text style={styles.boldText}>Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü (KOERI)</Text>'nden 
                    gerçek zamanlı olarak alınmaktadır. Sadece 3.0 ve üzeri büyüklükteki depremler gösterilir.
                  </Text>
                </View>
              </View>
            </View>

            {/* Ana Özellikler */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>🚨 Kapsamlı Güvenlik Özellikleri</Text>
              
              <View style={styles.featureCard}>
                <View style={styles.featureIcon}>
                  <Ionicons name="pulse" size={24} color="#D32F2F" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={styles.featureTitle}>Gerçek Zamanlı Deprem İzleme</Text>
                  <Text style={styles.featureDescription}>Kandilli Rasathanesi'nden anlık deprem verileri. Sismik dalga görselleştirmesi ve detaylı konum bilgisi ile deprem aktivitelerini takip edin.</Text>
                </View>
              </View>

              <View style={styles.featureCard}>
                <View style={styles.featureIcon}>
                  <Ionicons name="people" size={24} color="#2196F3" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={styles.featureTitle}>Akıllı Toplanma Alanı Sistemi</Text>
                  <Text style={styles.featureDescription}>GPS konumunuza göre en yakın 4 toplanma alanını mesafe sırasına göre listeler. Harita üzerinde navigasyon desteği.</Text>
                </View>
              </View>

              <View style={styles.featureCard}>
                <View style={styles.featureIcon}>
                  <Ionicons name="medical" size={24} color="#4CAF50" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={styles.featureTitle}>En Yakın Hastane Listesi</Text>
                  <Text style={styles.featureDescription}>Google Places API ile en yakın 4 hastaneyi bulur. Hastane rating'i, açık/kapalı durumu ve mesafe bilgisi sağlar.</Text>
                </View>
              </View>

              <View style={styles.featureCard}>
                <View style={styles.featureIcon}>
                  <Ionicons name="camera" size={24} color="#FF9800" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={styles.featureTitle}>Enkaz Bildirimi & Kayıp İhbar</Text>
                  <Text style={styles.featureDescription}>Fotoğraf ve GPS konum bilgisi ile enkaz durumunu bildirin. Kayıp kişiler için hızlı ihbar sistemi.</Text>
                </View>
              </View>

              <View style={styles.featureCard}>
                <View style={styles.featureIcon}>
                  <Ionicons name="volume-high" size={24} color="#9C27B0" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={styles.featureTitle}>Acil Durum Ses Sistemi</Text>
                  <Text style={styles.featureDescription}>Düdük sesi ve tiz frekanslı seslerle dikkat çekin. Enkaz altında kalma durumunda hayat kurtarıcı özellik.</Text>
                </View>
              </View>

              <View style={styles.featureCard}>
                <View style={styles.featureIcon}>
                  <Ionicons name="notifications" size={24} color="#FF5722" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={styles.featureTitle}>Aile Bildirim Sistemi</Text>
                  <Text style={styles.featureDescription}>Önceden tanımladığınız kişilere otomatik SMS gönderimi. Durumunuzu hızlıca ailenize bildirin.</Text>
                </View>
              </View>
            </View>

            {/* Nasıl Kullanılır */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📱 Detaylı Kullanım Kılavuzu</Text>
              
              <View style={styles.instructionCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepText}>1</Text>
                </View>
                <View style={styles.instructionContent}>
                  <Text style={styles.instructionTitle}>İlk Kurulum ve İzinler</Text>
                  <Text style={styles.instructionDescription}>Konum izni verin (GPS özelliği). Bildirim izni aktif edin. Ayarlar'dan aile üyelerinin iletişim bilgilerini ekleyin.</Text>
                </View>
              </View>

              <View style={styles.instructionCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepText}>2</Text>
                </View>
                <View style={styles.instructionContent}>
                  <Text style={styles.instructionTitle}>Deprem Verilerini İzleme</Text>
                  <Text style={styles.instructionDescription}>Ana sayfada son depremleri görüntüleyin. Sismik dalga grafiklerini inceleyin. "Tümünü Gör" ile detaylı liste ve koordinat bilgilerine erişin.</Text>
                </View>
              </View>

              <View style={styles.instructionCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepText}>3</Text>
                </View>
                <View style={styles.instructionContent}>
                  <Text style={styles.instructionTitle}>Toplanma Alanları ve Hastaneler</Text>
                  <Text style={styles.instructionDescription}>Tab sistemi ile toplanma alanları ve hastaneler arasında geçiş yapın. Harita üzerinde konumları görüntüleyin ve yol tarifi alın.</Text>
                </View>
              </View>

              <View style={styles.instructionCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepText}>4</Text>
                </View>
                <View style={styles.instructionContent}>
                  <Text style={styles.instructionTitle}>Acil Durum Eylem Planı</Text>
                  <Text style={styles.instructionDescription}>Kırmızı "ENKAZ BİLDİR" butonu ile fotoğraf çekin. "ENKAZ ALTINDAYIM" butonu ile GPS konumunuzu paylaşın. Horn özelliği ile ses çıkarın.</Text>
                </View>
              </View>

              <View style={styles.instructionCard}>
                <View style={styles.stepNumber}>
                  <Text style={styles.stepText}>5</Text>
                </View>
                <View style={styles.instructionContent}>
                  <Text style={styles.instructionTitle}>İletişim ve Bildirim</Text>
                  <Text style={styles.instructionDescription}>112 acil hattını hızlı arayın. "Ailene Bildir" ile önceden hazırladığınız mesajı tüm aile üyelerine gönderin.</Text>
                </View>
              </View>
            </View>

            {/* Acil Durum Rehberi */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>🆘 Kapsamlı Acil Durum Rehberi</Text>
              
              <View style={styles.emergencyCard}>
                <Text style={styles.emergencyTitle}>Deprem Anında Yapılacaklar</Text>
                <Text style={styles.emergencyStep}>• Sakin kalın, paniğe kapılmayın</Text>
                <Text style={styles.emergencyStep}>• Çök-Korun-Tutun pozisyonu alın (masa altına sığının)</Text>
                <Text style={styles.emergencyStep}>• Kapı ve pencerelerde durmayın</Text>
                <Text style={styles.emergencyStep}>• Sarsıntı durduktan sonra toplanma alanına gidin</Text>
                <Text style={styles.emergencyStep}>• "Ailene Bildir" ile durumunuzu iletin</Text>
              </View>

              <View style={styles.emergencyCard}>
                <Text style={styles.emergencyTitle}>Enkaz Altında Kalırsanız</Text>
                <Text style={styles.emergencyStep}>• "ENKAZ ALTINDAYIM" butonunu kullanın (GPS gönderir)</Text>
                <Text style={styles.emergencyStep}>• Düdük sesi çıkarın (Horn özelliği)</Text>
                <Text style={styles.emergencyStep}>• Bağırmak yerine metal cisimle vurarak ses çıkarın</Text>
                <Text style={styles.emergencyStep}>• Gücünüzü koruyun, su tasarrufu yapın</Text>
                <Text style={styles.emergencyStep}>• Telefonunuzun pilini koruyun</Text>
              </View>

              <View style={styles.emergencyCard}>
                <Text style={styles.emergencyTitle}>Deprem Sonrası</Text>
                <Text style={styles.emergencyStep}>• Gaz vanalarını kapatın</Text>
                <Text style={styles.emergencyStep}>• Elektrik ana şalterini kapatın</Text>
                <Text style={styles.emergencyStep}>• Hasar tespiti için fotoğraf çekin</Text>
                <Text style={styles.emergencyStep}>• Toplanma alanında kalın</Text>
                <Text style={styles.emergencyStep}>• Artçı sarsıntılara hazır olun</Text>
              </View>
            </View>

            {/* İpucu Bölümü - Yukarı taşındı */}
            <View style={styles.section}>
              <View style={styles.footerCard}>
                <Text style={styles.footerTitle}>💡 Önemli İpuçları</Text>
                <Text style={styles.footerText}>
                  🔄 Uygulamayı düzenli güncelleyin{'\n'}
                  📱 Telefonunuzun pilini her zaman şarjlı tutun{'\n'}
                  🎒 Acil durum çantanızı hazır bulundurun{'\n'}
                  👨‍👩‍👧‍👦 Aile üyelerinizle toplanma noktası belirleyin{'\n'}
                  📞 Acil durumda panik yapmayın, sistemli hareket edin
                </Text>
              </View>
            </View>

            {/* Acil Telefon Numarası - Sadece 112 */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📞 Acil Durum Hattı</Text>
              
              <View style={styles.phoneCard}>
                <View style={styles.singlePhoneRow}>
                  <Ionicons name="call" size={28} color="#D32F2F" />
                  <Text style={styles.emergencyNumber}>112</Text>
                  <Text style={styles.emergencyLabel}>Genel Acil Durum Hattı</Text>
                </View>
                <Text style={styles.phoneNote}>
                  112 numarası tüm acil durumlar için tek numara sistemidir. 
                  İtfaiye, ambulans, polis ve diğer acil servislere bu numaradan ulaşabilirsiniz.
                </Text>
              </View>
            </View>

          </View>
        </ScrollView>
      </SafeAreaView>
    </View>
  )
}

export default Info

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
  },
  content: {
    padding: 20,
    paddingBottom: 120,
  },
  section: {
    marginBottom: 30,
  },
  headerCard: {
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 30,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  appLogo: {
    width: 80,
    height: 80,
    marginBottom: 15,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 5,
  },
  appSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  dataSource: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2D2D2D',
    marginBottom: 15,
  },
  dataSourceCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  dataSourceIcon: {
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 12,
    marginRight: 15,
  },
  dataSourceContent: {
    flex: 1,
  },
  dataSourceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  dataSourceDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  dataSourceText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  featureCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  featureIcon: {
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 12,
    marginRight: 15,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  featureDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  instructionCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  stepNumber: {
    backgroundColor: '#D32F2F',
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  stepText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
  instructionContent: {
    flex: 1,
  },
  instructionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  instructionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  emergencyCard: {
    backgroundColor: '#FFF3E0',
    borderLeft: '4px solid #FF9800',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
  },
  emergencyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E65100',
    marginBottom: 10,
  },
  emergencyStep: {
    fontSize: 14,
    color: '#BF360C',
    lineHeight: 20,
    marginBottom: 5,
  },
  phoneCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  singlePhoneRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 8,
    backgroundColor: '#FFEBEE',
    borderRadius: 12,
    marginBottom: 12,
  },
  emergencyNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#D32F2F',
    marginLeft: 15,
    minWidth: 60,
  },
  emergencyLabel: {
    fontSize: 18,
    color: '#333',
    marginLeft: 15,
    fontWeight: '600',
  },
  phoneNote: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    textAlign: 'center',
    marginTop: 8,
    fontStyle: 'italic',
  },
  footerCard: {
    backgroundColor: '#E3F2FD',
    borderRadius: 15,
    padding: 20,
    borderLeft: '4px solid #2196F3',
  },
  footerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1565C0',
    marginBottom: 10,
  },
  footerText: {
    fontSize: 14,
    color: '#0D47A1',
    lineHeight: 20,
  },
  boldText: {
    fontWeight: 'bold',
    color: '#1976D2',
  },
});
