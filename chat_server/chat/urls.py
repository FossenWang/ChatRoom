from django.urls import path

from .views import chatroom_list


urlpatterns = [
    path('rooms/', chatroom_list, name='chatroom_list'),
]
