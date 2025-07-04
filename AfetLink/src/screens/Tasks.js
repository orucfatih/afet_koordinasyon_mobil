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
  KeyboardAvoidingView
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { Picker } from '@react-native-picker/picker';
import database from '@react-native-firebase/database';
import auth from '@react-native-firebase/auth';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const Tasks = ({ navigation }) => {
  const insets = useSafeAreaInsets();

  const [tasks, setTasks] = useState([]);
  const [taskHistory, setTaskHistory] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [searchLocation, setSearchLocation] = useState('');
  const [searchPriority, setSearchPriority] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'history'
  // Yeni görev için state'ler
  const [newTask, setNewTask] = useState({
    title: '',
    details: '',
    location: '',
    priority: 'Orta (2)',
    duration: '',
    status: 'active',
    created_at: Date.now() / 1000,
    updated_at: Date.now() / 1000
  });

  const priorityLevels = [
    { label: 'Düşük (1)', value: 'Düşük (1)' },
    { label: 'Orta (2)', value: 'Orta (2)' },
    { label: 'Yüksek (3)', value: 'Yüksek (3)' },
    { label: 'Acil (4)', value: 'Acil (4)' },
    { label: 'Kritik (4)', value: 'Kritik (4)' },
  ];

  useEffect(() => {
    // Authentication state dinleyicisi
    const unsubscribe = auth().onAuthStateChanged((user) => {
      setUser(user);
      setAuthLoading(false);
      if (user) {
        console.log('Kullanıcı oturum açmış:', user.email);
      } else {
        console.log('Kullanıcı oturum açmamış');
      }
    });

    return unsubscribe; // Cleanup
  }, []);

  useEffect(() => {
    if (!authLoading) {
      loadTasks();
    }
  }, [authLoading, user]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      // Aktif görevleri yükle
      const tasksRef = database().ref('operations/tasks');
      const tasksSnapshot = await tasksRef.once('value');
      const tasksData = tasksSnapshot.val();
      
      if (tasksData) {
        const tasksArray = Object.keys(tasksData).map(key => ({
          id: key,
          ...tasksData[key]
        }));
        setTasks(tasksArray);
      }

      // Görev geçmişini yükle
      const taskHistoryRef = database().ref('operations/task_history');
      const taskHistorySnapshot = await taskHistoryRef.once('value');
      const taskHistoryData = taskHistorySnapshot.val();
      
      if (taskHistoryData) {
        const taskHistoryArray = Object.keys(taskHistoryData).map(key => ({
          id: key,
          ...taskHistoryData[key]
        }));
        setTaskHistory(taskHistoryArray);
      }
    } catch (error) {
      console.error('Görevler yüklenirken hata:', error);
      Alert.alert('Hata', 'Görevler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async () => {
    if (!newTask.title || !newTask.details || !newTask.location) {
      Alert.alert('Hata', 'Lütfen başlık, detaylar ve konum alanlarını doldurun.');
      return;
    }

    setLoading(true);

    const task = {
      ...newTask,
      created_at: Date.now() / 1000,
      updated_at: Date.now() / 1000
    };

    try {
      // Firebase Realtime Database'e kaydet
      const tasksRef = database().ref('operations/tasks');
      const newTaskRef = tasksRef.push();
      await newTaskRef.set(task);
      
      setModalVisible(false);
      setNewTask({
        title: '',
        details: '',
        location: '',
        priority: 'Orta (2)',
        duration: '',
        status: 'active',
        created_at: Date.now() / 1000,
        updated_at: Date.now() / 1000
      });
      
      Alert.alert('Başarılı', 'Görev başarıyla eklendi.');
      loadTasks(); // Listeyi yenile
      
    } catch (error) {
      console.error('Görev ekleme hatası:', error);
      Alert.alert('Hata', 'Görev eklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = async () => {
    if (!selectedTask) return;

    setLoading(true);

    const updatedTask = {
      ...selectedTask,
      updated_at: Date.now() / 1000
    };

    try {
      // Firebase Realtime Database'de güncelle
      const taskRef = database().ref(`operations/tasks/${selectedTask.id}`);
      await taskRef.update(updatedTask);
      
      setEditModalVisible(false);
      setSelectedTask(null);
      
      Alert.alert('Başarılı', 'Görev başarıyla güncellendi.');
      loadTasks(); // Listeyi yenile
      
    } catch (error) {
      console.error('Görev güncelleme hatası:', error);
      Alert.alert('Hata', 'Görev güncellenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTask = async (taskId) => {
    Alert.alert(
      'Görevi Tamamla',
      'Bu görevi tamamlandı olarak işaretlemek istediğinizden emin misiniz?',
      [
        {
          text: 'İptal',
          style: 'cancel',
        },
        {
          text: 'Tamamla',
          style: 'default',
          onPress: async () => {
            setLoading(true);
            try {
              // Görevi tasks'tan al
              const taskRef = database().ref(`operations/tasks/${taskId}`);
              const taskSnapshot = await taskRef.once('value');
              const taskData = taskSnapshot.val();
              
              if (taskData) {
                // Görevi task_history'ye taşı
                const taskHistoryRef = database().ref(`operations/task_history/${taskId}`);
                const completedTask = {
                  ...taskData,
                  status: 'completed',
                  completed_at: Date.now() / 1000,
                  updated_at: Date.now() / 1000
                };
                
                await taskHistoryRef.set(completedTask);
                
                // Görevi tasks'tan sil
                await taskRef.remove();
                
                Alert.alert('Başarılı', 'Görev tamamlandı olarak işaretlendi.');
                loadTasks(); // Listeyi yenile
              }
            } catch (error) {
              console.error('Görev tamamlama hatası:', error);
              Alert.alert('Hata', 'Görev tamamlanırken bir hata oluştu.');
            } finally {
              setLoading(false);
            }
          },
        },
      ],
    );
  };

  const handleDeleteTask = async (taskId) => {
    Alert.alert(
      'Onay',
      'Bu görevi silmek istediğinizden emin misiniz?',
      [
        {
          text: 'İptal',
          style: 'cancel',
        },
        {
          text: 'Sil',
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
              const taskRef = database().ref(`operations/tasks/${taskId}`);
              await taskRef.remove();
              
              Alert.alert('Başarılı', 'Görev başarıyla silindi.');
              loadTasks(); // Listeyi yenile
            } catch (error) {
              console.error('Görev silme hatası:', error);
              Alert.alert('Hata', 'Görev silinirken bir hata oluştu.');
            } finally {
              setLoading(false);
            }
          },
        },
      ],
    );
  };

  const filterTasks = () => {
    const currentTasks = activeTab === 'active' ? tasks : taskHistory;
    
    return currentTasks.filter(task => {
      const locationMatch = searchLocation
        ? task.location.toLowerCase().includes(searchLocation.toLowerCase())
        : true;
      const priorityMatch = searchPriority
        ? task.priority === searchPriority
        : true;
      return locationMatch && priorityMatch;
    });
  };

  const getPriorityColor = (priority) => {
    if (priority.includes('Acil') || priority.includes('Kritik')) return '#D32F2F';
    if (priority.includes('Yüksek')) return '#FF9800';
    if (priority.includes('Orta')) return '#2196F3';
    return '#4CAF50';
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Tarih belirtilmemiş';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('tr-TR');
  };

  const renderTaskItem = ({ item }) => (
    <View style={styles.taskItem}>
      <View style={styles.taskHeader}>
        <View style={styles.taskTitleContainer}>
          <Text style={styles.taskTitle}>{item.title}</Text>
          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}>
            <Text style={styles.priorityText}>{item.priority}</Text>
          </View>
        </View>
        <View style={styles.taskActions}>
          {activeTab === 'active' && (
            <TouchableOpacity
              onPress={() => handleCompleteTask(item.id)}
              style={[styles.actionButton, styles.completeButton]}
            >
              <Ionicons name="checkmark-circle-outline" size={24} color="#4CAF50" />
            </TouchableOpacity>
          )}
          <TouchableOpacity
            onPress={() => {
              setSelectedTask(item);
              setEditModalVisible(true);
            }}
            style={styles.actionButton}
          >
            <Ionicons name="create-outline" size={24} color="#2196F3" />
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => handleDeleteTask(item.id)}
            style={styles.actionButton}
          >
            <Ionicons name="trash-outline" size={24} color="#D32F2F" />
          </TouchableOpacity>
        </View>
      </View>
      
      <Text style={styles.taskLocation}>📍 {item.location}</Text>
      <Text style={styles.taskDetails}>{item.details}</Text>
      
      {item.duration && (
        <Text style={styles.taskDuration}>⏱️ Süre: {item.duration}</Text>
      )}
      
      {item.team && (
        <Text style={styles.taskTeam}>👥 Ekip: {item.team}</Text>
      )}
      
      <Text style={styles.taskDate}>
        📅 Oluşturulma: {formatDate(item.created_at)}
      </Text>
      
      {item.completed_at && (
        <Text style={styles.taskCompletedDate}>
          ✅ Tamamlanma: {formatDate(item.completed_at)}
        </Text>
      )}
    </View>
  );

  const renderEmptyList = () => (
    <View style={styles.emptyListContainer}>
      <Ionicons name="list-outline" size={60} color="#ccc" />
      <Text style={styles.emptyListText}>
        {activeTab === 'active' ? 'Henüz aktif görev bulunmuyor' : 'Henüz tamamlanmış görev bulunmuyor'}
      </Text>
      <Text style={styles.emptyListSubText}>
        {activeTab === 'active' 
          ? 'Yeni bir görev eklemek için sağ üstteki "Yeni Görev" butonunu kullanın'
          : 'Tamamlanan görevler burada görünecek'
        }
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={[styles.safeArea, { marginBottom: insets.bottom }]}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#D32F2F" />
          <Text style={styles.loadingText}>İşlem yapılıyor...</Text>
        </View>
      )}
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color="white" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Görevler</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setModalVisible(true)}
            disabled={loading}
          >
            <Ionicons name="add" size={24} color="white" />
            <Text style={styles.addButtonText}>Yeni Görev</Text>
          </TouchableOpacity>
        </View>

        {/* Tab Navigation */}
        <View style={styles.tabContainer}>
          <TouchableOpacity 
            style={[styles.tabButton, activeTab === 'active' && styles.activeTabButton]}
            onPress={() => setActiveTab('active')}
          >
            <Ionicons 
              name="list" 
              size={20} 
              color={activeTab === 'active' ? '#fff' : '#666'} 
              style={styles.tabIcon}
            />
            <Text style={[styles.tabText, activeTab === 'active' && styles.activeTabText]}>
              Aktif Görevler
            </Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.tabButton, activeTab === 'history' && styles.activeTabButton]}
            onPress={() => setActiveTab('history')}
          >
            <Ionicons 
              name="checkmark-circle" 
              size={20} 
              color={activeTab === 'history' ? '#fff' : '#666'} 
              style={styles.tabIcon}
            />
            <Text style={[styles.tabText, activeTab === 'history' && styles.activeTabText]}>
              Tamamlanan Görevler
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.filterContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Konum Ara"
            placeholderTextColor="#999"
            value={searchLocation}
            onChangeText={setSearchLocation}
            autoCorrect={false}
            spellCheck={false}
            autoCapitalize="none"
            keyboardType="default"
            returnKeyType="search"
            {...(Platform.OS === 'ios' && {
              clearButtonMode: 'while-editing',
            })}
          />

          <View style={styles.priorityPickerContainer}>
            <Picker
              selectedValue={searchPriority}
              onValueChange={setSearchPriority}
              style={styles.priorityPicker}
              mode="dropdown"
            >
              <Picker.Item label="Tüm Öncelikler" value="" color="#999" />
              {priorityLevels.map(priority => (
                <Picker.Item
                  key={priority.value}
                  label={priority.label}
                  value={priority.value}
                  color="#999"
                />
              ))}
            </Picker>
          </View>
        </View>

        <FlatList
          data={filterTasks()}
          renderItem={renderTaskItem}
          keyExtractor={item => item.id}
          style={styles.list}
          contentContainerStyle={filterTasks().length === 0 ? {flex: 1} : {paddingBottom: 20}}
          ListEmptyComponent={renderEmptyList}
          refreshing={loading}
          onRefresh={loadTasks}
        />

        {/* Yeni Görev Modalı */}
        <Modal
          visible={modalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setModalVisible(false)}
        >
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.modalContainer}
          >
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Yeni Görev</Text>
                <TouchableOpacity onPress={() => setModalVisible(false)}>
                  <Ionicons name="close" size={24} color="#333" />
                </TouchableOpacity>
              </View>
              
              <ScrollView style={styles.modalScrollView}>
                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Görev Başlığı</Text>
                  <TextInput
                    style={styles.input}
                    value={newTask.title}
                    onChangeText={text => setNewTask({...newTask, title: text})}
                    placeholder="Görev başlığını giriniz..."
                    placeholderTextColor="#999"
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="default"
                    returnKeyType="next"
                    {...(Platform.OS === 'ios' && {
                      clearButtonMode: 'while-editing',
                    })}
                  />
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Konum</Text>
                  <TextInput
                    style={styles.input}
                    value={newTask.location}
                    onChangeText={text => setNewTask({...newTask, location: text})}
                    placeholder="Görev konumunu giriniz..."
                    placeholderTextColor="#999"
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="default"
                    returnKeyType="next"
                    {...(Platform.OS === 'ios' && {
                      clearButtonMode: 'while-editing',
                    })}
                  />
                </View>

                <View style={styles.pickerContainer}>
                  <Text style={styles.inputLabel}>Öncelik</Text>
                  <View style={styles.pickerWrapper}>
                    <Picker
                      selectedValue={newTask.priority}
                      onValueChange={value => setNewTask({...newTask, priority: value})}
                      style={styles.picker}
                      mode="dropdown"
                    >
                      {priorityLevels.map(priority => (
                        <Picker.Item
                          key={priority.value}
                          label={priority.label}
                          value={priority.value}
                          color="#999"
                        />
                      ))}
                    </Picker>
                  </View>
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Süre (Saat)</Text>
                  <TextInput
                    style={styles.input}
                    value={newTask.duration}
                    onChangeText={text => setNewTask({...newTask, duration: text})}
                    placeholder="Tahmini süreyi giriniz..."
                    placeholderTextColor="#999"
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="numeric"
                    returnKeyType="next"
                    {...(Platform.OS === 'ios' && {
                      clearButtonMode: 'while-editing',
                    })}
                  />
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Detaylar</Text>
                  <TextInput
                    style={[styles.input, styles.textArea]}
                    value={newTask.details}
                    onChangeText={text => setNewTask({...newTask, details: text})}
                    placeholder="Görev detaylarını giriniz..."
                    placeholderTextColor="#999"
                    multiline
                    numberOfLines={4}
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="default"
                    returnKeyType="default"
                    blurOnSubmit={false}
                  />
                </View>

                <View style={styles.modalButtons}>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.cancelButton]}
                    onPress={() => setModalVisible(false)}
                    disabled={loading}
                  >
                    <Text style={styles.modalButtonText}>İptal</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.saveButton, loading && styles.disabledButton]}
                    onPress={handleAddTask}
                    disabled={loading}
                  >
                    {loading ? (
                      <ActivityIndicator size="small" color="white" />
                    ) : (
                    <Text style={styles.modalButtonText}>Kaydet</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </ScrollView>
            </View>
          </KeyboardAvoidingView>
        </Modal>

        {/* Düzenleme Modalı */}
        <Modal
          visible={editModalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setEditModalVisible(false)}
        >
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.modalContainer}
          >
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Görevi Düzenle</Text>
                <TouchableOpacity onPress={() => setEditModalVisible(false)}>
                  <Ionicons name="close" size={24} color="#333" />
                </TouchableOpacity>
              </View>
              
              <ScrollView style={styles.modalScrollView}>
                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Görev Başlığı</Text>
                  <TextInput
                    style={styles.input}
                    value={selectedTask?.title || ''}
                    onChangeText={text => setSelectedTask({...selectedTask, title: text})}
                    placeholder="Görev başlığını giriniz..."
                    placeholderTextColor="#999"
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="default"
                    returnKeyType="next"
                    {...(Platform.OS === 'ios' && {
                      clearButtonMode: 'while-editing',
                    })}
                  />
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Konum</Text>
                  <TextInput
                    style={styles.input}
                    value={selectedTask?.location || ''}
                    onChangeText={text => setSelectedTask({...selectedTask, location: text})}
                    placeholder="Görev konumunu giriniz..."
                    placeholderTextColor="#999"
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="default"
                    returnKeyType="next"
                    {...(Platform.OS === 'ios' && {
                      clearButtonMode: 'while-editing',
                    })}
                  />
                </View>

                <View style={styles.pickerContainer}>
                  <Text style={styles.inputLabel}>Öncelik</Text>
                  <View style={styles.pickerWrapper}>
                    <Picker
                      selectedValue={selectedTask?.priority}
                      onValueChange={value => setSelectedTask({...selectedTask, priority: value})}
                      style={styles.picker}
                      mode="dropdown"
                    >
                      {priorityLevels.map(priority => (
                        <Picker.Item
                          key={priority.value}
                          label={priority.label}
                          value={priority.value}
                          color="#999"
                        />
                      ))}
                    </Picker>
                  </View>
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Süre (Saat)</Text>
                  <TextInput
                    style={styles.input}
                    value={selectedTask?.duration || ''}
                    onChangeText={text => setSelectedTask({...selectedTask, duration: text})}
                    placeholder="Tahmini süreyi giriniz..."
                    placeholderTextColor="#999"
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="numeric"
                    returnKeyType="next"
                    {...(Platform.OS === 'ios' && {
                      clearButtonMode: 'while-editing',
                    })}
                  />
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>Detaylar</Text>
                  <TextInput
                    style={[styles.input, styles.textArea]}
                    value={selectedTask?.details || ''}
                    onChangeText={text => setSelectedTask({...selectedTask, details: text})}
                    placeholder="Görev detaylarını giriniz..."
                    placeholderTextColor="#999"
                    multiline
                    numberOfLines={4}
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    keyboardType="default"
                    returnKeyType="default"
                    blurOnSubmit={false}
                  />
                </View>

                <View style={styles.modalButtons}>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.cancelButton]}
                    onPress={() => setEditModalVisible(false)}
                    disabled={loading}
                  >
                    <Text style={styles.modalButtonText}>İptal</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.saveButton, loading && styles.disabledButton]}
                    onPress={handleUpdateTask}
                    disabled={loading}
                  >
                    {loading ? (
                      <ActivityIndicator size="small" color="white" />
                    ) : (
                    <Text style={styles.modalButtonText}>Güncelle</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </ScrollView>
            </View>
          </KeyboardAvoidingView>
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
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    zIndex: 1000,
    position: 'relative',
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
  tabContainer: {
    flexDirection: 'row',
    marginHorizontal: 15,
    marginTop: 20,
    marginBottom: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 15,
    padding: 4,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 12,
  },
  activeTabButton: {
    backgroundColor: '#D32F2F',
    shadowColor: '#D32F2F',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  tabIcon: {
    marginRight: 6,
  },
  tabText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  activeTabText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  filterContainer: {
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    zIndex: 999,
    position: 'relative',
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    backgroundColor: '#fafafa',
    color: 'black',
  },
  priorityPickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#fafafa',
  },
  priorityPicker: {
    height: 50,
    color: '#black',
  },
  list: {
    flex: 1,
    paddingTop: 8,
  },
  taskItem: {
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
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  taskTitleContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  taskTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginLeft: 8,
  },
  priorityText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  taskActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    padding: 4,
    marginLeft: 8,
  },
  completeButton: {
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
    borderRadius: 4,
  },
  taskLocation: {
    color: '#666',
    marginBottom: 4,
    fontWeight: '500',
  },
  taskDetails: {
    marginBottom: 8,
    color: '#333',
    lineHeight: 20,
  },
  taskDuration: {
    color: '#666',
    marginBottom: 4,
    fontSize: 12,
  },
  taskTeam: {
    color: '#666',
    marginBottom: 4,
    fontSize: 12,
  },
  taskDate: {
    color: '#666',
    fontSize: 12,
    marginTop: 4,
  },
  taskCompletedDate: {
    color: '#4CAF50',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 2,
  },
  emptyListContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyListText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginTop: 10,
  },
  emptyListSubText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    margin: 20,
    borderRadius: 12,
    maxHeight: '90%',
    overflow: 'hidden',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  modalScrollView: {
    padding: 16,
    maxHeight: '100%',
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 16,
    marginBottom: 8,
    color: '#333',
    fontWeight: '500',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fafafa',
    color: 'black',
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#fafafa',
  },
  picker: {
    height: 50,
    color: '#black',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 8,
  },
  cancelButton: {
    backgroundColor: '#f5f5f5',
  },
  saveButton: {
    backgroundColor: '#4CAF50',
  },
  modalButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  },
  loadingText: {
    color: 'white',
    marginTop: 10,
    fontSize: 16,
  },
  disabledButton: {
    opacity: 0.7,
  },
});

export default Tasks; 