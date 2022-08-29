### django.env file

DJANGO_JWT_EXPIRATION_DELTA=72000
DJANGO_SECRET_KEY=

DJANGO_GOOGLE_OAUTH2_CLIENT_ID=
DJANGO_GOOGLE_OAUTH2_CLIENT_SECRET=

### react.env file

REACT_APP_BASE_BACKEND_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=

## Videoclips

initial data

```python
python manage.py shell < initdata.py
```

videoclips

#TODO make load video chunk

## Websockets

start websocket app

```python
uvicorn --port 8001 vidnet.asgi:application
```

connect to websocket

```python
ws://127.0.0.1:8001/ws/chat/

header
authorization: Bearer {{access_token}}
```

#TODO make access token inside message

### Private room

join private room with other user

```python
{
    "user_pk": 4,
    "action": "join_private_room",
    "request_id": 443215321
}
```

#TODO make websocket with subscribe to multiple rooms

send message to websocket other user

```python
{
    "message": "asdf",
    "action": "create_message",
    "request_id": 432153212344
}
```

#TODO make messages view to access old chat message with other user

### Public rooms

create public room

```python
{
    "name": "new chat",
    "action": "action_create_public_room",
    "request_id": 443215321
}
```

add user to room (only exists users)

```python
{
    "room_pk": 18,
    "user_pk": 4,
    "action": "action_add_user_to_room",
    "request_id": 443215321
}
```

remove user from room (only exists users)

```python
{
    "room_pk": 18,
    "user_pk": 4,
    "action": "action_remove_user_from_room",
    "request_id": 443215321
}
```
