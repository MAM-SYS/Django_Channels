from django.urls import path

from .views import index, room
from django.contrib.auth import views
urlpatterns = [
    path('', index, name='index'),
    path('<str:room_name>/', room, name='room'),
    path('login', views.LoginView.as_view(template_name='chat/login.html'), name="login")
]