import { StyleSheet, Text, View, TouchableOpacity, ScrollView, Image, StatusBar, SafeAreaView, Platform } from 'react-native'
import React from 'react'
import Ionicons from 'react-native-vector-icons/Ionicons' // İkon kütüphanesini içe aktar

const Info = ({ setInfo }) => {
  return (
    <View style={styles.mainContainer}>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#2D2D2D"
        translucent={true}
      />
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.topBar}>
          <Image source={require('../../assets/images/deneme.png')} style={styles.logoImage} />
          <TouchableOpacity style={styles.backButton} onPress={() => setInfo(false)}>
            <Ionicons name="close" size={24} color="#fff" />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.container}>
          <View style={styles.content}>
            <Text>İçerik Eklenecek</Text>
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
    backgroundColor: '#2D2D2D',
  },
  safeArea: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content: {
    alignItems: "center",
    justifyContent: "center",
    height: 500,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2D2D2D',
    paddingVertical: 25,
    borderTopWidth: 2,
    borderTopColor: '#444',
    elevation: 5,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    zIndex: 10,
    position: 'relative',
    minHeight: 100,
  },
  backButton: {
    position: 'absolute',
    right: 20,
    top: 35,
  },
  logoImage: {
    width: 50,
    height: 50,
    position: 'absolute',
    left: 30,
  },
})
