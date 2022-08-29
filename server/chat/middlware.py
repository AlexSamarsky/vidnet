import jwt
import os
from datetime import datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidnet.settings')
django.setup()

from django.db import close_old_connections
from users.models import User
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
# from channels.auth import AuthMiddlewareStack


ALGORITHM = "HS256"


@database_sync_to_async
def get_user(token, token_name):
    
    if not token_name == "Bearer":
        return AnonymousUser()
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        # print('payload', payload)
        # print('test user', payload['user_id'])
    except:
        # print('no payload')
        return AnonymousUser()

    token_exp = datetime.fromtimestamp(payload['exp'])
    if token_exp < datetime.utcnow():
        # print("no date-time")
        return AnonymousUser()

    try:
        user = User.objects.get(id=payload['user_id'])
        # print('user', user)
    except User.DoesNotExist:
        # print('no user')
        return AnonymousUser()

    return user


class TokenAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        close_old_connections()
        # token_key = scope['query_string'].decode().split('=')[-1]
        
        headers = dict(scope['headers'])
        
        try:
            token_name, token_key = headers[b'authorization'].decode().split()
        except KeyError:
            token_name, token_key = None, None
            
        
        # if b'authorization' in headers:
        #     token_name, token_key = headers[b'authorization'].decode().split()
            # if token_name == 'Token':
        scope['user'] = await get_user(token_key, token_name)
                    # token_key = Token.objects.get(key=token_key)
        #             scope['user'] = token.user
        #     except Token.DoesNotExist:
        #         scope['user'] = AnonymousUser()


        # try:
        #     token_key = (dict((x.split('=') for x in scope['query_string'].decode().split(
        #         "&")))).get('token', None)
        # except ValueError:
        #     token_key = None
        # try:
        #     token_key = dict(scope['headers'])[b'sec-websocket-protocol'].decode('utf-8')
        #     print('d1', token_key)
        # except ValueError:
        #     token_key = None

        # scope['user'] = await get_user(token_key)
        # print('d2', scope['user'])
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
