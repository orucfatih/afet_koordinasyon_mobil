import { Pressable, StyleSheet, Text, View } from 'react-native'
import React from 'react'
import {CustomButton, Loading} from '../components/index.js'
import { useDispatch, useSelector } from 'react-redux'
import { logout } from '../redux/userSlice'

const TemporaryHome = ({navigation}) => {

  const dispatch = useDispatch()

  const {isLoading} = useSelector(state=>state.user)

   //LOGOUT
   const handleLogout = () => {
    dispatch(logout())
  }

  if(isLoading){
    return <Loading/>
  }

  return (
    <View style={styles.container}>
      <CustomButton
        title={"Go to Profile Page"}
        onPress={()=> navigation.navigate("ProfilePage")}/>
        <CustomButton
        title={"Go to Home Page"}
        onPress={()=> navigation.navigate("HomePage")}/>
        <CustomButton title={"Logout"} onPress={handleLogout}/>
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