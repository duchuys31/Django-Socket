from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        query_string = scope['query_string'].decode()
        parsed_qs = parse_qs(query_string)
        user_token = parsed_qs['user'][0]
        print(user_token)
        if b'authorization' in headers:            
            token_name, token_key = headers[b'authorization'].decode().split()
            print(token_key)
            if token_name == 'Token':
                scope['user'] = await get_user(token_key)
                print(scope['user'])
        elif user_token != '': 
            scope['user'] = await get_user(user_token)
            print(scope['user'])
        return await super().__call__(scope, receive, send)

