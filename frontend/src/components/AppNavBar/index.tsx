import React, { useEffect } from "react";
import { Navbar, Container, Nav } from "react-bootstrap";
import { useSelector } from "react-redux";
import { Link } from "react-router-dom";
import { logout, selectUser } from "../../app/authSlice";
import { useAppDispatch } from "../../app/hooks";

export const AppNavBar = () => {
  const dispatch = useAppDispatch();

  const user = useSelector(selectUser);

  useEffect(() => {
    console.log(user);
  }, [user]);
  const handleLogout = () => {
    dispatch(logout());
  };
  return (
    <Navbar bg="light" expand="lg" className="mx-auto">
      <Container>
        <Navbar.Brand as={Link} to="/">
          Vidnet
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/home">
              Home
            </Nav.Link>
          </Nav>
          <Nav>
            {!user ? (
              <>
                <Nav.Link as={Link} to="/login">
                  Войти
                </Nav.Link>
              </>
            ) : (
              <>
                <Nav.Link>{user}</Nav.Link>
                <Nav.Link onClick={handleLogout}>Выйти</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};
