import { StyleSheet, Text, View, ActivityIndicator, Pressable } from 'react-native'
import React from 'react'

const Loading = (props) => {
  return (
    <View style={styles.container}>
        <Pressable 
        onPress={()=> props.changeIsLoading()}
        style={[{}, styles.closeButtonContainer]}>
            <Text style={styles.closeButton}>X</Text>
        </Pressable>
        <ActivityIndicator
        size={"large"}
        />
        <Text style={styles.loadingTextStyle}>Yükleniyor</Text>
    </View>
  )
}

export default Loading

const styles = StyleSheet.create({
    container:{
        width:"100%",
        height:"100%",
        position:"absolute",
        alignItems:"center",
        justifyContent:"center",
        backgroundColor:"white",
    },

    loadingTextStyle: {
        fontWeight:"bold"
    },
    closeButton:{
        color:"black",
        fontWeight:"bold",
        textAlign:"center",
    },
    closeButtonContainer:{
        backgroundColor:"lightgray",
        width:"30",
        height:"30",
        borderRadius:30,
        alignItems:"center",
        justifyContent:"center",
        position:"absolute",
        top:"50",
        right:"15",
    }
})