import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { HomePage2, UnderDebrisScreen, Report, Missing, Request, Tasks } from '../screens/index.js'
import { ViewAll,Horn } from '../components/index.js'
import CameraScreen from '../screens/CameraScreen'
import İnformation from '../components/İnformation'
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

const StaffStack = () => {
  return (
    <Stack.Navigator
      initialRouteName='HomePage2'
      screenOptions={{ headerShown: false }}>

      <Stack.Screen name='HomePage2' component={HomePage2} />
      <Stack.Screen name='ViewAll' component={ViewAll} />
      <Stack.Screen name='Camera' component={CameraScreen} />
      <Stack.Screen name='UnderDebris' component={UnderDebrisScreen} />
      <Stack.Screen name='Horn' component={Horn} />
      <Stack.Screen name='Report' component={Report} />
      <Stack.Screen name='Tasks' component={Tasks} />
      <Stack.Screen name='Missing' component={Missing} />
      <Stack.Screen name='Request' component={Request} />
      <Stack.Screen name='İnformation' component={İnformation} />

    </Stack.Navigator>
  )
}

export default StaffStack

const styles = StyleSheet.create({})