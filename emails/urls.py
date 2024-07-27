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
    path('crawl/', views.crawl_emails, name='crawl'),
]
