import { createSlice,createAsyncThunk } from "@reduxjs/toolkit";
import auth, { PhoneAuthProvider } from '@react-native-firebase/auth';
import firestore from '@react-native-firebase/firestore';
import AsyncStorage from "@react-native-async-storage/async-storage";
import { firebase } from '@react-native-firebase/auth';

// TODO: AsyncStorage yerine daha güvenli bir depolama yöntemi kullanılmalı
// TODO: Aynı kullanıcının birden fazla cihazdan giriş yapmasını engellenecek
// TODO: Kullanıcı kaydolurken telefon numarasının doğrulanması gerekiyor

//iki parametre alan ve asenkron yapı kullanan giriş yapma fonksiyonu
export const login = createAsyncThunk('user/login', async({email,password}, {rejectWithValue})=> {
    try {
        const userCredantial = await auth().signInWithEmailAndPassword(email, password)

        const user = userCredantial.user;
        const token = await user.getIdToken();

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
        }else if (error.code === 'auth/invalid-email') {
            return rejectWithValue('Geçersiz e-posta adresi. Lütfen geçerli bir e-posta adresi girin.');
        } else {
            return rejectWithValue(`Bilinmeyen hata: ${error.message}`); // Daha detaylı bir mesaj döndür
        }
    }
})

//!!Personel Giriş
export const staffLogin = createAsyncThunk('user/staffLogin', async ({ email, password,}, { rejectWithValue }) => {
  try {
      const userCredential = await auth().signInWithEmailAndPassword(email, password);

      const user = userCredential.user;
      const token = await user.getIdToken();

      // Kullanıcının personel olup olmadığını kontrol et
      const idTokenResult = await user.getIdTokenResult();
      const isStaff = (idTokenResult.claims.role === "staff" || idTokenResult.claims.role === "supervisor");

      if (!isStaff) {
        await auth().signOut();
        return rejectWithValue("Personel yetkiniz bulunmamaktadır.");
      }

      // Kullanıcının Firestore'daki verisini al
      const userRef = firestore().collection('users').doc(user.uid);
      const userDoc = await userRef.get();

      if (!userDoc.exists) {
          return rejectWithValue("Kullanıcı bilgileri bulunamadı.");
      }

      const userData = userDoc.data();
      //const phoneNumber = userData.phone;
      //!! Firebase Phone Auth'a test için eklemiş olduğumuz numara. Lütfen değiştirmeyin.
      const phoneNumber = "+905555555555";


      if (!phoneNumber) {
        return rejectWithValue("Telefon numaranız sistemde kayıtlı değil.");
      }


      const verificationId = await auth().verifyPhoneNumber(phoneNumber);

      const staffData = {
          token,
          user: user,
      };

      return {
        staffData,
        verificationId,
      };

  } catch (error) {
      if (error.code === 'auth/user-not-found') {
          return rejectWithValue('Personel kaydı bulunamadı. Lütfen yöneticinizle iletişime geçin.');
      } else if (error.code === 'auth/wrong-password' || error.code === 'auth/invalid-credential') {
          return rejectWithValue('Hatalı personel bilgileri. Lütfen tekrar deneyin.');
      } else if (error.code === 'auth/too-many-requests') {
          return rejectWithValue('Çok fazla giriş denemesi. Daha sonra tekrar deneyin.');
      } else if (error.code === 'auth/invalid-email') {
        return rejectWithValue('Geçersiz e-posta adresi. Lütfen geçerli bir e-posta adresi girin.');
      } else {
          return rejectWithValue(`Bilinmeyen hata: ${error.message}`);
      }
  }
});

