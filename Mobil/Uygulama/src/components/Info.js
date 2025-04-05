import { StyleSheet, Text, View, TouchableOpacity, ScrollView, Image } from 'react-native'
import React from 'react'
import Ionicons from 'react-native-vector-icons/Ionicons' // İkon kütüphanesini içe aktar

const Info = ({ setInfo }) => {
  return (
    <ScrollView style={styles.container}>
      
      <View style={styles.topBar}>
        <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
        <TouchableOpacity style={styles.backButton} onPress={() => setInfo(false)}>
          <Ionicons name="close" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        <Text>İçerik Eklenecek</Text>
      </View>

    </ScrollView>
  )
}

export default Info

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content:{
    alignItems:"center",
    justifyContent:"center",
    height:500,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#2D2D2D', // Koyu arka plan
    paddingVertical: 15,
    borderTopWidth: 2,
    borderTopColor: '#444',
    marginHorizontal: 0,
    elevation: 5,  // Gölgeleme efekti
    borderBottomLeftRadius: 20, // Üst sol köşe radius
    borderBottomRightRadius: 20, // Üst sağ köşe radius
  },
  backButton: {
    top: 20,
    right: 40,
  },
  logoImage: {
    width: 50,
    top: 5,
    left: 30,
    height: 50,
  },
})
