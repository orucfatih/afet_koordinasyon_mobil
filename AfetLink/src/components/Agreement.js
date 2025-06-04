import { StyleSheet, Text, View, Modal, TouchableOpacity, ScrollView, StatusBar} from 'react-native'
import React from 'react'
import Ionicons from 'react-native-vector-icons/Ionicons';
import * as Animatable from 'react-native-animatable';

const Agreement = ({isTermsModalVisible, setIsTermsModalVisible, setIsTermsAccepted}) => {
  return (
    <Modal visible={isTermsModalVisible} transparent animationType="slide">
        <StatusBar barStyle="light-content" backgroundColor="rgba(0,0,0,0.8)" />
        <View style={styles.modalContainer}>
            <Animatable.View 
                animation="slideInUp" 
                duration={300}
                style={styles.modalContent}
            >
                {/* Header */}
                <View style={styles.header}>
                    <View style={styles.iconContainer}>
                        <Ionicons name="document-text" size={24} color="#4CAF50" />
                    </View>
                    <Text style={styles.modalTitle}>Kullanıcı Sözleşmesi</Text>
                    <TouchableOpacity 
                        style={styles.closeButton} 
                        onPress={() => setIsTermsModalVisible(false)}
                        activeOpacity={0.8}
                    >
                        <Ionicons name="close" size={24} color="rgba(255,255,255,0.8)" />
                    </TouchableOpacity>
                </View>

                {/* Scrollable Content */}
                <ScrollView 
                    style={styles.scrollContainer}
                    showsVerticalScrollIndicator={false}
                >
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>1. Taraflar</Text>
                        <Text style={styles.modalText}>
                            İşbu Kullanıcı Sözleşmesi ("Sözleşme"), aşağıda bilgileri verilen taraflar arasında akdedilmiştir:
                        </Text>
                        <Text style={styles.modalText}>
                            • <Text style={styles.highlight}>Hizmet Sağlayıcı:</Text> AfetLink ("Uygulama") {"\n"}
                            • <Text style={styles.highlight}>Kullanıcı:</Text> Uygulamaya kayıt olan ve hizmetlerden faydalanan kişi
                        </Text>
                    </View>

                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>2. Kişisel Verilerin İşlenmesi ve Korunması</Text>
                        <Text style={styles.modalText}>AfetLink, Kullanıcı'nın aşağıdaki kişisel verilerini toplayabilir:</Text>
                        <View style={styles.bulletContainer}>
                            <Text style={styles.bulletPoint}>• Ad ve soyad</Text>
                            <Text style={styles.bulletPoint}>• Lokasyon bilgisi (GPS veya manuel giriş)</Text>
                            <Text style={styles.bulletPoint}>• Telefon numarası</Text>
                            <Text style={styles.bulletPoint}>• E-mail adresi</Text>
                        </View>

                        <Text style={styles.modalText}>Bu veriler aşağıdaki amaçlarla işlenmektedir:</Text>
                        <View style={styles.bulletContainer}>
                            <Text style={styles.bulletPoint}>• Kullanıcı kimliğinin doğrulanması</Text>
                            <Text style={styles.bulletPoint}>• Acil durum hizmetlerinin sağlanması</Text>
                            <Text style={styles.bulletPoint}>• Güvenlik önlemlerinin artırılması</Text>
                            <Text style={styles.bulletPoint}>• İstatistiksel analiz ve raporlama</Text>
                        </View>
                    </View>

                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>3. Kullanıcı Hak ve Yükümlülükleri</Text>
                        <Text style={styles.modalText}>
                            Kullanıcı, uygulamayı hukuka uygun şekilde kullanacağını ve kişisel verilerinin işlenmesini kabul ettiğini beyan eder.
                        </Text>
                        <View style={styles.bulletContainer}>
                            <Text style={styles.bulletPoint}>• Uygulamayı yalnızca meşru amaçlarla kullanacaktır</Text>
                            <Text style={styles.bulletPoint}>• Diğer kişilerin haklarını ihlal etmemeyi taahhüt eder</Text>
                            <Text style={styles.bulletPoint}>• Doğru ve güncel bilgi sağlamayı kabul eder</Text>
                        </View>
                    </View>

                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>4. Sözleşmenin Yürürlüğe Girmesi</Text>
                        <Text style={styles.modalText}>
                            Kullanıcı, bu sözleşmeyi onayladığında hükümleri kabul etmiş sayılır. AfetLink, sözleşmeye aykırı durumda hizmetleri durdurma hakkına sahiptir.
                        </Text>
                    </View>

                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>5. Son Hükümler</Text>
                        <Text style={styles.modalText}>
                            Bu sözleşme, Kullanıcı'nın onayı ile yürürlüğe girer ve taraflar arasında bağlayıcıdır. KVKK kapsamında haklarınız hakkında bilgi almak için iletişime geçebilirsiniz.
                        </Text>
                    </View>
                </ScrollView>

                {/* Accept Button */}
                <View style={styles.buttonContainer}>
                    <TouchableOpacity
                        style={styles.acceptButton}
                        onPress={() => {
                            setIsTermsAccepted(true);
                            setIsTermsModalVisible(false);
                        }}
                        activeOpacity={0.8}
                    >
                        <Ionicons name="checkmark-circle" size={20} color="white" style={styles.buttonIcon} />
                        <Text style={styles.acceptButtonText}>Okudum ve Onaylıyorum</Text>
                    </TouchableOpacity>
                </View>
            </Animatable.View>
        </View>
    </Modal>
  )
}

