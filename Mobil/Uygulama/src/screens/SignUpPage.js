import { StyleSheet, Text, View, SafeAreaView, Image, Pressable,} from 'react-native'
import React, {useState} from 'react'
import { CustomButton, CustomTextInput } from '../components'

const SignUpPage = ({navigation}) => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    return (
    <SafeAreaView style={styles.container}>
        <View style={styles.signUp}>
          <Text style={{fontSize:30,fontWeight:"bold"}}>Sign Up</Text>

          <Image
              style={[styles.image,
              {marginTop:"10",marginBottom:"10"}]}
              source={require("../../assets/images/login.png")}/>
        </View>

        <View style={styles.textInput}>

            <Text>Name</Text>
            <CustomTextInput
                secureTextEntry={false}
                placeholder='Enter Your Name'
                onChangeText={setName}
                value={name}
            />

            <Text>Email</Text>
            <CustomTextInput
                secureTextEntry={false}
                placeholder='Enter Your Email'
                onChangeText={setEmail}
                value={email}
            />

            <Text>Password</Text>
            <CustomTextInput
                secureTextEntry={true}
                placeholder='Create Password'
                onChangeText={setPassword}
                value={password}
            />
        </View>

        <View style={styles.buttons}>
            <CustomButton
                onPress={()=> console.log(name+" "+email+" "+password)}
                title="Sign Up"/>

            <View style={styles.bottomText}>
                <Text style={{textAlign:"center"}}>Already have an account? </Text>

                <Pressable onPress={()=> navigation.navigate("Login")}>
                    <Text style={{fontWeight:"bold"}}>Login</Text>
                </Pressable>
            </View>

        </View>

    </SafeAreaView> 
    )
}

export default SignUpPage

const styles = StyleSheet.create({
  container:{
    flex:1,
    alignItems:"center",
    justifyContent:"center",
    width:"100%",
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
  textInputStyle: {
    borderBottomWidth:1,
    width:"100%",
    height:"40",
    textAlign:"center",
    color:"black",
  },
  bottomText:{
    marginBottom:20,
    justifyContent:"center",
    flexDirection:"row",
    alignItems:"center",
    width:"100%"
  }
})