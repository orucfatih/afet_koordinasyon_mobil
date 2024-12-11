import { createSlice,createAsyncThunk } from "@reduxjs/toolkit";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "firebase/auth";

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

        return userData;

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
    }
})

export const {setEmail, setPassword, setIsLoading,} = userSlice.actions     //tam olarak ne yapıyor?
export default userSlice.reducer;
//default olarak export ettik ve store içinde user olarak import ettik