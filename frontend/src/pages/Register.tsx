import React, { useCallback, useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { Button, Form } from "react-bootstrap";
import { useRegisterMutation } from "../app/api/authApiSlice";

import styles from "./login.module.css";

const Register = () => {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [passwordCheck, setPasswordCheck] = useState<string>("");
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [errMsg, setErrMsg] = useState<string>("");

  const [register, { isLoading }] = useRegisterMutation();

  const navigate = useNavigate();

  const handleSetUser = (e: React.ChangeEvent<HTMLInputElement>) =>
    setEmail(e.target.value);
  const handleSetPwd = (e: React.ChangeEvent<HTMLInputElement>) =>
    setPassword(e.target.value);
  const handleSetPwdCheck = (e: React.ChangeEvent<HTMLInputElement>) =>
    setPasswordCheck(e.target.value);
  const handleSetFirstName = (e: React.ChangeEvent<HTMLInputElement>) =>
    setFirstName(e.target.value);
  const handleSetLastName = (e: React.ChangeEvent<HTMLInputElement>) =>
    setLastName(e.target.value);

  const handleSubmit = async (e: React.ChangeEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      if (password !== passwordCheck) {
        setErrMsg("Пароли должны совпадать");
        return;
      }
      await register({
        email,
        password,
        last_name: lastName,
        first_name: firstName,
      }).unwrap();
      navigate("/login");
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

  return (
    <>
      <div className={styles.form_login}>
        <Form onSubmit={handleSubmit}>
          <h2 className="text-center">Введите данные для регистрации</h2>
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
            <Form.Control
              type="text"
              placeholder="Введите имя"
              onChange={handleSetFirstName}
              defaultValue={firstName}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Control
              type="text"
              placeholder="Введите фамилию"
              onChange={handleSetLastName}
              defaultValue={lastName}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Control
              type="password"
              placeholder="Введите пароль"
              onChange={handleSetPwd}
              defaultValue={password}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Повторите пароль</Form.Label>
            <Form.Control
              type="password"
              placeholder="Повторите пароль пароль"
              onChange={handleSetPwdCheck}
              defaultValue={passwordCheck}
            />
            {errMsg ? <></> : <Form.Text>{errMsg}</Form.Text>}
          </Form.Group>
          <div className="row">
            <Button
              type="submit"
              className="primary"
              defaultChecked
              disabled={isLoading}
            >
              Зарегистрироваться
            </Button>
          </div>
        </Form>
      </div>
    </>
  );
};

export default Register;
