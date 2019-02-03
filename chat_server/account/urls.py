from django.urls import path

from .views import LoginView, logout_view, user_view


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/current/', user_view, name='current_user'),
]
