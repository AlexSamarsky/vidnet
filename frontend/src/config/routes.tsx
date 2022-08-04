import React from "react";

import { createBrowserHistory } from "history";
import { Route, Routes } from "react-router-dom";

import { LOGIN_URL, HOME_URL } from "./urls";

import { Login, Home } from "../pages";

export const history = createBrowserHistory();

const AppRoutes = () => {
  return (
    <Routes>
      <Route path={LOGIN_URL} element={<Login />} />
      <Route path={HOME_URL} element={<Home />} />
    </Routes>
  );
};

export default AppRoutes;
