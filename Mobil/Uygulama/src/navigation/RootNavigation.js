import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector } from 'react-redux';
import AuthStack from './AuthStack';
import UserStack from './UserStack';
import StaffStack from './StaffStack'; // Personel için ayrı Stack

const Stack = createStackNavigator();

const RootNavigation = () => {
  
  const { isAuth, isStaffAuth } = useSelector((state) => state.user);

  return (
    <NavigationContainer>
      {isStaffAuth ? <StaffStack /> : isAuth ? <UserStack /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default RootNavigation;
