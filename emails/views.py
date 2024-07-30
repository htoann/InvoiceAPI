from django.shortcuts import render

from emails.filter import MailAccountFilterSet, MailFilterSet
from emails.serializer import EmailAccountSerializer, MailSerializer
from .models import MailAccount, MailInbox
import os

from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Chỉ sử dụng cho mục đích phát triển

credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

class MailAccountViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    """
    API endpoint that allows email account to be viewed.
    """
    queryset = MailAccount.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = MailAccountFilterSet
    serializer_class = EmailAccountSerializer
    pagination_class = CustomPageNumberPagination

class MailInboxViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    """
    API endpoint that allows mail to be viewed or edited.
    """
    # permission_classes = [AllowAny]
    queryset = MailInbox.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = MailFilterSet
    serializer_class = MailSerializer
    pagination_class = CustomPageNumberPagination

def home(request):
    user_accounts = list(MailAccount.objects.all())
    return render(request, 'home.html', {'user_accounts': user_accounts})
