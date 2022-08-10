import React, { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { Button, Form } from "react-bootstrap";
import GoogleButton from "react-google-button";
import { useLoginMutation } from "../app/api/authApiSlice";
import { setCredentials, selectUser } from "../app/authSlice";

import { utilOpenGoogleLoginPage } from "../utils/authUtils";
import styles from "./login.module.css";

function Login() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [login, { isLoading, error, isError, data: userData }] =
    useLoginMutation();

  const handleSubmit = (e: React.ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      login({ email, password })
        .unwrap()
        .catch((err) => console.log(err));
    } catch (err: any) {}
  };

  useEffect(() => {
    try {
      if (error) {
        console.log(error);
      }
      if (userData?.username) {
        dispatch(
          setCredentials({
            username: userData?.username!,
            isLogged: true,
            token: userData?.access!,
          })
        );
        navigate("/");
      }
    } catch (err: any) {}
  }, [error, userData]);

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
            {isLoading ? <p>Загрузка</p> : <></>}
            {isError ? (
              <>
                <p>{JSON.stringify(error)}</p>
              </>
            ) : (
              <></>
            )}
            {error ? <p>{JSON.stringify(error)}</p> : <></>}
          </Form.Group>
          <div className="row">
            <Button
              type="submit"
              className="primary"
              defaultChecked
              disabled={isLoading}
            >
              Войти
            </Button>
          </div>
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
