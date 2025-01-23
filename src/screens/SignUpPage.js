import { StyleSheet, Text, View,Image, Pressable,} from 'react-native'
import React, {useState} from 'react'
import { CustomButton, CustomTextInput, Loading } from '../components'
import { useDispatch, useSelector } from 'react-redux'
import { register } from '../redux/userSlice'

const SignUpPage = ({navigation}) => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const dispatch= useDispatch()

    const {isLoading} = useSelector(state=>state.user)

    const signUp = () => {
      dispatch(register({email,password,name}))
    }

    if(isLoading){
      return <Loading/>
    }

    return (
      <View style={styles.container}>

        <View style={styles.signUp}>
          <Text style={{fontSize:30,fontWeight:"bold"}}>Kaydol</Text>

          <Image
              style={[styles.image,
              {marginTop:"10",marginBottom:"10"}]}
              source={require("../../assets/images/login.png")}/>
        </View>

        <View style={styles.textInput}>

            <Text>İsim</Text>
            <CustomTextInput
                secureTextEntry={false}
                placeholder='İsminizi Girin'
                onChangeText={setName}
                value={name}
            />

            <Text>Email</Text>
            <CustomTextInput
                secureTextEntry={false}
                placeholder='Email Adresinizi Girin'
                onChangeText={setEmail}
                value={email}
            />

            <Text>Şifre</Text>
            <CustomTextInput
                secureTextEntry={true}
                placeholder='Bir Şifre Oluşturun'
                onChangeText={setPassword}
                value={password}/>

        </View>

        <View style={styles.buttons}>
            <CustomButton
                onPress={signUp}
                title="Kaydol"/>

            <View style={styles.bottomText}>
                <Text style={{textAlign:"center"}}>Zaten bir hesabınız varmı? </Text>

                <Pressable onPress={()=> navigation.navigate("LoginPage")}>
                    <Text style={{fontWeight:"bold"}}>Giriş yapmak için tıklayın.</Text>
                </Pressable>
            </View>

        </View>

    </View>
    )
}

export default SignUpPage

const styles = StyleSheet.create({
  container:{
    flex:1,
    alignItems:"center",
    justifyContent:"center",
  },
  signUp:{
    flex:2,
    alignItems:"center",
    justifyContent:"flex-end",
    width:"100%",
  },
  textInput:{
    flex:1,
    justifyContent:"center",
    width:"70%",
  },
  buttons:{
    flex:2,
    alignItems:"center",
    justifyContent:"space-between",
    width:"100%",
  },
  image: {
    width:"100",
    height:"100"
  },
  bottomText:{
    marginBottom:20,
    justifyContent:"center",
    flexDirection:"row",
    alignItems:"center",
    width:"100%"
  }
})