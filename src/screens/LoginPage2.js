import {
    StyleSheet, 
    Text, 
    View,
    Image } from 'react-native';
  
import React, { useState, useEffect } from 'react';
import { Loading, CustomTextInput, CustomButton } from '../components/index.js';
import { useSelector, useDispatch } from 'react-redux';
import {setIsLoading,} from '../redux/userSlice.js';
import { login, autoLogin } from '../redux/userSlice.js';
  
  
const LoginPage = ({navigation}) => {

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    //Auto Login
    useEffect(() => {
      dispatch(autoLogin())
    }, [])
    


    //useSlice içindeki verilerin okunması
    const {isLoading} = useSelector((state) => state.user)

    //useSlice içerisindeki reducer yapılarını kullanma veya veri gönderme
    const dispatch = useDispatch()


    return (
      <View style={styles.container}>
      
      <Text style={{fontSize:30,fontWeight:"bold"}}>Hoşgeldiniz</Text>

      <Image
      style={[styles.image,
            {marginBottom:"20",marginTop:"10"}]}
            source={require("../../assets/images/login.png")}/>

        <View style={{width:"70%",}}>

          <Text>Email</Text>

          <CustomTextInput
            secureTextEntry={false}
            placeholder='Email Adresinizi Girin'
            onChangeText={(email) => setEmail(email)}
            value={email}/>

          <Text>Şifre</Text>

          <CustomTextInput
            secureTextEntry={true}
            placeholder='Şifre Girin'
            onChangeText={(password)=> setPassword(password)}
            value={password}/>

        </View>
        
            <CustomButton
              onPress={()=> dispatch(login({email, password}))}
              title="Giriş Yap"/>

            <CustomButton
              onPress={()=> navigation.navigate("SignUpPage")}
              title="Kaydol"/>

          {isLoading ? <Loading changeIsLoading={()=> dispatch(setIsLoading(false))}/> : null}
  
      </View>
    );
  }

  export default LoginPage
  
  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: 'white',
      alignItems: 'center',
      justifyContent: 'center',
    },
    image: {
      width:"100",
      height:"100"
    },
  
  });