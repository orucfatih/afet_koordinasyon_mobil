import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { HomePage } from '../screens/index.js'
import { ViewAll } from '../components/index.js'
import CameraScreen from '../screens/CameraScreen'
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const UserStack = () => {
  return (
    <Stack.Navigator
      initialRouteName='HomePage'
      screenOptions={{ headerShown: false }}>

      <Stack.Screen name='HomePage' component={HomePage} />
      <Stack.Screen name='ViewAll' component={ViewAll} />
      <Stack.Screen name='Camera' component={CameraScreen} />

    </Stack.Navigator>
  )
}

export default UserStack

const styles = StyleSheet.create({})