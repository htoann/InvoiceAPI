# emails/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .models import UserCredentials
from .forms import AddAccountForm
import os
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Chỉ sử dụng cho mục đích phát triển

credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')

@login_required
def home(request):
    user_accounts = UserCredentials.objects.filter(user=request.user)
    return render(request, 'home.html', {'user_accounts': user_accounts})

@login_required
def add_account(request):
    if request.method == 'POST':
        form = AddAccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            flow = Flow.from_client_secrets_file(
                credentials_path,
                scopes=SCOPES,
                redirect_uri='http://localhost:8000/oauth2callback'
            )
            authorization_url, state = flow.authorization_url(access_type='offline')
            request.session['state'] = state
            request.session['email'] = email
            return redirect(authorization_url)
    else:
        form = AddAccountForm()
    return render(request, 'add_account.html', {'form': form})

@login_required
def oauth2callback(request):
    state = request.session['state']
    email = request.session['email']
    flow = Flow.from_client_secrets_file(
        credentials_path,
        scopes=SCOPES,
        state=state,
        redirect_uri='http://localhost:8000/oauth2callback'
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    creds_json = json.dumps({
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    })

    user_cred = UserCredentials(user=request.user, email=email, credentials=creds_json)
    user_cred.save()
    return redirect('home')

@login_required
def list_emails(request):
    user_accounts = UserCredentials.objects.filter(user=request.user)
    all_emails = []

    for account in user_accounts:
        creds = account.get_credentials()

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            account.save_credentials(creds)

        service = build('gmail', 'v1', credentials=creds)
        
        # Define search queries for different email types
        queries = {
            'primary': 'category:primary in:inbox',
            'spam': 'label:spam',
            'promotions': 'label:promotions'
        }
        
        emails_by_type = {}

        # Fetch emails for each query
        for label, query in queries.items():
            results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
            messages = results.get('messages', [])

            emails = []
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                email_data = {header['name']: header['value'] for header in headers}
                emails.append({
                    'subject': email_data.get('Subject'),
                    'from': email_data.get('From'),
                    'date': email_data.get('Date'),
                })

            emails_by_type[label] = emails

        all_emails.append({
            'account': account.email,
            'emails_by_type': emails_by_type
        })

    return render(request, 'list_emails.html', {'all_emails': all_emails})
