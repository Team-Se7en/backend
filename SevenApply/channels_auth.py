from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from urllib.parse import parse_qsl

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user = get_user_model().objects.get(id=validated_token["user_id"])
        return user
    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()
        token_key = None

        if "query_string" in scope:
            query_string = scope["query_string"].decode()
            query_params = dict(parse_qsl(query_string))
            token_key = query_params.get("token", None)

        if not token_key:
            headers = dict(scope["headers"])
            if b"authorization" in headers:
                try:
                    token_name, token_key = headers[b"authorization"].decode().split()
                    if token_name != "JWT":
                        token_key = None
                except:
                    pass

        if token_key:
            print(f"token key:\t{token_key}")
            try:
                decoded_data = jwt_decode(
                    token_key, settings.SECRET_KEY, algorithms=["HS256"]
                )
                scope["user"] = await get_user(validated_token=decoded_data)
            except:
                pass
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
