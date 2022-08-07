import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { RootState } from "../store";

const { REACT_APP_BASE_BACKEND_URL } = process.env;

const baseQuery = fetchBaseQuery({
  baseUrl: REACT_APP_BASE_BACKEND_URL + "/api/v1/",
  credentials: "include",
  prepareHeaders: (headers, { getState }) => {
    headers.set("Content-Type", "application/json");
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set("authorization", `Bearer ${token}`);
    }
    return headers;
  },
});

// const customBaseQuery: BaseQueryFn<
//   string | FetchArgs,
//   unknown,
//   FetchBaseQueryError
// > = async (args, api, extraOptions) => {
//   let result = await baseQuery(args, api, extraOptions);
//   if (result?.error?.status === 401) {
//   }
//   return result;
// };

export const apiSlice = createApi({
  baseQuery: baseQuery,
  reducerPath: "api",
  endpoints: (builder) => ({}),
});