export const verifyPhoneCode = createAsyncThunk('user/verifyPhoneCode', async ({ verificationId, code, staffData }, { rejectWithValue, getState, dispatch }) => {
    try {
      
      const user = auth().currentUser;
      if (!user) {
        return rejectWithValue('Kullanıcı bulunamadı. Lütfen tekrar giriş yapın.');
      }

      console.log(code);
      const phoneCredential = PhoneAuthProvider.credential(verificationId, code);
      
      if(!phoneCredential || code!=='123123'){
        return rejectWithValue('Doğrulama kodu geçersiz. Lütfen tekrar deneyin.');
      }

      await AsyncStorage.setItem("staffToken", staffData.token);
      
      return { 
        success: true,
        token: staffData.token 
      };
      
    } catch (error) {
      console.log('Verification Error:', error);
      const { verifyAttempts, resendAttempts } = getState().user; // state'e doğru erişiyoruz
  
      if (verifyAttempts >= 3 && resendAttempts >= 1) {
        await dispatch(logout());
        return rejectWithValue('Çok fazla doğrulama denemesi. Lütfen daha sonra tekrar deneyin.');
      }
  
      if (error.code === 'auth/invalid-verification-code') {
        return rejectWithValue('Doğrulama kodu geçersiz. Lütfen tekrar deneyin.');
      } else if (error.code === 'auth/code-expired') {
        return rejectWithValue('Kodun süresi doldu. Tekrar kod istemelisiniz.');
      } else if (error.code === 'auth/invalid-verification-id') {
        return rejectWithValue('Doğrulama kimliği geçersiz.');
      } else {
        return rejectWithValue(`Bilinmeyen doğrulama hatası: ${error.message}`);
      }
    }
  });

  export const resendPhoneCode = createAsyncThunk('user/resendPhoneCode', async (_, { rejectWithValue }) => {
    try {
      const user = auth().currentUser;
  
      const userRef = firestore().collection("users").doc(user.uid);
      const userDoc = await userRef.get();

      if (!userDoc.exists) {
          return rejectWithValue("Kullanıcı bilgileri bulunamadı.");
      }

      const userData = userDoc.data();
      //const phoneNumber = userData.phone;
      //!! Firebase Phone Auth'a test için eklemiş olduğumuz numara. Lütfen değiştirmeyin.
      const phoneNumber = "+905555555555";


      if (!phoneNumber) {
        return rejectWithValue("Telefon numaranız sistemde kayıtlı değil.");
      }
      
      const verificationId = await auth().verifyPhoneNumber(phoneNumber);
  
      return { verificationId };
    } catch (error) {
      if (error.code === 'auth/too-many-requests') {
        return rejectWithValue('Çok fazla kod gönderme isteği. Lütfen daha sonra tekrar deneyin.');
      } else if (error.code === 'auth/invalid-phone-number') {
        return rejectWithValue('Telefon numarası geçersiz.');
      } else {
        return rejectWithValue(`Kod gönderme hatası: ${error.message}`);
      }
    }
  });
  


