import { configureStore } from "@reduxjs/toolkit";
import userReducer from "./userSlice"
import { thunk } from "redux-thunk";

export const store = configureStore({
    reducer: {
        user : userReducer,
    },
    middleware : (getDefaultMiddlWare) => getDefaultMiddlWare({serializableCheck:false})  //serializable hatası için
})

//user bilgilerini storea ekledik