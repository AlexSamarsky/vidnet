import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface Auth {
  user: string;
  isLogged: boolean;
}

const initialState: Auth = {
  user: "",
  isLogged: false,
};

export const authSlice = createSlice({
  name: "auth",
  initialState: initialState,
  reducers: {
    setUser(state: Auth, action: PayloadAction<string>) {
      state.user = action.payload;
    },
    setAuth(state: Auth, action: PayloadAction<Auth>) {
      state = action.payload;
    },
  },
});

export const { setUser, setAuth } = authSlice.actions;

export default authSlice.reducer;
