import { StyleSheet, Text, View, Modal, TouchableOpacity, ScrollView} from 'react-native'
import React from 'react'
import Icon from 'react-native-vector-icons/Ionicons';

const Agreement = ({isTermsModalVisible, setIsTermsModalVisible, setIsTermsAccepted}) => {
  return (
    <Modal visible={isTermsModalVisible} transparent animationType="slide">
        <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
            {/* Kapatma Butonu */}
            <TouchableOpacity style={styles.closeButton} onPress={() => setIsTermsModalVisible(false)}>
                <Icon name="close" size={24} color="black" />
            </TouchableOpacity>

            {/* Başlık */}
            <Text style={styles.modalTitle}>Kullanıcı Sözleşmesi</Text>

            {/* Kaydırılabilir İçerik */}
            <ScrollView style={styles.scrollContainer}>
                <Text style={styles.sectionTitle}>1. Taraflar</Text>
                <Text style={styles.modalText}>
                İşbu Kullanıcı Sözleşmesi (“Sözleşme”), aşağıda bilgileri verilen taraflar arasında akdedilmiştir:
                </Text>
                <Text style={styles.modalText}>
                - **Hizmet Sağlayıcı:** [İlgili Kurum/Kuruluş] (“İlgili Kurum/Kuruluş”) {"\n"}
                - **Kullanıcı:** Uygulamaya kayıt olan ve hizmetlerden faydalanan kişi (“Kullanıcı”)
                </Text>

                <Text style={styles.sectionTitle}>2. Kişisel Verilerin İşlenmesi ve Korunması</Text>
                <Text style={styles.modalText}>İlgili Kurum/Kuruluş, Kullanıcı'nın aşağıdaki kişisel verilerini toplayabilir:</Text>
                <Text style={styles.bulletPoint}>• Ad ve soyad</Text>
                <Text style={styles.bulletPoint}>• Lokasyon bilgisi (GPS veya manuel giriş)</Text>
                <Text style={styles.bulletPoint}>• Telefon numarası</Text>

                <Text style={styles.modalText}>
                Bu veriler aşağıdaki amaçlarla işlenmektedir:
                </Text>
                <Text style={styles.bulletPoint}>• Kullanıcı kimliğinin doğrulanması</Text>
                <Text style={styles.bulletPoint}>• Hizmetlerin kişiselleştirilmesi</Text>
                <Text style={styles.bulletPoint}>• Güvenlik önlemlerinin artırılması</Text>

                <Text style={styles.sectionTitle}>3. Kullanıcı Hak ve Yükümlülükleri</Text>
                <Text style={styles.modalText}>
                Kullanıcı, uygulamayı hukuka uygun şekilde kullanacağını ve kişisel verilerinin işlenmesini kabul ettiğini beyan eder.
                </Text>
                <Text style={styles.bulletPoint}>
                • Kullanıcı, uygulamayı yalnızca meşru amaçlarla kullanacaktır.
                </Text>
                <Text style={styles.bulletPoint}>
                • Kullanıcı, diğer kişilerin haklarını ihlal etmemeyi taahhüt eder.
                </Text>

                <Text style={styles.sectionTitle}>4. Sözleşmenin Yürürlüğe Girmesi ve Feshi</Text>
                <Text style={styles.modalText}>
                Kullanıcı, bu sözleşmeyi onayladığında hükümleri kabul etmiş sayılır.
                </Text>
                <Text style={styles.modalText}>
                İlgili Kurum/Kuruluş, Kullanıcı'nın sözleşmeye aykırı hareket ettiğini tespit ederse, hizmetleri durdurma hakkına sahiptir.
                </Text>

                <Text style={styles.sectionTitle}>5. Uyuşmazlıkların Çözümü</Text>
                <Text style={styles.modalText}>
                İşbu sözleşmeden doğabilecek uyuşmazlıkların çözümünde [İlgili Kurum/Kuruluş] 'un bulunduğu ülke/şehrin yetkili mahkemeleri ve icra daireleri yetkilidir.
                </Text>

                <Text style={styles.sectionTitle}>6. Son Hükümler</Text>
                <Text style={styles.modalText}>
                Bu sözleşme, Kullanıcı'nın onayı ile yürürlüğe girer ve taraflar arasında bağlayıcıdır.
                </Text>
            </ScrollView>

            {/* Onay Butonu */}
            <View style={styles.buttonContainer}>
                <TouchableOpacity
                style={styles.acceptButton}
                onPress={() => {
                    setIsTermsAccepted(true); // Checkbox işaretlensin
                    setIsTermsModalVisible(false); // Modal kapansın
                }}
                >
                <Text style={styles.acceptButtonText}>Okudum ve Onaylıyorum</Text>
                </TouchableOpacity>
            </View>
            </View>
        </View>
    </Modal>
  )
}

export default Agreement

const styles = StyleSheet.create({
    termsContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 15,
      },
      termsText: {
        fontSize: 14,
        color: '#007BFF',
        textDecorationLine: 'underline',
        marginLeft: 5,
      },
      modalText: {
        fontSize: 14,
        textAlign: "justify",
        marginBottom: 5,
      },
      modalContainer: {
        flex: 1,
        backgroundColor: "rgba(0, 0, 0, 0.5)", // Saydam arka plan
        justifyContent: "center",
        alignItems: "center",
      },
      modalContent: {
        width: "85%",
        backgroundColor: "#fff",
        borderRadius: 10,
        padding: 20,
        maxHeight: "80%", // Modalın çok büyük olmaması için
        flexGrow: 1, // İçeriğin büyümesine izin verir
        justifyContent: "space-between", // İçeriği dağıtır
      },
      modalTitle: {
        fontSize: 18,
        fontWeight: "bold",
        marginBottom: 10,
        textAlign: "center",
      },
      closeButton: {
        position: "absolute",
        top: 10,
        right: 10,
        padding: 5,
      },
      bulletPoint: {
        fontSize: 14,
        marginLeft: 10,
        marginBottom: 3,
      },
      scrollContainer: {
        flexGrow: 1, // İçeriğin tam kaydırılmasını sağlar
        marginBottom: 15,
      },
      scrollContainer: {
        flexGrow: 1, // İçeriğin tam kaydırılmasını sağlar
        marginBottom: 15,
      },
      sectionTitle: {
        fontSize: 16,
        fontWeight: "bold",
        marginTop: 10,
      },
      buttonContainer: {
        alignItems: "center",
        marginTop: 10,
      },
      acceptButton: {
        backgroundColor: "#007BFF",
        paddingVertical: 12,
        paddingHorizontal: 30,
        borderRadius: 5,
        alignItems: "center",
      },
      acceptButtonText: {
        color: "#fff",
        fontWeight: "bold",
        fontSize: 16,
      },
      acceptButton: {
        backgroundColor: '#007BFF',
        paddingVertical: 10,
        paddingHorizontal: 20,
        borderRadius: 5,
      },
      
      acceptButtonText: {
        color: 'white',
        fontSize: 16,
      },
})