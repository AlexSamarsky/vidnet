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

export interface UserRegister extends UserCredentials {
  first_name: string;
  last_name: string;
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
    register: builder.mutation<any, UserRegister>({
      query: (credentials) => ({
        url: "auth/register/",
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

export const {
  useLoginMutation,
  useCheckQuery,
  useLazyCheckQuery,
  useRegisterMutation,
} = authSlice;
