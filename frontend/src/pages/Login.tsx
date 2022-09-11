import React, { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { Button, Form, Spinner } from "react-bootstrap";
import GoogleButton from "react-google-button";
import { useLoginMutation, UserCredentials } from "../app/api/authApiSlice";
import { setCredentials } from "../app/authSlice";

import { utilOpenGoogleLoginPage } from "../utils/authUtils";
import styles from "./login.module.css";

import { useForm } from "react-hook-form";

// #TODO make react hook form

function Login() {
  // const [email, setEmail] = useState<string>("");
  // const [password, setPassword] = useState<string>("");
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid, touchedFields },
  } = useForm<UserCredentials>({
    mode: "onBlur",
  });

  const [login, { isLoading, error, isError, data: userData }] =
    useLoginMutation();

  const handleSubmitForm = async ({ email, password }: UserCredentials) => {
    // console.log(email, password);
    // e.preventDefault();
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
  }, [error, userData, dispatch, navigate]);

  const openGoogleLoginPage = useCallback(() => {
    utilOpenGoogleLoginPage();
  }, []);

  return (
    <>
      <div className={styles.form_login}>
        <Form
          // className="was-validated"
          onSubmit={handleSubmit(handleSubmitForm)}
        >
          <Form.Group className="mb-3">
            <Form.Control
              {...register("email", {
                required: "Введите email",
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: "Некорректный email",
                },
              })}
              placeholder="Введите email"
              className={
                !errors?.email && touchedFields?.email ? "is-valid" : ""
              }
            ></Form.Control>
            {errors?.email && (
              <p className="invalid-feedback d-block">{errors.email.message}</p>
            )}
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Пароль</Form.Label>
            <Form.Control
              {...register("password", { required: "Введите пароль" })}
              type="password"
              placeholder="Введите пароль"
              className={
                !errors?.password && touchedFields?.password ? "is-valid" : ""
              }
            />
            {errors?.password && (
              <p className="invalid-feedback d-block">
                {errors.password.message}
              </p>
            )}
          </Form.Group>
          <div className="row">
            {isError ? (
              <div className="invalid-feedback d-block">
                Неправильный логин/пароль
              </div>
            ) : (
              <></>
            )}
            <Button
              type="submit"
              className="primary"
              defaultChecked
              disabled={isLoading || !isValid}
            >
              {isLoading ? (
                <Spinner
                  as="span"
                  animation="grow"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />
              ) : (
                <></>
              )}
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
