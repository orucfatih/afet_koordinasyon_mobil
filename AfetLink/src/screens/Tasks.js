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
  const [selectedTask, setSelectedTask] = useState(null);
  const [searchLocation, setSearchLocation] = useState('');
  const [searchPriority, setSearchPriority] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'history'
  
  // Görev tamamlama/geri bildirim modalı için state'ler
  const [taskActionModalVisible, setTaskActionModalVisible] = useState(false);
  const [taskActionType, setTaskActionType] = useState(''); // 'complete' veya 'feedback'
  const [taskActionComment, setTaskActionComment] = useState('');

  const [userTeams, setUserTeams] = useState([]);
  const [teamsData, setTeamsData] = useState({});

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
    if (!authLoading && user) {
      loadUserTeams();
    }
  }, [authLoading, user]);

  const loadUserTeams = async () => {
    // Kullanıcının ekiplerini bul
    const teamsRef = database().ref('operations/teams');
    const teamsSnapshot = await teamsRef.once('value');
    const teamsData = teamsSnapshot.val();
    if (teamsData) {
      const userTeamIds = Object.keys(teamsData).filter(teamKey => {
        const team = teamsData[teamKey];
        return team.members && Array.isArray(team.members) && team.members.some(member => member.email && member.email.toLowerCase() === user.email.toLowerCase());
      });
      setUserTeams(userTeamIds);
      setTeamsData(teamsData);
      loadTasks(userTeamIds);
    } else {
      setUserTeams([]);
      setTeamsData({});
      loadTasks([]);
    }
  };

  const loadTasks = async (userTeamIds = userTeams) => {
    if (!user) return;
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
        // Sadece kullanıcının ekiplerine atanmış görevleri filtrele
        const filteredTasks = tasksArray.filter(task => userTeamIds.includes(task.team_id));
        setTasks(filteredTasks);
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
        // Sadece kullanıcının ekiplerine atanmış tamamlanan görevleri filtrele
        const filteredHistory = taskHistoryArray.filter(task => userTeamIds.includes(task.team_id));
        setTaskHistory(filteredHistory);
      }
    } catch (error) {
      console.error('Görevler yüklenirken hata:', error);
      Alert.alert('Hata', 'Görevler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleTaskAction = (task, actionType) => {
    setSelectedTask(task);
    setTaskActionType(actionType);
    setTaskActionComment('');
    setTaskActionModalVisible(true);
  };

  const submitTaskAction = async () => {
    if (!selectedTask) return;

    setLoading(true);

    try {
      if (taskActionType === 'complete') {
        // Görevi tamamlandı olarak işaretle
        const taskRef = database().ref(`operations/tasks/${selectedTask.id}`);
        const taskSnapshot = await taskRef.once('value');
        const taskData = taskSnapshot.val();
        
        if (taskData) {
          // Görevi task_history'ye taşı
          const taskHistoryRef = database().ref(`operations/task_history/${selectedTask.id}`);
          const completedTask = {
            ...taskData,
            status: 'completed',
            completed_at: Date.now() / 1000,
            updated_at: Date.now() / 1000,
            completion_comment: taskActionComment || null
          };
          
          await taskHistoryRef.set(completedTask);
          
          // Görevi tasks'tan sil
          await taskRef.remove();
          
          Alert.alert('Başarılı', 'Görev tamamlandı olarak işaretlendi.');
        }
      } else if (taskActionType === 'feedback') {
        // Görev için geri bildirim ekle
        const taskRef = database().ref(`operations/tasks/${selectedTask.id}`);
        const updatedTask = {
          ...selectedTask,
          feedback: taskActionComment,
          feedback_at: Date.now() / 1000,
          updated_at: Date.now() / 1000
        };
        
        await taskRef.update(updatedTask);
        
        Alert.alert('Başarılı', 'Geri bildirim başarıyla eklendi.');
      }
      
      setTaskActionModalVisible(false);
      setSelectedTask(null);
      setTaskActionComment('');
      loadTasks(); // Listeyi yenile
      
    } catch (error) {
      console.error('İşlem hatası:', error);
      Alert.alert('Hata', 'İşlem sırasında bir hata oluştu.');
    } finally {
      setLoading(false);
    }
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
            <>
              <TouchableOpacity
                onPress={() => handleTaskAction(item, 'complete')}
                style={[styles.actionButton, styles.completeButton]}
              >
                <Ionicons name="checkmark-circle-outline" size={24} color="#4CAF50" />
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => handleTaskAction(item, 'feedback')}
                style={[styles.actionButton, styles.feedbackButton]}
              >
                <Ionicons name="chatbubble-outline" size={24} color="#FF9800" />
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
      
      <Text style={styles.taskLocation}>📍 {item.location}</Text>
      <Text style={styles.taskDetails}>{item.details}</Text>
      
      {item.duration && (
        <Text style={styles.taskDuration}>⏱️ Süre: {item.duration}</Text>
      )}
      
      {item.team_id && teamsData[item.team_id] && (
        <Text style={styles.taskTeam}>👥 Ekip: {teamsData[item.team_id].name}</Text>
      )}
      
      <Text style={styles.taskDate}>
        📅 Oluşturulma: {formatDate(item.created_at)}
      </Text>
      
      {item.feedback && (
        <View style={styles.feedbackContainer}>
          <Text style={styles.feedbackLabel}>💬 Geri Bildirim:</Text>
          <Text style={styles.feedbackText}>{item.feedback}</Text>
          <Text style={styles.feedbackDate}>
            📅 {formatDate(item.feedback_at)}
          </Text>
        </View>
      )}
      
      {item.completed_at && (
        <Text style={styles.taskCompletedDate}>
          ✅ Tamamlanma: {formatDate(item.completed_at)}
        </Text>
      )}
      
      {item.completion_comment && (
        <View style={styles.completionCommentContainer}>
          <Text style={styles.completionCommentLabel}>📝 Tamamlama Notu:</Text>
          <Text style={styles.completionCommentText}>{item.completion_comment}</Text>
        </View>
      )}
    </View>
  );

  const renderEmptyList = () => (
    <View style={styles.emptyListContainer}>
      <Ionicons name="list-outline" size={60} color="#ccc" />
      <Text style={styles.emptyListText}>
        {activeTab === 'active' ? 'Henüz size atanan görev bulunmuyor' : 'Henüz tamamlanmış görev bulunmuyor'}
      </Text>
      <Text style={styles.emptyListSubText}>
        {activeTab === 'active' 
          ? 'Size atanan görevler burada görünecek'
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
          <Text style={styles.headerTitle}>Görevlerim</Text>
          <View style={styles.headerSpacer} />
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

        {/* Görev İşlem Modalı */}
        <Modal
          visible={taskActionModalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setTaskActionModalVisible(false)}
        >
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.modalContainer}
          >
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>
                  {taskActionType === 'complete' ? 'Görevi Tamamla' : 'Geri Bildirim Ekle'}
                </Text>
                <TouchableOpacity onPress={() => setTaskActionModalVisible(false)}>
                  <Ionicons name="close" size={24} color="#333" />
                </TouchableOpacity>
              </View>
              
              <ScrollView style={styles.modalScrollView}>
                <View style={styles.taskInfoContainer}>
                  <Text style={styles.taskInfoTitle}>{selectedTask?.title}</Text>
                  <Text style={styles.taskInfoLocation}>📍 {selectedTask?.location}</Text>
                </View>

                <View style={styles.inputContainer}>
                  <Text style={styles.inputLabel}>
                    {taskActionType === 'complete' ? 'Tamamlama Notu (İsteğe bağlı)' : 'Geri Bildirim'}
                  </Text>
                  <TextInput
                    style={[styles.input, styles.textArea]}
                    value={taskActionComment}
                    onChangeText={setTaskActionComment}
                    placeholder={
                      taskActionType === 'complete' 
                        ? 'Görev tamamlanırken eklemek istediğiniz notları yazın...'
                        : 'Görev hakkında geri bildiriminizi yazın...'
                    }
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
                    onPress={() => setTaskActionModalVisible(false)}
                    disabled={loading}
                  >
                    <Text style={styles.modalButtonText}>İptal</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.modalButton, styles.saveButton, loading && styles.disabledButton]}
                    onPress={submitTaskAction}
                    disabled={loading}
                  >
                    {loading ? (
                      <ActivityIndicator size="small" color="white" />
                    ) : (
                      <Text style={styles.modalButtonText}>
                        {taskActionType === 'complete' ? 'Tamamla' : 'Gönder'}
                      </Text>
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
  headerSpacer: {
    width: 40,
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
  feedbackButton: {
    backgroundColor: 'rgba(255, 152, 0, 0.1)',
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
  feedbackContainer: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#FFF3E0',
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#FF9800',
  },
  feedbackLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FF9800',
    marginBottom: 4,
  },
  feedbackText: {
    fontSize: 12,
    color: '#333',
    lineHeight: 16,
  },
  feedbackDate: {
    fontSize: 10,
    color: '#666',
    marginTop: 4,
  },
  completionCommentContainer: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#E8F5E8',
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#4CAF50',
  },
  completionCommentLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 4,
  },
  completionCommentText: {
    fontSize: 12,
    color: '#333',
    lineHeight: 16,
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
  taskInfoContainer: {
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  taskInfoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  taskInfoLocation: {
    fontSize: 14,
    color: '#666',
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