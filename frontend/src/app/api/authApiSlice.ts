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

export interface UserCheck {
  id: number;
  name: string;
  email: string;
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
    check: builder.query<UserCheck, void>({
      query: () => ({
        url: "users/me/",
      }),
    }),
  }),
});

export const { useLoginMutation, useCheckQuery, useLazyCheckQuery } = authSlice;
