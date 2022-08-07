import React, { useEffect } from "react";
import { Button, Card, Container } from "react-bootstrap";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { selectToken, setCredentials } from "../../app/authSlice";
import { useLocation, useNavigate } from "react-router-dom";
import { useCheckQuery, useLazyCheckQuery } from "../../app/api/authApiSlice";

function Home() {
  const navigate = useNavigate();
  const token = useAppSelector(selectToken);
  const dispatch = useAppDispatch();

  // const params = useParams();
  const loc = useLocation().search;
  const username = new URLSearchParams(loc).get("username");
  const access = new URLSearchParams(loc).get("access");

  const [fetch_data, { data: data2, isError }] = useLazyCheckQuery();

  const clickHandle = async () => {
    fetch_data();
  };

  useEffect(() => {}, [isError]);

  useEffect(() => {
    if (access) {
      dispatch(
        setCredentials({
          username: username!,
          isLogged: true,
          token: access!,
        })
      );
      navigate("/");
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetch_data();
    }
  }, [token]);

  return (
    <Container>
      <Button onClick={clickHandle}>Clickme</Button>
      <Card>
        <Card.Title>{isError ? "Error" : JSON.stringify(data2)}</Card.Title>
      </Card>
    </Container>
  );
}

export default Home;
