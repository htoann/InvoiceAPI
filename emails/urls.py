from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('oauth2login/', views.oauth2_login, name='oauth2_login'),
    path('oauth2callback/', views.oauth2_callback, name='oauth2_callback'),
    path('inbox/', views.inbox, name='inbox'),
]
