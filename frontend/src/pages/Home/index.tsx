import React, { useEffect } from "react";
import { Button, Card, Container } from "react-bootstrap";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { selectToken, setToken } from "../../app/authSlice";

function Home() {
  const token = useAppSelector(selectToken);
  const dispatch = useAppDispatch();
  const clickHandle = () => {
    dispatch(setToken("test"));
  };

  useEffect(() => {
    console.log(token);
  }, [token]);

  return (
    <Container>
      <Button onClick={clickHandle}>Clickme</Button>
      <Card>
        <Card.Title>{token}</Card.Title>
      </Card>
    </Container>
  );
}

export default Home;
