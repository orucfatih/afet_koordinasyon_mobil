import { createSlice,createAsyncThunk } from "@reduxjs/toolkit";
import { getAuth, createUserWithEmailAndPassword, 
    updatePassword ,updateProfile, 
    EmailAuthProvider, reauthenticateWithCredential, 
    signInWithEmailAndPassword, signOut, sendEmailVerification} from "firebase/auth";
import AsyncStorage from "@react-native-async-storage/async-storage";

//iki parametre alan ve asenkron yapı kullanan giriş yapma fonksiyonu
export const login = createAsyncThunk('user/login', async({email,password}, {rejectWithValue})=> {
    try {
        //auth nasıl çalışıyor bilmiyorum
        const auth =getAuth();
        const userCredantial = await signInWithEmailAndPassword(auth, email, password)

        const user = userCredantial.user;
        const token = user.stsTokenManager.accessToken;

        const userData = {
            token,
            user: user,
        }

        await AsyncStorage.setItem("userToken", token)

        return userData;

    } catch (error) {
        console.log('Hata kodu:', error.code); // Hata kodunu konsola yazdır
  
        // Hata türüne göre mesaj döndür
        if (error.code === 'auth/user-not-found') {
            return rejectWithValue('Kullanıcı bulunamadı. Lütfen kayıt olun.');
        } else if (error.code === 'auth/wrong-password' || error.code === 'auth/invalid-credential') {
            return rejectWithValue('Hatalı kullanıcı adı veya şifre. Lütfen tekrar deneyin.');
        } else if (error.code === 'auth/too-many-requests') {
            return rejectWithValue('Çok fazla giriş denemesi. Daha sonra tekrar deneyin.');
        } else {
            return rejectWithValue(`Bilinmeyen hata: ${error.message}`); // Daha detaylı bir mesaj döndür
        }
    }
})
  

//Şifre Değiştirme
export const updateCipher = createAsyncThunk(
    'user/updatePassword',
    async ({ oldPassword, newPassword, confirmPassword }, { rejectWithValue }) => {
      const auth = getAuth();
      const user = auth.currentUser;
  
      if (!user) {
        return rejectWithValue('Kullanıcı oturumu açık değil.');
      }
  
      if (newPassword !== confirmPassword) {
        return rejectWithValue('Yeni şifreler birbiriyle eşleşmiyor.');
      }
  
      try {
        // Eski şifre ile kullanıcıyı yeniden doğrula
        const credential = EmailAuthProvider.credential(user.email, oldPassword);
        await reauthenticateWithCredential(user, credential);
  
        // Şifreyi güncelle
        await updatePassword(user, newPassword);
        return 'Şifreniz başarıyla güncellendi!';
      } catch (error) {
        if (error.code === 'auth/wrong-password') {
          return rejectWithValue('Eski şifreniz hatalı.');
        } else if (error.code === 'auth/weak-password') {
          return rejectWithValue('Yeni şifreniz yeterince güçlü değil.');
        }
        return rejectWithValue('Şifre güncellenirken bir hata oluştu.');
      }
    }
  );

//Kullanıcı bilgilerini alma
export const getUser = () => {
    const auth = getAuth();
    const user = auth.currentUser;
    return user;
}

//Otomatik giriş

export const autoLogin = createAsyncThunk('user/autoLogin', async() => {
    try {
        const token = await AsyncStorage.getItem("userToken")
        
        if(token){
            return token
        }
        else{
            throw new Error("User not found.")
        }
    } catch (error) {
        throw error
    }
})

//Çıkış
export const logout = createAsyncThunk('user/logout', async () => {
    try {
        const auth = getAuth()
        await signOut(auth)

        await AsyncStorage.removeItem("userToken")
        return null

    } catch (error) {
        throw error
    }
})

