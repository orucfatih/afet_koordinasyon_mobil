import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector } from 'react-redux';
import AuthStack from './AuthStack'; // AuthStack'ı burada kullanmak için import edin
import UserStack from './UserStack'; // UserStack'ı burada kullanmak için import edin


// Ana navigatör (RootNavigation) için Stack oluşturuluyor
const Stack = createStackNavigator();

const RootNavigation = () => {

  const {isAuth} = useSelector((state) => state.user)

  return (
    <NavigationContainer>

      {isAuth ? <UserStack/> : <AuthStack/>}

    </NavigationContainer>
  );
};

export default RootNavigation;