//Şifre Değiştirme
export const updateCipher = createAsyncThunk('user/updatePassword', 
    async ({ oldPassword, newPassword, confirmPassword }, { rejectWithValue }) => {
      const user = auth().currentUser;
  
      if (!user) {
        return rejectWithValue('Kullanıcı oturumu açık değil.');
      }
  
      if (newPassword !== confirmPassword) {
        return rejectWithValue('Yeni şifreler birbiriyle eşleşmiyor.');
      }
  
      try {
        // Eski şifre ile kullanıcıyı yeniden doğrula
        const credential = auth.EmailAuthProvider.credential(user.email, oldPassword);
        await user.reauthenticateWithCredential(credential);
  
        // Şifreyi güncelle
        await user.updatePassword(newPassword);
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
export const getUser = createAsyncThunk("user/getUser", async (_, { rejectWithValue }) => {
    try {
      const user = auth().currentUser;
  
      if (!user) {
        return rejectWithValue("Kullanıcı oturum açmamış.");
      }
  
      const userRef = firestore().collection("users").doc(user.uid);
      const userDoc = await userRef.get();
  
      if (!userDoc.exists) {
        return rejectWithValue("Kullanıcı bilgileri bulunamadı.");
      }
  
      return userDoc.data();
    } catch (error) {
      console.error("Kullanıcı bilgileri getirilirken hata:", error);
  
      // Firebase yetkilendirme hatasını kontrol et
      if (error.code === "permission-denied") {
        return rejectWithValue("Yetkisiz erişim: Bu bilgilere erişim izniniz yok.");
      }
  
      return rejectWithValue("Kullanıcı bilgileri alınırken bir hata oluştu.");
    }
  });

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

//!!Personel Otomatik Giriş
export const staffAutoLogin = createAsyncThunk('user/staffAutoLogin', async() => {
  try {
      const token = await AsyncStorage.getItem("staffToken")
      
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

//!!Çıkış
export const logout = createAsyncThunk('user/logout', async () => {
    try {
        await auth().signOut()

        await AsyncStorage.removeItem("userToken")
        await AsyncStorage.removeItem("staffToken")
        return null

    } catch (error) {
        throw error
    }
})

//Kaydol
export const register = createAsyncThunk(
    'user/register',
    async ({ email, password, confirmPassword, name, surname, phone }, { rejectWithValue }) => {
      try {
        if(password !== confirmPassword){
          return rejectWithValue("Şifreler birbiriyle eşleşmiyor.");
        }
        
        const userCredential = await auth().createUserWithEmailAndPassword(email, password);
        const user = userCredential.user;
        const token = await user.getIdToken();
        
        await user.updateProfile({ displayName: `${name} ${surname}` });
        await user.sendEmailVerification();
        
        // Firestore'a kullanıcı bilgilerini kaydetme
        await firestore().collection('users').doc(user.uid).set({
          name,
          surname,
          phone,
          email,
          uid: user.uid,
          createdAt: firestore.FieldValue.serverTimestamp(),
        });
        
        await AsyncStorage.setItem('userToken', token);
        return token;
      } catch (error) {
        console.log('Hata kodu:', error.code);
        
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
    }
  );

//burada fonksiyon içinden kontrole edilen parametreler varken dışarıdan email ve password geliyor
const initialState = {
    isLoading: false,
    isAuth: false,
    isStaffAuth:false,
    isFullyAuth:false,
    verifyAttempts: 0,
    resendAttempts: 0,
    resendCooldown: 60,
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

            .addCase(staffLogin.pending,(state)=>{
              state.isLoading=true
              state.isStaffAuth=false
          })
          .addCase(staffLogin.fulfilled,(state,action)=>{
              state.isLoading=false
              state.isStaffAuth=true
              state.user=action.payload.user
              state.token=action.payload.token
          })
          .addCase(staffLogin.rejected,(state, action)=>{
              state.isLoading=false
              state.isStaffAuth=false
              state.error=action.error.message
          })

          .addCase(verifyPhoneCode.pending,(state)=>{
            state.isLoading=true
            state.isFullyAuth=false
          })
          .addCase(verifyPhoneCode.fulfilled,(state,action)=>{
            state.isLoading=false
            state.isFullyAuth=true
            state.token=action.payload.token
            state.verifyAttempts = 0;
            state.resendAttempts = 0;
          })
          .addCase(verifyPhoneCode.rejected,(state,action)=>{
            state.isLoading=false
            state.isFullyAuth=false
            state.error=action.error.message
            state.verifyAttempts += 1
          })
          .addCase(resendPhoneCode.fulfilled, (state, action) => {
            state.isLoading = false;
            state.resendAttempts += 1;
          })
          .addCase(resendPhoneCode.pending, (state) => {
            state.isLoading = true;
          })
          .addCase(resendPhoneCode.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.error.message;
            state.resendAttempts += 1;
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

            .addCase(staffAutoLogin.pending,(state)=>{
              state.isLoading=true
              state.isStaffAuth=false
              state.isFullyAuth=false
          })
          .addCase(staffAutoLogin.fulfilled,(state,action)=>{
              state.isLoading=false
              state.isFullyAuth=true
              state.isStaffAuth=true
              state.token=action.payload
          })
          .addCase(staffAutoLogin.rejected,(state)=>{
              state.isLoading=false
              state.isFullyAuth=false
              state.isStaffAuth=false
              state.token=null
          })

            .addCase(logout.pending, (state)=> {
                state.isLoading=true
            })
            .addCase(logout.fulfilled, (state)=> {
                state.isLoading=false
                state.isAuth=false
                state.isStaffAuth=false
                state.isFullyAuth=false
                state.token=null
                state.error=null
                state.verifyAttempts = 0;
                state.resendAttempts = 0;
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