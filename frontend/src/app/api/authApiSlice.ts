import { apiSlice } from "./apiSlice";

export interface UserData {
  username: string;
  refresh: string;
  access: string;
}

export interface UserCredentials {
  email: string;
  password: string;
}

const authSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<UserData, UserCredentials>({
      query: (credentials) => ({
        url: "auth/login/",
        method: "POST",
        body: { ...credentials },
      }),
    }),
  }),
});

export const { useLoginMutation } = authSlice;
