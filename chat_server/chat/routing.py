from django.urls import path

from .consumers import ChatConsumer


websocket_urlpatterns = [
    path('ws/chat/room/<int:room_id>/', ChatConsumer),
]
