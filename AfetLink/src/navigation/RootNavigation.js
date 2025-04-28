import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector, useDispatch } from 'react-redux';
import AuthStack from './AuthStack';
import UserStack from './UserStack';
import StaffStack from './StaffStack'; // Personel için ayrı Stack
import { autoLogin, staffAutoLogin } from '../redux/userSlice';

const Stack = createStackNavigator();

const RootNavigation = () => {
  const dispatch = useDispatch();
  const { isAuth, isFullyAuth } = useSelector((state) => state.user);

  useEffect(() => {
    dispatch(autoLogin());
    dispatch(staffAutoLogin());
  }, [dispatch]);

  return (
    <NavigationContainer>
      {isFullyAuth ? <StaffStack /> : isAuth ? <UserStack /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default RootNavigation;
