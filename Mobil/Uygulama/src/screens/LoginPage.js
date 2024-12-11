import {
    StyleSheet, 
    Text, 
    View,
    Image } from 'react-native';
  
import React, { useState } from 'react';
import { Loading, CustomTextInput, CustomButton } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import {setIsLoading,} from '../redux/userSlice.js';
import { login } from '../redux/userSlice.js';
  
  
const LoginPage = ({navigation}) => {

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    //useSlice içindeki verilerin okunması
    const {isLoading} = useSelector((state) => state.user)

    //useSlice içerisindeki reducer yapılarını kullanma veya veri gönderme
    const dispatch = useDispatch()


    return (
      <View style={styles.container}>
      
      <Text style={{fontSize:30,fontWeight:"bold"}}>Welcome</Text>

      <Image
      style={[styles.image,
            {marginBottom:"20",marginTop:"10"}]}

      source={require("../../assets/images/login.png")}
      />
        <View style={{width:"70%",}}>

        <Text>Email</Text>

        <CustomTextInput
          secureTextEntry={false}
          placeholder='Enter Your Email'
          onChangeText={(email) => setEmail(email)}
          value={email}
        />

        <Text>Password</Text>

        <CustomTextInput
          secureTextEntry={true}
          placeholder='Enter Your Password'
          onChangeText={(password)=> setPassword(password)}
          value={password}
        />
        </View>
        

          <CustomButton
            onPress={()=> dispatch(login({email, password}))}
            title="Login"/>

          <CustomButton
            onPress={()=> navigation.navigate("SignUp")}
            title="Sign Up"/>

          {isLoading ? <Loading changeIsLoading={()=> dispatch(setIsLoading(false))}/> : null}
  
      </View>
    );
  }

  export default LoginPage
  
  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: '#fff',
      alignItems: 'center',
      justifyContent: 'center',
    },
    image: {
      width:"100",
      height:"100"
    },
  
  });