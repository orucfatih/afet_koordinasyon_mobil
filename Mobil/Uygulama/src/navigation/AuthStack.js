import { StyleSheet, Text, View } from 'react-native';
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { AnaMenu, AraMenu, AraMenu2, ViewAll } from '../components/index.js';
import { LoginPage, LoginPage2, SignUpPage, SignUpPage2} from '../screens/index.js';

const Stack = createNativeStackNavigator();

const AuthStack = () => {
  return (
    <Stack.Navigator initialRouteName="AnaMenu" screenOptions={{ headerShown: false }}>
      <Stack.Screen
        name="AnaMenu"
        component={AnaMenu}
        options={{ headerTitle: 'Ana Menü' }}
      />
      <Stack.Screen
        name="AraMenu"
        component={AraMenu}
        options={{ headerTitle: 'Vatandaş Giriş' }}
      />
      <Stack.Screen
        name="AraMenu2"
        component={AraMenu2}
        options={{ headerTitle: 'Personel Giriş' }}
      />
      <Stack.Screen
        name="LoginPage"
        component={LoginPage}
        options={{ headerTitle: 'E-mail ile Giriş' }}
      />
      <Stack.Screen
        name="LoginPage2"
        component={LoginPage2}
        options={{ headerTitle: 'E-mail ile Giriş (Personel)' }}
      />
      <Stack.Screen
        name="SignUpPage"
        component={SignUpPage}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="SignUpPage2"
        component={SignUpPage2}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

export default AuthStack;

const styles = StyleSheet.create({});
