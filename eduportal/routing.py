from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/chat/<int:group_id>/", ChatConsumer.as_asgi()),
]
