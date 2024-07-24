from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.email_login, name='email_login'),
    path('inbox/', views.inbox, name='inbox'),
]
