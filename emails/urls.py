from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

main_router = DefaultRouter()
main_router.register(r"inbox", views.MailInboxViewSet, "inbox")
main_router.register(r"accounts", views.MailAccountViewSet, "accounts")

urlpatterns = [
    path("", include(main_router.urls)),
    # path('register/', views.register, name='register'),
    # path('login/', views.email_login, name='email_login'),
    # path('crawl/', views.crawl_emails, name='crawl'),
    # path('save-credential/', views.save_google_credential, name='save_google_credential'),
    # path('lmao/', views.get_inbox_emails, name='get_inbox_emails'),

]
