import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import Icon from 'react-native-vector-icons/MaterialIcons'; // İkon setini seçebilirsiniz

const SettingsScreen = () => {

  return (
    <View style={styles.screen}>
      <Icon name="settings" size={100} color="white" />
      <Text style={styles.screenText}>Ayarlar Sayfası</Text>
    </View>
  )
};

export default SettingsScreen

const styles = StyleSheet.create({
    screen: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#ff1744',
      },
      screenText: {
        color: 'white',
        fontSize: 20,
        marginTop: 10,
      },
})