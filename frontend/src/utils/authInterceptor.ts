import { isRejectedWithValue, Middleware } from "@reduxjs/toolkit";

const authInterceptor: Middleware = () => (next) => (action) => {
  if (isRejectedWithValue(action) && action.payload.status === 401) {
    console.log("401 error");
  }

  return next(action);
};

export default authInterceptor;