//Kaydol
export const register = createAsyncThunk('user/register', async ({email, password, name}, {rejectWithValue}) => {
    try {
        const auth = getAuth()
        const userCredantial = await createUserWithEmailAndPassword(auth, email, password)

        const user = userCredantial.user
        const token = user.stsTokenManager.accessToken

        await updateProfile(user, {displayName:name,});

        await sendEmailVerification(user)

        await AsyncStorage.setItem("userToken", token)

        return token

    } catch (error) {
        console.log('Hata kodu:', error.code); // Hata kodunu konsola yazdır

        if (error.code === 'auth/email-already-in-use') {
            return rejectWithValue('Bu e-posta adresi zaten kullanılıyor. Lütfen başka bir e-posta adresi deneyin.');
          } else if (error.code === 'auth/weak-password') {
            return rejectWithValue('Şifre çok zayıf. Lütfen daha güçlü bir şifre seçin.');
          } else if (error.code === 'auth/invalid-email') {
            return rejectWithValue('Geçersiz e-posta adresi. Lütfen geçerli bir e-posta adresi girin.');
          } else {
            return rejectWithValue('Kaydolma sırasında bir hata oluştu. Lütfen tekrar deneyin.');
          }
    }
})

//burada fonksiyon içinden kontrole edilen parametreler varken dışarıdan email ve password geliyor
const initialState = {
    isLoading: false,
    isAuth: false,
    token:null,
    user:null,
    error: null,
}

//state ve actionları içeren userSlice yapısı
export const userSlice = createSlice({
    name:'user',
    initialState,
    //setEmail ve setPassword gereksiz gibi
    reducers: {
        setEmail: (state, action) => {
            state.email= action.payload.toLowerCase()
        },
        setPassword : (state,action) => {
            state.password = action.payload
        },
        setIsLoading : (state, action) => {
            state.isLoading = action.payload
        },
    },
    //asenkron yapıdan faydalanıyoruz
    extraReducers: (builder) => {
        builder
            .addCase(login.pending,(state)=>{
                state.isLoading=true
                state.isAuth=false
            })
            .addCase(login.fulfilled,(state,action)=>{
                state.isLoading=false
                state.isAuth=true
                state.user=action.payload.user
                state.token=action.payload.token
            })
            .addCase(login.rejected,(state, action)=>{
                state.isLoading=false
                state.isAuth=false
                state.error=action.error.message
            })

            .addCase(autoLogin.pending,(state)=>{
                state.isLoading=true
                state.isAuth=false
            })
            .addCase(autoLogin.fulfilled,(state,action)=>{
                state.isLoading=false
                state.isAuth=true
                state.token=action.payload
            })
            .addCase(autoLogin.rejected,(state)=>{
                state.isLoading=false
                state.isAuth=false
                state.token=null
            })

            .addCase(logout.pending, (state)=> {
                state.isLoading=true
            })
            .addCase(logout.fulfilled, (state)=> {
                state.isLoading=false
                state.isAuth=false
                state.token=null
                state.error=null
            })
            .addCase(logout.rejected, (state, action)=> {
                state.isLoading=false
                state.error=action.payload
            })

            .addCase(register.pending, (state)=> {
                state.isLoading = true
                state.isAuth = false
            })
            .addCase(register.fulfilled, (state, action)=> {
                state.isLoading= false
                state.isAuth= true
                state.token= action.payload
            })
            .addCase(register.rejected, (state, action)=> {
                state.isLoading= false
                state.isAuth= false
                state.error= "Geçersiz email veya şifre."
            })

            .addCase(updateCipher.pending, (state)=> {
                state.isLoading= true
            })
            .addCase(updateCipher.fulfilled, (state)=> {
                state.isLoading= false
            })
            .addCase(updateCipher.rejected, (state)=> {
                state.isLoading= false
                state.error= "Geçersiz şifre."
            })
    }
})

export const {setEmail, setPassword, setIsLoading,} = userSlice.actions
export default userSlice.reducer;
//default olarak export ettik ve store içinde user olarak import ettik