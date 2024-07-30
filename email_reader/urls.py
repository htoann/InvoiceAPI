from django.contrib import admin
from django.urls import include, path
from emails import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mails/', include('emails.urls')),
]