export default Agreement

const styles = StyleSheet.create({
    modalContainer: {
        flex: 1,
        backgroundColor: "rgba(26, 26, 26, 0.95)",
        justifyContent: "center",
        alignItems: "center",
        paddingHorizontal: 20,
    },
    modalContent: {
        width: "100%",
        maxWidth: 400,
        backgroundColor: "#2D2D2D",
        borderRadius: 20,
        height: "90%",
        shadowColor: '#4CAF50',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 20,
        elevation: 15,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 20,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.1)',
    },
    iconContainer: {
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        padding: 8,
        borderRadius: 10,
    },
    modalTitle: {
        flex: 1,
        fontSize: 20,
        fontWeight: "bold",
        color: 'white',
        textAlign: "center",
        marginHorizontal: 10,
    },
    closeButton: {
        backgroundColor: 'rgba(255,255,255,0.1)',
        padding: 8,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.2)',
    },
    scrollContainer: {
        flex: 1,
        paddingHorizontal: 20,
        paddingVertical: 10,
    },
    section: {
        marginBottom: 20,
        backgroundColor: 'rgba(255,255,255,0.05)',
        padding: 16,
        borderRadius: 12,
        borderLeftWidth: 4,
        borderLeftColor: '#4CAF50',
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: "bold",
        color: '#4CAF50',
        marginBottom: 10,
        textShadowColor: 'rgba(76, 175, 80, 0.3)',
        textShadowOffset: { width: 0, height: 1 },
        textShadowRadius: 2,
    },
    modalText: {
        fontSize: 15,
        color: 'rgba(255,255,255,0.9)',
        lineHeight: 22,
        marginBottom: 8,
        textAlign: "justify",
    },
    highlight: {
        fontWeight: 'bold',
        color: '#4CAF50',
    },
    bulletContainer: {
        marginLeft: 8,
        marginVertical: 8,
    },
    bulletPoint: {
        fontSize: 15,
        color: 'rgba(255,255,255,0.8)',
        marginBottom: 6,
        lineHeight: 20,
    },
    buttonContainer: {
        padding: 20,
        borderTopWidth: 1,
        borderTopColor: 'rgba(255,255,255,0.1)',
    },
    acceptButton: {
        backgroundColor: '#4CAF50',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 16,
        paddingHorizontal: 30,
        borderRadius: 12,
        shadowColor: '#4CAF50',
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
        elevation: 8,
    },
    buttonIcon: {
        marginRight: 8,
    },
    acceptButtonText: {
        color: "#fff",
        fontWeight: "bold",
        fontSize: 16,
    },
});