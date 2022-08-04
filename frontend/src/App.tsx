import React from "react";
import { Routes, Route, Outlet } from "react-router-dom";
import { Home, Login } from "./pages";
import Missing from "./pages/Missing";
function App() {
  return (
    <Routes>
      <Route path="/" element={<Outlet />}>
        <Route path="home" element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="*" element={<Missing />} />
      </Route>
    </Routes>
  );
}

export default App;
