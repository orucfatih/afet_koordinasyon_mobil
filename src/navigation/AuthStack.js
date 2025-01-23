import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { LoginPage, SignUpPage,} from '../screens/index.js'
import {createNativeStackNavigator} from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const AuthStack = () => {
  return (
    <Stack.Navigator 
    initialRouteName='LoginPage'
    screenOptions={{headerShown:false}}>

        <Stack.Screen name='LoginPage' component={LoginPage}/>
        
        <Stack.Screen name='SignUpPage' component={SignUpPage}/>

    </Stack.Navigator>

  )
}

export default AuthStack

const styles = StyleSheet.create({})