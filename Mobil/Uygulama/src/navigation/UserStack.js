import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { HomePage, ProfilePage, TemporaryHome } from '../screens/index.js'
import {createNativeStackNavigator} from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const UserStack = () => {
  return (
    <Stack.Navigator
        initialRouteName='TemporaryHome'
        screenOptions={{headerShown:false}}>

        <Stack.Screen name='HomePage' component={HomePage}/>
        
        <Stack.Screen name='ProfilePage' component={ProfilePage}/>

        <Stack.Screen name='TemporaryHome' component={TemporaryHome}/>

    </Stack.Navigator>
  )
}

export default UserStack

const styles = StyleSheet.create({})