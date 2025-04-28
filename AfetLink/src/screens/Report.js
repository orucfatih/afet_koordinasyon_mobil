import React, { useState, useEffect } from 'react';
 import {
   View,
   Text,
   StyleSheet,
   TouchableOpacity,
   FlatList,
   TextInput,
   Modal,
   Platform,
   ScrollView,
   Alert,
   ActivityIndicator,
   StatusBar,
   SafeAreaView,
   PermissionsAndroid
 } from 'react-native';
 import AsyncStorage from '@react-native-async-storage/async-storage';
 import DateTimePicker from '@react-native-community/datetimepicker';
 import Ionicons from 'react-native-vector-icons/Ionicons';
 import { Picker } from '@react-native-picker/picker';
 // API_KEY'i buraya ekleyin
 const GOOGLE_CLOUD_API_KEY = 'AIzaSyDJA0mwT65t6sEDg4qow-L00LuK1nZycPo';
 
 const Report = ({ navigation }) => {
   const [reports, setReports] = useState([]);
   const [modalVisible, setModalVisible] = useState(false);
   const [editModalVisible, setEditModalVisible] = useState(false);
   const [selectedReport, setSelectedReport] = useState(null);
   const [searchRegion, setSearchRegion] = useState('');
   const [searchType, setSearchType] = useState('');
   const [isListening, setIsListening] = useState(false);
   const [currentField, setCurrentField] = useState('');
   const [audioRecording, setAudioRecording] = useState(null);
 
   // Yeni rapor için state'ler
   const [newReport, setNewReport] = useState({
     bolge: '',
     tur: 'Durum Değerlendirme Raporu',
     ozet: '',
     detaylar: '',
     ihtiyaclar: '',
     tarih: new Date().toISOString(),
     created_at: Date.now() / 1000,
     updated_at: Date.now() / 1000
   });
 
   const reportTypes = [
     { label: 'Durum Değerlendirme Raporu', value: 'Durum Değerlendirme Raporu' },
     { label: 'Hasar Tespit Raporu', value: 'Hasar Tespit Raporu' },
     { label: 'İhtiyaç Analiz Raporu', value: 'İhtiyaç Analiz Raporu' },
     { label: 'Müdahale Raporu', value: 'Müdahale Raporu' },
     { label: 'Koordinasyon Raporu', value: 'Koordinasyon Raporu' },
   ];
 
   const requestMicrophonePermission = async () => {
     try {
       if (Platform.OS === 'android') {
         const granted = await PermissionsAndroid.request(
           PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
           {
             title: 'Mikrofon İzni',
             message: 'Sesli not almak için mikrofon izni gerekiyor.',
             buttonNeutral: 'Daha Sonra Sor',
             buttonNegative: 'İptal',
             buttonPositive: 'Tamam',
           }
         );
         return granted === PermissionsAndroid.RESULTS.GRANTED;
       }
       return true;
     } catch (err) {
       console.error('Mikrofon izni hatası:', err);
       return false;
     }
   };
 
   const startListening = async (field) => {
     try {
       const hasPermission = await requestMicrophonePermission();
       if (!hasPermission) {
         Alert.alert('Hata', 'Mikrofon izni verilmedi');
         return;
       }
 
       setCurrentField(field);
       setIsListening(true);
 
       // Google Cloud Speech-to-Text API'ye istek gönderme
       const response = await fetch(
         `https://speech.googleapis.com/v1/speech:recognize?key=${GOOGLE_CLOUD_API_KEY}`,
         {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json',
           },
           body: JSON.stringify({
             config: {
               encoding: 'LINEAR16',
               sampleRateHertz: 16000,
               languageCode: 'tr-TR',
             },
             audio: {
               content: audioRecording, // Base64 encoded audio content
             },
           }),
         }
       );
 
       const data = await response.json();
       
       if (data.results && data.results[0]) {
         const transcription = data.results[0].alternatives[0].transcript;
         
         if (selectedReport) {
           setSelectedReport(prev => ({
             ...prev,
             [currentField]: transcription
           }));
         } else {
           setNewReport(prev => ({
             ...prev,
             [currentField]: transcription
           }));
         }
       }
 
     } catch (error) {
       console.error('Ses tanıma hatası:', error);
       Alert.alert('Hata', 'Ses tanıma sırasında bir hata oluştu.');
     } finally {
       setIsListening(false);
     }
   };
 
   const stopListening = async () => {
     setIsListening(false);
     // Ses kaydını durdurma ve API'ye gönderme işlemleri burada yapılacak
   };
 
   const loadReports = async () => {
     try {
       const savedReports = await AsyncStorage.getItem('reports');
       if (savedReports) {
         setReports(JSON.parse(savedReports));
       }
     } catch (error) {
       console.error('Raporlar yüklenirken hata:', error);
     }
   };
 
   const saveReports = async (updatedReports) => {
     try {
       await AsyncStorage.setItem('reports', JSON.stringify(updatedReports));
       setReports(updatedReports);
     } catch (error) {
       console.error('Raporlar kaydedilirken hata:', error);
     }
   };
 
   const handleAddReport = async () => {
     if (!newReport.bolge || !newReport.ozet || !newReport.detaylar || !newReport.ihtiyaclar) {
       Alert.alert('Hata', 'Lütfen tüm alanları doldurun.');
       return;
     }
 
     const report = {
       id: Date.now().toString(),
       ...newReport,
       created_at: Date.now() / 1000,
       updated_at: Date.now() / 1000
     };
 
     const updatedReports = [...reports, report];
     await saveReports(updatedReports);
     setModalVisible(false);
     setNewReport({
       bolge: '',
       tur: 'Durum Değerlendirme Raporu',
       ozet: '',
       detaylar: '',
       ihtiyaclar: '',
       tarih: new Date().toISOString(),
       created_at: Date.now() / 1000,
       updated_at: Date.now() / 1000
     });
   };
 
   const handleUpdateReport = async () => {
     if (!selectedReport) return;
 
     const updatedReport = {
       ...selectedReport,
       updated_at: Date.now() / 1000
     };
 
     const updatedReports = reports.map(report =>
       report.id === selectedReport.id ? updatedReport : report
     );
 
     await saveReports(updatedReports);
     setEditModalVisible(false);
     setSelectedReport(null);
   };
 
   const handleDeleteReport = async (reportId) => {
     Alert.alert(
       'Onay',
       'Bu raporu silmek istediğinizden emin misiniz?',
       [
         {
           text: 'İptal',
           style: 'cancel',
         },
         {
           text: 'Sil',
           style: 'destructive',
           onPress: async () => {
             const updatedReports = reports.filter(report => report.id !== reportId);
             await saveReports(updatedReports);
           },
         },
       ],
     );
   };
 
   const filterReports = () => {
     return reports.filter(report => {
       const regionMatch = searchRegion
         ? report.bolge.toLowerCase().includes(searchRegion.toLowerCase())
         : true;
       const typeMatch = searchType
         ? report.tur === searchType
         : true;
       return regionMatch && typeMatch;
     });
   };
 
   const renderInputWithVoice = (label, value, onChangeText, field) => (
     <View style={styles.inputContainer}>
       <Text style={styles.inputLabel}>{label}</Text>
       <View style={styles.inputWrapper}>
         <TextInput
           style={[styles.input, field === 'detaylar' && styles.textArea]}
           multiline={field === 'detaylar'}
           numberOfLines={field === 'detaylar' ? 4 : 1}
           value={value}
           onChangeText={onChangeText}
         />
         <TouchableOpacity
           style={styles.voiceButton}
           onPress={() => isListening ? stopListening() : startListening(field)}
         >
           <Ionicons
             name={isListening && currentField === field ? "mic" : "mic-outline"}
             size={24}
             color={isListening && currentField === field ? "#D32F2F" : "#666"}
           />
         </TouchableOpacity>
       </View>
       {isListening && currentField === field && (
         <ActivityIndicator style={styles.loader} color="#D32F2F" />
       )}
     </View>
   );
 
   const renderReportItem = ({ item }) => (
     <View style={styles.reportItem}>
       <View style={styles.reportHeader}>
         <Text style={styles.reportTitle}>{item.bolge}</Text>
         <View style={styles.reportActions}>
           <TouchableOpacity
             onPress={() => {
               setSelectedReport(item);
               setEditModalVisible(true);
             }}
             style={styles.actionButton}
           >
             <Ionicons name="create-outline" size={24} color="#2196F3" />
           </TouchableOpacity>
           <TouchableOpacity
             onPress={() => handleDeleteReport(item.id)}
             style={styles.actionButton}
           >
             <Ionicons name="trash-outline" size={24} color="#D32F2F" />
           </TouchableOpacity>
         </View>
       </View>
       <Text style={styles.reportType}>Tür: {item.tur}</Text>
       <Text style={styles.reportDescription}>Özet: {item.ozet}</Text>
       <Text style={styles.reportDate}>
         Tarih: {new Date(item.tarih).toLocaleString()}
       </Text>
     </View>
   );
 
   return (
     <SafeAreaView style={styles.safeArea}>
       <StatusBar
         barStyle="light-content"
         backgroundColor="#2D2D2D"
         translucent={true}
       />
       <View style={styles.container}>
         <View style={styles.header}>
           <TouchableOpacity
             style={styles.backButton}
             onPress={() => navigation.goBack()}
           >
             <Ionicons name="arrow-back" size={24} color="white" />
           </TouchableOpacity>
           <Text style={styles.headerTitle}>Raporlar</Text>
           <TouchableOpacity
             style={styles.addButton}
             onPress={() => setModalVisible(true)}
           >
             <Ionicons name="add" size={24} color="white" />
             <Text style={styles.addButtonText}>Yeni Rapor</Text>
           </TouchableOpacity>
         </View>
 
         <View style={styles.filterContainer}>
           <TextInput
             style={styles.searchInput}
             placeholder="Afet Bölgesi Ara"
             value={searchRegion}
             onChangeText={setSearchRegion}
           />
 
           <View style={styles.typePickerContainer}>
             <Picker
               selectedValue={searchType}
               onValueChange={setSearchType}
               style={styles.typePicker}
             >
               <Picker.Item label="Tüm Türler" value="" />
               {reportTypes.map(type => (
                 <Picker.Item
                   key={type.value}
                   label={type.label}
                   value={type.value}
                 />
               ))}
             </Picker>
           </View>
         </View>
 
         <FlatList
           data={filterReports()}
           renderItem={renderReportItem}
           keyExtractor={item => item.id}
           style={styles.list}
         />
 
         {/* Yeni Rapor Modalı */}
         <Modal
           visible={modalVisible}
           animationType="slide"
           transparent={true}
           onRequestClose={() => setModalVisible(false)}
         >
           <View style={styles.modalContainer}>
             <ScrollView style={styles.modalContent}>
               <Text style={styles.modalTitle}>Yeni Rapor</Text>
               
               {renderInputWithVoice(
                 "Afet Bölgesi",
                 newReport.bolge,
                 text => setNewReport({...newReport, bolge: text}),
                 "bolge"
               )}
 
               <View style={styles.pickerContainer}>
                 <Text style={styles.inputLabel}>Rapor Türü</Text>
                 <Picker
                   selectedValue={newReport.tur}
                   onValueChange={value => setNewReport({...newReport, tur: value})}
                   style={styles.picker}
                 >
                   {reportTypes.map(type => (
                     <Picker.Item
                       key={type.value}
                       label={type.label}
                       value={type.value}
                     />
                   ))}
                 </Picker>
               </View>
 
               {renderInputWithVoice(
                 "Durum Özeti",
                 newReport.ozet,
                 text => setNewReport({...newReport, ozet: text}),
                 "ozet"
               )}
 
               {renderInputWithVoice(
                 "Detaylı Bilgiler",
                 newReport.detaylar,
                 text => setNewReport({...newReport, detaylar: text}),
                 "detaylar"
               )}
 
               {renderInputWithVoice(
                 "İhtiyaçlar ve Öneriler",
                 newReport.ihtiyaclar,
                 text => setNewReport({...newReport, ihtiyaclar: text}),
                 "ihtiyaclar"
               )}
 
               <View style={styles.modalButtons}>
                 <TouchableOpacity
                   style={[styles.modalButton, styles.cancelButton]}
                   onPress={() => setModalVisible(false)}
                 >
                   <Text style={styles.modalButtonText}>İptal</Text>
                 </TouchableOpacity>
                 <TouchableOpacity
                   style={[styles.modalButton, styles.saveButton]}
                   onPress={handleAddReport}
                 >
                   <Text style={styles.modalButtonText}>Kaydet</Text>
                 </TouchableOpacity>
               </View>
             </ScrollView>
           </View>
         </Modal>
 
         {/* Düzenleme Modalı */}
         <Modal
           visible={editModalVisible}
           animationType="slide"
           transparent={true}
           onRequestClose={() => setEditModalVisible(false)}
         >
           <View style={styles.modalContainer}>
             <ScrollView style={styles.modalContent}>
               <Text style={styles.modalTitle}>Raporu Düzenle</Text>
               
               {renderInputWithVoice(
                 "Afet Bölgesi",
                 selectedReport?.bolge || '',
                 text => setSelectedReport({...selectedReport, bolge: text}),
                 "bolge"
               )}
 
               <View style={styles.pickerContainer}>
                 <Text style={styles.inputLabel}>Rapor Türü</Text>
                 <Picker
                   selectedValue={selectedReport?.tur}
                   onValueChange={value => setSelectedReport({...selectedReport, tur: value})}
                   style={styles.picker}
                 >
                   {reportTypes.map(type => (
                     <Picker.Item
                       key={type.value}
                       label={type.label}
                       value={type.value}
                     />
                   ))}
                 </Picker>
               </View>
 
               {renderInputWithVoice(
                 "Durum Özeti",
                 selectedReport?.ozet || '',
                 text => setSelectedReport({...selectedReport, ozet: text}),
                 "ozet"
               )}
 
               {renderInputWithVoice(
                 "Detaylı Bilgiler",
                 selectedReport?.detaylar || '',
                 text => setSelectedReport({...selectedReport, detaylar: text}),
                 "detaylar"
               )}
 
               {renderInputWithVoice(
                 "İhtiyaçlar ve Öneriler",
                 selectedReport?.ihtiyaclar || '',
                 text => setSelectedReport({...selectedReport, ihtiyaclar: text}),
                 "ihtiyaclar"
               )}
 
               <View style={styles.modalButtons}>
                 <TouchableOpacity
                   style={[styles.modalButton, styles.cancelButton]}
                   onPress={() => setEditModalVisible(false)}
                 >
                   <Text style={styles.modalButtonText}>İptal</Text>
                 </TouchableOpacity>
                 <TouchableOpacity
                   style={[styles.modalButton, styles.saveButton]}
                   onPress={handleUpdateReport}
                 >
                   <Text style={styles.modalButtonText}>Güncelle</Text>
                 </TouchableOpacity>
               </View>
             </ScrollView>
           </View>
         </Modal>
       </View>
     </SafeAreaView>
   );
 };
 
 const styles = StyleSheet.create({
   safeArea: {
     flex: 1,
     backgroundColor: '#2D2D2D',
     paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
   },
   container: {
     flex: 1,
     backgroundColor: '#f8f9fa',
   },
   header: {
     flexDirection: 'row',
     justifyContent: 'space-between',
     alignItems: 'center',
     padding: 16,
     backgroundColor: '#2D2D2D',
     paddingTop: Platform.OS === 'android' ? 20 : 16,
     borderBottomLeftRadius: 20,
     borderBottomRightRadius: 20,
     elevation: 5,
   },
   backButton: {
     padding: 8,
   },
   headerTitle: {
     fontSize: 20,
     fontWeight: 'bold',
     color: 'white',
     flex: 1,
     textAlign: 'center',
   },
   addButton: {
     flexDirection: 'row',
     alignItems: 'center',
     backgroundColor: '#4CAF50',
     padding: 8,
     borderRadius: 8,
   },
   addButtonText: {
     color: 'white',
     marginLeft: 4,
   },
   filterContainer: {
     padding: 16,
     backgroundColor: 'white',
     borderBottomWidth: 1,
     borderBottomColor: '#e0e0e0',
   },
   searchInput: {
     borderWidth: 1,
     borderColor: '#ddd',
     borderRadius: 8,
     padding: 12,
     marginBottom: 8,
   },
   typePickerContainer: {
     borderWidth: 1,
     borderColor: '#ddd',
     borderRadius: 8,
     overflow: 'hidden',
   },
   typePicker: {
     height: 40,
   },
   list: {
     flex: 1,
   },
   reportItem: {
     backgroundColor: 'white',
     padding: 16,
     marginHorizontal: 16,
     marginVertical: 8,
     borderRadius: 8,
     elevation: 2,
     shadowColor: '#000',
     shadowOffset: { width: 0, height: 2 },
     shadowOpacity: 0.1,
     shadowRadius: 4,
   },
   reportHeader: {
     flexDirection: 'row',
     justifyContent: 'space-between',
     alignItems: 'center',
     marginBottom: 8,
   },
   reportTitle: {
     fontSize: 18,
     fontWeight: 'bold',
     flex: 1,
   },
   reportActions: {
     flexDirection: 'row',
   },
   actionButton: {
     padding: 4,
     marginLeft: 8,
   },
   reportType: {
     color: '#666',
     marginBottom: 4,
   },
   reportDescription: {
     marginBottom: 8,
   },
   reportDate: {
     color: '#666',
     fontSize: 12,
   },
   modalContainer: {
     flex: 1,
     backgroundColor: 'rgba(0, 0, 0, 0.5)',
   },
   modalContent: {
     backgroundColor: 'white',
     margin: 20,
     padding: 20,
     borderRadius: 8,
     maxHeight: '90%',
   },
   modalTitle: {
     fontSize: 20,
     fontWeight: 'bold',
     marginBottom: 16,
   },
   inputContainer: {
     marginBottom: 16,
   },
   inputLabel: {
     fontSize: 16,
     marginBottom: 8,
     color: '#333',
   },
   inputWrapper: {
     flexDirection: 'row',
     alignItems: 'center',
   },
   input: {
     flex: 1,
     borderWidth: 1,
     borderColor: '#ddd',
     borderRadius: 8,
     padding: 12,
   },
   textArea: {
     height: 100,
     textAlignVertical: 'top',
   },
   voiceButton: {
     padding: 8,
     marginLeft: 8,
   },
   loader: {
     marginTop: 8,
   },
   pickerContainer: {
     marginBottom: 16,
   },
   picker: {
     borderWidth: 1,
     borderColor: '#ddd',
     borderRadius: 8,
   },
   modalButtons: {
     flexDirection: 'row',
     justifyContent: 'flex-end',
     marginTop: 16,
   },
   modalButton: {
     padding: 12,
     borderRadius: 8,
     minWidth: 100,
     alignItems: 'center',
     marginLeft: 8,
   },
   cancelButton: {
     backgroundColor: '#666',
   },
   saveButton: {
     backgroundColor: '#4CAF50',
   },
   modalButtonText: {
     color: 'white',
     fontWeight: 'bold',
   },
 });
 
 export default Report;