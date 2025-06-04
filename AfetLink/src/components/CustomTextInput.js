import { StyleSheet, Text, View, TextInput } from 'react-native'
import React from 'react'

const CustomTextInput = ({secureTextEntry,placeholder,onChangeText,value}) => {
  return (
    <TextInput 
        secureTextEntry={secureTextEntry}
        placeholder={placeholder}
        placeholderTextColor={"lightgray"}
        style={styles.textInputStyle}
        onChangeText={onChangeText}
        value={value}/>
  )
}

export default CustomTextInput

const styles = StyleSheet.create({
    textInputStyle: {
        borderBottomWidth:1,
        width:"100%",
        height:"40",
        textAlign:"center",
        color:"white",
      },
})