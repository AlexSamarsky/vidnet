import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "./store";

interface Auth {
  username: string;
  token: string;
  isLogged: boolean;
}

const initialState: Auth = {
  username: "",
  token: "",
  isLogged: false,
};

export const authSlice = createSlice({
  name: "auth",
  initialState: initialState,
  reducers: {
    setUser(state: Auth, action: PayloadAction<string>) {
      state.username = action.payload;
    },
    setIsLogged(state: Auth, action: PayloadAction<boolean>) {
      state.isLogged = action.payload;
    },
    setToken(state: Auth, action: PayloadAction<string>) {
      state.token = action.payload;
    },
    setCredentials(state: Auth, action: PayloadAction<Auth>) {
      const { isLogged, token, username } = action.payload;
      state.isLogged = isLogged;
      state.token = token;
      state.username = username;
    },
    logout(state: Auth) {
      state.username = "";
      state.token = "";
      state.isLogged = false;
    },
  },
});

export const { setUser, setCredentials, setToken, setIsLogged, logout } =
  authSlice.actions;

export default authSlice.reducer;

export const selectUser = (state: RootState) => state.auth.username;
export const selectToken = (state: RootState) => state.auth.token;
export const selectIsLogged = (state: RootState) => state.auth.isLogged;
export const selectAuth = (state: RootState) => state.auth;
