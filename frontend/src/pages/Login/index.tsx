import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { Button, Form } from "react-bootstrap";
import GoogleButton from "react-google-button";
import { useLoginMutation } from "../../app/api/authApiSlice";
import { setCredentials, selectUser } from "../../app/authSlice";

import styles from "./login.module.css";
import { utilOpenGoogleLoginPage } from "../../utils/authUtils";

function Login() {
  const [email, setEmail] = useState<string>("xsami@yandex.ru");
  const [password, setPassword] = useState<string>("123");
  const [errMsg, setErrMsg] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const user = useSelector(selectUser);

  const [login, { isLoading }] = useLoginMutation();
  useEffect(() => {
    setErrMsg("");
  }, [email, password]);

  const handleSubmit = async (e: React.ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const userData = await login({ email, password }).unwrap();
      dispatch(
        setCredentials({
          username: userData.username,
          isLogged: true,
          token: userData.access,
        })
      );
      navigate("/");
    } catch (err: any) {
      if (!err?.status) {
        // isLoading: true until timeout occurs
        setErrMsg("No Server Response");
      } else if (err.status === 400) {
        setErrMsg("Missing Username or Password");
      } else if (err.status === 401) {
        setErrMsg("Unauthorized");
      } else {
        setErrMsg("Login Failed");
      }
    }
  };

  const openGoogleLoginPage = useCallback(() => {
    utilOpenGoogleLoginPage();
  }, []);

  const handleSetUser = (e: React.ChangeEvent<HTMLInputElement>) =>
    setEmail(e.target.value);
  const handleSetPwd = (e: React.ChangeEvent<HTMLInputElement>) =>
    setPassword(e.target.value);

  return (
    <>
      <div className={styles.form_login}>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            {/* <Form.Label>Имя/email пользователя</Form.Label> */}
            <Form.Control
              type="email"
              placeholder="Введите имя пользователя"
              onChange={handleSetUser}
              autoFocus
              defaultValue={email}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Пароль</Form.Label>
            <Form.Control
              type="password"
              placeholder="Введите пароль"
              onChange={handleSetPwd}
              defaultValue={password}
            />
          </Form.Group>
          <Button
            type="submit"
            className="primary"
            defaultChecked
            disabled={isLoading}
          >
            Войти
          </Button>
          <GoogleButton
            onClick={openGoogleLoginPage}
            label="Login by Google"
            className="mt-3 mx-auto"
          />
        </Form>
      </div>
    </>
  );
}

export default Login;
