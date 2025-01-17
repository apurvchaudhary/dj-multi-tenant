import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from mt_app.consumers import UpdateConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mt_pro.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/updates/", UpdateConsumer.as_asgi()),  # WebSocket route
                ]
            )
        ),
    }
)
