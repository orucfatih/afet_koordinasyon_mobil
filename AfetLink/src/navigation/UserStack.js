import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { HomePage, UnderDebrisScreen, Missing } from '../screens/index.js'
import { ViewAll,Horn } from '../components/index.js'
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
      <Stack.Screen name='UnderDebris' component={UnderDebrisScreen} />
      <Stack.Screen name='Horn' component={Horn} />
      <Stack.Screen name='Missing' component={Missing} />

    </Stack.Navigator>
  )
}

export default UserStack

const styles = StyleSheet.create({})