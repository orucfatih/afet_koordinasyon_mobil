import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { HomePage,TemporaryHome } from '../screens/index.js'
import {createNativeStackNavigator} from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const UserStack = () => {
  return (
    <Stack.Navigator
        initialRouteName='HomePage'
        screenOptions={{headerShown:false}}>

        <Stack.Screen name='HomePage' component={HomePage}/>

        <Stack.Screen name='TemporaryHome' component={TemporaryHome}/>

    </Stack.Navigator>
  )
}

export default UserStack

const styles = StyleSheet.create({})