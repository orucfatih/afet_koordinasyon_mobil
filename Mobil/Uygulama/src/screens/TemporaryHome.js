import { Pressable, StyleSheet, Text, View } from 'react-native'
import React from 'react'
import CustomButton from '../components/CustomButton'

const TemporaryHome = ({navigation}) => {
  return (
    <View style={styles.container}>
      <CustomButton
        title={"Go to Profile Page"}
        onPress={()=> navigation.navigate("ProfilePage")}/>
        <CustomButton
        title={"Go to Home Page"}
        onPress={()=> navigation.navigate("HomePage")}/>
    </View>
  )
}

export default TemporaryHome

const styles = StyleSheet.create({
  container:{
    alignItems:"center",
    justifyContent:"center",
    flex:1,
  },
})

//burası fonksiyonel değil sadece geçici