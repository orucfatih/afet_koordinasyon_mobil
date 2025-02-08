import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { HomePage} from '../screens/index.js'
import {ViewAll} from '../components/index.js'
import {createNativeStackNavigator} from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const UserStack = () => {
  return (
    <Stack.Navigator
        initialRouteName='HomePage'
        screenOptions={{headerShown:false}}>

        <Stack.Screen name='HomePage' component={HomePage}/>

        <Stack.Screen name='ViewAll' component={ViewAll}/>

    </Stack.Navigator>
  )
}

export default UserStack

const styles = StyleSheet.create({})