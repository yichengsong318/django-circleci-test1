from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user(id_jwt):
    try:
        return User.objects.get(id=id_jwt)
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)


class TokenAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        query_string = parse_qs(self.scope['query_string'].decode())
        token = query_string.get('token')
        print(token)

        if not token:
            self.scope['user'] = AnonymousUser()

        else:
            try:
                print("trying to validate token")
                access_token = AccessToken(token[0], verify=False)
                print(access_token)
                print(access_token["id"])
                self.scope['user'] = await get_user(access_token['id'])

            except Exception as exception:
                print(exception)
                self.scope['user'] = AnonymousUser()

        inner = self.inner(self.scope)
        return await inner(receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
