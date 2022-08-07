import React, { useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { useLoginMutation } from "../../app/api/authApiSlice";
import { setCredentials, selectUser, setUser } from "../../app/authSlice";

import styles from "./login.module.css";

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
      console.log(userData);
      console.log(user);
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
      console.log(err);
      console.log(errMsg);
    }
  };

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
        </Form>
      </div>
    </>
  );
}

export default Login;
