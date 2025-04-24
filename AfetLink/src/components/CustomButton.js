import { StyleSheet, Text, View, TouchableOpacity } from 'react-native'
import React from 'react'

const CustomButton = ({onPress,title}) => {
  return (
    <TouchableOpacity 
        onPress={onPress}
        style={styles.buttonStyle}>
  
          <Text style={{color: "white",fontWeight:"bold"}}>{title}</Text>
        </TouchableOpacity>
  )
}

export default CustomButton

const styles = StyleSheet.create({
    buttonStyle: {
        width:"70%",
        height:"40",
        backgroundColor:"#D32F2F",
        marginTop:20,
        borderRadius:10,
        alignItems:"center",
        justifyContent:"center", 
      },
})