import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/Ionicons';

const AraMenu2 = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.button} 
        onPress={() => navigation.navigate('LoginPage2')}
      >
        <Icon name="person" size={24} color="#333" />
        <Text style={styles.buttonText}>Personel Girişi</Text>
      </TouchableOpacity>
      <TouchableOpacity 
        style={styles.button} 
        onPress={() => navigation.navigate('SignUpPage2')}
      >
        <Icon name="person-add" size={24} color="#333" />
        <Text style={styles.buttonText}>Personel Kaydı</Text>
      </TouchableOpacity>
    </View>
  );
};

export default AraMenu2;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    padding: 15,
    borderRadius: 10,
    marginVertical: 10,
    width: '80%',
  },
  buttonText: {
    marginLeft: 10,
    fontSize: 16,
    color: '#333',
  },
});
