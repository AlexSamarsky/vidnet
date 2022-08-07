import { isRejectedWithValue, Middleware } from "@reduxjs/toolkit";

const { REACT_APP_GOOGLE_CLIENT_ID, REACT_APP_BASE_BACKEND_URL } = process.env;

const authInterceptor: Middleware = () => (next) => (action) => {
  if (isRejectedWithValue(action) && action.payload.status === 401) {
    console.log("401 error");
  }

  return next(action);
};

export default authInterceptor;

export const utilOpenGoogleLoginPage = () => {
  const googleAuthUrl = "https://accounts.google.com/o/oauth2/v2/auth";
  const redirectUri = "api/v1/auth/login/google/";

  const scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
  ].join(" ");

  const params: Object = {
    response_type: "code",
    client_id: REACT_APP_GOOGLE_CLIENT_ID,
    redirect_uri: `${REACT_APP_BASE_BACKEND_URL}/${redirectUri}`,
    prompt: "select_account",
    // access_type: "offline",
    scope,
  };

  const urlParams = new URLSearchParams(Object.entries(params)).toString();

  window.location.href = `${googleAuthUrl}?${urlParams}`;
};
