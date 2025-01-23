import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AuthStack from './AuthStack'; // AuthStack'ı burada kullanmak için import edin
import UserStack from './UserStack'; // UserStack'ı burada kullanmak için import edin
import AnaMenu from '../components/AnaMenu';
import AraMenu from '../components/AraMenu';
import AraMenu2 from '../components/AraMenu2';
import LoginPage from '../screens/LoginPage';
import LoginPage2 from '../screens/LoginPage2';
import { SignUpPage } from '../screens';

// Ana navigatör (RootNavigation) için Stack oluşturuluyor
const Stack = createStackNavigator();

const RootNavigation = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="AnaMenu">
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

        {/* Nested Stack Navigators for Authentication and User */}
        <Stack.Screen
          name="AuthStack"
          component={AuthStack} // Burada AuthStack component'ini kullanabilirsiniz
          options={{ headerShown: false }} // Eğer başlık gösterilmesin isteniyorsa
        />
        
        <Stack.Screen
          name="UserStack"
          component={UserStack} // Burada UserStack component'ini kullanabilirsiniz
          options={{ headerShown: false }} // Eğer başlık gösterilmesin isteniyorsa
        />
        <Stack.Screen name="SignUpPage" component={SignUpPage}  options={{headerShown: false}}/>
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default RootNavigation;
