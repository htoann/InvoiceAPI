from django.contrib import admin
from django.urls import include, path
from emails import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('add_account/', views.add_account, name='add_account'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    # path('list_emails/', views.list_emails, name='list_emails'),
    path('mails/', include('emails.urls')),
]
