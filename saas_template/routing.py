from django.conf.urls import url
from channels.routing import (
    ProtocolTypeRouter, URLRouter
)
from messaging.middleware import TokenAuthMiddlewareStack
from messaging.consumers import MessagingConsumer


application = ProtocolTypeRouter({
    "websocket": TokenAuthMiddlewareStack(
        URLRouter([
            url(r'^messaging/$', MessagingConsumer)
        ])
    )
})
