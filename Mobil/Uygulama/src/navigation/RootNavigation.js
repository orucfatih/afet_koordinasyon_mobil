import React from 'react'
import {NavigationContainer} from '@react-navigation/native';
import AuthStack from './AuthStack';
import UserStack from './UserStack';
import { useSelector } from 'react-redux';
import app from '../../firebaseConfig';
//firebaseConfig burada


const RootNavigation = () => {

    const {isAuth} = useSelector((state) => state.user)

  return (
    <NavigationContainer>
        {isAuth ? <UserStack/> : <AuthStack/> }
    </NavigationContainer>
  )
}

export default RootNavigation