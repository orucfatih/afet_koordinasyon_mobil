import { StyleSheet, Text, View } from 'react-native'
import React, {useState, useEffect} from 'react'
import { collection, addDoc, getDocs, doc, deleteDoc, updateDoc} from 'firebase/firestore'
import { db } from '../../firebaseConfig'
import CustomButton from '../components/CustomButton'
import { isAsyncThunkAction } from '@reduxjs/toolkit'



//BURADAKİ FONKSİYONLAR İLERİDE GEREKTİĞİ YERLERDE KULLANILABİLMESİ İÇİN YAZILDI


const HomePage = () => {

  //yerel hafıza
  const [data, setData] = useState([])
  const [isSaved, setIsSaved] = useState(false)

  console.log("data: ", data)

  //Her sayfaya girildiğinde çalışması sağlanıyor
  // useEffect(() => {
  //     getData()
  //   }, [isSaved])

  
  //Send data to firebase
  const sendData = async() => {
    try {
      const docRef = await addDoc(collection(db, "lessons"), {
        title: "zero to hero",
        content: "beginning",
        lesson: 95,
      });
      console.log("Document written with ID: ", docRef.id);
    } catch (e) {
      console.error("Error adding document: ", e);
    }
  }

  //Get data from firebase
  const getData = async() => {
    allData=[]
    try {
      const querySnapshot = await getDocs(collection(db, "lessons"));
    querySnapshot.forEach((doc) => {
    allData.push({...doc.data(), id: doc.id})})
    setData(allData);
    } 
    catch (error) {
      console.log(error)
    }

  }

  //Delete data
  const deleteData = async(id) => {
    try {
      await deleteDoc(doc(db, "lessons", id))
    } catch (error) {
      console.log(error)
    }
  }

  //Update Data
  const updateData = async(id) => {
    try{
      const lessonData = doc(db, "lessons", id);
      
      await updateDoc(lessonData, {
      lesson: 145}
      
      );}
    catch(error){
      console.log(error)
    }
  
  }

  return (
    <View style={styles.container}>

      {data.map((value,index)=> {
        return(
          <View key={index}>
            <Text>{index}</Text>
            <Text>{value.title}</Text>
            <Text>{value.content}</Text>
            <Text>{value.lesson}</Text>
          </View>
        )
      })}

      <CustomButton title={"Save"} onPress={()=> {sendData(),setIsSaved(isSaved===false ? true : false)}}/>

      <CustomButton title={"Get"} onPress={getData}/>

    </View>
  )
}

export default HomePage

const styles = StyleSheet.create({
    container:{
        flex:1,
        alignItems:"center",
        justifyContent:"center",
    }
})