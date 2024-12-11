import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { LoginPage, SignUpPage,} from '../screens/index.js'
import {createNativeStackNavigator} from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const AuthStack = () => {
  return (
    <Stack.Navigator 
    initialRouteName='Login'
    screenOptions={{headerShown:false}}>

        <Stack.Screen name='Login' component={LoginPage}/>
        
        <Stack.Screen name='SignUp' component={SignUpPage}/>

    </Stack.Navigator>

  )
}

export default AuthStack

const styles = StyleSheet.create({})