import { StyleSheet, Text, View, Pressable } from 'react-native'
import React from 'react'

const CustomButton = ({onPress,title}) => {
  return (
    <Pressable  
        onPress={onPress}
        style={
          ({pressed}) => [
          {backgroundColor: pressed ? "gray": "red",
          marginTop:"20",},
          styles.buttonStyle]}>
  
          <Text style={{color: "white",fontWeight:"bold"}}>{title}</Text>
        </Pressable>
  )
}

export default CustomButton

const styles = StyleSheet.create({
    buttonStyle: {
        width:"70%",
        height:"40",
        borderRadius:20,
        alignItems:"center",
        justifyContent:"center", 
      },
})