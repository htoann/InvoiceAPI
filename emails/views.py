import datetime
import email
import imaplib
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import requests

from emails.filter import MailAccountFilterSet, MailFilterSet
from emails.serializer import EmailAccountSerializer, MailSerializer
from emails.service import EmailService
from .models import MailAccount, MailInbox
from .forms import AddAccountForm
import os
import json

from django.http import JsonResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from rest_framework import views, viewsets, mixins
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

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

    # def create(self, request, *args, **kwargs):
    #     inboxes = EmailService.load_inbox(request.data['email'], request.data['password'])
    #     request.data['inboxes'] = inboxes

    #     return super().create(request, *args, **kwargs)

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

# def add_account(request):
#     if request.method == 'POST':
#         form = AddAccountForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             flow = Flow.from_client_secrets_file(
#                 credentials_path,
#                 scopes=SCOPES,
#                 redirect_uri='http://localhost:8000/oauth2callback'
#             )
#             authorization_url, state = flow.authorization_url(access_type='offline')
#             request.session['state'] = state
#             request.session['email'] = email
#             return redirect(authorization_url)
#     else:
#         form = AddAccountForm()
#     return render(request, 'add_account.html', {'form': form})

# def oauth2callback(request):
#     state = request.session['state']
#     email = request.session['email']
#     flow = Flow.from_client_secrets_file(
#         credentials_path,
#         scopes=SCOPES,
#         state=state,
#         redirect_uri='http://localhost:8000/oauth2callback'
#     )
#     flow.fetch_token(authorization_response=request.build_absolute_uri())

#     credentials = flow.credentials
#     creds_dict = {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }

#     user_cred = MailAccount(email=email, credentials=creds_dict)
#     user_cred.save()
#     return redirect('home')

# def crawl_emails(request):
#     username = request.GET.get('username', None)
#     filter_param = request.GET.get('filter', 'primary')
#     page_size = int(request.GET.get('page_size', 10))
#     page = int(request.GET.get('page', 1))
    
#     queries = {
#         'primary': 'category:primary in:inbox',
#         'spam': 'label:spam',
#         'promotions': 'category:promotions'
#     }
    
#     query = queries.get(filter_param, queries['primary'])
    
#     if username:
#         mail_accounts = MailAccount.objects.filter(email=username)
#     else:
#         mail_accounts = MailAccount.objects.all()
    
#     all_emails = []

#     MailInbox.objects.all().delete()

#     for account in mail_accounts:
#         creds = account.get_credentials()
        
#         if creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#             account.credentials = creds
#             account.save()

#         service = build('gmail', 'v1', credentials=creds)
        
#         # Adjusted for page size and page token
#         results = service.users().messages().list(userId='me', q=query, maxResults=page_size, pageToken=str(page)).execute()
#         messages = results.get('messages', [])

#         for message in messages:
#             msg = service.users().messages().get(userId='me', id=message['id']).execute()
#             payload = msg.get('payload', {})
#             headers = payload.get('headers', [])
#             email_data = {header['name']: header['value'] for header in headers}
#             all_emails.append(MailInbox(**{
#                 'mail_account_id': account.id,
#                 'subject': email_data.get('Subject'),
#                 'sender': email_data.get('From'),
#                 'date': datetime.datetime.now(), # email_data.get('Date')
#                 'label': filter_param,
#             }))

#         MailInbox.objects.bulk_create(all_emails)

#     return JsonResponse({
#         'success': "ok",
#     }, safe=False)

# def save_google_credential(request):
#     data = request.data
#     access_token = data.get('access_token')
#     email = data.get('email')  # Assuming you pass the email to identify the MailAccount

#     if not access_token or not email:
#         return Response({'error': 'Missing access_token or email'}, status=status.HTTP_400_BAD_REQUEST)

#     # Fetch and verify the token
#     response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={access_token}')
#     token_info = response.json()

#     if response.status_code != 200:
#         return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

#     # Get or create the MailAccount
#     mail_account, created = MailAccount.objects.update_or_create(
#         email=email,
#         defaults={
#             'name': token_info.get('name', 'Unknown'),  # Assuming 'name' can be extracted or set to 'Unknown'
#             'credentials': {
#                 'access_token': access_token,
#                 'refresh_token': token_info.get('refresh_token'),
#                 'token_type': token_info.get('token_type'),
#                 'expires_in': token_info.get('expires_in'),
#                 'scope': token_info.get('scope'),
#             }
#         }
#     )

#     # Return the updated MailAccount
#     return Response({'email': mail_account.email, 'credentials': mail_account.credentials}, status=status.HTTP_200_OK)
    
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def get_inbox_emails(request):
    EMAIL = 'mycloud.dev.07@gmail.com'
    PASSWORD = 'xczh qecu sgjk ibjy'
    SERVER = 'imap.gmail.com'

    try:
        # Kết nối và đăng nhập
        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')

        # Tìm tất cả email
        status, data = mail.search(None, 'ALL')
        mail_ids = [block.decode() for block in data[0].split()]

        # Lấy 10 email đầu tiên
        mail_ids = mail_ids[:10]
        
        res = []

        for i in mail_ids:
            status, data = mail.fetch(i, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    mail_from = message['from']
                    mail_subject = message['subject']
                    mail_content = ''
                    
                    # Xử lý email multipart
                    if message.is_multipart():
                        for part in message.walk():
                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                    else:
                        mail_content = message.get_payload(decode=True).decode(message.get_content_charset(), errors='ignore')

                    # Thêm thông tin email vào danh sách
                    res.append({
                        "from": mail_from,
                        "subject": mail_subject,
                        "content": mail_content
                    })

        # Đóng kết nối và đăng xuất
        mail.close()
        mail.logout()

        return Response(res)

    except Exception as e:
        # Trả về phản hồi lỗi với mã trạng thái 500
        return Response({"error": str(e)})