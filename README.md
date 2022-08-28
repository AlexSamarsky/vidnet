## Videoclips

initial data

```python
python manage.py shell < initdata.py
```

videoclips

#TODO make

## Websockets

start websocket app

```python
uvicorn --port 8001 vidnet.asgi:application
```

connect to websocket

```python
ws://127.0.0.1:8001/ws/chat/?token={{access_token}}
```

#TODO make access token inside message

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
