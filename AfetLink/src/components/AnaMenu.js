import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/Ionicons';

const AnaMenu = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      <Image 
        source={require('../../assets/images/deneme.png')} 
        style={styles.logo}
      />
      <Text style={styles.title}>Ana Menü</Text>
      <TouchableOpacity 
        style={styles.button} 
        onPress={() => navigation.navigate('AraMenu')}
      >
        <Icon name="person" size={24} color="#333" />
        <Text style={styles.buttonText}>Vatandaş Girişi</Text>
      </TouchableOpacity>
      <TouchableOpacity 
        style={styles.button} 
        onPress={() => navigation.navigate('AraMenu2')}
      >
        <Icon name="people" size={24} color="#333" />
        <Text style={styles.buttonText}>Personel Girişi</Text>
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
  logo: {
    width: 200,
    height: 200,
    marginBottom: 50,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#333',
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

export default AnaMenu;