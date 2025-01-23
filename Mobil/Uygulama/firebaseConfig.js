import { initializeApp } from "firebase/app";
import { initializeAuth, getReactNativePersistence } from 'firebase/auth';
import ReactNativeAsyncStorage from '@react-native-async-storage/async-storage';
import { getFirestore } from "firebase/firestore";
import { getAnalytics } from "firebase/analytics";

//authentication çalışıyor ama firestore database çalışmıyor.
//firestore database kuralları değişmeli.

const firebaseConfig = {
  apiKey: "AIzaSyD9ogbozKtQyppbbJG6U8WA9D8MVfs4ZE0",
  authDomain: "afad-proje.firebaseapp.com",
  databaseURL: "https://afad-proje-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "afad-proje",
  storageBucket: "afad-proje.firebasestorage.app",
  messagingSenderId: "992617585430",
  appId: "1:992617585430:web:124b01a79f4047682a4e37",
  measurementId: "G-C6D0PWNGNJ"
  };
  
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

const auth = initializeAuth(app, {
persistence: getReactNativePersistence(ReactNativeAsyncStorage)
});

export const db = getFirestore(app);

export default app;

