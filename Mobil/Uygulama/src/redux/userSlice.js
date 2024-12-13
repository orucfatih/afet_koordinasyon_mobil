import { createSlice,createAsyncThunk } from "@reduxjs/toolkit";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, sendEmailVerification} from "firebase/auth";
import AsyncStorage from "@react-native-async-storage/async-storage";

//iki parametre alan ve asenkron yapı kullanan giriş yapma fonksiyonu
export const login = createAsyncThunk('user/login', async({email,password})=> {
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
        throw error
    }
})

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
export const register = createAsyncThunk('user/register', async ({email, password}) => {
    try {
        const auth = getAuth()
        const userCredantial = await createUserWithEmailAndPassword(auth, email, password)

        const user = userCredantial.user
        const token = user.stsTokenManager.accessToken

        await sendEmailVerification(user)

        await AsyncStorage.setItem("userToken", token)

        return token

    } catch (error) {
        throw error
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
    }
})

export const {setEmail, setPassword, setIsLoading,} = userSlice.actions
export default userSlice.reducer;
//default olarak export ettik ve store içinde user olarak import ettik